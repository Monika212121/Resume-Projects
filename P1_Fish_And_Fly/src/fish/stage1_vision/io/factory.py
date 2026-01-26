# Aim: This file build Vision Input, avoiding if-else chaos in main.py.
from typing import Any

from src.fish.stage1_vision.io.video import VideoInput
from src.fish.stage1_vision.io.camera import CameraInput
from src.common.logging import logger


# Returns the Vision Input object, after detecting the source of visual feed (CAMERA/ VIDEO/ SIMULATION).
def build_vision_input(io_cfg: Any):
    try:
        logger.info(f"build_vision_input(): STARTS, vision source: {io_cfg.source}")
        if io_cfg.source == "camera":
            return CameraInput(device_id= io_cfg.camera.device_id)
        
        elif io_cfg.source == "video":
            return VideoInput(video_path= io_cfg.video.path)
        
        else:
            raise ValueError(f"Unknown video source: {io_cfg.source}")
    

    except Exception as e:
        logger.info(f"Error occurred in build_vision_input(): {e}")
        raise e