import time
from enum import Enum
from typing import Optional, List
from dataclasses import dataclass, field

from src.common.entity.position import Waypoint



class ManateeMode(Enum):
    IDLE = "rest"
    SHADOW = "shadow fish machine"
    COLLECTION = "collection of dump point"
    RESCUE = "rescue fish machine"
    FINAL_SWEEP = "unload all 8 dump points"
    UNLOADING_SELF_BIN = "unload its self bin to HQ"


class TaskStatus(Enum):
    RUNNING = 0
    COMPLETED = 1
    FAILED = 2


@dataclass
class DumpInfo:
    dump_id: int
    dump_position: Waypoint
    dump_current_load: float = 0.0