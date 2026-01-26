import time
from typing import Optional, Dict, Any

from src.common.logging import logger
from src.common.alerts_and_notifications.notifier import AlertNotifier
from src.common.alerts_and_notifications.alert_types import AlertType, ErrorType
from src.common.alerts_and_notifications.notification_types import NotificationType
from src.common.visualization.world_projection import WorldObject

from src.fish.stage2_decision.entity import ActionIntent
from src.fish.stage3_action.bin_manager import BinManager
from src.fish.stage3_action.navigation import PathNavigator
from src.fish.stage3_action.executor import ActionExecutor
from src.fish.stage3_action.pipeline import ActionPipeline
from src.fish.stage3_action.unload_behavior import UnloadGarbageBehavior
from src.fish.stage3_action.entity import Mission, Bin, Navigation, CostModel, DumpLocation, MissionPhase, Depths, MissionCheckpoint, ActionStatus, ActionFeedback



class FishMissionPlanner:
    """
    Contains and activates the mission plan layout for the fish machine.

    Responsibilities:
        - Phase management (SURFACE → DESCEND -> UNDERWATER → ASCEND -> RETURN → DONE)
        - Trigger navigation
        - Pause navigation when action is required
        - Resume after action feedback

    """
    def __init__(self, mission_cfg: Mission, bin_cfg: Bin, navigation_cfg: Navigation, cost_model_cfg: CostModel, dump_location_cfg: DumpLocation):
        self.mission_cfg = mission_cfg

        self.notifier = AlertNotifier()   
        self.bin_manager = BinManager(bin_cfg)
        self.navigator = PathNavigator(navigation_cfg= navigation_cfg)
        self.executor = ActionExecutor(bin_manager_obj= self.bin_manager)
        self.action_pipeline = ActionPipeline(executor_obj = self.executor)
        self.garbage_unloader = UnloadGarbageBehavior(
            cost_cfg= cost_model_cfg, 
            notifier_obj= self.notifier, 
            navigator_obj= self.navigator, 
            garbage_dump= dump_location_cfg,
            depths = self.mission_cfg.depths
        )

        self.mission_start_time = time.time()
        self.mission_end_time = time.time()
        self.phase = MissionPhase.SURFACE    
        self.depths: Depths = mission_cfg.depths                                                            # Mission state initiated
        self.active_target = None
        self.retry_count: int = 0
        self.max_retries: int = self.mission_cfg.limits.max_operation_retries
        self.lost_target: int = 0                                                                           # No. of lost targets
        self.max_target_loss: int = self.mission_cfg.limits.max_target_loss_ignore                          # Maximum no. of targets can be lost.

        self.navigator.set_path(depth = self.depths.surface, start_position= self.mission_cfg.start_point)  # setting first surface level path for navigation

        # TODO: REMOVE AFTER TESTING
        self.tick_count = 0


    def mission_is_active(self) -> bool:
        """
        Returns confirmation that mission is active or not.
        
        :param self: Belongs to the FishMissionPlanner class.
        :return: Confirmation whether mission is active/not.
        :rtype: bool
        """
        try:
            logger.info(f"FishMissionPlanner -> mission_is_active(): STARTS")

            # Mission is not active when its current phase is completed, aborted or failed.
            if self.phase in {MissionPhase.DONE, MissionPhase.ABORT, MissionPhase.FAILED}:
                logger.info(f"misssion_is_active(): Mission is not active, current state: {self.phase}")
                return False

            logger.info(f"FishMissionPlanner -> misssion_is_active(): ENDS")
            return True
    

        except Exception as e:
            logger.info(f"Error occurred in FishMissionPlanner -> mission_is_active(), error: {e}")
            raise e
        

    def action_is_allowed(self) -> bool:
        """
        Gate for the Action pipeline. Returns confirmation that action is allowed or not.
        
        :param self: Belongs to the FishMissionPlanner class.
        :return: Confirmation that action is allowed/not.
        :rtype: bool
        """
        try:
            logger.info(f"FishMissionPlanner -> action_is_allowed(): STARTS")

            # Action is allowed only when machine is cleaning at surface level(Phase1) and underwater level(Phase3).
            if self.phase in {MissionPhase.SURFACE, MissionPhase.UNDERWATER}:
                return True

            logger.info(f"FishMissionPlanner -> action_is_allowed(): ENDS")
            return False
        

        except Exception as e:
            logger.info(f"Error occurred in FishMissionPlanner -> action_is_allowed(), error: {e}")
            raise e
            


    def tick(self, action_intent: Optional[ActionIntent], world_object: Optional[WorldObject]) -> ActionFeedback:
        """
        Gate of Action pipeline. 

        Supervise and command the Fish machine's whole operation.
        
        Determines and trigger the different operations like: 
        - When to Unload garbage bin,
        - When to do Garbage collection,
        - When to Navigate forward,
        - And when to Advance phase.

        :param self: Belongs to FishMissionPlanner
        :param action_intent: Information of selected/locked target (VALUE / NONE).
        :type action_intent: Optional[ActionIntent]
        :param world_object: Information of target's location and distance in world frame.
        :type world_object: Optional[WorldObject]
        :param navigation_only: Flag signalling the task needs to be done (GARBAGE COLLECTION / NAVIGATION) 
        :type navigation_only: bool
        :return: Action feedback according to the action execution's result (status = SUCCESS / FAILED / MOVED_FORWARD / NONE)
        :rtype: ActionFeedback
        """
        
        try:
            logger.info(f"FishMissionPlanner -> tick(): STARTS, action_intent: {action_intent}, mission phase: {self.phase}")
            feedback : ActionFeedback         

            # Coordinates garbage collection, navigation and garbage unloading at same time.

            # 1. FREEZING CURRENT INFO: Saving the current mission data for future use.
            self.freeze_mission_data = MissionCheckpoint(
                last_phase= self.phase,
                last_position= self.navigator.current_position,
                last_timestamp= time.time()
            )

            # 2. UNLOADING BIN: Check if the dustbin is full or not, in case of full, first unload the bin, then proceed to execute action.
            if self.bin_manager.bin_is_full():
                self.phase = MissionPhase.UNLOADING

                bin_is_unloaded = self.garbage_unloader.unload_garbage(self.freeze_mission_data)
                if bin_is_unloaded:
                    logger.info(f"tick(): Bin unloaded successfully")

                    # Resets bin load
                    self.bin_manager.reset_bin()

                    # Retrieve back the same phase before unloading started.
                    self.phase = self.freeze_mission_data.last_phase

                else:
                    logger.info(f"tick(): Error occurred in unloading bin")
                    self._abort_mission()

                    feedback = ActionFeedback(
                        status= ActionStatus.FAILED,
                        track_id= None,
                        reason= "Unloading of bin is failed"
                    ) 
                    return feedback


            # NOTE: If action_intent = None, then world_object = None.

            # 3. Handle GARBAGE COLLECI and Navigation together.
                       
            # Case1: If the target is identified(action_intent = valid) and is within reach, then collect it.
            if action_intent and world_object and self.navigator.target_is_near(world_object):
                logger.info(f"garbage is near, we have to handle target at location: {action_intent.bbox}")
                feedback = self._handle_target(action_intent)                           # SUCCESS/FAILED

            # Case2: If the target is not identified / If there is no object in frame (action_intent = None)
            # Case3: If the given target is not within reach (action_intent = valid and target_is_near() = False), 
            # If both above cases, then move 1 step forward.
            else: 
                target_id = action_intent.track_id if action_intent else None           
                
                moved_forward = self.navigator.step()  
                if moved_forward:
                    feedback = ActionFeedback(
                        status= ActionStatus.MOVED_FORWARD,
                        track_id= target_id,
                        reason= "Either given target is not in reach or there is no object in current frame"
                    ) 
                else:
                    feedback = ActionFeedback(
                        status= ActionStatus.NONE,
                        track_id= target_id,
                        reason= "Navigator failed in stepping 1 step forward"
                    ) 
                                          
            # 4. MISSION PHASE ADVANCEMENT: Mission advances to the next phase, when current phase is finished successfully.
            if self.navigator.path_is_finished():
                self._advance_phase()

            self.tick_count += 1
            logger.info(f"FishMissionPlanner -> tick(): ENDS, tick_count: {self.tick_count}, feedback: {feedback}")
            return feedback


        except Exception as e:
            logger.info("Error occurred in FishMissionPlanner -> tick(), error: {e}")
            raise e



    def _handle_target(self, action_intent: ActionIntent) -> ActionFeedback:
        """
        Handles the target, implement action execution on the identifed target(action_intent) and also handle failure.

        Resets the active target and move forward.
        
        :param self: Belongs to FishMissionPlanner
        :param action_intent: Information of selected/locked target.
        :type action_intent: ActionIntent
        :return: Returns the action feedback, received from action execution(status = SUCCESS/FAILED)
        :rtype: ActionFeedback
        """

        try:
            logger.info(f"FishMisssionPlanner -> handle_target(): STARTS")

            # 1. Pause navigation
            self.navigator.pause()

            # 2. Recognize the current target.
            self.active_target = action_intent.track_id

            # 3. Collect the target garbage.
            feedback = self.action_pipeline.run(action_intent)

            # 4. Handle the target.
            # If target is collected successfully or after retry, reset the active target.
            if feedback.status == ActionStatus.SUCCESS or self._handle_failure(action_intent):

                # Update the feedback status to SUCCESS, if handle_failure() succeeds.
                if feedback.status == ActionStatus.FAILED:                                          # first attempt failed but retry is success
                    feedback.status = ActionStatus.SUCCESS                                          # refer ACTION_NOTE.md (5)
                    feedback.reason = "Action retry is success"

                # Update the bin's load by 1 collected garbage.
                self.bin_manager.add_garbage()

            # In both cases status = SUCCESS or status = FAILED, then reset the active target and resume moving forward.
            # Reset the active target and resume moving forward.
            self.active_target = None
            self.retry_count = 0
            self.navigator.resume()

            logger.info(f"FishMisssionPlanner -> handle_target(): ENDS")
            return feedback


        except Exception as e:
            logger.info(f"Error occurred in FishMissionPlanner -> handle_target(), error: {e}")
            raise e 



    def _handle_failure(self, action_intent: ActionIntent) -> bool:
        try:
            logger.info(f"handle_failure(): STARTS")

            # Soft retry
            while self.retry_count < self.max_retries:
                logger.info(f"handle_failure(): retry count: {self.retry_count + 1}")

                feedback = self.action_pipeline.run(action_intent)
                if feedback and feedback.status == ActionStatus.SUCCESS:
                    logger.info(f"handle_failure(): Soft retry is successful in retry count: {self.retry_count+ 1}")
                    return True

                self.retry_count += 1

            # NOTE: It means the target is lost. If number of failed target loss is reached to a limit, then abort the mission and return to HQ immediately.

            # Hard abort
            self.lost_target += 1
            if self.lost_target >= self.max_target_loss:
                self.phase = MissionPhase.ABORT
                self._abort_mission()

            logger.info(f"handle_failure(): ENDS, lost target : {self.lost_target}")
            return False


        except Exception as e:
            logger.info(f"Error occurred in FishMissionPlanner -> handle_failure(), error: {e}")
            raise e
        


    def _advance_phase(self):
        try:
            logger.info(f"FishMissionPlanner -> advance_phase(): STARTS, before position: {self.navigator.current_position}")

            if self.phase == MissionPhase.SURFACE:
                self.notifier.raise_notification(NotificationType.SURFACE_CLEANING_ENDED, "SURFACE CLEANING SUCCESS", {})

                self.phase = MissionPhase.DESCEND

                # Move downwards to reach the underwater level.
                underwater_start_pos = self.mission_cfg.end_point               # (100, 100, 0)
                underwater_start_pos.z = self.depths.underwater                 # (100, 100, -8)
            
                reached_down = self.navigator.move_to(target_point= underwater_start_pos)
                if not reached_down:            
                    # Raise alert and abort the mission immediately.
                    logger.info(f"advance_phase(): Error occurred in DESCENDING, error: {ErrorType.EXECUTION_ERROR}")
                    self.notifier.raise_alert(alert_type= AlertType.DESCEND_FAIL, message= "descend fail", metadata = {"error": ErrorType.EXECUTION_ERROR, "current location": self.navigator.current_position})
                    self.phase = MissionPhase.ABORT
                    self._abort_mission()

                logger.info(f"advance_phase(): Mission phase DESCEND is successful. Advance to next phase -> UNDERWATER")
                self.notifier.raise_notification(NotificationType.MACHINE_DESCENDED, "DESCEND SUCCESS", {})

                # Advance to the next phase.
                self.phase = MissionPhase.UNDERWATER

                # Underwater cleaning path is set for navigator.
                self.navigator.set_path(depth = self.depths.underwater, start_position= underwater_start_pos)
                logger.info(f"advance_phase(): Path is set for underwater level cleaning, speed: {self.navigator.curr_speed}")

                # Machine's speed is adjusted to underwater level.
                self.navigator.curr_speed = self.navigator.speeds.underwater
                logger.info(f"advance_phase(): Machine's speed is changed for underwater level, updated speed: {self.navigator.curr_speed}")


            elif self.phase == MissionPhase.UNDERWATER:
                self.notifier.raise_notification(NotificationType.UNDERWATER_CLEANING_ENDED, "UNDERWATER CLEANING SUCCESS", {})

                self.phase = MissionPhase.ASCEND

                # Move upwards to reach the surface level.
                reached_up = self.navigator.move_to(target_point= self.mission_cfg.start_point)
                if not reached_up:
                    # Raise alert and abort the mission immediately.
                    logger.info(f"advance_phase(): Error occurred in ASCENDING, error: {ErrorType.EXECUTION_ERROR}")
                    self.notifier.raise_alert(alert_type= AlertType.ASCEND_FAIL, message= "ascend fail", metadata = {"error": ErrorType.EXECUTION_ERROR, "current location": self.navigator.current_position})
                    self.phase = MissionPhase.ABORT
                    self._abort_mission()

                logger.info(f"advance_phase(): Mission phase ASCEND is successful. CLEANING is done successfully. Advance to next phase -> RETURN")
                self.notifier.raise_notification(NotificationType.MACHINE_ASCENDED, "ASCEND SUCCESS", {})

                # Advance to the next phase.
                self.phase = MissionPhase.RETURN
                
                # Returning to the HQ, from mission start point.
                hq_pos = self.mission_cfg.hq_point

                reached_HQ = self.navigator.move_to(target_point= hq_pos)
                if not reached_HQ:
                    # Raise alert and retry the return.
                    logger.info(f"advance_phase(): Error occurred in RETURNING TO HQ, error: {ErrorType.EXECUTION_ERROR}")
                    self.notifier.raise_alert(alert_type= AlertType.HQ_RETURN_FAIL, message= "return fail", metadata = {"error": ErrorType.EXECUTION_ERROR, "current location": self.navigator.current_position})
                    self._abort_mission()

                logger.info(f"advance_phase(): Mission phase RETURN TO HQ is successful.")
                self.notifier.raise_notification(NotificationType.REACHED_HEADQUARTER, "HQ RETURN IS SUCCESS", {})

                self.phase = MissionPhase.DONE

                # Raise notification for successful mission completion.
                self.mission_end_time = time.time()
                self.notifier.raise_notification(NotificationType.MISSION_COMPLETED, "MISSION IS SUCCESSFUL", {"mission_finish_at": self.mission_end_time})
                logger.info(f"advance_phase(): Mission is completed successfully.")

            logger.info(f"FishMissionPlanner -> advance_phase(): ENDS, final position: {self.navigator.current_position}")
            return


        except Exception as e:
            logger.info(f"Error occurred in FishMissionPlanner -> advance_phase(), error: {e}")
            raise e
        


    def _abort_mission(self):
        try:
            logger.info(f"abort_mission(): STARTS, reason to abort: {self.phase}")

            self.freeze_mission_data = MissionCheckpoint(
                last_phase= self.phase,
                last_position= self.navigator.current_position,
                last_timestamp= time.time()
            )
         
            # Return to the HQ immediately.
            curr_pos = self.navigator.current_position
            curr_level = curr_pos.z

            # Case1: If currently in surface level, directly approach HQ.
            if curr_level == self.depths.surface:
                reached_HQ = self.navigator.move_to(target_point= self.mission_cfg.hq_point)
                if not reached_HQ:
                    logger.info(f"abort_mission(): Error occurred in reaching the HQ")
                    self._get_manual_help()
                    return


            # Case2: If currently in underwater, first ascend to the surface level, then approach the HQ.
            else: 
                # first move up to the surface
                curr_pos.z = self.depths.surface
                reached_up = self.navigator.move_to(target_point= curr_pos)
                if not reached_up:
                    logger.info(f"abort_mission(): Error occurred in reaching the water surface level.")
                    self._get_manual_help()
                    return

                # then move towards HQ.
                reached_HQ = self.navigator.move_to(target_point= self.mission_cfg.hq_point)
                if not reached_HQ:
                    logger.info(f"abort_mission(): Error occurred in reaching the HQ")
                    self._get_manual_help()
                    return
                
            # Handle abort cases.
            # Case1: If returning to HQ is failed, then it means cleaning is already completed.
            # Reached HQ after retry, means the mission is completed sucessfully.
            if self.phase == MissionPhase.RETURN:
                logger.info(f"Cleaning process is already completed and now reached the HQ too after retry.")
                self.phase = MissionPhase.DONE
            
            # Case2: If the mission is aborted in middle of cleaning.
            if self.phase == MissionPhase.ABORT:
                self.notifier.raise_alert(AlertType.HARD_ABORT, "Mission aborted in middle of water body cleaning", {"last_active_checkpoint": self.freeze_mission_data})
                self.phase = MissionPhase.FAILED

            if self.phase == MissionPhase.UNLOADING:
                self.notifier.raise_alert(AlertType.UNLOADING_FAIL, "Mission aborted in middle of unloading garbage process", {"last_active_checkpoint": self.freeze_mission_data})
                self.phase = MissionPhase.FAILED

            logger.info(f"abort_mission(): ENDS, reached HQ on its own, CHECK-> curr_pos: {self.navigator.current_position}, curr phase: {self.phase}")
            return


        except Exception as e:
            logger.info(f"Error occurred in FishMissionPlanner -> abort_mission(), error: {e}")
            raise e



    def _get_manual_help(self):
        try:
            logger.info(f"FishMissionPlanner() -> get_manual_help(): STARTS")

            meta : Dict[Any, Any] = {
                "current time": time.time(),
                "last location": self.navigator.current_position,
                "current phase": self.phase
            }

            self.notifier.raise_alert(AlertType.MACHINE_FAILURE, "NEEDS HUMAN SUPPORT, PLEASE SEND HELP FROM THE HQ", metadata= meta)
            logger.info(f"FishMissionPlanner() -> get_manual_help(): ENDS")
            return
        

        except Exception as e:
            logger.info(f"Error occurred in FishMissionPlanner -> get_manual_help(), error: {e}")
            raise e
    
