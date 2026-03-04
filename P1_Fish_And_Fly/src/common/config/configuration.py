from typing import List
from box import ConfigBox
from dataclasses import fields

from src.common.config.config_loader import load_machine_config
from src.common.visualization.entity import PerceptionVisualization
from src.common.config.config_mapper import parse_waypoint, parse_waypoint_list

from src.fly.stage2_action.entity import MonitorConfig
from src.fly.stage2_action.entity import FlightControllerConfig

from src.fish.stage5_simulation.entity import SimulationVisualization
from src.fish.stage1_vision.entity import IOConfig, ModelParameter, YOLOModelTrainerConfig, InferenceConfig, TrackingConfig, AggregationConfig, VisionConfig
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
    
    
    # ******************************************************FISH CONFIGURATION*************************************************
    
    # 1. VISION CONFIGURATIONS
    
    def get_vision_config(self) -> VisionConfig:
        vision_cfg = VisionConfig(
            io= self.get_io_config(),
            class_names= self.get_class_names(),
            training= self.get_training_config(),
            inference= self.get_inference_config(),
            tracking= self.get_tracking_config(),
            aggregation= self.get_aggregation_config()
        )

        return vision_cfg
        
    
    def get_io_config(self) -> IOConfig:
        cfg = self._config.vision.io

        # Mapping IO from ConfgBox ->  IOConfig object
        cfg_dict = {}
        for f in fields(IOConfig):
            cfg_dict[f.name] = cfg.get(f.name, f.default)

        model_io_cfg = IOConfig(**cfg_dict)
        return model_io_cfg


    def get_class_names(self) -> List[str]:
        cfg = self._config.vision.class_names

        class_list = list(cfg)
        return class_list
    


    def get_training_config(self) -> YOLOModelTrainerConfig:
        model_name_used: str = self._config.vision.training.model_name
        cfg = self._config.vision.training.model_parameters

        # Mapping training parameters from ConfgBox ->  ModelParameter object
        cfg_dict = {}
        for f in fields(ModelParameter):
            cfg_dict[f.name] = cfg.get(f.name, f.default)

        model_trainer_cfg = YOLOModelTrainerConfig(
            model_name= model_name_used,
            model_parameters= ModelParameter(**cfg_dict)
        )

        return model_trainer_cfg


    def get_inference_config(self) -> InferenceConfig:
        cfg = self._config.vision.inference

        # Mapping inference from ConfgBox ->  InfernceConfig object
        cfg_dict = {}
        for f in fields(InferenceConfig):
            cfg_dict[f.name] = cfg.get(f.name, f.default)

        model_inference_cfg = InferenceConfig(**cfg_dict)
        return model_inference_cfg
    

    # Used technique = BORTSORT
    def get_tracking_config(self) -> TrackingConfig:
        cfg = self._config.vision.tracking

        # Mapping tracking from ConfgBox ->  TrackingConfig object
        cfg_dict = {}
        for f in fields(TrackingConfig):
            cfg_dict[f.name] = cfg.get(f.name, f.default)

        model_tracking_cfg = TrackingConfig(**cfg_dict)
        return model_tracking_cfg
    

    def get_aggregation_config(self) -> AggregationConfig:
        cfg = self._config.vision.aggregation

        # Mapping aggregation from ConfgBox ->  AggregationConfig object
        cfg_dict = {}
        for f in fields(AggregationConfig):
            cfg_dict[f.name] = cfg.get(f.name, f.default)

        model_aggregation_cfg = AggregationConfig(**cfg_dict)
        return model_aggregation_cfg
    

        
    # 2. DECISION CONFIGURATIONS

    def get_decision_config(self) -> ConfigBox:
        return self._config.decision
    
    def get_rules_config(self) -> ConfigBox:
        return self._config.decision.rules
    
    def get_reasoner_config(self) -> ConfigBox:
        return self._config.decision.reasoner

    def get_planner_config(self) -> ConfigBox:
        return self._config.decision.planner
    

 
    # 3. ACTION CONFIGURATIONS

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

    
    #-----------------------------------------VISUALIZATION CONFIGURATIONS---------------------------------------------------------------

    # 1. PERCEPTION
    def get_perception_visualization_config(self) -> PerceptionVisualization:
        cfg = self._config.vision.visualization

        visualizer_config = PerceptionVisualization(
            enabled_gui= cfg.enabled_gui,
        )

        return visualizer_config    

    
    # 2. SIMULATION
    def get_simulation_visualization_config(self) -> SimulationVisualization:
        cfg = self._config.simulation.visualization

        simulation_config = SimulationVisualization(
            enabled_gui= cfg.enabled_gui,
        )

        return simulation_config
    



    # ******************************************************FLY CONFIGURATIONS*************************************************

    # 2. ACTION CONFIGURATIONS
    
    # FLIGHT CONTROLLER
    def get_controller_config(self) -> FlightControllerConfig:
        cfg = self._config.action.controller

        controller_cfg = FlightControllerConfig(
            home= cfg.home
        )

        return controller_cfg


    # HEARTBEAT MONITOR
    def get_monitor_config(self) -> MonitorConfig:
        cfg = self._config.action.monitor

        monitor_cfg = MonitorConfig(
            timeout_sec= cfg.timeout_sec,
            freeze_sec= cfg.freeze_sec
        )

        return monitor_cfg
