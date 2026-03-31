# NOTE: This file is not part of the main pipeline, it is just for quick sanity check to see detections are accurate or not(in an image)
# How to use: Just give the image path, you want to infer, in main() of this file.
# How to test: In the terminal, run this file, run command `python src/fish/stage1_vision/predict.py` and we will see the detections in the given image.


import cv2

from src.common.logging import logger
from src.common.vision.pipeline import CommonVisionPipeline
from src.common.config.configuration import ConfigurationManager



def predict_image(image_path: str):
    try:
        logger.info("predict_image(): STARTS")

        # Loading configurations for the fish machine
        fish_cfg_mg = ConfigurationManager("fish")

        vision = CommonVisionPipeline(vision_config= fish_cfg_mg.get_vision_config())

        image = cv2.imread(image_path)

        # Running inference on the given image
        results = vision.tracker.infer_yolo_model(frame = image)

        # Visualizing detections
        for r in results:
            r.show()

        logger.info("predict_image(): ENDS")
        return


    except Exception  as e:
        logger.info(f"Error occurred in predict_image(), error: {e}")
        raise e



if __name__ == "__main__":
    predict_image("dataset/test_images/test_img6.jfif")