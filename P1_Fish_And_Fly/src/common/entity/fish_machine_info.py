from dataclasses import dataclass

from src.fish.stage3_action.entity import Waypoint



@dataclass
class FishNavigationInfo:
    position: Waypoint
    direction: int

