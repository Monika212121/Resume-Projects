import time
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

from src.fish.stage3_action.entity import MissionPhase, Waypoint



class OperationMode(Enum):
    IDLE = "idle"
    COLLECTION = "collection"
    RESCUE = "rescue"


@dataclass
class DispatchOrder:
    source: str
    operation_mode: OperationMode                     
    mission_phase: MissionPhase
    target_dump_points: List[int]
    timestamp: float
    fish_rescue_position: Optional[Waypoint] = None                  # Last active position of Fish machine

    @staticmethod
    def now(mode: OperationMode, mission_phase: MissionPhase, target_ids: List[int], rescue_position: Waypoint):
    
        return DispatchOrder(
            source= "Fly",
            operation_mode = mode,
            mission_phase= mission_phase,
            target_dump_points = target_ids,
            timestamp= time.time(),
            fish_rescue_position= rescue_position
        )
