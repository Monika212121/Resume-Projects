# Object tracking for underwater objects

from box import ConfigBox
from src.common.logging import logger


class GarbageTracker:
    """
    Object tracking using "BORT-SORT" algorithmn inside Ultralytics YOLO.
    NOTE: Tracking is a thin wrapper around Detection, not a post-process. Tracking is part of inference process.
    """
    def __init__(self, tracker_cfg: ConfigBox):
        self.tracking_enabled = tracker_cfg.enabled
        self.tracker_cfg = tracker_cfg


    def infer_yolo_model(self, model, frame, infer_cfg):
        """
        YOLO Inference is done.
        If tracking_enabled = true, tracking happens, else tracking does not happen, just detection
        """
        try: 
            logger.info("infer_yolo_model(): STARTS")

            model_tracker_cfg = self.tracker_cfg
            logger.info(f"infer_yolo_model(): INFERENCE CONFIGURATIONS: {infer_cfg}")
            logger.info(f"infer_yolo_model(): TRACKING CONFIGURATIONS: {model_tracker_cfg}")

            # CASE1: When tracking is enabled : (DETECTION + TRACKING)
            if self.tracking_enabled:
                results =  model.track(
                    source = frame,
                    conf = infer_cfg.conf,
                    imgsz = infer_cfg.imgsz,
                    tracker = model_tracker_cfg.tracker,
                    persist = model_tracker_cfg.persist,
                    verbose = model_tracker_cfg.verbose
                )

                logger.info("infer_yolo_model(): Detection is done with Tracking")

            # CASE2: When tracking is not enabled : (ONLY DETECTION)
            else:
                results = model(
                    frame,
                    conf = infer_cfg.conf,
                    imgsz = infer_cfg.imgsz,
                    verbose = infer_cfg.verbose
                )

                logger.info("infer_yolo_model(): Detection is done without Tracking")
                

            logger.info("infer_yolo_model(): ENDS")
            return results


        except Exception as e:
            logger.info(f"Error occured in infer_yolo_model(): {e}")
            raise e
        
    

    