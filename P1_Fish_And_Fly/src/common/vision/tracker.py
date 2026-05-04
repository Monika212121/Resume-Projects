# Object tracking for underwater objects
from ultralytics import YOLO

from src.common.logging import logger
from src.common.vision.entity import InferenceConfig, TrackingConfig



class ObjectTracker:
    """
    Object tracking using "BORT-SORT" algorithmn inside Ultralytics YOLO.
    NOTE: Tracking is a thin wrapper around Detection, not a post-process. Tracking is part of inference process.
    """
    def __init__(self, model: YOLO, infer_cfg: InferenceConfig, tracker_cfg: TrackingConfig):
        self.model = model
        self.infer_cfg = infer_cfg
        self.tracker_cfg = tracker_cfg

        self.tracking_enabled = tracker_cfg.enabled



    def infer_yolo_model(self, frame):
        """
        YOLO Inference is done.
        If tracking_enabled = true, tracking happens, else tracking does not happen, just detection
        """
        try: 
            #logger.info("infer_yolo_model(): STARTS")

            # CASE1: When tracking is enabled : (DETECTION + TRACKING)
            if self.tracking_enabled:
                results =  self.model.track(
                    source = frame,
                    conf = self.infer_cfg.conf,
                    imgsz = self.infer_cfg.imgsz,
                    tracker = self.tracker_cfg.tracker,
                    persist = self.tracker_cfg.persist,
                    verbose = self.tracker_cfg.verbose
                )

                #logger.info("infer_yolo_model(): Detection is done with Tracking")

            # CASE2: When tracking is not enabled : (ONLY DETECTION)
            else:
                results = self.model(
                    frame,
                    conf = self.infer_cfg.conf,
                    imgsz = self.infer_cfg.imgsz,
                    verbose = self.infer_cfg.verbose
                )

                #logger.info("infer_yolo_model(): Detection is done without Tracking")
                
            #logger.info("infer_yolo_model(): ENDS")
            return results


        except Exception as e:
            logger.info(f"Error occured in ObjectTracker -> infer_yolo_model(): {e}")
            raise e
        
    

    