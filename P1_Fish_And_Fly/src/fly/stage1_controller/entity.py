from enum import Enum
from dataclasses import dataclass

from src.common.entity.position import Waypoint



@dataclass
class FlightControllerConfig:
    hover_position: Waypoint                 


class FlightMode(Enum):
    IDLE = "IDLE"
    TAKEOFF = "TAKEOFF"
    HOVER = "HOVER"
    HOLD = "HOLD"
    RETURN_HOME = "RETURN_HOME"
    LAND = "LAND"