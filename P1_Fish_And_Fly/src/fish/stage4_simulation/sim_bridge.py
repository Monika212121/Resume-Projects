import pybullet as p

from src.common.logging import logger
from src.common.utils.mission import get_target_distance
from src.common.entity.fish_machine_info import FishNavigationInfo

from src.fish.stage2_decision.entity import CategorizedObjects
from src.fish.stage3_action.entity import Waypoint, DumpLocation, MissionPhase
from src.fish.stage4_simulation.entity import SimulationConfig
from src.fish.stage4_simulation.object_manager import ObjectManager
from src.fish.stage4_simulation.pybullet_world import PyBulletWorld
from src.fish.stage4_simulation.robot_controller import RobotController



class SimulationBridge:
    def __init__(self, simulation_config: SimulationConfig, garbage_dump: DumpLocation):
        self.simulation_cfg = simulation_config

        self.ENABLE_SIM_GUI = self.simulation_cfg.visualization.enabled_gui
        self.spawn_visual_config = self.simulation_cfg.spawning.visual
        #self.spawn_zone_config = self.simulation_cfg.spawning.zone                                              # not used now (might be used later)

        self.world = PyBulletWorld(garbage_dump_location = garbage_dump)
        self.robot_controller = RobotController()
        self.object_manager = ObjectManager(visual_config = self.spawn_visual_config)

        self.simulation_started = False
        self.grasp_threshold: float = self.simulation_cfg.grasp_threshold



    def start(self):
        try:
            # NOTE: Ensure simulation is started exactly once

            # If Pybullet is already started, then skip
            if self.simulation_started:
                return

            # Connect to Pybullet and create the workspace
            self.world.connect(enable_GUI= self.ENABLE_SIM_GUI)

            # Spawn the Fish machine robot
            self.robot_controller.spawn_fish_robot()

            # Mark the simulation flag as started
            self.simulation_started = True
            return


        except Exception as e:
            logger.info(f"Error occurred in SimulationBridge -> start(), error: {e}")
            raise e



    def step(self, pose: Waypoint, curr_mission_phase: MissionPhase):
        try:
            # Traverse Fish robot to the given position
            self.robot_controller.teleport(pose, current_mission_phase= curr_mission_phase)

            # Update the camera view
            self.world.update_camera_follow_fish(pose)
            p.addUserDebugText(
                curr_mission_phase.name,
                [pose.x, pose.y, pose.z + 2],
                textColorRGB=[0, 1, 0],
                lifeTime=0.1
            )

            p.stepSimulation()

            # Updating lifecycle of all spawned objects
            self.object_manager.update_object_lifecycle()

            # Updating hazard blinking
            self.object_manager.update_hazard_blinking()

            return
        

        except Exception as e:
            logger.info(f"Error occurred in SimulationBridge -> step(), error: {e}")
            raise e
            


    def get_robot_pose(self):
        try:
            return self.robot_controller.get_fish_robot_pose()


        except Exception as e:
            logger.info(f"Error occurred in SimulationBridge -> get_robot_pose(), error: {e}")
            raise e


#----------------------------------------------------------------------------------------------------------------------------


    def update_all_objects_spawning(self, cat_objects: CategorizedObjects, fish_navigation_info: FishNavigationInfo) -> None:
        try:
            logger.info(f"SimulationBridge -> update_all_objects_spawning(): STARTS, categorized_objects: {cat_objects}, fish_nav_info: {fish_navigation_info}")

            # Flatten the categorized objects into 1 list
            all_objects = (cat_objects.collection_targets + cat_objects.environment_entities + cat_objects.navigation_hazards)

            self.object_manager.spawn_objects(objects= all_objects, fish_info = fish_navigation_info)

            logger.info(f"SimulationBridge -> update_all_objects_spawning(): ENDS")
            return 


        except Exception as e:
            logger.info(f"Error occurred in SimulationBridge -> update_all_objects_spawning(), error: {e}")
            raise e



    def try_collect_garbage(self, target_track_id: int) -> bool:
        try:
            logger.info(f"SimulationBridge -> try_collect_garbage(): STARTS, track_id:{ target_track_id}")
            
            # Validate garbage existence, in simulation world
            if not self.object_manager.exists(target_track_id):
                logger.info(f"SimulationBridge -> try_collect_garbage(): Garbage does not exist of track_id: {target_track_id}, or might be already collected and despawned")
                return True

            # Now, as given garbage exists in simulation world, we can perform collection operation

            # Retrieve garbage body_id
            garbage_body_id = self.object_manager.get_body_id(track_id= target_track_id)
            if garbage_body_id is None:
                logger.info(f"SimulationBridge -> try_collect_garbage(): Garbage is not found of track_id: {target_track_id}")
                return False

            # Retrieve Fish robot body_id
            fish_robot_body_id = self.robot_controller.get_fish_robot_body_id()
            if fish_robot_body_id is None:
                logger.info(f"SimulationBridge -> try_collect_garbage(): Fish robot does not exist in simulation world")
                return False
            
            # Stop the Fish robot
            self.robot_controller.stop_fish(body_id= fish_robot_body_id)
            
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

            logger.info(f"SimulationBridge -> try_collect_garbage(): SUCCESS, track_id={target_track_id} visually marked as collected")
            return True
                        

        except Exception as e:
            logger.info(f"Error occurred in SimulationBridge -> try_collect_garbage(), error: {e}")
            raise e



    def is_target_within_collection_range(self, track_id: int) -> bool:
        try:
            logger.info(f"SimulationBridge -> is_target_within_collection_range(): STARTS, track_id:{ track_id}")
            
            # Validate garbage existence, in simulation world
            if not self.object_manager.exists(track_id):
                logger.info(f"SimulationBridge -> is_target_within_collection_range(): Garbage does not exist of track_id: {track_id}")
                return False

            # Retrieve target position from the object metadata memory
            target_meta_data = self.object_manager.objects_meta[track_id]
            target_world_position = target_meta_data.spawn_world_position

            # Retrieve fish robot position
            fish_robot_world_position = self.robot_controller.get_fish_robot_pose()
            if fish_robot_world_position is None:
                logger.info(f"SimulationBridge -> is_target_within_collection_range(): Fish robot does not exist : {track_id}")
                return False
            
            # Calculate distance between fish machine and target in simulation world
            target_distance = get_target_distance(current_position= fish_robot_world_position, target_position= target_world_position)

            # Check if the given target is in grasp range of Fish robot or not
            target_in_range = target_distance < self.grasp_threshold

            logger.info(f"SimulationBridge -> is_target_within_collection_range(): ENDS, fish_pos:{fish_robot_world_position}, target_pos: {target_world_position}, target_in_range: {target_in_range}")
            return target_in_range            
                        

        except Exception as e:
            logger.info(f"Error occurred in SimulationBridge -> is_target_within_collection_range(), error: {e}")
            raise e