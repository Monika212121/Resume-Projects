from typing import List, Dict, Optional, Tuple, Any

from src.common.logging import logger
from src.common.entity.position import Waypoint
from src.common.entity.dump import DumpPointState
from src.common.utils.mission import MissionPhase
from src.common.action.bin_manager import BinManager
from src.common.entity.machine_types import MachineType
from src.common.utils.mission import get_target_distance
from src.common.simulation.sim_bridge import SimulationBridge
from src.common.utils.mission import is_reached_target, compute_yaw
from src.common.entity.dispatch import DispatchOrder, DispatchOutcome
from src.common.entity.manatee_communication import DumpInfo, ManateeMode, TaskStatus

from src.fly.stage3_decision.entity import DumpConfig

from src.manatee.stage3_action.navigation import BoundaryNavigator
from src.manatee.stage3_action.entity import ManateeActionConfig, MissionSubTask



class MissionPlanner:
    def __init__(self, action_config: ManateeActionConfig, dump_points: List[DumpConfig], simulation_bridge: SimulationBridge):
        self.action_cfg = action_config
        self.dump_points = dump_points
        self.sim_bridge = simulation_bridge

        self.HQ_point = self.action_cfg.mission.hq_point

        self.bin_manager = BinManager(bin_cfg= self.action_cfg.mission.bin_manager)
        self.navigator = BoundaryNavigator(navigation_config= self.action_cfg.mission.navigation)

        # Dict[dump id , projected point on boundary], Nearest projected dump point, on the current boundary edge
        self.dump_projected_points: Dict[int, Waypoint] = self.create_dump_projected_points_map()           
        self.mode = ManateeMode.IDLE
        self.phase = MissionPhase.SURFACE

        self.mission_state: Dict[str, Any] = {
            "operation_mode": ManateeMode.IDLE,
            "sub_task": None
        }
        
        self.freezed_state: Optional[Dict[str, Any]] = None
        self.step_retry_count = 0
        self.max_step_retry_count = 3

        self.cleaned_dump_ids = set()
        self.safe_distance = 50                                             # distance till which manatee won't patrol/shadow for Fish

        self.active_dispatch_order = None                                                                                       



    def create_dump_projected_points_map(self) -> Dict[int, Waypoint]:
        try:
            logger.info(f"MissionPlaneer -> create_dump_projected_points_map(), DUMP: {self.dump_points}")
            dump_projected_map: Dict[int, Waypoint] = {}        # {dump_id, projected_point}

            for dump in self.dump_points:
                dump_projection_point_on_boundary = self.navigator.get_boundary_projection(point= dump.position)
                dump_projected_map[dump.dump_id] = dump_projection_point_on_boundary

            logger.info(f"MissionPlaneer -> create_dump_projected_points_map(), DUMP PROJECTED MAP: {dump_projected_map}")
            return dump_projected_map


        except Exception as e:
            logger.error(f"Error occurred in MissionPlanner -> tick(), error: {e}")
            raise e
        


    def tick(self, dispatch_order: Optional[DispatchOrder]) -> DispatchOutcome:
        try:
            logger.info(f"MissionPlanner -> tick(): STARTS, dispatch_order: {dispatch_order}")

            # Scheduler already manages ownership (manatee_task)
            if dispatch_order is not None:
                self.active_dispatch_order = dispatch_order                 # rescue case / no active D.O.

            operation_status = TaskStatus.FAILED
            operation_issue = "No issue"
            cleaned_dump_ids = []

            # UNLOADING MANATEE'S BIN: 

            # If Manatee's bin is filled, first unload bin to the HQ, then resume current mission, if not, then IDLE/PATROL
            if self.bin_manager.is_bin_full():

                # Freezing current mission state, to resume current mission, after unloading
                if self.freezed_state is None:
                    self.freezed_state = {
                        "operation_mode": self.active_dispatch_order.operation_mode if self.active_dispatch_order else ManateeMode.IDLE,
                        "current_position": self.navigator.current_position
                    }

                logger.info(f"*****************freezed checkpoint: {self.freezed_state}********************")

                unloading_status = self.unload_manatee_bin()

                if unloading_status == TaskStatus.FAILED:
                    unloading_issue = "Simulation error"
                    logger.error(f"UNLOADING FAILED TO HQ, current position: {self.navigator.current_position}, issue: {unloading_issue}")

                elif unloading_status == TaskStatus.COMPLETED:
                    unloading_issue = "No issue"
                    self.freezed_state = None                                                               # Resets freezed state for future unloading process
                    logger.info(f"UNLOADING COMPLETED, current position: {self.navigator.current_position}")                    

                else:
                    logger.info(f"UNLOADING RUNNING, curretn position: {self.navigator.current_position}")
                    unloading_issue = "No issue, WIP"
                
                dispatch_result = DispatchOutcome(
                    dispatch_order= self.active_dispatch_order,
                    task_status= unloading_status,
                    issue= unloading_issue,
                    cleaned_dump_ids= cleaned_dump_ids
                )

                logger.info(f"MissionPlanner -> tick(): Unloading Manatee's Bin, dispatch_result: {dispatch_result}")
                return dispatch_result


            # No active task -> Idol / Patrol
            if self.active_dispatch_order is None:
                fish_pose = self.sim_bridge.get_robot_pose(robot= MachineType.FISH)
                if fish_pose is None:
                    logger.error("MissionPlanner -> tick(), fish position is invalid")

                    return DispatchOutcome(
                        dispatch_order= None,
                        task_status= TaskStatus.FAILED,
                        issue= "Fish position is invalid",
                        cleaned_dump_ids= cleaned_dump_ids
                    )

                fish_position = Waypoint(x= fish_pose[0], y= fish_pose[1], z= fish_pose[2])

                # IDLE / PATROL
                operation_status = self.handle_idle_or_patrol(fish_position= fish_position)

                if operation_status == TaskStatus.FAILED:
                    logger.info(f"MissionPlanner -> tick(), FAILED in IDLE/PATROL")
                    operation_issue = "PATROL failed due to simulation error"

                elif operation_status == TaskStatus.COMPLETED:
                    logger.info(f"MissionPlanner -> tick(), SUCCESS in IDLE/PATROL")
                    operation_issue = "No issue"

                else:
                    logger.info(f"MissionPlanner -> tick(), RUNNING IDLE/PATROL")
                    operation_issue = "No issue, WIP"

                return DispatchOutcome(
                    dispatch_order= self.active_dispatch_order,
                    task_status= operation_status,
                    issue= operation_issue,
                    cleaned_dump_ids= []
                )


            # If there is an active dispatch order, then process it.
            operation_mode = self.active_dispatch_order.operation_mode

            logger.info(f"MissionPlanner -> tick(), active dispatch_order: {self.active_dispatch_order}")

            # COLLECTION
            if operation_mode == ManateeMode.COLLECTION:
                logger.info("MODE = COLLECTION")

                if self.active_dispatch_order.dump_info is None:
                    logger.error("COLLECTION failed -> dump_info is None")

                    dispatch_result = DispatchOutcome(
                        dispatch_order= self.active_dispatch_order,
                        task_status= TaskStatus.FAILED,
                        issue= "No valid dump info provided",
                        cleaned_dump_ids= []
                    )

                    self.active_dispatch_order = None
                    return dispatch_result

                # Fetching target dump id
                target_dump_id = self.active_dispatch_order.dump_info.dump_id

                # Updating filled dump in simulation to enable dump mark as full
                self.sim_bridge.filled_dump_id = target_dump_id if target_dump_id not in self.cleaned_dump_ids else -1
                    
                operation_status = self.handle_collection(dump_info= self.active_dispatch_order.dump_info)

                if operation_status == TaskStatus.FAILED:
                    operation_issue = "COLLECTION failed due to simulation error"
                    logger.error(f"COLLECTION FAILED for dump_id: {target_dump_id}")

                elif operation_status == TaskStatus.COMPLETED:
                    logger.info(f"COLLECTION COMPLETED for dump_id: {target_dump_id}")
                    operation_issue = "No issue"
                    self.cleaned_dump_ids.add(target_dump_id)
                    cleaned_dump_ids.append(target_dump_id)
                    self.sim_bridge.filled_dump_id = -1
                    
                else:
                    logger.info(f"COLLECTION RUNNING for dump_id: {target_dump_id}")
                    operation_issue = "No issue, WIP"
                

                dispatch_result = DispatchOutcome(
                    dispatch_order= self.active_dispatch_order,
                    task_status= operation_status,
                    issue= operation_issue,
                    cleaned_dump_ids= cleaned_dump_ids
                )

                # Release the dispatch order lock, after it is processed completely (either SUCESS/FAIL)
                if operation_status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    self.active_dispatch_order = None

                logger.info(f"MissionPlanner -> tick(), dispatch_result: {dispatch_result}")
                return dispatch_result


            # RESCUE
            elif operation_mode == ManateeMode.RESCUE:
                logger.info("MODE = RESCUE")

                operation_status = self.handle_rescue(fish_position= self.active_dispatch_order.fish_position, all_dump_state= self.active_dispatch_order.all_dumps_state)
                if operation_status == TaskStatus.FAILED:
                    operation_issue = "RESCUE failed due to simulation error"
                    logger.error("RESCUE FAILED")
                    self.active_dispatch_order = None

                elif operation_status == TaskStatus.COMPLETED:
                    logger.info("RESCUE COMPLETED")
                    self.active_dispatch_order = None
                    self.mode = ManateeMode.IDLE

                else:
                    logger.info("RESCUE RUNNING")


            # FINAL SWEEP
            elif operation_mode == ManateeMode.FINAL_SWEEP:
                logger.info("MODE = FINAL SWEEP")
                operation_status, cleaned_dump_ids = self.handle_final_sweep(all_dump_state= self.active_dispatch_order.all_dumps_state)

                if operation_status == TaskStatus.FAILED:
                    operation_issue = "FINAL SWEEP failed due to simulation error"
                    logger.error("FINAL SWEEP FAILED")
                    self.active_dispatch_order = None

                elif operation_status == TaskStatus.COMPLETED:
                    logger.info("FINAL SWEEP COMPLETED")
                    self.active_dispatch_order = None
                    self.mode = ManateeMode.IDLE

                else:
                    logger.info("FINAL SWEEP RUNNING")


            # Unknown mode
            else:
                logger.error(f"Unknown operation mode: {operation_mode}")

                operation_status = TaskStatus.FAILED
                operation_issue = "Unknown operation mode"
                self.active_dispatch_order = None

            dispatch_result = DispatchOutcome(
                dispatch_order= self.active_dispatch_order,
                task_status= TaskStatus.FAILED,
                issue= operation_issue,
                cleaned_dump_ids= cleaned_dump_ids
            )

            logger.info(f"MissionPlanner -> tick(): ENDS, dispatch_result: {dispatch_result}")
            return dispatch_result


        except Exception as e:
            logger.error(f"Error occurred in MissionPlanner -> tick(), error: {e}", exc_info= True)
            raise e



    # PATROL/IDLE
    def handle_idle_or_patrol(self, fish_position: Waypoint) -> TaskStatus:               
        try:
            logger.info(f"MissionPlanner -> handle_idle_or_patrol(): STARTS")

            # IDLE
            if self.fish_is_near(fish_position= fish_position):
                logger.info("MissionPlanner -> handle_idle_or_patrol(), Fish is near, sitting IDLE")
                self.mode = ManateeMode.IDLE
                self.sim_bridge.display_current_phase(curr_mode= self.mode)
                return TaskStatus.COMPLETED
            
            # PATROL
            if self.mission_state["operation_mode"] != ManateeMode.PATROL:
                self.mission_state = {
                    "operation_mode": ManateeMode.PATROL,
                    "sub_task": MissionSubTask.GO_TO_PROJECTED_BOUNDARY_POINT,
                    "dump_point": None,
                    "projected_point": self.navigator.get_boundary_projection(point= fish_position)
                }

                self.mode = ManateeMode.PATROL
                self.sim_bridge.display_current_phase(curr_mode= self.mode)

            current_task = self.mission_state["sub_task"]
            proj_point = self.mission_state["projected_point"]

            if current_task == MissionSubTask.GO_TO_PROJECTED_BOUNDARY_POINT:
                next_position = self.navigator.step_boundary_edge()
                if not self.simulate_step_forward2(target_position = next_position):
                    logger.info(f"MissionPlanner -> handle_idle_or_patrol(): Error occurred in reaching next pos: {next_position}")
                    self.step_retry_count += 1
                    if self.step_retry_count > self.max_step_retry_count:
                        return TaskStatus.FAILED
                
                # Check if Manatee reached the projected boundary position, near Fish machine
                if self.navigator.is_close(a= self.navigator.current_position, b= proj_point):
                    logger.info(f"MissionPlanner -> handle_idle_or_patrol(): PATROLLING MISSION IS SUCCESSFUL")
                    #self.reset_mission_state()
                    return TaskStatus.COMPLETED

            logger.info(f"MissionPlanner -> handle_idle_or_patrol(): ENDS")
            return TaskStatus.RUNNING
        

        except Exception as e:
            logger.error(f"Error occurred in MissionPlanner -> handle_idle_or_patrol(), error: {e}")
            raise e



    def fish_is_near(self, fish_position: Waypoint) -> bool:
        try:
            is_fish_near: bool = True

            manatee_pos = self.navigator.current_position
            if fish_position is None:
                logger.error(f"MissionPlanner -> fish_is_near(), Fish pos is not valid")
                return is_fish_near

            # Calculating distance between Manatee and Fish machine
            distance = get_target_distance(current_pos= manatee_pos, target_pos= fish_position)

            is_fish_near = distance < self.safe_distance
            logger.info(f"MissionPlanner -> fish_is_near(), is_fish_near: {is_fish_near}")
            return is_fish_near
        

        except Exception as e:
            logger.error(f"Error occurred in MissionPlanner -> fish_is_near(), error: {e}")
            raise e
        


    def handle_collection(self, dump_info: DumpInfo) -> TaskStatus:
        try:
            logger.info(f"MissionPlaneer -> handle_collection(): STARTS, dump_info: {dump_info}, mode: {self.mode}")
            
            self.mode = ManateeMode.COLLECTION

            # Reinitialize mission state whenever entering COLLECTION from PATROL/IDLE/other modes
            if self.mission_state["operation_mode"] != ManateeMode.COLLECTION:
                self.mission_state = {
                    "operation_mode": ManateeMode.COLLECTION,
                    "sub_task": MissionSubTask.GO_TO_PROJECTED_BOUNDARY_POINT,
                    "dump_point": dump_info.dump_position,
                    "projected_point": self.dump_projected_points[dump_info.dump_id]
                }

            current_task = self.mission_state["sub_task"]
            proj_point = self.mission_state["projected_point"]
            dump_point = self.mission_state["dump_point"]

            logger.info(f"MissionPlaneer -> handle_collection(), MISSION STATE: {self.mission_state}")

            # Continue collection of dump garbage mission
            if current_task == MissionSubTask.GO_TO_PROJECTED_BOUNDARY_POINT:
                logger.info(f"MissionPlaneer -> handle_collection(), GO_TO_PROJECTED_BOUNDARY_POINT")
                next_position = self.navigator.step_boundary_edge()

                if not self.simulate_step_forward2(target_position = next_position):
                    logger.error(f"MissionPlanner -> handle_collection(): Error occurred in reaching next pos: {next_position}")
                    self.step_retry_count += 1
                    if self.step_retry_count > self.max_step_retry_count:
                        logger.error(f"MissionPlanner -> handle_collection(): Retry failed, in reaching projected boundary pos: {next_position}")  
                        return TaskStatus.FAILED

                # Advancing to next sub-task of the Collection mission
                if self.navigator.is_close(a= self.navigator.current_position, b= proj_point):
                    self.mission_state["sub_task"] = MissionSubTask.GO_TO_DUMP


            elif current_task == MissionSubTask.GO_TO_DUMP:
                logger.info(f"MissionPlaneer -> handle_collection(), GO_TO_DUMP")
                next_position = self.navigator.get_linear_step_to_destination(dump_info.dump_position)

                if not self.simulate_step_forward2(target_position = next_position):
                    logger.error(f"MissionPlanner -> handle_collection(): Error occurred in reaching next pos: {next_position}")
                    self.step_retry_count += 1
                    if self.step_retry_count > self.max_step_retry_count:
                        logger.error(f"MissionPlanner -> handle_collection(): Retry failed, in dump position: {dump_info.dump_position}")  
                        return TaskStatus.FAILED

                # Advancing to next sub-task of the Collection mission
                if self.navigator.is_close(a= self.navigator.current_position, b= dump_point):
                    self.mission_state["sub_task"] = MissionSubTask.COLLECT_DUMP


            elif current_task == MissionSubTask.COLLECT_DUMP:
                logger.info(f"MissionPlaneer -> handle_collection(), COLLECT_DUMP")
                #self.bin_manager.add_garbage(load_added= dump_info.dump_current_load)

                # Advancing to next sub-task of the Collection mission
                self.mission_state["sub_task"] = MissionSubTask.RETURN_TO_PROJECTED_BOUNDARY_POINT


            elif current_task == MissionSubTask.RETURN_TO_PROJECTED_BOUNDARY_POINT:
                logger.info(f"MissionPlaneer -> handle_collection(), RETURN_TO_PROJECTED_BOUNDARY_POINT")
                next_position = self.navigator.get_linear_step_to_destination(destination= proj_point)

                if not self.simulate_step_forward2(target_position = next_position):
                    logger.error(f"MissionPlanner -> handle_collection(): Error occurred in reaching proj next pos: {next_position}")
                    self.step_retry_count += 1
                    if self.step_retry_count > self.max_step_retry_count:
                        logger.error(f"MissionPlanner -> handle_collection(): Retry failed, in reaching projected boundary pos: {next_position}")      
                        return TaskStatus.FAILED

                # Advancing to next sub-task of the Collection mission
                if self.navigator.is_close(a= self.navigator.current_position, b= proj_point):
                    logger.info(f"MissionPlanner -> handle_collection(): COLLECTION MISSION IS SUCCESSFUL")

                    self.bin_manager.add_garbage(load_added= dump_info.dump_current_load)

                    self.reset_mission_state()
                    return TaskStatus.COMPLETED


            logger.info(f"MissionPlaneer -> handle_collection(): ENDS, COLLECTION RUNNING")
            return TaskStatus.RUNNING


        except Exception as e:
            logger.error(f"Error occurred in MissionPlanner -> handle_collection(), error: {e}")
            raise e



    def reset_mission_state(self):
        try:
            new_mission_state = {
                "operation_mode": ManateeMode.IDLE,
                "sub_task": None,
                "dump_point": None,
                "projected_point": None
            }

            self.mission_state = new_mission_state

            self.mode = ManateeMode.IDLE
            self.freezed_state = None
            self.step_retry_count = 0

            logger.info(f"MisssionPlanner -> reset_mission_state(): ENDS")
            return
        

        except Exception as e:
            logger.error(f"Error occurred in MissionPlanner -> reset_mission_state(), error: {e}")
            raise e



    def unload_manatee_bin(self) -> TaskStatus:
        try:
            logger.info(f"MisssionPlanner -> unload_manatee_bin(): STARTS, curr_load: {self.bin_manager.current_load}")
            
            self.mode = ManateeMode.UNLOADING_SELF_BIN
            current_task = self.mission_state["sub_task"]

            # For first time inside this if block, update current task
            if current_task not in [MissionSubTask.GO_TO_HQ, MissionSubTask.UNLOAD_SELF_BIN, MissionSubTask.RETURN_FROM_HQ]:
                current_task = MissionSubTask.GO_TO_HQ
                self.mission_state["sub_task"] = current_task
                
            # Unloading self bin, to dump all its collected garbage from dump points, to the HQ.
            if current_task == MissionSubTask.GO_TO_HQ:
                next_position = self.navigator.get_linear_step_to_destination(destination= self.HQ_point)

                if not self.simulate_step_forward2(target_position = next_position):
                    logger.error(f"MisssionPlanner -> unload_manatee_bin(): Error occurred in reaching the HQ: {next_position}")
                    
                    self.step_retry_count += 1
                    if self.step_retry_count > self.max_step_retry_count:
                        logger.error(f"MissionPlanner -> unload_manatee_bin(): Retry failed, in reaching next position: {next_position}") 
                        return TaskStatus.FAILED
                
                # Advancing to next sub-task of the Unloading mission
                if self.navigator.is_close(a= self.navigator.current_position, b= self.HQ_point):
                    self.mission_state["sub_task"] = MissionSubTask.UNLOAD_SELF_BIN
                    return TaskStatus.RUNNING
            

            elif current_task == MissionSubTask.UNLOAD_SELF_BIN:
                    logger.info(f"handle_collection(): MANATEE BIN is unloaded in HQ successfully")
                    self.mission_state["sub_task"] = MissionSubTask.RETURN_FROM_HQ
                    return TaskStatus.RUNNING


            elif current_task == MissionSubTask.RETURN_FROM_HQ:
                freezed_position = self.freezed_state["current_position"] if self.freezed_state else self.HQ_point

                next_position = self.navigator.get_linear_step_to_destination(destination= freezed_position)
                if not self.simulate_step_forward2(target_position = next_position):
                    logger.error(f"MisssionPlanner -> unload_manatee_bin(): Error occurred reaching the freezed point: {freezed_position}, curr pos: {self.navigator.current_position}, next pos: {next_position}")
                    
                    self.step_retry_count += 1
                    if self.step_retry_count > self.max_step_retry_count:
                        logger.error(f"MissionPlanner -> unload_manatee_bin(): Retry failed, in reaching next position: {next_position}") 
                        return TaskStatus.FAILED
                
                # Advancing to next sub-task of the Unloading mission, resuming its cleaning dump points mission
                if self.navigator.is_close(a= self.navigator.current_position, b= freezed_position):
                    logger.info(f"MisssionPlanner -> unload_manatee_bin(): MANATEE returned to the freezed position: {freezed_position}")
                    #self.mission_state["sub_task"] = freezed_current_task

                    # Reset Manatee's bin and freezed checkpoint
                    self.bin_manager.reset_bin()
                    self.freezed_state = None
                    return TaskStatus.COMPLETED
            
            
            logger.info(f"MisssionPlanner -> unload_manatee_bin(): ENDS, Manatee RUNNING UNLOADING SELF BIN")
            return TaskStatus.RUNNING


        except Exception as e:
            logger.error(f"Error occurred in MisssionPlanner -> unload_manatee_bin(), error: {e}")
            raise e



    # Bridge function between simulator and navigator
    def simulate_step_forward2(self, target_position: Waypoint) -> bool:
        try:
            logger.info(f"MissionPlanner -> simulate_step_forward2(): STARTS, before current postion: {self.navigator.current_position}")

            # Connecting PyBullet Simulation / real control
            # NOTE: Here, I am not passing target waypoint, I am passing the new target position

            # Computing orientation of Manatee machine
            yaw = compute_yaw(current_position= self.navigator.current_position, target_position = target_position)
            
            # Execute simulation step (teleport-based kinematic execution)
            self.sim_bridge.step(robot= MachineType.MANATEE, pose= target_position, robot_yaw = yaw, curr_operation_mode= self.mode)

            # Read back pose from simulation (after stepping)
            sim_curr_pose = self.sim_bridge.get_robot_pose(robot= MachineType.MANATEE)
            if sim_curr_pose is None:
                logger.error(f"MissionPlanner -> simulate_step_forward2(): SIMULATION ISSUE: Current Manatee machine's position cannot be retrieved from Simulation")
                return False
            
            # Retrieve the waypoint from Tuple[x,y,z,yaw]
            sim_current_position = Waypoint(sim_curr_pose[0], sim_curr_pose[1], sim_curr_pose[2])

            # Validate simulation result
            if not is_reached_target(current_position= sim_current_position, target_position= target_position):
                logger.error("MissionPlanner -> simulate_step_forward2(): "f"Simulation mismatch | sim={sim_curr_pose}, target={target_position}")
                logger.warning(f"SIM clamp applied: target_position: {target_position} → safe_position: {sim_curr_pose}")
                return False
            
            # Update Manatee machine's operation mode for this step
            self.sim_bridge.robot_controller.update_robot_state(robot_name= MachineType.MANATEE, current_phase= None, curr_mode= self.mode)

            # Commit Manatee machine pose, from simulation world, back to Navigation (single source of truth)
            self.navigator.current_position = sim_current_position
           
            logger.info(f"MissionPlanner -> simulate_step_forward2(): ENDS, after current position: {self.navigator.current_position}")
            return True

    
        except Exception as e:
            logger.error(f"Error occurred in MissionPlanner -> simulate_step_forward2(), error: {e}")
            raise e



    def handle_rescue(self, fish_position: Optional[Waypoint], all_dump_state: List[DumpPointState]) -> bool:
        try:
            logger.info(f"MissionPlanner -> handle_rescue(): STARTS")
            self.mode = ManateeMode.RESCUE
            
            if fish_position is None:
                logger.info(f"MissionPlanner -> handle_rescue(), There is no valid fish position provided.")
                return False
                               
            # Traverse towards the Fish machine
            reached_fish = self.simulate_step_forward2(target_position= fish_position)
            if not reached_fish:
                logger.error(f"MissionPlanner -> handle_rescue(), Error occurred in reaching Fish")
                return False

            # Manatee extract Fish machine inside it
            self.sim_bridge.robot_controller.remove_robot(MachineType.FISH)
            
            # Traverse to HQ, with Fish machine
            reached_HQ = self.simulate_step_forward2(target_position= self.HQ_point)
            if not reached_HQ:
                logger.error(f"MissionPlanner -> handle_rescue(), Error occurred in reaching the HQ")
                return False

            logger.info(f"^^^^^^^^^^^^^^^^^^^FINAL SWEEP^^^^^^^^^^^^^^^^^^^^^^^^^")
            # After Fish machine is extracted safely to HQ, perform final sweep to unload collected garbage from all 8 dump points          
            final_sweep_success, cleaned_dump_points = self.handle_final_sweep(all_dump_state= all_dump_state)
            if not final_sweep_success or (len(cleaned_dump_points) != len(all_dump_state)):
                logger.error(f"MissionPlanner -> handle_rescue(), Error occurred in final sweep, all dump points are not cleaned or Manatee couldn't reach HQ.")
                return False

            logger.info(f"MissionPlanner -> handle_rescue(): ENDS")
            return True
        

        except Exception as e:
            logger.error(f"Error occurred in MissionPlanner -> handle_rescue(), error: {e}")
            raise e
        


    def handle_final_sweep(self, all_dump_state: List[DumpPointState]) -> Tuple[bool,List[int]]:
        try:
            logger.info(f"MissionPlanner -> handle_final_sweep(): STARTS")
            self.mode = ManateeMode.FINAL_SWEEP

            final_sweep_success: bool = False                                                              
            cleaned_dump_points: List[int] = []                                                             # List of cleaned dump ids

            if len(all_dump_state) == 0:
                logger.info(f"MissionPlanner -> handle_final_sweep(): There is not a single dump provided.")
                return (final_sweep_success, cleaned_dump_points)

            # Collect garbage from all 8 dump points
            for dump in all_dump_state:
                dump_info = DumpInfo(dump_id= dump.dump_id, dump_position= dump.position, dump_current_load= dump.current_load)

                if dump.current_load > 0:
                    collected_garbage = self.handle_collection(dump_info= dump_info) 
                    if not collected_garbage: 
                        logger.info(f"handle_final_sweep(), Collection failed for dump_id: {dump_info.dump_id}")
                        continue

                # If dump point is empty or unloaded by Manatee, mark it as cleaned
                cleaned_dump_points.append(dump_info.dump_id)

            # After cleaning of last dump point, return back to the HQ.
            reached_HQ = self.execute_navigation_to(destination= self.HQ_point)
            if not reached_HQ:
                logger.info(f"MissionPlanner -> handle_final_sweep(), Cleaning is done but Error occurred in reaching the HQ")
                return (final_sweep_success, cleaned_dump_points)
            
            # Marking the final sweep mission as success, if Manatee returned to the HQ safely.
            final_sweep_success = True

            logger.info(f"MissionPlanner -> handle_final_sweep(): ENDS, cleaned dumps: {cleaned_dump_points}")
            return (final_sweep_success, cleaned_dump_points)

        
        except Exception as e:
            logger.error(f"Error occurred in MissionPlanner -> handle_final_sweep(), error: {e}")
            raise e
        
      

    def execute_navigation_to(self, destination: Waypoint, return_back: bool = False) -> bool:
        try:
            logger.info(f"MissionPlanner -> execute_navigation_to(): STARTS, destination: {destination}, returning: {return_back}")

            # List of positions, fish machine travels to reach destination (used when fish machien has to return start point)
            path_waypoints: List[Waypoint] = []

            # Appending the fist position of the path, (start_position = current position)
            start_position = self.navigator.current_position                     
            path_waypoints.append(start_position)
            
            # Stepping forward step-wise, till fish machine reached destination
            while not self.navigator.is_reached_destination(target_position= destination):

                # Defining current position and depth
                curr_pos = self.navigator.current_position
                curr_operation_depth = curr_pos.z

                # If currently in underwater, first ascend to the surface level, then approach the HQ.
                if curr_operation_depth < 0:
                    curr_surface_pos = Waypoint(curr_pos.x, curr_pos.y, 0.0)

                    # Ascend vertically upwards to surface level
                    reached_up = self.simulate_step_forward2(target_position= curr_surface_pos)
                    if not reached_up:
                        logger.info(f"MissionPlanner -> execute_navigation_to(): Error occurred in reaching the water surface level")
                        return False
                    path_waypoints.append(curr_surface_pos)
                    

                # Now the fish machine is currently in surface, so directly traverse to the destination.
                next_robot_pos = self.navigator.get_linear_step_to_destination(destination= destination)
                reached = self.simulate_step_forward2(target_position= next_robot_pos)
                if not reached:
                    logger.info(f"MissionPlanner -> execute_navigation_to(): Simulation failed in reaching the HQ")
                    return False
                path_waypoints.append(next_robot_pos)

            
            # Appending the last position of the path
            path_waypoints.append(destination)
            logger.info(f"MissionPlanner -> execute_navigation_to(): path_waypoints: {path_waypoints}, no. of points: {len(path_waypoints)}")


            # NOTE: If return_back = True, it means that we need to return to the start(mid way freezed) position too (in case of Garbage Unloading)
            if return_back:
                path_waypoints.reverse()                                                                        # refer ACTION_NOTES.md()

                # Return in the same path as unloading
                for point in path_waypoints:
                    reached = self.simulate_step_forward2(target_position= point)
                    if not reached:
                        logger.info(f"MissionPlanner -> execute_navigation_to(): Simulation failed in reaching the HQ")
                        return False
                    

                # Validate simulation result, if fish machine reached the start position or not
                navigation_success = self.navigator.is_close(a= self.navigator.current_position, b= start_position)
                if not navigation_success:
                    logger.info(f"MissionPlanner -> execute_navigation_to(): return is FAILED")
                    return False
                
                logger.info(f"MissionPlanner -> execute_navigation_to(): return is SUCCESSFUL")

            logger.info(f"MissionPlanner -> execute_navigation_to(): ENDS, final location: {self.navigator.current_position}")
            return True


        except Exception as e:
            logger.error(f"Error occurred in MissionPlanner -> execute_navigation_to(), error: {e}")
            raise e