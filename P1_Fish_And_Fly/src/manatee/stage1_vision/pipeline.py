from typing import List, Tuple

from src.common.logging import logger
from src.common.vision.pipeline import CommonVisionPipeline
from src.common.vision.entity import TrackedObject, Detection, EntityRole, TrackedState, VisionConfig



class VisionPipeline:
    def __init__(self, vision_config: VisionConfig):
        self.cfg = vision_config

        self.class_names = self.cfg.class_names
        self.categories_config = self.cfg.categories

        self.vision = CommonVisionPipeline(vision_config= self.cfg)



    def run(self, frame) -> List[TrackedObject]:
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

            # Mapping detections to trackedObject class object
            tracked_objects = self.convert_detections(detections = detection_list)

            # Taking only navigation hazard detections
            navigation_hazards: List[TrackedObject] = [obj for obj in tracked_objects if obj.entity_role == EntityRole.NAVIGATION_HAZARD]

            logger.info(f"VisionPipeline-> run(): ENDS, navigation hazards: {navigation_hazards}")
            return navigation_hazards                                           

        except Exception as e:
            logger.info(f"Error occurred in VisionPipeline -> run(), error: {e}")  
            raise e
        


    def convert_detections(self, detections: List[Detection]) -> List[TrackedObject]:
        try:
            
            tracked_objects: List[TrackedObject] = []

            # Mapping Detection -> trackedObject class
            for det in detections:
                if det.track_id is None:
                    continue

                track_id: int = det.track_id
                det_bbox: Tuple[int, int, int, int] = tuple(det.bbox)
                                          
                tracked_object = TrackedObject(
                    track_id = track_id,
                    class_id = det.class_id,
                    class_name = det.class_name,
                    avg_confidence = det.confidence,
                    bbox = det_bbox,
                    age = 1,
                    last_seen_frame = 0,
                    state = TrackedState.NEW,
                    entity_role = det.entity_role
                )

                tracked_objects.append(tracked_object)
            
            logger.info(f"VisionPipeline-> convert_detections(): ENDS, tracked_objects: {tracked_objects}")
            return tracked_objects

        except Exception as e:
            logger.info(f"Error occurred in VisionPipeline -> convert_detections(), error: {e}")  
            raise e