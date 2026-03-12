import time
import numpy as np
import pybullet as p
from typing import Optional, Tuple

from src.common.logging import logger

from src.fish.stage3_action.entity import Waypoint, MissionPhase
from src.fish.stage4_simulation.clamper import clamp_position
from src.fish.stage4_simulation.constants import SLOW_TELEPORT_PHASES



class RobotController:
    def __init__(self):
        self.fish_robot_id: Optional[int] = None


    def get_fish_robot_body_id(self) -> Optional[int]:
        return self.fish_robot_id
    

    def spawn_fish_robot(self):
        collision = p.createCollisionShape(p.GEOM_BOX, halfExtents=[1.0, 0.4, 0.30])
        visual = p.createVisualShape(
            p.GEOM_BOX,
            halfExtents=[1.0, 0.4, 0.30],
            rgbaColor=[0.18, 0.18, 0.18, 1.0],
        )

        self.fish_robot_id = p.createMultiBody(
            baseMass=0.0,
            baseCollisionShapeIndex=collision,
            baseVisualShapeIndex=visual,
            basePosition=[0, 0, 0],
        )
        
        return



    def teleport(self, pose: Waypoint, current_mission_phase: MissionPhase):
        logger.info(f"RobotController -> teleport(): STARTS, pose: {pose}")

        if self.fish_robot_id is None:
            raise RuntimeError("RobotController -> teleport() called before spawn()")

        # Defensive check (saves hours of debugging)
        if p.getConnectionInfo()["isConnected"] == 0:
            raise RuntimeError("PyBullet is not connected. Did you forget sim_bridge.start()?")

        # Clamping Fish robot position, to avoid going outside the defined operation workspace 
        allowed_to_exit_safe_boundary = current_mission_phase in SLOW_TELEPORT_PHASES

        # Fish machine can cross this safe boundary, only when in UNLOADING/ ABORT/ RETURN phase
        safe_position = pose if allowed_to_exit_safe_boundary else clamp_position(position=pose)

        logger.info(f"RobotController -> teleport(), safe_position: {safe_position}")

        # CASE1: If mission phase is SLOW_TELEPORT_PHASES, then traverse slower
        if allowed_to_exit_safe_boundary:
            fish_current_pos, _ = p.getBasePositionAndOrientation(self.fish_robot_id)
            start = Waypoint(*fish_current_pos)
            self._slow_teleport(
                start=start,
                end=safe_position,
                steps=40,
                step_delay=0.04,  # slower & visible
            )
        # CASE2: Normal traversal
        else:
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



    def _slow_teleport(self, start: Waypoint, end: Waypoint, steps: int = 30, step_delay: float = 0.03):
        for alpha in np.linspace(0.0, 1.0, steps):
            interp_pos = Waypoint(
                x=start.x + alpha * (end.x - start.x),
                y=start.y + alpha * (end.y - start.y),
                z=start.z + alpha * (end.z - start.z),
            )

            p.resetBasePositionAndOrientation(
                self.fish_robot_id,
                [interp_pos.x, interp_pos.y, interp_pos.z],
                [0, 0, 0, 1],
            )

            p.stepSimulation()
            time.sleep(step_delay)
        
        
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



    def stop_fish(self, body_id: int):
        """
        Physically stop fish movement in simulation.
        """
        # Zero linear + angular velocity
        p.resetBaseVelocity(
            objectUniqueId=body_id,
            linearVelocity=[0, 0, 0],
            angularVelocity=[0, 0, 0]
        )
        return