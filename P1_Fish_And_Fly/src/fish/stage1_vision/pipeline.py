from typing import List
from box import ConfigBox

from src.common.logging import logger

from src.fish.stage1_vision.tracker import GarbageTracker
from src.fish.stage1_vision.detector import GarbageDetector
from src.fish.stage1_vision.aggregator import GarbageAggregator
from src.fish.stage1_vision.entity import Detection, TrackedGarbage



class VisionPipeline:
    """
    Stage1: Vision Pipeline
    """
    def __init__(self, vision_cfg: ConfigBox):
        self.infer_config = vision_cfg.inference
        self.tracker_config = vision_cfg.tracking
        self.class_names = vision_cfg.class_names
        self.aggregator_config = vision_cfg.aggregation

        self.detector = GarbageDetector(self.infer_config)
        self.tracker = GarbageTracker(self.tracker_config)
        self.aggregator = GarbageAggregator(self.aggregator_config)
        logger.info(f"vision init(): vision cfg: {vision_cfg}")



    def run(self, frame) -> List[TrackedGarbage]:
        try:
            logger.info("VisionPipeline-> run(): STARTS")

            # Loading the trained YOLO model
            detection_model = self.detector.detection_model

            # Creating tracker object
            garbage_tracker_obj = self.tracker

            # Running Inference on this model
            results = garbage_tracker_obj.infer_yolo_model(model = detection_model, frame = frame, infer_cfg = self.infer_config)
            
            detection_list: List[Detection] = []

            # Processing the results from YOLO inference(DETECTION + TRACKING), to create list of detections.
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    detection = Detection(
                        class_id = cls_id,
                        class_name = self.class_names[cls_id],
                        confidence = float(box.conf[0]),
                        bbox = list(map(int, box.xyxy[0])),
                        track_id = int(box.id[0]) if box.id is not None else None
                    )

                    detection_list.append(detection)

            # Creating tracked garbage aggregations, from the list of detections. 
            active_aggregations = self.aggregator.create_garbage_aggregations(detections = detection_list)

            logger.info("VisionPipeline-> run(): ENDS")
            return active_aggregations


        except Exception as e:
            logger.info(f"Error occurred in VisionPipeline-> run(): {e}")  
            raise e