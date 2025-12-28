# Aim: This is action feedback from Action module to Decision module.
from enum import Enum
from dataclasses import dataclass

class ActionStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"

@dataclass
class ActionFeedback:
    track_id: int
    status: ActionStatus
    reason: str = ""