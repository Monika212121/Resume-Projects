from typing import List
from src.common.logging import logger
from src.fish.stage1_vision.entity import Detection, TrackedGarbage
from src.fish.stage1_vision.detector import GarbageDetector
from src.fish.stage1_vision.tracker import GarbageTracker
from src.fish.stage1_vision.aggregator import GarbageAggregator


class VisionPipeline:
    """
    Stage1: Vision Pipeline
    """
    def __init__(self, vision_cfg):
        self.infer_config = vision_cfg.inference
        self.tracker_config = vision_cfg.tracking
        self.class_names = vision_cfg.class_names
        self.aggregator_config = vision_cfg.aggregation

        self.detector = GarbageDetector(self.infer_config)
        self.tracker = GarbageTracker(self.tracker_config)
        self.aggregator = GarbageAggregator(self.aggregator_config)


    def run(self, frame) -> List[TrackedGarbage]:
        try:
            logger.info("VisionPipeline-> run(): STARTS")

            # Loading the trained YOLO model
            detection_model = self.detector.detection_model

            # Creating tracker object
            garbage_tracker_obj = self.tracker

            # Running Inference on this model
            results = garbage_tracker_obj.infer_yolo_model(model = detection_model, frame = frame, infer_cfg = self.infer_config)
            
            detections: List[Detection] = []

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

                    detections.append(detection)

            # Creating tracked garbage aggregations, from the list of detections. 
            aggregations = self.aggregator.create_garbage_aggregations(detections = detections)

            logger.info("VisionPipeline-> run(): ENDS")
            return aggregations


        except Exception as e:
            logger.info(f"Error occured in VisionPipeline-> run(): {e}")  
            raise e