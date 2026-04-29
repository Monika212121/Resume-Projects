import math
from typing import Tuple
from enum import Enum

from src.common.logging import logger
from src.common.entity.position import Waypoint



class MissionPhase(Enum):
    SURFACE = 1
    DESCEND = 2
    UNDERWATER = 3
    ASCEND = 4
    RETURN_HQ = 5
    DONE = 6
    ABORT = 7
    FAILED = 8
    UNLOADING = 9



def mission_is_active(current_mission_phase: MissionPhase) -> bool:
    try:
        # Mission is not active when its current phase is completed, aborted or failed.
        is_active = current_mission_phase not in {MissionPhase.DONE, MissionPhase.ABORT, MissionPhase.FAILED}

        logger.info("mission_is_active(): %s (current phase: %s)", "ACTIVE" if is_active else "INACTIVE", current_mission_phase)
        return is_active

    except Exception as e:
        logger.info(f"Error occurred in mission_is_active(), error: {e}")
        raise e



def action_is_allowed(current_mission_phase: MissionPhase) -> bool:
    try:
        # Action is allowed only when machine is cleaning at surface level and underwater level.
        is_allowed = current_mission_phase in {MissionPhase.SURFACE, MissionPhase.UNDERWATER}

        logger.info("action_is_allowed(): %s (current phase: %s)", "ACTIVE" if is_allowed else "INACTIVE", current_mission_phase)
        return is_allowed
    
    except Exception as e:
        logger.info(f"Error occurred in action_is_allowed(), error: {e}")
        raise e



def is_reached_target(current_position: Waypoint, target_position: Waypoint) -> bool:
    try:
        eps = 1e-3

        # Check if 2 positions are close or not
        is_x_close: bool = abs(current_position.x - target_position.x) < eps
        is_y_close: bool = abs(current_position.y - target_position.y) < eps
        is_z_close: bool = abs(current_position.z - target_position.z) < eps

        is_close: bool = is_x_close and is_y_close and is_z_close

        logger.info("is_reached_target(): current and target position are: %s", "SAME" if is_close else "NOT SAME")
        return is_close

    except Exception as e:
        logger.info(f"Error occurred in is_reached_target(), error: {e}")
        raise e



def get_target_distance(current_position: Tuple[float,float,float,float], target_position: Tuple[float, float, float]) -> float:
    try:
        
        current_pos = Waypoint(current_position[0], current_position[1], current_position[2])
        target_pos = Waypoint(target_position[0], target_position[1], target_position[2])

        dx = abs(current_pos.x - target_pos.x)
        dy = abs(current_pos.y - target_pos.y)
        dz = abs(current_pos.z - target_pos.z)

        distance = math.sqrt(dx*dx + dy*dy + dz*dz)       

        logger.info(f"get_target_distance(): current and target position are at distance: {distance}")
        return distance


    except Exception as e:
        logger.info(f"Error occurred in get_target_distance(), error: {e}")
        raise e