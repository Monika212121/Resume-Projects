from enum import Enum
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass


# IO configuration objects
@dataclass
class CameraConfig:
    device_id: int

@dataclass
class VideoConfig:
    path: Path

@dataclass
class IOConfig:
    source: str                                                 # "camera" | "video" | "sim"
    camera: Optional[CameraConfig] = None
    video: Optional[VideoConfig] = None


# Model training configuration objects
@dataclass
class ModelParameter:
    data: Path                                                  # specify location of data.yaml file, reading image dataset
    imgsz: int
    epochs: int
    batch: int
    device: str
    optimizer: str
    project: Path                                               # specify location to save trained YOLO weights
    name: str
    patience: Optional[int] = 0
    degrees: Optional[int] = 0
    lr0: Optional[float] = 0.0
    hsv_h: Optional[float] = 0.0
    hsv_s: Optional[float] = 0.0
    hsv_v: Optional[float] = 0.0
    mosaic: Optional[float] = 0.0
    shear: Optional[float] = 0.0
    flipud: Optional[float] = 0.0
    fliplr: Optional[float] = 0.0
    translate: Optional[float] = 0.0
    scale: Optional[float] = 0.0

@dataclass
class YOLOModelTrainerConfig:
   model_name: str
   model_parameters: ModelParameter


# Model tracking configuration object
@dataclass
class TrackingConfig:
    enabled: bool
    tracker: Path
    persist: bool
    verbose: bool


# Model inference configuration object
@dataclass
class InferenceConfig:
    weights: Path
    conf: float
    imgsz: int
    verbose: bool


# Aggregation configuration object
@dataclass
class AggregationConfig:
    max_history: int
    stable_age: int                                             # Number of frames an object is seen
    max_idle_frames: int



# -----------------------------
# Main Vision Config
# -----------------------------
@dataclass
class VisionConfig:
    io: IOConfig
    class_names: List[str]
    training: YOLOModelTrainerConfig
    inference: InferenceConfig
    tracking: TrackingConfig
    aggregation: AggregationConfig



# This object avoids passing raw YOLO tensors everywhere, used in Vision module only
@dataclass
class Detection:                    
    class_id: int
    class_name: str
    confidence: float
    bbox: List[int]                                             # [x1, y1, x2, y2]
    track_id: int | None = None


# This is enum, maintaining lifecycle state of an object
class TrackedState(Enum):
    NEW = "new"
    STABLE = "stable"
    SELECTED = "selected"
    DONE = "done"
    LOST = "lost"
    UNATTEMPTED = "unattempted"


# This object representing a tracked item, used outside Vision module 
@dataclass
class TrackedGarbage:
    track_id: int
    class_id: int
    class_name: str
    avg_confidence: float
    bbox: Tuple[int, int, int, int]                             # (x1, y1, x2, y2)
    age: int                                                    # number of frames seen
    last_seen_frame: int
    state: TrackedState
    fade_frames_remaining: int = 0                              # UI related