from box import ConfigBox
from src.common.utils.config_loader import load_machine_config


class ConfigurationManager():
    """
    Central Configuration Mananger for Fish/ Fly
    """
    #-----------------------------------------BASIC CONFIGURATIONS-------------------------------------------------------------
    def __init__(self, machine: str):
        self._config: ConfigBox = load_machine_config(machine)

    # It contains (base + all 4 stages) configs
    def get_all_config(self) -> ConfigBox:
        return self._config
    
    
    #-----------------------------------------VISION CONFIGURATIONS-------------------------------------------------------------
    
    def get_vision_config(self) -> ConfigBox:
        return self._config.vision

    def get_garbage_class_names(self):
        return self._config.vision.class_names
    
    # Phase1: Garbage Detection(model = YOLO)
    def get_detection_model_name(self) -> str:
        return self._config.vision.training.model_name

    def get_model_trainer_config(self) -> ConfigBox:
        return self._config.vision.training.model_parameters
    
    def get_model_inference_config(self) -> ConfigBox:
        return self._config.vision.inference


    # Phase2: Garbage Tracking(technique = BORTSORT)
    def get_garbage_tracking_config(self) -> ConfigBox:
        return self._config.vision.tracking

    
    
    #-----------------------------------------DECISION CONFIGURATIONS-------------------------------------------------------------

    def get_decision_config(self) -> ConfigBox:
        return self._config.decision
    
    def get_rules_config(self) -> ConfigBox:
        return self._config.decision.rules
    
    def get_reasoner_config(self) -> ConfigBox:
            return self._config.decision.reasoner

    def get_planner_config(self) -> ConfigBox:
            return self._config.decision.planner
    

    #-----------------------------------------LANGUAGE CONFIGURATIONS-------------------------------------------------------------

    def get_language_config(self) -> ConfigBox:
        return self._config.language
    


    #-----------------------------------------ACTION CONFIGURATIONS---------------------------------------------------------------

    def get_action_config(self) -> ConfigBox:
        return self._config.action