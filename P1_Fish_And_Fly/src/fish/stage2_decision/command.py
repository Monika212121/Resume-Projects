# AIM: This is the only thing Decision module is allowed to output regarding state.
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class LifeCycleAction(Enum):
    SELECT = "select"
    MARK_DONE = "mark_done"
    LOST = "lost"
    FAILED = "failed"
    UNATTEMPTED = "unattempted"

@dataclass
class LifeCycleCommand:
    action: LifeCycleAction
    track_id: Optional[int]