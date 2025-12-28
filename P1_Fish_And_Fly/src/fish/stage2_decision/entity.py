from enum import Enum
from typing import Tuple
from dataclasses import dataclass

@dataclass
class ActionIntent:
    """
    High-level decision output for Action layer
    """
    track_id: int
    class_name: str
    priority_score: float
    bbox: Tuple[int, int, int, int]
    reason: str
