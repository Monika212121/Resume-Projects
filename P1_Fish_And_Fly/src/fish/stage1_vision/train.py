# Aim: Perform training of the pre-trained YOLO model(from ultralytics) with the custom dataset(marine dataset)

from ultralytics import YOLO

from src.common.logging import logger

from src.fish.stage1_vision.entity import YOLOModelTrainerConfig



class ModelTrainer:
    def __init__(self, yolo_model_trainer_config: YOLOModelTrainerConfig):
        self.model_trainer_cfg = yolo_model_trainer_config



    def train_yolo_model(self):
        """
        Train YOLO model for Fish vision (object detection)
        """
        try:
            logger.info("ModelTrainer -> train_yolo_model(): START")

            # Loading the YOLO model training configurations
            #fish_cfg_mgr = ConfigurationManager("fish")
            #model_trainer_cfg = fish_cfg_mgr.get_training_config()

            model_name = self.model_trainer_cfg.model_name
            params = self.model_trainer_cfg.model_parameters
            logger.info(f"ModelTrainer -> train_yolo_model(): MODEL NAME: {model_name}, MODEL PARAMETERS: {params}")

            # Loading pre-trained YOLOv8s model
            # Here: model_name = path to model file, i.e. 'model/yolo8s.pt'. This function displays model info on load.
            model = YOLO(model_name)

            # Performing model training of the pre-trained YOLO model
            model.train(
                data = params.data,                                                                         # I/P = location where input dataset(images) is present
                imgsz = params.imgsz,
                epochs = params.epochs,
                batch = params.batch,
                device = params.device,
                optimizer = params.optimizer,
                hsv_h = params.hsv_h,
                hsv_s = params.hsv_s,
                hsv_v = params.hsv_v,
                mosaic = params.mosaic,
                degrees = params.degrees,
                shear = params.shear,
                flipud = params.flipud,
                fliplr = params.fliplr,
                translate = params.translate,
                scale = params.scale,
                project = params.project,                                                                   # O/P = location to save trained model's weights  
                name = params.name
            )

            logger.info(f"ModelTrainer -> train_yolo_model(): ENDS, Trained YOLO model weights are saved in this location: {params.project}")
            return


        except Exception as e:
            logger.info(f"Error occurred in ModelTrainer -> train_yolo_model(), error: {e}")
            raise e