import time
from typing import Optional, Dict, Any, List

from common.entity.dispatch_order import DispatchOrder
from src.fly.stage1_action.entity import FishStatus, StateDeltas

from src.common.logging import logger
from src.common.utils.mission import is_reached_target
from src.common.projection.entity import FishFrameObject
from src.common.simulation.entity import SimulationConfig
from src.common.entity.fish_machine_info import FishNavigationInfo
from src.common.logging.telemetry_csv_logger import TelemetryCSVLogger
from src.common.alerts_and_notifications.notifier import AlertNotifier
from src.common.alerts_and_notifications.alert_types import AlertType, ErrorType
from src.common.alerts_and_notifications.notification_types import NotificationType

from src.fish.stage2_decision.entity import ActionIntent, CategorizedObjects
from src.fish.stage3_action.bin_manager import BinManager
from src.fish.stage3_action.manipulator import Manipulator
from src.fish.stage3_action.navigation import PathNavigator
from src.fish.stage3_action.unload_behavior import UnloadGarbageBehavior
from src.fish.stage3_action.entity import ActionConfig, MissionPhase, Depths, MissionCheckpoint, ActionStatus, ActionFeedback, Waypoint
from src.fish.stage4_simulation.sim_bridge import SimulationBridge



class MissionPlanner:
    """
    Contains and activates the mission plan layout for the fish machine.

    Responsibilities:
        - Phase management (SURFACE → DESCEND -> UNDERWATER → ASCEND -> RETURN_HQ) → DONE
        - Trigger navigation
        - Pause navigation when action is required
        - Resume after action feedback

    """
    def __init__(self, action_config: ActionConfig, simulation_config: SimulationConfig, telemetry_logger: TelemetryCSVLogger):
        self.cfg = action_config

        self.mission_cfg = self.cfg.mission
        self.cost_cfg = self.cfg.cost_model
        self.dump_location_cfg = self.cfg.dump_location

        self.notifier = AlertNotifier()   
        self.navigator = PathNavigator(navigation_cfg= self.mission_cfg.navigation)
        self.manipulator = Manipulator()
        self.garbage_unloader = UnloadGarbageBehavior(
            cost_cfg= self.cost_cfg, 
            notifier_obj= self.notifier, 
            navigator_obj= self.navigator, 
            garbage_dump= self.dump_location_cfg,
            depths = self.mission_cfg.depths
        )
        self.sim_bridge = SimulationBridge(simulation_config = simulation_config, garbage_dump = self.dump_location_cfg)

        self.navigator.set_path(start_position= self.mission_cfg.start_point)                               # setting first surface level path for navigation



    def tick(self, dispatch_order: DispatchOrder, hazard_objects: List[FishFrameObject]) -> bool:       
        try:
            logger.info(f"MissionPlanner -> tick(): STARTS, action_intent: {dispatch_order}, hazard_objects: {hazard_objects}")      

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
            if self.bin_manager.bin_is_full():
                self.phase = MissionPhase.UNLOADING

                best_dump_point = self.garbage_unloader.find_best_dump_point(current_position= self.freeze_mission_data.last_position)
                
                # First reach the best dump-point and then return to the freezed last position, from where bin unloading started
                is_reached_after_unload = self.execute_navigation_to(destination= best_dump_point, return_back= True)       # telemetry logged inside
                if not is_reached_after_unload:
                    logger.info(f"MissionPlanner -> tick(): Error occurred in unloading bin, Simulation error")
                    self.abort_mission()

                    feedback = ActionFeedback(
                        status= ActionStatus.FAILED,
                        track_id= action_intent.track_id if action_intent else -1,                                       # track_id = -1 means there is no target object
                        reason= "Unloading of bin is failed"
                    ) 
                    return feedback

                logger.info(f"MissionPlanner -> tick(): Bin unloaded successfully")

                # Reset bin load
                self.bin_manager.reset_bin()

                # Update garbage unloader
                self.garbage_unloader.resolve_unload_garbage()

                # Retrieve back the same phase before unloading started.
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
                        reason= "Moved forward because either the given target is not in reach or there is no object in current frame"
                    ) 

                    # Log the new position for trajectory visualization.
                    self.navigator.step_count += 1                                                          # Maintaining step count for trajectory logging.
                    self.navigator.log_trajectory_point() 

                else:
                    logger.info(f"MissionPlanner -> tick(): Simulation failed, error from Simulation module")
                    feedback = ActionFeedback(
                        status= ActionStatus.NONE,
                        track_id= target_id,
                        reason= "Simulator failed in moving a step forward"
                    )


            # 4. MISSION PHASE ADVANCEMENT: Mission advances to the next phase, when current phase is finished successfully.
            if self.navigator.path_is_finished():
                self._advance_phase()

            self.tick_count += 1
            logger.info(f"MissionPlanner -> tick(): ENDS, tick_count: {self.tick_count}, feedback: {feedback}")
            return feedback


        except Exception as e:
            logger.info(f"Error occurred in MissionPlanner -> tick(), error: {e}")
            raise e



    def get_telemetry_for_non_exposed_phases(self) -> StateDeltas:                                          #refer ACTION_NOTES.md(12)
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

            # Appending the fist position of the path, (start_position = current position)
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


    # bridge function between simulator and navigator
    def simulate_step_forward(self, target_position: Waypoint) -> bool:
        try:
            logger.info(f"MissionPlanner -> simulate_step_forward(): STARTS, before current postion: {self.navigator.current_position}")

            # Connecting PyBullet Simulation / real control
            # NOTE: Here, I am not passing target waypoint, I am passing the new target position (already calculated in step_forward())
            
            # Execute simulation step (teleport-based kinematic execution)
            self.sim_bridge.step(pose= target_position, curr_mission_phase= self.phase)

            # Read back pose from simulation (after stepping)
            sim_curr_pose = self.sim_bridge.get_robot_pose()
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

            # Commit Fish machine pose, from simulation world, back to Navigation (single source of truth)
            self.navigator.current_position = sim_current_position
            
            logger.info(f"MissionPlanner -> simulate_step_forward(): ENDS, after current position: {self.navigator.current_position}")
            return True

    
        except Exception as e:
            logger.info(f"Error occurred in MissionPlanner -> simulate_step_forward(), error: {e}")
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
            
            # Log intermediate motion steps, in `mission_telemetry_log.csv` file                                        # refer ACTION_NOTES.md(12)
            self.telemetry_logger.log_fish_machine_telemetry(delta= self.get_telemetry_for_non_exposed_phases())
            
            logger.info(f"MissionPlanner() -> execute_depth_transition(): ENDS, Depth transition is successful")
            return


        except Exception as e:
            logger.info(f"Error occurred in MissionPlanner -> execute_depth_transition(), error: {e}")
            raise e
        

