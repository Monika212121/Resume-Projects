import os

from src.common.logging import logger
from src.common.vision.train import ModelTrainer
from src.common.vision.tracker import ObjectTracker
from src.common.vision.detector import ObjectDetector
from src.common.vision.entity import VisionConfig




class CommonVisionPipeline:
    def __init__(self, vision_config: VisionConfig):
        self.cfg = vision_config

        self.training_config = self.cfg.training
        self.infer_config = self.cfg.inference
        self.tracker_config = self.cfg.tracking

        # Model training 
        self.model_weights_path = self.infer_config.weights
        self.model_trainer = ModelTrainer(self.training_config)
        self.ensure_model_ready()                                                                           # refer VISION_NOTE.md(3)

        # Object detection
        self.detector = ObjectDetector(self.infer_config)

        # Object tracking
        self.detection_model = self.detector.detection_model
        self.tracker = ObjectTracker(model= self.detection_model, infer_cfg= self.infer_config, tracker_cfg= self.tracker_config)




    def ensure_model_ready(self) -> None:
        try: 
            logger.debug("CommonVisionPipeline -> ensure_model_ready(): STARTS")

            if not os.path.exists(self.model_weights_path):                                                 # check if `weights/best.pt` file exists
                logger.warning("Weights not found. Training model..............")
                self.model_trainer.train_yolo_model()
            
            logger.debug("CommonVisionPipeline -> ensure_model_ready(): ENDS, YOLO model trained")
            return


        except Exception as e:
            logger.info(f"Error occurred in CommonVisionPipeline -> ensure_model_ready(), error: {e}") 
            raise e