from typing import Tuple
from dataclasses import dataclass



@dataclass
class WorldObject:
    track_id: int
    x: float                            # left/right (mtrs, relative)
    y: float                            # forward (mtrs, relative)
    z: float
    distance: float                     # scalar distance proxy
    bbox: Tuple[int, int, int, int]
