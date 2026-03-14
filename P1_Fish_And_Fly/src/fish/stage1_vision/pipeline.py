import os
from typing import List, Tuple

from src.common.logging import logger

from src.fish.stage1_vision.train import ModelTrainer
from src.fish.stage1_vision.tracker import GarbageTracker
from src.fish.stage1_vision.detector import GarbageDetector
from src.fish.stage1_vision.aggregator import GarbageAggregator
from src.fish.stage1_vision.entity import VisionConfig, Detection, TrackedGarbage, EntityRole



class VisionPipeline:
    """
    Stage1: Vision Pipeline
    """
    def __init__(self, vision_config: VisionConfig):
        self.class_names = vision_config.class_names
        self.training_config = vision_config.training
        self.infer_config = vision_config.inference
        self.tracker_config = vision_config.tracking
        self.aggregator_config = vision_config.aggregation
        self.categories_config = vision_config.categories

        self.model_weights_path = self.infer_config.weights
        self.model_trainer = ModelTrainer(self.training_config)
        self.ensure_model_ready()                                                                           # refer VISION_NOTE.md(3)

        self.detector = GarbageDetector(self.infer_config)
        self.tracker = GarbageTracker(self.tracker_config)
        self.aggregator = GarbageAggregator(self.aggregator_config)



    def ensure_model_ready(self) -> None:
        try: 
            logger.info("VisionPipeline -> ensure_model_ready()")

            if not os.path.exists(self.model_weights_path):                                                 # check if `weights/best.pt` file exists
                logger.warning("Weights not found. Training model..............")
                self.model_trainer.train_yolo_model()

            return


        except Exception as e:
            logger.info(f"Error occurred in VisionPipeline -> ensure_model_ready(), error: {e}") 
            raise e
    


    def run(self, frame) -> Tuple[List[TrackedGarbage], List[TrackedGarbage]]:
        try:
            logger.info("VisionPipeline-> run(): STARTS")

            # Loading the trained YOLO model
            detection_model = self.detector.detection_model

            # Running inference on this model
            results = self.tracker.infer_yolo_model(model = detection_model, frame = frame, infer_cfg = self.infer_config)
            
            detection_list: List[Detection] = []

            # Processing the results from YOLO inference(DETECTION + TRACKING), to create list of detections.
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    cls_name = self.class_names[cls_id]
                    entity_role: EntityRole = EntityRole.ENVIRONMENT_ENTITY

                    # Assign entity role for Semantic categorization(later in Decision module)
                    if cls_name in self.categories_config.collection_targets:
                        entity_role = EntityRole.COLLECTION_TARGET

                    elif cls_name in self.categories_config.environmental_entities:
                        entity_role = EntityRole.ENVIRONMENT_ENTITY

                    elif cls_name in self.categories_config.navigation_hazards:
                        entity_role = EntityRole.NAVIGATION_HAZARD

                    detection = Detection(
                        class_id = cls_id,
                        class_name = cls_name,
                        confidence = float(box.conf[0]),
                        bbox = list(map(int, box.xyxy[0])),
                        track_id = int(box.id[0]) if box.id is not None else None,
                        entity_role = entity_role
                    )

                    detection_list.append(detection)


            # Creating tracked objects aggregation, from the list of detections. 
            active_aggregations, lost_aggregations = self.aggregator.create_garbage_aggregations(detections = detection_list)
            
            logger.info("VisionPipeline-> run(): ENDS")
            return (active_aggregations, lost_aggregations)                                              


        except Exception as e:
            logger.info(f"Error occurred in VisionPipeline -> run(), error: {e}")  
            raise e