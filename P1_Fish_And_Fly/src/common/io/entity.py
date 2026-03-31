from pathlib import Path
from dataclasses import dataclass
from typing import Optional



# IO configuration objects
@dataclass
class CameraConfig:
    device_id: int


@dataclass
class VideoConfig:
    path: Path


@dataclass
class ScreenDimensions:
    source_width: int
    source_height: int
    display_width: int
    display_height: int


@dataclass
class IOConfig:
    source: str                                                 # "camera" | "video" | "sim"
    screen_dimensions: ScreenDimensions
    record_output: bool                                        # toggle enabling inference video recording
    camera: Optional[CameraConfig] = None
    video: Optional[VideoConfig] = None