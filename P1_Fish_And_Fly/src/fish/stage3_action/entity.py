# Aim: This is action feedback from Action module to Decision module.

from enum import Enum
from typing import Optional, List
from dataclasses import dataclass

class ActionStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    MOVED_FORWARD = "moved"
    NONE = "nothing_happened"


@dataclass
class ActionFeedback:
    status: ActionStatus
    track_id: Optional[int] = None
    reason: str = ""


@dataclass
class Waypoint:
    x: float
    y: float
    z: float

@dataclass
class Bin:
    bin_capacity: int               # Number of items dustbin can contain
    alert_threshold: float          # Percentage of bin, allowed to filled before unloading

@dataclass
class Speeds:
    surface: float
    underwater: float

@dataclass
class Navigation:
    start_point: Waypoint
    end_point: Waypoint
    sweep_step: float
    reach_threshold: float
    speeds: Speeds

@dataclass
class Depths:
    surface: float
    underwater: float

@dataclass
class Limits:
    max_operation_retries: int
    max_mission_time_sec : int
    max_target_loss_ignore: int

@dataclass
class Mission:
    start_point: Waypoint
    end_point: Waypoint
    hq_point: Waypoint
    depths: Depths
    navigation: Navigation
    limits: Limits
    bin_manager: Bin


class MissionPhase(Enum):
    SURFACE = 1
    DESCEND = 2
    UNDERWATER = 3
    ASCEND = 4
    RETURN = 5
    DONE = 6
    ABORT = 7
    FAILED = 8
    UNLOADING = 9


@dataclass(frozen= True)
class CostWeights:
    travel_time: float
    energy: float
    current: float
    drag: float
    risk: float
    uncertainty: float

@dataclass(frozen= True)
class VehicleModel:
    cruise_speed: float
    drag_coeff: float
    avg_drag_force: float

@dataclass(frozen= True)
class NormalizationLimits:
    max_distance: float
    max_energy: float
    max_current: float
    max_risk: float
    max_uncertainty: float

@dataclass
class CostModel:
    cost_weigths: CostWeights
    vehicle_model: VehicleModel
    normalization_limits: NormalizationLimits


@dataclass
class DumpLocation:
    d_points: List[Waypoint]        # Coordinates of the points where unloading of dustbin takes place


@dataclass(frozen= True)
class MissionCheckpoint:
    last_phase: MissionPhase         # tells phase/depth
    last_position: Waypoint
    last_timestamp: float