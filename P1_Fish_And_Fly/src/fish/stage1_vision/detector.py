# YOLO + classifier detection for underwater garbage
from ultralytics import YOLO

from src.fish.stage1_vision.entity import InferenceConfig


class GarbageDetector:
    """
    YOLO based Garbage Detector
    Detector just owns YOLO model, whereas Tracker decided Inference mode.
    """
    def __init__(self, cfg: InferenceConfig):
        self.detection_cfg = cfg
        self.detection_model = YOLO(self.detection_cfg.weights)