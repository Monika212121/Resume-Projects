# AIM: Define our operational workspace. 
from src.fish.stage3_action.entity import MissionPhase



WORKSPACE_BOUNDS = {
    "x_min": 0.0,
    "x_max": 120.0,
    "y_min": 0.0,
    "y_max": 120.0,
    "z_min": -8.0,
    "z_max": 0.0,
}


SIM_GARBAGE_SPAWN_OFFSET_X = 8.0  # meters, forward in Fish heading


SLOW_TELEPORT_PHASES = {
    MissionPhase.UNLOADING,
    MissionPhase.ABORT,
    MissionPhase.RETURN,
}