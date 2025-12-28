import cv2
from src.common.config.configuration import ConfigurationManager
from src.fish.stage1_vision.detector import GarbageDetector
from src.fish.stage1_vision.tracker import GarbageTracker
from src.common.logging import logger


def predict_image(image_path: str):
    try:
        logger.info("predict_image(): STARTS")

        # Loading configurations for the fish machine
        fish_cfg_mg = ConfigurationManager("fish")

        # Loading configuratiosn for inference and tracking
        garbage_detector_cfg = fish_cfg_mg.get_model_inference_config()
        garbage_tracker_cfg = fish_cfg_mg.get_garbage_tracking_config()

        # Creating objects of detector and tracker
        garbage_detector_obj = GarbageDetector(garbage_detector_cfg)
        garbage_tracker_obj = GarbageTracker(garbage_tracker_cfg)

        # Loading the YOLO model with trained best weights
        detection_model = garbage_detector_obj.detection_model

        image = cv2.imread(image_path)

        # Running inference on the given image
        results = garbage_tracker_obj.infer_yolo_model(model = detection_model, frame = image, infer_cfg = garbage_detector_cfg)

        # Visualizing detections 
        for r in results:
            r.show()

        logger.info("predict_image(): ENDS")
        return


    except Exception  as e:
        logger.info(f"Error occurred in predict_image(): {e}")
        raise e



if __name__ == "__main__":
    predict_image("data/yolo/images/val/119.jpg")