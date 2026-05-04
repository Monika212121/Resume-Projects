from typing import List, Tuple

from src.common.logging import logger
from src.common.vision.pipeline import CommonVisionPipeline
from src.common.vision.entity import Detection, TrackedObject, EntityRole, VisionConfig

from src.fish.stage1_vision.aggregator import ObjectAggregator



class VisionPipeline:
    """
    Stage1: Vision Pipeline
    """
    def __init__(self, vision_config: VisionConfig):
        self.cfg = vision_config

        self.class_names = self.cfg.class_names
        self.aggregator_config = self.cfg.aggregation
        self.categories_config = self.cfg.categories

        self.aggregator = ObjectAggregator(self.aggregator_config)
        self.vision = CommonVisionPipeline(vision_config= self.cfg)

    

    def run(self, frame) -> Tuple[List[TrackedObject], List[TrackedObject], List[TrackedObject]]:
        try:
            logger.info("VisionPipeline-> run(): STARTS")

            # Running inference on YOLOv8s model
            results = self.vision.tracker.infer_yolo_model(frame = frame)
            
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
            active_objects, collected_object, lost_objects = self.aggregator.create_garbage_aggregations(detections = detection_list)
            
            logger.info("VisionPipeline-> run(): ENDS")
            return active_objects, collected_object, lost_objects                                              


        except Exception as e:
            logger.info(f"Error occurred in VisionPipeline -> run(), error: {e}")  
            raise e