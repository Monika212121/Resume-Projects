from typing import Tuple, Optional
from dataclasses import dataclass



@dataclass
class ActionIntent:
    """
    High-level decision output for Action layer
    """
    track_id: Optional[int]
    class_name: str
    priority_score: float
    bbox: Optional[Tuple[int, int, int, int]]
    reason: str
