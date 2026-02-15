import pybullet as p
from typing import Optional, Tuple

from src.common.logging import logger

from src.fish.stage3_action.entity import Waypoint
from src.fish.stage5_simulation.constants import WORKSPACE_BOUNDS



class RobotController:
    def __init__(self):
        self.fish_robot_id: Optional[int] = None


    def spawn_fish_robot(self):
        collision = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.5, 0.2, 0.15])
        visual = p.createVisualShape(
            p.GEOM_BOX,
            halfExtents=[0.5, 0.2, 0.15],
            rgbaColor=[0.2, 0.6, 0.9, 1.0],
        )

        self.fish_robot_id = p.createMultiBody(
            baseMass=0.0,
            baseCollisionShapeIndex=collision,
            baseVisualShapeIndex=visual,
            basePosition=[0, 0, 0],
        )
        
        return



    def teleport(self, pose: Waypoint):
        logger.info(f"RobotController -> teleport(): STARTS, pose: {pose}")

        if self.fish_robot_id is None:
            raise RuntimeError("RobotController -> teleport() called before spawn()")

        # Defensive check (saves hours of debugging)
        if p.getConnectionInfo()["isConnected"] == 0:
            raise RuntimeError("PyBullet is not connected. Did you forget sim_bridge.start()?")

        # Adding workspace constraints, avoiding Fish robot to go outside the defined workspace
        safe_position = self.clamp_workspace_position(pos= pose)
        logger.info(f"RobotController -> teleport(), safe_position: {safe_position}")

        p.resetBasePositionAndOrientation(
            self.fish_robot_id,
            [safe_position.x, safe_position.y, safe_position.z],
            [0, 0, 0, 1],
        )

        '''
        p.resetDebugVisualizerCamera(
            cameraDistance=5,
            cameraYaw=45,
            cameraPitch=-30,
            cameraTargetPosition=[pose.x, pose.y, pose.z],
        )
        '''
        
        logger.info(f"RobotController -> teleport(): ENDS")
        return


    def get_fish_robot_pose(self) -> Optional[Tuple[float, float, float, float]]:
        """
        Returns fish pose in simulation frame:
        (x, y, z, yaw)
        """
        logger.info(f"RobotController -> get_robot_fish_pose(): STARTS")

        if self.fish_robot_id is None:
            logger.info(f"RobotController -> get_robot_fish_pose(): fish_robot_id = None")
            return None
        
        position, orientation = p.getBasePositionAndOrientation(self.fish_robot_id)
        roll, pitch, yaw = p.getEulerFromQuaternion(orientation)

        x, y, z = position
        x = float(x)
        y = float(y)
        z = float(z)
        yaw = float(yaw)

        fish_pose = (x, y, z, yaw)

        logger.info(f"RobotController -> get_robot_fish_pose() : ENDS, fish_pose: {fish_pose}")
        return fish_pose



    def clamp_workspace_position(self, pos: Waypoint) -> Waypoint:
        x = min(max(pos.x, WORKSPACE_BOUNDS["x_min"]), WORKSPACE_BOUNDS["x_max"])
        y = min(max(pos.y, WORKSPACE_BOUNDS["y_min"]), WORKSPACE_BOUNDS["y_max"])
        z = min(max(pos.z, WORKSPACE_BOUNDS["z_min"]), WORKSPACE_BOUNDS["z_max"])

        safe_position = Waypoint(x, y, z)
        return safe_position
