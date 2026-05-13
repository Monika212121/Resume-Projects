import time

from typing import Optional, List
from dataclasses import dataclass

from src.common.entity.position import Waypoint
from src.common.utils.mission import MissionPhase
from src.common.entity.machine_types import MachineType



@dataclass 
class FishControlSignal:
    locked_dump_ids: List[int]


@dataclass
class FishNavigationInfo:
    position: Waypoint
    direction: int


@dataclass
class DumpEvent:
    agent: MachineType
    event_id: int
    dump_id: int
    load_added: float
    timestamp: float


@dataclass
class SystemHeartbeat:
    source: str                     
    mission_phase: MissionPhase             
    position: Waypoint                                          # Fish machine's position
    timestamp: float
    dump_event: Optional[DumpEvent]
    issue: Optional[str] = ""
    need_help: Optional[bool] = False

    @staticmethod
    def now(mission_phase: MissionPhase, position: Waypoint, dump_event: Optional[DumpEvent], issue: Optional[str] = "", need_help: Optional[bool]= False):

        return SystemHeartbeat(
            source= "Fish",
            mission_phase= mission_phase,
            position= position,
            timestamp= time.time(),
            dump_event= dump_event,
            issue= issue,
            need_help= need_help
        )