import time
from typing import Optional, List, Tuple

from src.common.logging import logger
from src.common.utils.mission import MissionPhase
from src.common.action.bin_manager import BinManager
from src.common.utils.mission import is_reached_target
from src.common.entity.machine_types import MachineType
from src.common.projection.entity import FishFrameObject
from src.common.simulation.sim_bridge import SimulationBridge
from src.common.utils.path_cost_calculator import PathCostCalculator
from src.common.logging.telemetry_csv_logger import TelemetryCSVLogger
from src.common.alerts_and_notifications.notifier import AlertNotifier
from src.common.entity.fish_communication import DumpEvent, FishNavigationInfo
from src.common.alerts_and_notifications.alert_types import AlertType, ErrorType
from src.common.alerts_and_notifications.notification_types import NotificationType

from src.fly.stage3_decision.entity import DumpConfig, FishStatus, StateDeltas

from src.fish.stage2_decision.entity import ActionIntent, CategorizedObjects
from src.fish.stage3_action.manipulator import Manipulator
from src.fish.stage3_action.navigation import PathNavigator
from src.fish.stage3_action.entity import ActionConfig, Depths, MissionCheckpoint, ActionStatus, ActionFeedback, Waypoint



class MissionPlanner:
    """
    Contains and activates the mission plan layout for the fish machine.

    Responsibilities:
        - Phase management (SURFACE → DESCEND -> UNDERWATER → ASCEND -> RETURN_HQ) → DONE
        - Trigger navigation
        - Pause navigation when action is required
        - Resume after action feedback

    """
    def __init__(self, action_config: ActionConfig, telemetry_logger: TelemetryCSVLogger, dump_points: List[DumpConfig], simulation_bridge: SimulationBridge):
        self.cfg = action_config

        self.mission_cfg = self.cfg.mission
        self.cost_cfg = self.cfg.cost_model
        self.dump_points = dump_points

        self.notifier = AlertNotifier()   
        self.bin_manager = BinManager(bin_cfg= self.mission_cfg.bin_manager)
        self.navigator = PathNavigator(navigation_cfg= self.mission_cfg.navigation)
        self.manipulator = Manipulator()
        self.cost_calculator = PathCostCalculator(cost_model_cfg= self.cost_cfg, dump_points = self.dump_points)
        #self.sim_bridge = SimulationBridge(simulation_config = simulation_config, dump_points_info = self.dump_points)            # Connection to PyBullet Simulation
        self.sim_bridge = simulation_bridge                                                                 # shared simulation

        self.phase: MissionPhase = MissionPhase.SURFACE
        self.depths: Depths = self.mission_cfg.depths                                                       # Mission state initiated
        self.active_target: Optional[int] = None
        self.retry_count: int = 0
        self.max_retries: int = self.mission_cfg.limits.max_operation_retries
        self.lost_target: int = 0                                                                           # No. of lost targets
        self.max_target_loss: int = self.mission_cfg.limits.max_target_loss_ignore                          # Maximum no. of targets can be lost.
        self.step_retry_count: int = 0
        self.max_step_retry_count: int = self.mission_cfg.limits.max_step_retry_ignore                      # Maximum no. of steps that can be lost, before asking Manatee's help        

        self.navigator.set_path(depth = self.depths.surface, start_position= self.mission_cfg.start_point)  # Setting first surface level path for navigation

        # TODO: REMOVE AFTER TESTING
        self.tick_count: int = 0
        self.telemetry_logger = telemetry_logger                                                            # To log intermediate phases, refer ACTION_NOTES.md(12)



    def tick(self, action_intent: Optional[ActionIntent], selected_target: Optional[FishFrameObject], categorized_objects: CategorizedObjects, locked_dump_ids: List[int]) -> ActionFeedback:
        """
        Gate of Action pipeline. 

        Supervise and command the Fish machine's whole operation.
        
        Determines and trigger the different operations like: 
        - When to Unload garbage bin,
        - When to do Garbage collection,
        - When to Navigate forward,
        - And when to Advance phase.

        :param self: Belongs to the MissionPlanner class
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
            logger.info(f"MissionPlanner -> tick(): STARTS, action_intent: {action_intent}, mission phase: {self.phase}")
            feedback : ActionFeedback   
            dump_event: Optional[DumpEvent] = None
            need_manatee_help: bool = False

            # NOTE: Implementing `Perception-driven Digital twin simulation`
            
            # Start Simulation
            #self.sim_bridge.start()     

            # Retrieve Fish machine's current navigation information(will be used in spawning)
            fish_nav_info = FishNavigationInfo(
                position= self.navigator.current_position,
                direction= self.navigator.curr_fish_direction
            )

            # Spawn all objects in front of Fish machine 
            if categorized_objects:
                self.sim_bridge.update_all_objects_spawning(cat_objects= categorized_objects, fish_navigation_info = fish_nav_info)
        

            # Coordinates Garbage collection, Navigation and Garbage unloading

            # 1. FREEZING CURRENT INFO: Saving the current mission data (for future use).
            self.freeze_mission_data = MissionCheckpoint(
                last_phase= self.phase,
                last_position= self.navigator.current_position,
                last_timestamp= time.time()
            )

            # 2. UNLOADING BIN: Check if the dustbin is full or not, in case of full, first unload the bin, then proceed to execute action.
            if self.bin_manager.is_bin_full():
                self.phase = MissionPhase.UNLOADING

                dump_event, need_manatee_help = self.unload_fish_bin(current_position= self.freeze_mission_data.last_position, locked_dump_ids = locked_dump_ids)
                if need_manatee_help:
                    feedback = ActionFeedback(
                       status= ActionStatus.FAILED,
                       track_id= action_intent.track_id if action_intent else -1,
                       need_manatee_help= need_manatee_help,
                       reason= "Issue in Unloading fish bin, Simulation error",
                       dump_event= dump_event 
                    )
                    return feedback

                # Retrieve back the same phase before unloading started an continue mission.
                self.phase = self.freeze_mission_data.last_phase


            # NOTE: If action_intent = None, then selected_object = None.

            # 3. Handles GARBAGE COLLECTION and NAVIGATION together.
           
            # Case1: If the target is identified(action_intent = valid), and is withing collection range, then collect it.
            if action_intent and action_intent.track_id and selected_target and self.sim_bridge.is_target_within_collection_range(track_id= action_intent.track_id):
                logger.info(f"MissionPlanner -> tick(): Target identified at relative position: {selected_target.relative_position}")
                feedback = self._handle_target(garbage_track_id = action_intent.track_id)                                               # SUCCESS/FAILED

            # Case2: If the target is not identified / If there is no object in frame (action_intent = None)
            # Case3: If the given target is not within reach (action_intent = valid and target_is_near() = False), 
            # If both above cases, then move 1 step forward.
            else:
                target_id = action_intent.track_id if action_intent else -1                                                             # refer ACTION_NOTES.md(11)  

                # NOTE: If target_id == -1, then it means no valid target is present, else it means the target is too far                         
                next_robot_position = self.navigator.get_next_position_in_path()

                # SIMULATION for moving 1 step forward
                moved_in_sim = self.simulate_step_forward(target_position= next_robot_position)
                if moved_in_sim:
                    feedback = ActionFeedback(
                        status= ActionStatus.MOVED_FORWARD,
                        track_id= target_id,
                        need_manatee_help= need_manatee_help,                                               # False
                        reason= "Moved forward because either the given target is not in reach or there is no object in current frame",
                        dump_event= dump_event
                    ) 

                    # Log the new position for trajectory visualization.
                    self.navigator.step_count += 1                                                          # Maintaining step count for trajectory logging.
                    self.navigator.log_trajectory_point() 

                else:
                    logger.info(f"MissionPlanner -> tick(): Simulation failed, error from Simulation module")
                    if self.step_retry_count >= self.max_step_retry_count:
                        need_manatee_help = self.abort_mission()

                        feedback = ActionFeedback(
                            status= ActionStatus.NONE,
                            track_id= target_id,
                            need_manatee_help= need_manatee_help,
                            reason= "Simulator failed in moving a step forward and retry count exceeded",
                            dump_event= dump_event
                        )
                        return feedback

                    self.step_retry_count += 1


            # 4. MISSION PHASE ADVANCEMENT: Mission advances to the next phase, when current phase is finished successfully.
            if self.navigator.path_is_finished():
                self._advance_phase()

            self.tick_count += 1
            logger.info(f"MissionPlanner -> tick(): ENDS, tick_count: {self.tick_count}, feedback: {feedback}")
            return feedback


        except Exception as e:
            logger.info(f"Error occurred in MissionPlanner -> tick(), error: {e}")
            raise e



    def unload_fish_bin(self, current_position: Waypoint, locked_dump_ids: List[int]) -> Tuple[Optional[DumpEvent], bool]:
        try:
            dump_event: Optional[DumpEvent] = None
            need_manatee_help: bool = False

            # Finding the nearest, cheapest dump point (out of 8 dump points)
            best_dump_point = self.cost_calculator.find_best_dump_point(current_position= current_position, locked_dump_ids = locked_dump_ids)
            
            # First reach the best dump-point and then return to the freezed last position, from where bin unloading process started
            is_reached_after_unload = self.execute_navigation_to(destination= best_dump_point.position, return_back= True)       # telemetry logged inside
            if not is_reached_after_unload:
                logger.info(f"MissionPlanner -> unload_fish_bin(): Error occurred in unloading bin, Simulation error")
                need_manatee_help = self.abort_mission()                                                    # refer ACTION_NOTES.md(13)
                return dump_event, need_manatee_help                                                        # o/p = None, True/False

            # Creating DumpEvent after returning back to the freezed checkpoint position 
            dump_event = DumpEvent(dump_id= best_dump_point.dump_id, load_added= self.bin_manager.current_load)

            # Reset bin load
            self.bin_manager.reset_bin()

            logger.info(f"MissionPlanner -> unload_fish_bin(): Bin unloaded successfully")
            return dump_event, need_manatee_help                                                            # o/p = value, False


        except Exception as e:
            logger.info(f"Error occurred in MissionPlanner -> unload_fish_bin(), error: {e}")
            raise e
        


    def get_telemetry_for_non_exposed_phases(self) -> StateDeltas:                                          # refer ACTION_NOTES.md(12)
        try:
            # Non exposed Phases: ASCEND | DESCEND | ABORT | RETURN_HQ | UNLOADING

            telemetry = StateDeltas(
                mission_phase= self.phase.name,
                fish_state= FishStatus.ALIVE.name,
                fish_x= self.navigator.current_position.x,
                fish_y= self.navigator.current_position.y,
                fish_z= self.navigator.current_position.z,
                surface_coverage_pct= 0.0,
                underwater_coverage_pct= 0.0,
                communication_delta= 0.0,
                fish_progress_delta= 0.0,
                silence_delta= 0.0
            )

            return telemetry


        except Exception as e:
            logger.info(f"Error occurred in MissionPlanner -> get_telemetry_for_non_exposed_phases(), error: {e}")
            raise e



    def execute_navigation_to(self, destination: Waypoint, return_back: bool = False) -> bool:
        try:
            logger.info(f"MissionPlanner -> execute_navigation_to(): STARTS, destination: {destination}, returning: {return_back}")

            # List of positions, fish machine travels to reach destination (used when fish machien has to return start point)
            path_waypoints: List[Waypoint] = []

            # Appending the fish position of the path, (start_position = current position)
            start_position = self.freeze_mission_data.last_position                     
            path_waypoints.append(start_position)
            
            # Stepping forward step-wise, till fish machine reached destination
            while not self.navigator.is_reached_destination(target_position= destination):

                # Defining current position and depth
                curr_pos = self.navigator.current_position
                curr_operation_depth = curr_pos.z

                # If currently in underwater, first ascend to the surface level, then approach the HQ.
                if curr_operation_depth == self.depths.underwater:
                    curr_surface_pos = Waypoint(curr_pos.x, curr_pos.y, self.depths.surface)

                    # Ascend vertically upwards to surface level
                    reached_up = self.simulate_step_forward(target_position= curr_surface_pos)
                    if not reached_up:
                        logger.info(f"MissionPlanner -> execute_navigation_to(): Error occurred in reaching the water surface level")
                        return False
                    
                    path_waypoints.append(curr_surface_pos)
                    
                    # Log intermediate motion steps, in `mission_telemetry_log.csv` file                                        # refer ACTION_NOTES.md(12)
                    self.telemetry_logger.log_fish_machine_telemetry(delta= self.get_telemetry_for_non_exposed_phases())


                # Now the fish machine is currently in surface, so directly traverse to the destination.
                next_robot_pos = self.navigator.get_linear_step_to_destination(destination= destination)
                reached = self.simulate_step_forward(target_position= next_robot_pos)
                if not reached:
                    logger.info(f"MissionPlanner -> execute_navigation_to(): Simulation failed in reaching the HQ")
                    return False
                
                path_waypoints.append(next_robot_pos)

                # Log intermediate motion steps, in `mission_telemetry_log.csv` file
                self.telemetry_logger.log_fish_machine_telemetry(delta= self.get_telemetry_for_non_exposed_phases())
            
            # Appending the last position of the path
            path_waypoints.append(destination)
            logger.info(f"MissionPlanner -> execute_navigation_to(): path_waypoints: {path_waypoints}, no. of points: {len(path_waypoints)}")


            # NOTE: If return_back = True, it means that we need to return to the start(mid way freezed) position too (in case of Garbage Unloading)
            if return_back:
                path_waypoints.reverse()                                                                        # refer ACTION_NOTES.md()

                # Return in the same path as unloading
                for point in path_waypoints:
                    reached = self.simulate_step_forward(target_position= point)
                    if not reached:
                        logger.info(f"MissionPlanner -> execute_navigation_to(): Simulation failed in reaching the HQ")
                        return False
                    
                    # Log intermediate motion steps, in `mission_telemetry_log.csv` file
                    self.telemetry_logger.log_fish_machine_telemetry(delta= self.get_telemetry_for_non_exposed_phases())

                # Validate simulation result, if fish machine reached the start position or not
                navigation_success = is_reached_target(current_position= self.navigator.current_position, target_position= start_position)
                if not navigation_success:
                    logger.info(f"MissionPlanner -> execute_navigation_to(): In {self.phase.name} phase, return is FAILED")
                    return False
                
                logger.info(f"MissionPlanner -> execute_navigation_to(): In {self.phase.name} phase, return is SUCCESSFUL")

            logger.info(f"MissionPlanner -> execute_navigation_to(): ENDS, final location: {self.navigator.current_position}")
            return True


        except Exception as e:
            logger.info(f"Error occurred in MissionPlanner -> execute_navigation_to(), error: {e}")
            raise e      



    def abort_mission(self) -> bool:
        "Returns boolean to indicate whether it needs help to reach HQ or not"
        try:
            logger.info(f"MissionPlanner -> abort_mission(): STARTS, Last phase before abort: {self.phase}")

            # Saving the current mission data, before proceeding to the destination
            self.freeze_mission_data = MissionCheckpoint(
                last_phase= self.phase,
                last_position= self.navigator.current_position,
                last_timestamp= time.time()
            )
         
            # Update the mission's phase to ABORT (Used in Simulation)
            self.phase = MissionPhase.ABORT

            # Return to the HQ immediately

            # Set destination to the Head Quarter and move step-wise to reach there. 
            HQ_point = self.mission_cfg.hq_point
            is_reached_HQ = self.execute_navigation_to(destination = HQ_point, return_back= False)
            if not is_reached_HQ:
                logger.info(f"MissionPlanner -> abort_mission(): Simulation failed in reaching the HQ, get_manatee_help: {True}")
                return True

            self.notifier.raise_alert(AlertType.HARD_ABORT, "Mission aborted in middle of water body cleaning", {"last_active_checkpoint": self.freeze_mission_data})

            logger.info(f"MissionPlanner -> abort_mission(): ENDS, CHECK-> POSITION MUST BE HQ: {self.navigator.current_position}, get_manatee_help: {False}")
            return False


        except Exception as e:
            logger.info(f"Error occurred in MissionPlanner -> abort_mission(), error: {e}")
            raise e



    def _handle_target(self, garbage_track_id: int) -> ActionFeedback:
        """
        Handles the target, implement action execution on the identifed target(action_intent) and also handle failure.

        Resets the active target and move forward.
        
        :param self: Belongs to MissionPlanner
        :param action_intent: Information of selected/locked target.
        :type action_intent: ActionIntent
        :return: Returns the action feedback, received from action execution(status = SUCCESS/FAILED)
        :rtype: ActionFeedback
        """
        try:
            logger.info(f"MissionPlanner -> handle_target(): STARTS")

            # Pause navigation
            self.navigator.pause()

            # Execute target collection in simulation world 
            sim_collected = self.sim_bridge.try_collect_garbage(target_track_id= garbage_track_id)

            # Update garbage's grasp status and creates feedback
            feedback = self.manipulator.resolve_garbage_collection(garbage_track_id= garbage_track_id, sim_collected= sim_collected)

            # Update the garbage bin load, based on the garbage collection status
            if feedback.status == ActionStatus.COLLECTED or self._handle_failure(garbage_track_id= garbage_track_id):

                # Update the feedback status to SUCCESS, if handle_failure() succeeds.
                if feedback.status == ActionStatus.FAILED:                                                  # first attempt failed but retry is success
                    feedback.status = ActionStatus.COLLECTED                                                # refer ACTION_NOTE.md (5)
                    feedback.reason = "Action retry is success"

                # Update the Fish bin's load by 1 collected garbage.
                self.bin_manager.add_garbage(load_added= 1)

            # Reset the active target, regardless of current target's feedback
            self.retry_count = 0

            # Resume navigation
            self.navigator.resume()

            logger.info(f"MissionPlanner -> handle_target(): ENDS")
            return feedback


        except Exception as e:
            logger.info(f"Error occurred in MissionPlanner -> handle_target(), error: {e}")
            raise e



    def _handle_failure(self, garbage_track_id: int) -> bool:
        try:
            logger.info(f"MissionPlanner -> handle_failure(): STARTS")

            # Soft retry
            while self.retry_count < self.max_retries:
                logger.info(f"MissionPlanner -> handle_failure(): retry count: {self.retry_count + 1}")

                # Execute garbage collection in Simulation
                sim_collect_retry = self.sim_bridge.try_collect_garbage(target_track_id= garbage_track_id)

                feedback = self.manipulator.resolve_garbage_collection(garbage_track_id= garbage_track_id, sim_collected= sim_collect_retry)
                if feedback and feedback.status == ActionStatus.COLLECTED:
                    logger.info(f"MissionPlanner -> handle_failure(): Soft retry is successful in retry count: {self.retry_count+ 1}")
                    return True

                self.retry_count += 1

            # NOTE: It means the target is lost. If number of failed target loss exceeds limit, then abort the mission and return to HQ immediately.

            # Hard abort
            self.lost_target += 1
            if self.lost_target >= self.max_target_loss:
                self.phase = MissionPhase.ABORT
                self.abort_mission()

            logger.info(f"MissionPlanner -> handle_failure(): ENDS, lost target : {self.lost_target}")
            return False


        except Exception as e:
            logger.info(f"Error occurred in MissionPlanner -> handle_failure(), error: {e}")
            raise e


    # bridge function between simulator and navigator
    def simulate_step_forward(self, target_position: Waypoint) -> bool:
        """
        Apply a precomputed robot pose to the simulation.

        IMPORTANT:
        - Motion computation is performed in Navigation.
        - Simulation acts as a state executor and visual/physics mirror only.

        Do NOT add motion integration or stepping logic here unless
        motion ownership is explicitly moved out of Navigation.
    
        
        :param self: Belongs to the PathNavigator class
        :param target_position: The computed target position, the Fish machine needs to reach.
        :type target_position: Waypoint
        :param sim_dt: The time difference for calculating incremental motion(not used currently)
        :type sim_dt: float
        :return: Returns confirmation whether the Simulation movement executed successfully or not.
        :rtype: bool
        """
        try:
            logger.info(f"MissionPlanner -> simulate_step_forward(): STARTS, before current postion: {self.navigator.current_position}")

            # Connecting PyBullet Simulation / real control
            # NOTE: Here, I am not passing target waypoint, I am passing the new target position (already calculated in step_forward())
            
            # Execute simulation step (teleport-based kinematic execution)
            self.sim_bridge.step(robot= MachineType.FISH, pose= target_position, curr_mission_phase= self.phase)

            # Read back pose from simulation (after stepping)
            sim_curr_pose = self.sim_bridge.get_robot_pose(robot= MachineType.FISH)
            if sim_curr_pose is None:
                logger.info(f"MissionPlanner -> simulate_step_forward(): SIMULATION ISSUE: Current Fish machine's position cannot be retrieved from Simulation")
                return False
            
            # Retrieve the waypoint from Tuple[x,y,z,yaw]
            sim_current_position = Waypoint(sim_curr_pose[0], sim_curr_pose[1], sim_curr_pose[2])

            # Validate simulation result
            if not is_reached_target(current_position= sim_current_position, target_position= target_position):
                logger.error("MissionPlanner -> simulate_step_forward(): "f"Simulation mismatch | sim={sim_curr_pose}, target={target_position}")
                logger.warning(f"SIM clamp applied: target_position: {target_position} → safe_position: {sim_curr_pose}")
                return False

            # Update Fish machine state for this step
            self.sim_bridge.robot_controller.update_robot_state(robot_name= MachineType.FISH, current_phase= self.phase, curr_mode= None)

            # Commit Fish machine pose, from simulation world, back to Navigation (single source of truth)
            self.navigator.current_position = sim_current_position
            
            logger.info(f"MissionPlanner -> simulate_step_forward(): ENDS, after current position: {self.navigator.current_position}")
            return True

    
        except Exception as e:
            logger.info(f"Error occurred in MissionPlanner -> simulate_step_forward(), error: {e}")
            raise e



    def _advance_phase(self):
        try:
            logger.info(f"MissionPlanner -> advance_phase(): STARTS, before position: {self.navigator.current_position}")

            if self.phase == MissionPhase.SURFACE:
                self.notifier.raise_notification(NotificationType.SURFACE_CLEANING_ENDED, "SURFACE CLEANING SUCCESS", {})

                # Advance to the next phase: SURFACE -> DESCEND, moving vertically downwards, to reach the underwater level
                self.phase = MissionPhase.DESCEND
                underwater_start_pos = self.mission_cfg.navigation.end_point                                # (110, 110, 0)
                underwater_start_pos.z = self.depths.underwater                                             # (110, 110, -8)            # changed depth
                self._execute_depth_transition(target_position= underwater_start_pos)                       # telemetry logged inside

                # Advance to the next phase: DESCEND -> UNDERWATER, moving in underwater level, updated Fish machine's speed, for underwater navigation
                self.phase = MissionPhase.UNDERWATER
                self.navigator.set_path(depth = self.depths.underwater, start_position= underwater_start_pos)
                self.navigator.curr_speed = self.navigator.speeds.underwater
                logger.info(f"MissionPlanner -> advance_phase(): Path and speed are set, for underwater level cleaning, current speed: {self.navigator.curr_speed}")


            elif self.phase == MissionPhase.UNDERWATER:
                self.notifier.raise_notification(NotificationType.UNDERWATER_CLEANING_ENDED, "UNDERWATER CLEANING SUCCESS", {})

                # Advance to the next phase: UNDERWATER -> ASCEND, moving upwards to reach the surface level
                self.phase = MissionPhase.ASCEND                                                            # (10, 10, -8)
                self._execute_depth_transition(target_position= self.mission_cfg.navigation.start_point)    # (10, 10, 0)               # changed depth  

                # Advance to the next phase: ASCEND -> RETURN_HQ, returning to the Base HQ, from allowed workspace's start point.
                self.phase = MissionPhase.RETURN_HQ
                reached_HQ = self.simulate_step_forward(target_position= self.mission_cfg.hq_point)
                if not reached_HQ:
                    self.notifier.raise_alert(alert_type= AlertType.HQ_RETURN_FAIL, message= "return fail", metadata = {"error": ErrorType.EXECUTION_ERROR, "current location": self.navigator.current_position})
                    self.abort_mission()

                self.notifier.raise_notification(NotificationType.REACHED_HEADQUARTER, "HQ RETURN IS SUCCESS", {})
                
                # Log intermediate motion steps, in `mission_telemetry_log.csv` file                        , refer ACTION_NOTES.md(12)
                self.telemetry_logger.log_fish_machine_telemetry(delta= self.get_telemetry_for_non_exposed_phases())

                # Marking the mission as DONE, raising notification of SUCCESSFUL MISSION COMPLETION and stopping this project execution
                self.phase = MissionPhase.DONE
                self.notifier.raise_notification(NotificationType.MISSION_COMPLETED, "MISSION IS SUCCESSFUL", {"mission_finish_at": time.time()})
                

            logger.info(f"MissionPlanner -> advance_phase(): ENDS, final position: {self.navigator.current_position}")
            return


        except Exception as e:
            logger.info(f"Error occurred in MissionPlanner -> advance_phase(), error: {e}")
            raise e


    
    def _execute_depth_transition(self, target_position: Waypoint):
        try:
            logger.info(f"MissionPlanner() -> execute_depth_transition(): STARTS")

            meta = {"error": ErrorType.EXECUTION_ERROR, "current location": self.navigator.current_position}
            alert_type = AlertType.DESCEND_FAIL if self.phase == MissionPhase.DESCEND else AlertType.ASCEND_FAIL
            notif_type = NotificationType.MACHINE_DESCENDED if self.phase == MissionPhase.DESCEND else NotificationType.MACHINE_ASCENDED

            is_reached = self.simulate_step_forward(target_position= target_position)
            if not is_reached:
                self.notifier.raise_alert(alert_type= alert_type, message= alert_type.value, metadata = meta)
                self.phase = MissionPhase.ABORT
                self.abort_mission()

            self.notifier.raise_notification(notification_type= notif_type, message= notif_type.value, metadata= meta)
            
            # Log intermediate motion steps, in `mission_telemetry_log.csv` file                            # refer ACTION_NOTES.md(12)
            self.telemetry_logger.log_fish_machine_telemetry(delta= self.get_telemetry_for_non_exposed_phases())
            
            logger.info(f"MissionPlanner() -> execute_depth_transition(): ENDS, Depth transition is successful")
            return


        except Exception as e:
            logger.info(f"Error occurred in MissionPlanner -> execute_depth_transition(), error: {e}")
            raise e