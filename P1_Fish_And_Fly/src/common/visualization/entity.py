from dataclasses import dataclass
from typing import List, Optional, Tuple



@dataclass
class WorldObject:
    track_id: int
    x: float                            # left/right (mtrs, relative)
    y: float                            # forward (mtrs, relative)
    distance: float                     # scalar distance proxy
    bbox: Tuple[int, int, int, int]


@dataclass
class VisualObject:
    id: int
    bbox: Tuple[int, int, int, int]
    label: str
    confidence: float
    status: str
    color: Tuple[int, int, int]


@dataclass
class VisualizationEntity:
    objects: List[VisualObject]
    selected_id: Optional[int]
    action_label: Optional[str]
    grasp_threshold: float

