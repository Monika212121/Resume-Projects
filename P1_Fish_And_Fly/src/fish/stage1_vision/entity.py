from enum import Enum
from typing import List, Tuple
from dataclasses import dataclass



# This avoids passing raw YOLO tensors everywhere. This entity will later flow into: language, decision, action modules.
@dataclass
class Detection:                    
    class_id: int
    class_name: str
    confidence: float
    bbox: List[int]                     # [x1, y1, x2, y2]
    track_id: int | None = None



class TrackedState(Enum):
    NEW = "new"
    STABLE = "stable"
    SELECTED = "selected"
    DONE = "done"
    LOST = "lost"
    UNATTEMPTED = "unattempted"

@dataclass
class TrackedGarbage:
    track_id: int
    class_id: int
    class_name: str
    avg_confidence: float
    bbox: Tuple[int, int, int, int]     # (x1, y1, x2, y2)
    age: int                            # number of frames seen
    last_seen_frame: int
    state: TrackedState
    fade_frames_remaining: int = 0      # UI related

