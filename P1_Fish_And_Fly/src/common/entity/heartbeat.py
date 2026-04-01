

import time
from dataclasses import dataclass
from typing import Optional, Dict

from src.fish.stage3_action.entity import MissionPhase, Waypoint



@dataclass
class SystemHeartbeat:
    source: str                     
    mission_phase: MissionPhase             
    position: Waypoint                                          # Fish machine's position
    timestamp: float
    issue: Optional[str] = ""
    used_dump_point: Optional[int] = None
    need_help: Optional[bool] = False

    @staticmethod
    def now(mission_phase: MissionPhase, position: Waypoint, dump_point: Optional[int] = None, issue: Optional[str] = "", need_help: Optional[bool]= False):

        return SystemHeartbeat(
            source= "Fish",
            mission_phase= mission_phase,
            position= position,
            timestamp= time.time(),
            used_dump_point= dump_point,
            issue= issue,
            need_help= need_help
        )
