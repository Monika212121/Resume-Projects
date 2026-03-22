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
    MissionPhase.ABORT,
    MissionPhase.FAILED,
    MissionPhase.UNLOADING,
    MissionPhase.RETURN_HQ,             # RETURN_HQ is normal traversal but the reason I kept it in slow traversal is to avoid clamping of destination as HQ can be anywhere
    MissionPhase.DESCEND,
    MissionPhase.ASCEND
}


STOP_DELAY = {
    MissionPhase.ABORT: 0.08,
    MissionPhase.FAILED: 0.08,
    MissionPhase.UNLOADING: 0.08,
    MissionPhase.RETURN_HQ: 0.12,
    MissionPhase.DESCEND: 0.12,
    MissionPhase.ASCEND: 0.12
}


TEXT_COLOR = {
    MissionPhase.ABORT: [1,0,0],                # red
    MissionPhase.FAILED: [1,0,0],               # red
    MissionPhase.UNLOADING: [1,1,0],            # yellow
    MissionPhase.RETURN_HQ: [0,1,0],            # green
    MissionPhase.DESCEND: [0,1,0],              # green
    MissionPhase.ASCEND: [0,1,0]                # green
}