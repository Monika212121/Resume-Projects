import pybullet as p

from typing import List

from streamlit import rerun

from src.common.logging import logger
from src.common.entity.position import Waypoint
from src.common.utils.mission import MissionPhase
from src.common.entity.machine_types import MachineType
from src.common.utils.mission import get_target_distance
from src.common.simulation.entity import SimulationConfig
from src.common.simulation.camera_manager import CameraManager
from src.common.simulation.object_manager import ObjectManager
from src.common.simulation.pybullet_world import PyBulletWorld
from src.common.entity.manatee_communication import ManateeMode
from src.common.simulation.robot_controller import RobotController
from src.common.entity.fish_communication import FishNavigationInfo
from src.common.simulation.constants import FISH_TEXT_COLOR, MANATEE_TEXT_COLOR

from src.fly.stage3_decision.entity import DumpConfig

from src.fish.stage2_decision.entity import CategorizedObjects



class SimulationBridge:
    def __init__(self, simulation_config: SimulationConfig, dump_points_info: List[DumpConfig]):
        self.simulation_cfg = simulation_config

        self.ENABLE_SIM_GUI = self.simulation_cfg.visualization.enabled_gui
        self.spawn_visual_config = self.simulation_cfg.spawning.visual
        #self.spawn_zone_config = self.simulation_cfg.spawning.zone                                              # not used now (might be used later)

        self.world = PyBulletWorld(dump_points_info = dump_points_info)
        self.robot_controller = RobotController()
        self.object_manager = ObjectManager(visual_config = self.spawn_visual_config)
        self.camera_manager = CameraManager()

        self.simulation_started = False
        self.grasp_threshold: float = self.simulation_cfg.grasp_threshold
        self.recording_enabled: bool = self.simulation_cfg.record_output

        self.filled_dump_id = -1
        self.manatee_text_id = -1

        self.fish_phase: MissionPhase = MissionPhase.SURFACE
        self.manatee_mode: ManateeMode = ManateeMode.IDLE
        


    def start(self):
        try:
            # NOTE: Ensure simulation is started exactly once

            # If Pybullet is already started, then skip
            if self.simulation_started:
                return

            # Connect to Pybullet and create the workspace
            self.world.connect(enable_GUI= self.ENABLE_SIM_GUI)

            # Getting all machines's visual configurations
            fish_robot_visual_info = self.spawn_visual_config.machines[0]
            manatee_robot_visual_info = self.spawn_visual_config.machines[1]

            # Spawn all the robots, Fish and Manatee
            self.robot_controller.spawn_robot(robot_name= MachineType.FISH, body_info = fish_robot_visual_info)
            self.robot_controller.spawn_robot(robot_name= MachineType.MANATEE, body_info = manatee_robot_visual_info)           

            # Mark the simulation flag as started
            self.simulation_started = True
            return


        except Exception as e:
            logger.error(f"Error occurred in SimulationBridge -> start(), error: {e}")
            raise e



    def stop(self):
        try:
            # Disconnect to Pybullet 
            if self.simulation_started:
                self.world.shutdown()

            # Release the simulation recorder
            #self.world.recorder.stop()

            # Mark the simulation flag as stopped
            self.simulation_started = False
            return


        except Exception as e:
            logger.error(f"Error occurred in SimulationBridge -> stop(), error: {e}")
            raise e


    def display_current_phase(self, curr_mode: ManateeMode):
        try:
            pos= self.get_robot_pose(robot= MachineType.MANATEE)
            if pos is None:
                logger.error(f"SimulationBridge -> display_current_phase(), Manatee pos is not valid")
                return 
            
            pose = Waypoint(x= pos[0], y= pos[1], z= pos[2])
            logger.info(f"SimulationBridge -> display_current_phase(), Manatee_position: {pose}")

            self.manatee_text_id = p.addUserDebugText(
                curr_mode.name,
                [pose.x, pose.y, pose.z + 2],
                textColorRGB= MANATEE_TEXT_COLOR[curr_mode],
                lifeTime= 0,                                                # persistent
                replaceItemUniqueId= self.manatee_text_id,
            )
            return
        

        except Exception as e:
            logger.error(f"Error occurred in SimulationBridge -> display_current_phase(), error: {e}")
            raise e



    def step(
            self, 
            robot: MachineType, 
            pose: Waypoint, 
            robot_yaw: float, 
            extraTxt: str = "",
            curr_mission_phase: MissionPhase = MissionPhase.SURFACE, 
            curr_operation_mode: ManateeMode = ManateeMode.IDLE
        ):

        try:

            # Initialize debug ids once
            if not hasattr(self, "fish_text_id"):
                self.fish_text_id = -1

            if not hasattr(self, "manatee_text_id"):
                self.manatee_text_id = -1

            # Traverse Fish robot to the given position
            if robot == MachineType.FISH:
                self.fish_phase = curr_mission_phase
                self.robot_controller.teleport_fish_robot(pose= pose, robot_yaw = robot_yaw, current_mission_phase= curr_mission_phase, debug_id= self.fish_text_id)

                debug_text = extraTxt if extraTxt != "" else curr_mission_phase.name

                # Updating debug text and displaying above Fish robot
                self.fish_text_id = p.addUserDebugText(
                    debug_text,
                    [pose.x, pose.y, pose.z + 2],
                    textColorRGB= FISH_TEXT_COLOR[curr_mission_phase],
                    lifeTime= 0,                                                                            # persistent
                    replaceItemUniqueId= self.fish_text_id,
                )

            else:
                self.manatee_mode = curr_operation_mode
                self.robot_controller.teleport_manatee_robot(pose= pose, robot_yaw = robot_yaw, current_mission_mode = curr_operation_mode, debug_id= self.manatee_text_id)

                debug_text = extraTxt if extraTxt != "" else curr_operation_mode.name

                # Updating debug text and displaying above Manatee robot
                if curr_operation_mode != ManateeMode.UNLOADING_SELF_BIN:
                    self.manatee_text_id = p.addUserDebugText(
                        debug_text,
                        [pose.x, pose.y, pose.z + 2],
                        textColorRGB=[1, 1, 1],                                                             # white for normal operation modes
                        lifeTime=0,                                                                         # persistent
                        replaceItemUniqueId = self.manatee_text_id
                    )

            p.stepSimulation()

            self.update_world()

            # Record the Simulation visualization
            if self.recording_enabled:
                self.world.recorder.record(target = pose)

            return
        

        except Exception as e:
            logger.error(f"Error occurred in SimulationBridge -> step(), error: {e}")
            raise e
            
    

    def update_world(self):
        try:
            # Updating lifecycle of all spawned objects
            self.object_manager.update_object_lifecycle()

            # Updating hazard blinking
            self.object_manager.update_hazard_blinking()

            # Updating dump points
            self.world.update_dump_blinking(dump_id= self.filled_dump_id)

            self.camera_manager.update_keyboard_controls()

            fish_pose = self.get_robot_pose(robot= MachineType.FISH)
            manatee_pose = self.get_robot_pose(robot= MachineType.MANATEE)

            fish_wp = Waypoint(*fish_pose[:3]) if fish_pose else None
            manatee_wp = Waypoint(*manatee_pose[:3]) if manatee_pose else None

            self.camera_manager.update_camera(fish_pose= fish_wp, manatee_pose= manatee_wp)
            return


        except Exception as e:
            logger.error(f"Error occurred in SimulationBridge -> update_world(), error: {e}")
            raise e    



    def get_robot_pose(self, robot: MachineType):
        try:
            return self.robot_controller.get_robot_pose(robot= robot)


        except Exception as e:
            logger.error(f"Error occurred in SimulationBridge -> get_robot_pose(), error: {e}")
            raise e


#----------------------------------------------------------------------------------------------------------------------------


    def update_all_objects_spawning(self, cat_objects: CategorizedObjects, fish_navigation_info: FishNavigationInfo) -> None:
        try:
            logger.debug(f"SimulationBridge -> update_all_objects_spawning(): STARTS, categorized_objects: {cat_objects}, fish_nav_info: {fish_navigation_info}")

            # Flatten the categorized objects into 1 list
            all_objects = (cat_objects.collection_targets + cat_objects.environment_entities + cat_objects.navigation_hazards)

            self.object_manager.spawn_objects(objects= all_objects, fish_info = fish_navigation_info)

            logger.debug(f"SimulationBridge -> update_all_objects_spawning(): ENDS")
            return 


        except Exception as e:
            logger.error(f"Error occurred in SimulationBridge -> update_all_objects_spawning(), error: {e}")
            raise e



    def try_collect_garbage(self, target_track_id: int) -> bool:
        try:
            logger.debug(f"SimulationBridge -> try_collect_garbage(): STARTS, track_id:{ target_track_id}")
            
            # Validate garbage existence, in simulation world
            if not self.object_manager.exists(target_track_id):
                logger.error(f"SimulationBridge -> try_collect_garbage(): Garbage does not exist of track_id: {target_track_id}, or might be already collected and despawned")
                return True

            # Now, as given garbage exists in simulation world, we can perform collection operation

            # Retrieve garbage body_id
            garbage_body_id = self.object_manager.get_body_id(track_id= target_track_id)
            if garbage_body_id is None:
                logger.error(f"SimulationBridge -> try_collect_garbage(): Garbage is not found of track_id: {target_track_id}")
                return False

            # Retrieve Fish robot body_id
            fish_robot_body_id = self.robot_controller.get_robot_body_id(robot_name= MachineType.FISH)
            if fish_robot_body_id is None:
                logger.error(f"SimulationBridge -> try_collect_garbage(): Fish robot does not exist in simulation world yet")
                return False
            
            # Stop the Fish robot
            self.robot_controller.stop_robot(body_id= fish_robot_body_id)
            
            # Change visual color of spawned garbage (RED -> GREEN)
            p.changeVisualShape(
                objectUniqueId=garbage_body_id,
                linkIndex=-1,
                rgbaColor=[0.2, 1.0, 0.0, 1.0],                                                              # Bright Green (RGBA) = collected
                specularColor=[1.0, 1.0, 0.2]                                                                # Glow effect
            )

            # Mark internal object's state from ACTIVE -> COLLECTED (Just for simulation internal marking, this status is not being used in backend code logic)
            self.object_manager.mark_collected(track_id= target_track_id)

           # NOTE: No need to resume the Fish robot, as it automatically moves in `step()` command in next tick()

            logger.debug(f"SimulationBridge -> try_collect_garbage(): SUCCESS, track_id={target_track_id} visually marked as collected")
            return True
                        

        except Exception as e:
            logger.error(f"Error occurred in SimulationBridge -> try_collect_garbage(), error: {e}")
            raise e



    def is_target_within_collection_range(self, track_id: int) -> bool:
        try:
            logger.debug(f"SimulationBridge -> is_target_within_collection_range(): STARTS, track_id:{ track_id}")
            
            # Validate garbage existence, in simulation world
            if not self.object_manager.exists(track_id):
                logger.error(f"SimulationBridge -> is_target_within_collection_range(): Garbage does not exist of track_id: {track_id}")
                return False

            # Retrieve target position from the object metadata memory
            target_meta_data = self.object_manager.objects_meta[track_id]
            target_world_position = target_meta_data.spawn_world_position

            # Retrieve fish robot position
            fish_robot_world_position = self.robot_controller.get_robot_pose(robot= MachineType.FISH)
            if fish_robot_world_position is None:
                logger.error(f"SimulationBridge -> is_target_within_collection_range(): Fish robot does not exist : {track_id}")
                return False
            
            # Calculate distance between fish machine and target in simulation world
            fish_pos = Waypoint(fish_robot_world_position[0], fish_robot_world_position[1], fish_robot_world_position[2])
            target_pos = Waypoint(target_world_position[0], target_world_position[1], target_world_position[2])
            target_distance = get_target_distance(current_pos= fish_pos, target_pos= target_pos)

            # Check if the given target is in grasp range of Fish robot or not
            target_in_range = target_distance < self.grasp_threshold

            logger.debug(f"SimulationBridge -> is_target_within_collection_range(): ENDS, fish_pos:{fish_robot_world_position}, target_pos: {target_world_position}, target_in_range: {target_in_range}")
            return target_in_range            
                        

        except Exception as e:
            logger.error(f"Error occurred in SimulationBridge -> is_target_within_collection_range(), error: {e}")
            raise e