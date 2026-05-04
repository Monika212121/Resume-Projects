# Aim: This is action feedback from Action module to Decision module.

from enum import Enum
from typing import Optional
from dataclasses import dataclass

from src.common.entity.position import Waypoint
from src.common.utils.mission import MissionPhase
from src.common.entity.cost_models import CostModel
from src.common.entity.fish_communication import DumpEvent
from src.common.action.entity import Speeds, Bin, Depths, Limits



class ActionStatus(Enum):
    ACTIVE = "active"                               # Only used in Simulation
    COLLECTED = "success"
    FAILED = "failed"
    MOVED_FORWARD = "moved"
    NONE = "nothing_happened"
    LOST = "object_lost"
    IGNORED = "ignored"
    AVOIDED = "avoid"
    UNLOADED = "unloaded_bin"


@dataclass
class ActionFeedback:
    status: ActionStatus
    track_id: int
    need_manatee_help: bool
    reason: str = ""
    dump_event: Optional[DumpEvent] = None


@dataclass
class Navigation:
    start_point: Waypoint
    end_point: Waypoint
    sweep_step: float
    reach_threshold: float
    speeds: Speeds


@dataclass
class Mission:
    start_point: Waypoint
    end_point: Waypoint
    hq_point: Waypoint
    depths: Depths
    navigation: Navigation
    limits: Limits
    bin_manager: Bin


@dataclass(frozen= True)
class MissionCheckpoint:
    last_phase: MissionPhase         # tells phase/depth
    last_position: Waypoint
    last_timestamp: float


@dataclass
class ActionConfig:
    mission: Mission
    cost_model: CostModel