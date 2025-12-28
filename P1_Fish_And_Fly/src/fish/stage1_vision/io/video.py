import cv2
from src.common.logging import logger
from src.fish.stage1_vision.io.base import VisionInput


class VideoInput(VisionInput):
    def __init__(self, video_path: str):
        self.video_path = video_path
        self.cap = None


    def start(self):
        logger.info(f"VideoInput -> start() : path = {self.video_path}")
        self.cap = cv2.VideoCapture(self.video_path)

        if not self.cap.isOpened():
            logger.info("VideoInput -> start(): Unable to open video file")
            raise RuntimeError("Unable to open video file")
        

    def read(self):        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        return frame
    

    def stop(self):
        if self.cap:
            self.cap.release()
            logger.info("VideoInput -> stop(): released")  