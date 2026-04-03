from dataclasses import dataclass

from src.common.entity.position import Waypoint



@dataclass
class FishNavigationInfo:
    position: Waypoint
    direction: int

