# YOLO + classifier detection for underwater garbage
from ultralytics import YOLO
from box import ConfigBox
from src.common.logging import logger


class GarbageDetector:
    """
    YOLO based Garbage Detector
    Detector just owns YOLO model, whereas Tracker decided Inference mode.
    """
    def __init__(self, cfg: ConfigBox):
        self.detection_cfg = cfg
        self.detection_model = YOLO(self.detection_cfg.weights)