from enum import Enum
from typing import Tuple
from dataclasses import dataclass

from src.common.entity.position import Waypoint
from src.common.utils.mission import MissionPhase
from src.common.entity.manatee_communication import ManateeMode



class MachineType(Enum):
    FLY = "aerial drone"
    FISH = "water body cleaning agent"
    MANATEE = "dump points cleaning and fish rescue agent"



@dataclass
class MachineState:
    current_position: Tuple[float, float, float, float]
    current_phase: MissionPhase
    current_operation_mode: ManateeMode