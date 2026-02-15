import pybullet as p
from typing import Dict

from src.common.logging import logger
from src.common.projection.entity import FishFrameObject

from src.fish.stage3_action.entity import Waypoint
from src.fish.stage5_simulation.pybullet_world import PyBulletWorld
from src.fish.stage5_simulation.robot_controller import RobotController
from src.fish.stage5_simulation.object_manager import ObjectManager
from src.fish.stage5_simulation.entity import SimulationVisualization



class SimulationBridge:
    def __init__(self, simulation_cfg: SimulationVisualization):
        self.ENABLE_SIM_GUI = simulation_cfg.enabled_gui

        self.world = PyBulletWorld()
        self.robot_controller = RobotController()
        self.object_manager = ObjectManager()

        self.simulation_started = False



    def start(self):

        # If Pybullet is already started, then skip
        if self.simulation_started:
            return

        # Connect to Pybullet and create the workspace
        self.world.connect(enable_GUI= self.ENABLE_SIM_GUI)

        # Spawn the Fish machine robot
        self.robot_controller.spawn_fish_robot()

        # Mark the simulation flag as started
        self.simulation_started = True



    def step(self, pose: Waypoint, curr_mission_phase: str):

        # Traverse Fish robot to the given position waypoint
        self.robot_controller.teleport(pose)

        # Update the camera view
        self.world.update_camera_follow_fish(pose)
        p.addUserDebugText(
            curr_mission_phase,
            [pose.x, pose.y, pose.z + 2],
            textColorRGB=[0, 1, 0],
            lifeTime=0.1
        )

        p.stepSimulation()

        # Maintaining last fish position, for finding fish direction
        self.last_fish_position = pose



#----------------------------------------------------------------------------------------------------------------------------

    def update_garbage_spawning(self, fish_frame_objects: Dict[int, FishFrameObject], curr_fish_position: Waypoint, curr_fish_direction: int) -> None:
        try:
            logger.info(f"SimulationBridge -> update_garbage_spawning(): STARTS, len(objects): {len(fish_frame_objects)}")

            for track_id, obj in fish_frame_objects.items():

                # Case1: If current garbage is already spawned and is active, then skip spawning it
                if self.object_manager.exists(track_id):
                    logger.info(f"SimulationBridge -> update_garbage_spawning(): track_id: {track_id} already exists")
                    continue


                # Case2: If current garbage is new in simulation, then transform them into world frame and then spawn.

                # Create a world object for the garbage, received in fish frame
                garbage_world_object = self.object_manager.create_sim_world_object_from_fish_frame(fish_frame_obj= obj, fish_pos= curr_fish_position, fish_direction = curr_fish_direction)

                # Spawn the new garbage object, in a distance(= OFFSET), in front
                self.object_manager.spawn_garbage(world_obj= garbage_world_object)


            logger.info(f"SimulationBridge -> update_garbage_spawning(): ENDS")
            return 


        except Exception as e:
            logger.info(f"Error occurred in SimulationBridge -> update_garbage_spawning(), error: {e}")
            raise e



    def get_fish_curr_direction(self, curr_position: Waypoint) -> int:
        try:
            logger.info(f"ObjectManager -> get_curr_fish_direction(), STARTS")

            # Calculating delta in x_axis, for fish robot
            last_x_coord = self.last_fish_position.x
            curr_x_coord = curr_position.x
            logger.info(f"ObjectManager -> get_curr_fish_direction(), last_pos: {self.last_fish_position}, curr_pos: {curr_position}")
            fish_delta_x = curr_x_coord - last_x_coord

            # If dir = 1, then fish moving [0->100] and if dir = -1, then fish moving in [100->0] direction
            curr_fish_direction = 1 if fish_delta_x >= 0 else -1                

            logger.info(f"ObjectManager -> get_curr_fish_direction(), ENDS, direction: {curr_fish_direction}")
            return curr_fish_direction
        

        except Exception as e:
            logger.info(f"Error occurred in ObjectManager -> get_curr_fish_direction(), error: {e}")
            raise e


    def get_robot_pose(self):
        return self.robot_controller.get_fish_robot_pose()


#----------------------------------------------------------------------------------------------------------------------------



