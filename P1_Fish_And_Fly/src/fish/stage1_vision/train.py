from ultralytics import YOLO
from src.common.config.configuration import ConfigurationManager
from src.common.logging import logger


def train_yolo_model():
    """
    Train YOLO model for Fish vision (garbage detection)
    """
    try:
        logger.info("train_yolo_model(): START")
        fish_cfg_mgr = ConfigurationManager("fish")

        model_name = fish_cfg_mgr.get_detection_model_name()
        model_trainer_cfg = fish_cfg_mgr.get_model_trainer_config()

        logger.info("train_yolo_model(): MODEL NAME:", model_name, "MODEL TRAINER CONFIG:", model_trainer_cfg)

        # Load pre-trained YOLOv8n
        model = YOLO(model_name)

        model.train(
            data = model_trainer_cfg.data,
            imgsz = model_trainer_cfg.imgsz,
            epochs = model_trainer_cfg.epochs,
            batch = model_trainer_cfg.batch,
            device = model_trainer_cfg.device,
            optimizer = model_trainer_cfg.optimizer,
            hsv_h = model_trainer_cfg.hsv_h,
            hsv_s = model_trainer_cfg.hsv_s,
            hsv_v = model_trainer_cfg.hsv_v,
            mosaic = model_trainer_cfg.mosaic,
            degrees = model_trainer_cfg.degrees,
            shear = model_trainer_cfg.shear,
            flipud = model_trainer_cfg.flipud,
            fliplr = model_trainer_cfg.fliplr,
            translate = model_trainer_cfg.translate,
            scale = model_trainer_cfg.scale,
            project = model_trainer_cfg.project,                # save weights directly in this location 
            name = model_trainer_cfg.name
        )

        logger.info("train_yolo_model(): Trained YOLO model is saved in this location: {model_trainer_cfg.project}")
        logger.info("train_yolo_model(): END")


    except Exception as e:
        logger.info(f"Error occurred in train_yolo_model(): {e}")
        raise e




if __name__ == "__main__":
    train_yolo_model()



