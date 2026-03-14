# Aim: This file build Vision Input, avoiding if-else chaos in main.py.

from src.common.logging import logger

from src.fish.stage1_vision.entity import IOConfig
from src.fish.stage1_vision.io.video import VideoInput
from src.fish.stage1_vision.io.camera import CameraInput
from src.fish.stage1_vision.io.folder_video import FolderVideoInput


# Returns the Vision Input object, after detecting the source of visual feed (CAMERA/ VIDEO/ SIMULATION).
def build_vision_input(io_cfg: IOConfig):
    try:
        logger.info(f"build_vision_input(): STARTS, vision source: {io_cfg.source}")

        if io_cfg.source == "camera" and io_cfg.camera:
            return CameraInput(device_id= io_cfg.camera.device_id)
        
        elif io_cfg.source == "video" and io_cfg.video:
            return VideoInput(video_path= str(io_cfg.video.path))
        
        elif io_cfg.source == "folder_video" and io_cfg.video:
            return FolderVideoInput(root_folder= str(io_cfg.video.path))
        
        else:
            raise ValueError(f"Unknown video source: {io_cfg.source}")
    

    except Exception as e:
        logger.info(f"Error occurred in build_vision_input(): {e}")
        raise e