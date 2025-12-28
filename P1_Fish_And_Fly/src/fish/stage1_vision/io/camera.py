import cv2
from src.common.logging import logger
from src.fish.stage1_vision.io.base import VisionInput


class CameraInput(VisionInput):
    def __init__(self, device_id: int = 0):
        self.device_id = device_id
        self.cap = None

    def start(self):
        logger.info(f"CameraInput-> start(): device = {self.device_id}")
        self.cap = cv2.VideoCapture(self.device_id)


        if not self.cap.isOpened():
            logger.info("CameraInput -> start(): Unable to open camera")
            raise RuntimeError("Unable to open camera")
        

    def read(self):
        if self.cap is None:
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        logger.info(f"CameraInput-> read() Camera read sucessfully")
        return frame
    

    def stop(self):
        if self.cap:
            self.cap.release()
            logger.info("CameraInput -> stop(): released")
