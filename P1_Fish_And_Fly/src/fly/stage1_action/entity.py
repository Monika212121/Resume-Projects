from enum import Enum
from dataclasses import dataclass

from src.fish.stage3_action.entity import Waypoint



@dataclass
class FlightControllerConfig:
    home: Waypoint                  #(X, Y, Hover height)


class FlightMode(Enum):
    IDLE = "IDLE"
    TAKEOFF = "TAKEOFF"
    HOVER = "HOVER"
    HOLD = "HOLD"
    RETURN_HOME = "RETURN_HOME"
    LAND = "LAND"



@dataclass
class MonitorConfig:
    timeout_sec: float
    freeze_sec: float


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