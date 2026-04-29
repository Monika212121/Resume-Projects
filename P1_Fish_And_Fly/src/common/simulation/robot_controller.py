import time
import numpy as np
import pybullet as p
from typing import Optional, Tuple, Dict, List

from src.common.logging import logger
from src.common.entity.position import Waypoint
from src.common.simulation.entity import SpawnObject
from src.common.simulation.clamper import clamp_position
from src.common.entity.manatee_communication import ManateeMode
from src.common.entity.machine_types import MachineState, MachineType
from src.common.simulation.constants import SLOW_TELEPORT_PHASES, STOP_DELAY, TEXT_COLOR, SHAPE_MAP

from src.common.utils.mission import MissionPhase



class RobotController:
    def __init__(self):
        self.robots_body_ID: Dict[MachineType, int] = {}                                # [machine name, machine body_id]
        self.robot_states: Dict[MachineType, MachineState] = {}                         # {machine name, machine state}

        self.last_mission_phase: MissionPhase = MissionPhase.SURFACE
        self.last_operation_mode: ManateeMode = ManateeMode.IDLE



    def get_robot_body_id(self, robot_name: MachineType) -> Optional[int]:
        return self.robots_body_ID[robot_name]


    def get_robot_last_state(self, robot_name: MachineType) -> Optional[MachineState]:
        return self.robot_states[robot_name]



    def spawn_robot(self, robot_name: MachineType, body_info: SpawnObject):

        robot_shape, robot_size, robot_color = body_info.shape, body_info.size, body_info.color
        start_pos: List[int] = [10,10,0] if robot_name == MachineType.FISH else [8, 20, 0]

        # Retrieve shape type
        shape_type = SHAPE_MAP.get(robot_shape)
        if shape_type is None:
            logger.info(f"RobotController -> spawn_robot(), Unsupported shape: {robot_shape}")
            return -1 
        
        if robot_shape == "box": 
            collision = p.createCollisionShape(
                shapeType = shape_type, 
                halfExtents = robot_size
            )

            visual = p.createVisualShape(
                shapeType= shape_type,
                halfExtents= robot_size,
                rgbaColor= robot_color,
            )


        # not getting used now
        elif robot_shape in ["capsule", "cylinder"]:
            radius = robot_size[0]
            height = robot_size[1]

            visual = p.createVisualShape(
                shapeType = shape_type,
                radius = radius,
                length = height,
                rgbaColor = robot_color
            )

            collision = p.createCollisionShape(
                shapeType = shape_type,
                radius = radius,
                height = height
            )


        # Create robot body in simulation
        robot_id = p.createMultiBody(
            baseMass= 0.0,
            baseCollisionShapeIndex= collision,
            baseVisualShapeIndex= visual,
            basePosition= start_pos
        )
        
        self.robots_body_ID[robot_name] = robot_id
        return



    def teleport_fish_robot(self, pose: Waypoint, current_mission_phase: MissionPhase):
        logger.info(f"RobotController -> teleport_fish_robot(): STARTS, pose: {pose}")

        robot_id = self.get_robot_body_id(robot_name= MachineType.FISH)
        if robot_id is None:
            raise RuntimeError(f"RobotController -> teleport_fish_robot(): Fish robot of body_id: {robot_id} is not spawned")

        # Defensive check (saves hours of debugging)
        if p.getConnectionInfo()["isConnected"] == 0:
            raise RuntimeError("PyBullet is not connected. Did you forget sim_bridge.start()?")

        # Clamping Fish robot position, to avoid going outside the defined operation workspace 
        allowed_to_exit_safe_boundary = current_mission_phase in SLOW_TELEPORT_PHASES

        # Fish machine can cross this safe boundary, only when in UNLOADING/ RETURN_HQ/ ABORT/ FAILED phases
        safe_position = pose if allowed_to_exit_safe_boundary else clamp_position(position= pose)

        logger.info(f"RobotController -> teleport_fish_robot(), safe_position: {safe_position}")

        # CASE1: SLOW TRAVERSAL: If mission phase is SLOW_TELEPORT_PHASES, then traverse slower
        if allowed_to_exit_safe_boundary:
            fish_current_pos, _ = p.getBasePositionAndOrientation(robot_id)
            start = Waypoint(*fish_current_pos)

            # Moves slowly towards the target destination
            self._slow_teleport(
                fish_body_id= robot_id,
                start= start,
                end= safe_position,
                curr_phase = current_mission_phase,
                steps= 40,
                step_delay= STOP_DELAY[current_mission_phase],                                               # slower & visible
            )


        # CASE2: NORMAL TRAVERSAL
        else:
            p.resetBasePositionAndOrientation(
                robot_id,
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
        
        logger.info(f"RobotController -> teleport_fish_robot(): ENDS")
        return
    


    def _slow_teleport(self, fish_body_id: int, start: Waypoint, end: Waypoint, curr_phase: MissionPhase, steps: int = 30, step_delay: float = 0.04):

        for alpha in np.linspace(0.0, 1.0, steps):
            interp_pos = Waypoint(
                x=start.x + alpha * (end.x - start.x),
                y=start.y + alpha * (end.y - start.y),
                z=start.z + alpha * (end.z - start.z),
            )

            p.resetBasePositionAndOrientation(
                fish_body_id,
                [interp_pos.x, interp_pos.y, interp_pos.z],
                [0, 0, 0, 1],
            )

            p.addUserDebugText(
                curr_phase.name,
                [interp_pos.x, interp_pos.y, interp_pos.z + 2],
                textColorRGB= TEXT_COLOR[curr_phase],
                lifeTime=0.1
            )

            p.stepSimulation()
            time.sleep(step_delay)
        
        
        return



    def get_robot_pose(self, robot: MachineType) -> Optional[Tuple[float, float, float, float]]:
        """
        Returns fish pose in simulation frame:
        (x, y, z, yaw)
        """
        logger.info(f"RobotController -> get_robot_pose(): STARTS")

        robot_id = self.get_robot_body_id(robot_name= robot)
        if robot_id is None:
            logger.info(f"RobotController -> get_robot_pose(): This robot {robot} is not spawned yet")
            return None
        
        position, orientation = p.getBasePositionAndOrientation(robot_id)
        roll, pitch, yaw = p.getEulerFromQuaternion(orientation)

        x, y, z = position
        x = float(x)
        y = float(y)
        z = float(z)
        yaw = float(yaw)

        robot_pose = (x, y, z, yaw)

        logger.info(f"RobotController -> get_robot_pose() : ENDS, tobot: {robot}, robot_id: {robot_id}, robot_pose: {robot_pose}")
        return robot_pose



    def stop_robot(self, body_id: int):
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
    


    def teleport_manatee_robot(self, pose: Waypoint, current_operation_mode: ManateeMode):
        logger.info(f"RobotController -> teleport_manatee_robot(): STARTS, pose: {pose}")

        robot_id = self.get_robot_body_id(robot_name= MachineType.MANATEE)
        if robot_id is None:
            raise RuntimeError(f"RobotController -> teleport_manatee_robot(): Manatee robot of body_id: {robot_id} is not spawned")

        # Defensive check (saves hours of debugging)
        if p.getConnectionInfo()["isConnected"] == 0:
            raise RuntimeError("PyBullet is not connected. Did you forget sim_bridge.start()?")

        # Normal traversal
        p.resetBasePositionAndOrientation(
            robot_id,
            [pose.x, pose.y, pose.z],
            [0, 0, 0, 1],
        )
        '''
        p.addUserDebugText(
            curr_phase.name,
            [interp_pos.x, interp_pos.y, interp_pos.z + 2],
            textColorRGB= TEXT_COLOR[curr_phase],
            lifeTime=0.1
        )
        '''

        logger.info(f"RobotController -> teleport_manatee_robot(): ENDS")
        return
    


    def update_robot_state(self, robot_name: MachineType, current_phase: Optional[MissionPhase], curr_mode: Optional[ManateeMode]):

        curr_pos = self.get_robot_pose(robot= robot_name)
        if curr_pos is None:
            logger.info(f"Error occurred in update_robot_pose(), getting curr_pos")
            return
                       
        machine_state: MachineState = MachineState(
            current_position= curr_pos,
            current_phase= current_phase if current_phase else self.last_mission_phase,
            current_operation_mode= curr_mode if curr_mode else self.last_operation_mode
        )

        # Update last mission phase (Fish) and operation mode (Manatee)
        self.last_mission_phase = machine_state.current_phase
        self.last_operation_mode = machine_state.current_operation_mode

        # Update Robot's mission state
        self.robot_states[robot_name] = machine_state
        return