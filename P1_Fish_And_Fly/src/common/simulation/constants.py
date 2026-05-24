# AIM: Define our operational workspace. 
import pybullet as p

from src.common.utils.mission import MissionPhase
from src.common.entity.manatee_communication import ManateeMode



WORKSPACE_BOUNDS = {
    "x_min": 0.0,
    "x_max": 120.0,
    "y_min": 0.0,
    "y_max": 120.0,
    "z_min": -8.0,
    "z_max": 0.0,
}


SIM_GARBAGE_SPAWN_OFFSET_X = 8.0           # distance forward Fish machine, a garbage is spawned
SPAWN_X_FACTOR = 100                       # Y_rel = distance of BB in fish world = distance of object(x-axis) in sim frame. Y_rel is very small value(eg: 0.0065).  
SPAWN_Y_FACTOR = -1                        # X_rel = offset of object(left/right) in fish frame = distance of object(negative y-axis) in sim frame, that's why multiplied by -1.

SLOW_TELEPORT_PHASES = {
    MissionPhase.ABORT,
    MissionPhase.FAILED,
    MissionPhase.UNLOADING,
    MissionPhase.RETURN_HQ,                # RETURN_HQ is normal traversal but the reason I kept it in slow traversal is to avoid clamping of destination as HQ can be anywhere
    MissionPhase.DESCEND,
    MissionPhase.ASCEND
}


STOP_DELAY = {
    MissionPhase.ABORT: 0.08,
    MissionPhase.FAILED: 0.08,
    MissionPhase.UNLOADING: 0.08,
    MissionPhase.RETURN_HQ: 0.12,
    MissionPhase.DESCEND: 0.12,
    MissionPhase.ASCEND: 0.12,
    ManateeMode.RESCUE: 0.15,
    ManateeMode.UNLOADING_SELF_BIN: 0.0,
    ManateeMode.RETURN_HQ: 1.0
}


FISH_TEXT_COLOR = {
    MissionPhase.ABORT: [1,0,0],                # red
    MissionPhase.FAILED: [1,0,0],               # red
    MissionPhase.UNLOADING: [1,1,0],            # yellow
    MissionPhase.RETURN_HQ: [1,1,1],            # white
    MissionPhase.DESCEND: [1,1,1],              # white
    MissionPhase.ASCEND: [1,1,1],               # white
    MissionPhase.SURFACE: [1,1,1],              # white
    MissionPhase.UNDERWATER: [1,1,1]            # white
}


MANATEE_TEXT_COLOR = {
    ManateeMode.IDLE: [1, 1, 1],                        # white
    ManateeMode.PATROL: [1, 1, 1],                      # white
    ManateeMode.COLLECTION: [1, 1, 1],                  # white
    ManateeMode.RESCUE: [1, 0, 0],                      # red
    ManateeMode.UNLOADING_SELF_BIN: [1, 1, 0],          # yellow
    ManateeMode.RETURN_HQ: [0, 0, 1]                    # blue
}



SHAPE_MAP = {
    "sphere": p.GEOM_SPHERE,
    "box": p.GEOM_BOX,
    "capsule": p.GEOM_CAPSULE,
    "cylinder": p.GEOM_CYLINDER
}