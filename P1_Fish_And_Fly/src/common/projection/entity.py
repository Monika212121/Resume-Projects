from enum import Enum
from typing import Tuple
from dataclasses import dataclass

from src.common.entity.decision_types import DecisionStatus
from src.common.vision.entity import TrackedState, EntityRole

from src.fish.stage3_action.entity import Waypoint



class CoordinateFrame(Enum):
    IMAGE = "image"
    FISH = "fish"
    WORLD = "world"


@dataclass
class FishFrameObject:
    track_id: int
    class_id: int
    class_name: str
    age: int
    state: TrackedState
    avg_confidence: float
    entity_role : EntityRole
    
    # 3D position expressed in Fish coordinate frame
    # Fish is assumed at origin (0,0,0)
    relative_position: Waypoint

    # Euclidean distance from Fish to object (derived from relative_position)
    relative_distance: float

    # Bounding box in image frame (x1, y1, x2, y2) from detector
    original_bbox: Tuple[int, int, int, int]
    
    priority_score: float = 0.0
    decision_status: DecisionStatus = DecisionStatus.TARGET_IGNORED
    frame : CoordinateFrame = CoordinateFrame.FISH


# NOTE: In FishFrameObject class, `relative_position` coordinates displays

# x: left/right (mtrs, relative)
# y: forward (mtrs, relative)
# z: same as original
