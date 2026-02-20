from src.common.logging import logger

from src.fish.stage3_action.entity import MissionPhase, Waypoint



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
