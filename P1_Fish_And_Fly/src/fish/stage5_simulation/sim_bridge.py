import pybullet as p
from typing import Dict

from src.common.logging import logger
from src.common.projection.entity import WorldObject

from src.fish.stage3_action.entity import Waypoint
from src.fish.stage5_simulation.pybullet_world import PyBulletWorld
from src.fish.stage5_simulation.robot_controller import RobotController
from src.fish.stage5_simulation.object_manager import ObjectManager
from src.fish.stage5_simulation.entity import Simulation



class SimulationBridge:
    def __init__(self, simulation_cfg: Simulation):
        self.world = PyBulletWorld()
        self.robot = RobotController()
        self.object_manager = ObjectManager()
        self.started = False

        self.ENABLE_SIM_GUI = simulation_cfg.enabled_gui


    def start(self):
        if self.started:
            return

        self.world.connect(enable_GUI= self.ENABLE_SIM_GUI)
        self.robot.spawn()
        self.started = True


    def step(self, pose: Waypoint):
        self.robot.teleport(pose)
        self.world.update_camera_follow_fish(pose)
        p.addUserDebugText(
            "CAMERA OK",
            [pose.x, pose.y, pose.z + 2],
            textColorRGB=[0, 1, 0],
            lifeTime=0.1
        )

        p.stepSimulation()



#----------------------------------------------------------------------------------------------------------------------------

    def update_garbage_projection(self, world_objects: Dict[int, WorldObject], fish_pos: Waypoint):
        """
        world_objects: Dict[track_id, WorldObject]
        WorldObject must have .position (x, y, z)
        """
        logger.info(f"SimulationBridge -> update_garbage_projection(): STARTS, world_objects: {world_objects}, fish_pos: {fish_pos}")              

        # Iterate to spawn all garbage objects, one by one
        for _, obj in world_objects.items():
            self.object_manager.spawn_garbage_objects(obj, fish_pos)

        logger.info(f"SimulationBridge -> update_garbage_projection(): ENDS")
        return
    

    def get_robot_pose(self):
        return self.robot.get_robot_fish_pose()


#----------------------------------------------------------------------------------------------------------------------------



