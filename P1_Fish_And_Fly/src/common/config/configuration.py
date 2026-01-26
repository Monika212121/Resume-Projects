from box import ConfigBox

from src.common.config.config_mapper import parse_waypoint, parse_waypoint_list
from src.common.config.config_loader import load_machine_config

from src.fish.stage3_action.entity import Mission, Bin, Navigation, CostWeights, VehicleModel, NormalizationLimits, CostModel, DumpLocation


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
    

    def get_mission_config(self) -> Mission:
        cfg = self._config.action.mission

        mission_cfg = Mission(
            start_point= parse_waypoint(cfg.start_point),
            end_point= parse_waypoint(cfg.end_point),
            hq_point= parse_waypoint(cfg.hq_point),
            depths= cfg.depths,
            navigation= cfg.navigation,
            limits= cfg.limits,
            bin_manager= cfg.bin_manager
        )

        return mission_cfg
    

    def get_bin_manager_config(self) -> Bin:
        cfg = self._config.action.mission.bin_manager

        bin_cfg = Bin(
            bin_capacity= int(cfg.bin_capacity),
            alert_threshold= float(cfg.alert_threshold)
        )

        return bin_cfg
    

    def get_navigation_config(self) -> Navigation:
        cfg = self._config.action.mission.navigation 

        nav_cfg = Navigation(
            start_point= parse_waypoint(cfg.start_point),
            end_point= parse_waypoint(cfg.end_point),
            sweep_step= cfg.sweep_step,
            reach_threshold= cfg.reach_threshold,
            speeds= cfg.speeds
        )

        return nav_cfg
    

    def get_dump_location_config(self) -> DumpLocation:
        cfg = self._config.action

        dump_location = DumpLocation(
            d_points = parse_waypoint_list(cfg.d_points)
        )

        return dump_location


    def get_cost_model_config(self) -> CostModel:
        cfg = self._config.action.cost_model

        weights = CostWeights(
            travel_time=cfg.weights.travel_time,
            energy=cfg.weights.energy,
            current=cfg.weights.current,
            drag=cfg.weights.drag,
            risk=cfg.weights.risk,
            uncertainty=cfg.weights.uncertainty,
        )

        vehicle = VehicleModel(
            cruise_speed=cfg.vehicle.cruise_speed,
            drag_coeff=cfg.vehicle.drag_coeff,
            avg_drag_force=cfg.vehicle.avg_drag_force,
        )

        norm = NormalizationLimits(
            max_distance=cfg.normalization.max_distance,
            max_energy=cfg.normalization.max_energy,
            max_current=cfg.normalization.max_current,
            max_risk=cfg.normalization.max_risk,
            max_uncertainty=cfg.normalization.max_uncertainty,
        )

        cost_model_config = CostModel(
            cost_weigths= weights,
            vehicle_model= vehicle,
            normalization_limits= norm
        )

        return cost_model_config
