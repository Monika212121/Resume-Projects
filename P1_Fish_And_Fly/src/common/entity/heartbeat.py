

import time
from dataclasses import dataclass
from src.fish.stage3_action.entity import MissionPhase

from src.fish.stage3_action.entity import Waypoint


@dataclass
class SystemHeartbeat:
    source: str                     
    mission_phase: MissionPhase             
    position: Waypoint
    timestamp: float
    alive: bool = True
    issue: str = ""

    @staticmethod
    def now(mission_phase: MissionPhase, position: Waypoint, issue: str):

        return SystemHeartbeat(
            source= "Fish",
            mission_phase=mission_phase,
            position=position,
            timestamp=time.time(),
            alive=True,
            issue= issue
        )
