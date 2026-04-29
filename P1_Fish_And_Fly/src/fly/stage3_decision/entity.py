import time
from enum import Enum
from typing import Optional, List
from dataclasses import dataclass, field

from src.common.entity.position import Waypoint
from src.common.entity.dispatch import DispatchOrder
 


class FishStatus(Enum):
    INIT = 1
    ALIVE = 2
    LAGGING = 3
    FROZEN = 4
    DEAD = 5



@dataclass
class StateDeltas:
    mission_phase: str
    fish_state: str
    fish_x: float
    fish_y: float
    fish_z: float
    surface_coverage_pct: float
    underwater_coverage_pct: float
    communication_delta: float
    fish_progress_delta: float
    silence_delta: float




@dataclass
class MonitoringConfig:
    timeout_sec: float
    freeze_sec: float


@dataclass
class DumpConfig:
    dump_id: int
    position: Waypoint
    capacity: float


# For 8 bins placed near perimenter of the workspace
@dataclass
class DMSConfig:
    threshold: float
    cooldown: float


@dataclass
class FlyDecisionConfig:
    dms: DMSConfig
    monitor: MonitoringConfig