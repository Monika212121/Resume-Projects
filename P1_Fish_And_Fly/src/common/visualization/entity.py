from dataclasses import dataclass
from typing import List, Optional, Tuple



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

