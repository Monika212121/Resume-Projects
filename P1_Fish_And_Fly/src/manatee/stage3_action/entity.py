from enum import Enum
from dataclasses import dataclass

from src.common.entity.position import Waypoint
from src.common.entity.cost_models import CostModel
from src.common.action.entity import Speeds, Bin, Depths, Limits



class MissionSubTask(Enum):
    GO_TO_PROJECTED_BOUNDARY_POINT = "reach boundary point nearest to target dump"
    GO_TO_DUMP = "reach dump point"
    COLLECT_DUMP = "collect garbage from the dump point"
    RETURN_TO_PROJECTED_BOUNDARY_POINT = "reach boundary point back from dump"
    GO_TO_FISH = "reach to Fish machine position"
    ATTACH_FISH = "attach Fish machine for towing"
    GO_TO_HQ = "reach the Head Quarter"
    UNLOAD_SELF_BIN = "unload its self bin in HQ"
    RETURN_FROM_HQ = "return fro HQ to the freezed position"


class ManateeMode(Enum):
    IDLE = "rest"
    SHADOW = "shadow fish machine"
    COLLECTION = "collection of dump point"
    RESCUE = "rescue fish machine"
    FINAL_SWEEP = "unload all 8 dump points"

@dataclass
class ManateeNavigation:
    start_point: Waypoint
    end_point: Waypoint
    speeds: Speeds
    reach_threshold: float


@dataclass
class ManateeMission:
    hq_point: Waypoint
    depths: Depths
    navigation: ManateeNavigation
    limits: Limits
    bin_manager: Bin


@dataclass
class ManateeActionConfig:
    mission: ManateeMission
    cost_model: CostModel
