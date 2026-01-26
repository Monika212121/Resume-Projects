from dataclasses import dataclass
from typing import Optional

@dataclass
class GarbageLogEntry:
    track_id: int
    class_name: str
    first_seen_frame: int
    last_seen_frame: int
    final_state: str                                # collected / lost / ignored / failed
    lifecycle_state: str                            # NEW / STABLE / SELECTED / DONE / LOST     
    age: int
    avg_confidence: float
    priority_score: Optional[float] = None
    selected_at: Optional[int] = None
    completed_at: Optional[int] = None
    failure_reason: Optional[str] = None
    ignore_rason: Optional[str] = None