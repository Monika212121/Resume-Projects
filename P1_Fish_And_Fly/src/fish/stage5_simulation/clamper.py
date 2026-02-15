
from src.common.logging import logger

from src.fish.stage3_action.entity import Waypoint
from src.fish.stage5_simulation.constants import WORKSPACE_BOUNDS



def clamp_garbage_position(position: Waypoint):
    try:
        x = min(max(position.x, WORKSPACE_BOUNDS["x_min"]), WORKSPACE_BOUNDS["x_max"])
        y = min(max(position.y, WORKSPACE_BOUNDS["y_min"]), WORKSPACE_BOUNDS["y_max"])
        z = min(max(position.z, WORKSPACE_BOUNDS["z_min"]), WORKSPACE_BOUNDS["z_max"])

        safe_position = Waypoint(x, y, z)

        logger.info(f"clamp_garbage_position(), position: {position}, safe_position: {safe_position}")
        return safe_position


    except Exception as e:
        logger.info(f"Error occurred in clamp_garbage_position(), error: {e}")
        raise e  