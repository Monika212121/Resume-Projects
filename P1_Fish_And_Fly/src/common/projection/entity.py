from typing import Tuple
from dataclasses import dataclass

from src.fish.stage3_action.entity import Waypoint



@dataclass
class WorldObject:
    track_id: int
    class_id: int
    position: Waypoint                  # transformed position in world frame (X, Y, Z)
    distance: float                     # scalar distance proxy
    bbox: Tuple[int, int, int, int]     # original position in image frame (reveived from YOLO)


"""
x: float                            # left/right (mtrs, relative)
y: float                            # forward (mtrs, relative)
z: float
"""