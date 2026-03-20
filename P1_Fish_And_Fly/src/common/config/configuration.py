from typing import List
from box import ConfigBox
from dataclasses import fields

from src.common.entity.log_file_paths import LogFilePaths
from src.common.config.config_loader import load_machine_config
from src.common.config.config_mapper import parse_waypoint, parse_waypoint_list

from src.fly.stage1_action.entity import MonitorConfig
from src.fly.stage1_action.entity import FlightControllerConfig

from src.fish.stage1_vision.entity import PerceptionVisualization, IOConfig, ModelParameter, YOLOModelTrainerConfig, InferenceConfig, TrackingConfig, AggregationConfig, Categories, VisionConfig
from src.fish.stage2_decision.entity import RuleFilterConfig, PriorityReasonerConfig, DecisionConfig
from src.fish.stage3_action.entity import ActionConfig, Mission, Bin, Navigation, CostWeights, VehicleModel, NormalizationLimits, CostModel, DumpLocation
from src.fish.stage4_simulation.entity import SimulationVisualization, SimulationConfig, SpawningConfig, SpawnObject, Visual, SpawnZone



class ConfigurationManager():
    """
    Central Configuration Mananger for Fish/ Fly
    """

    # NOTE: self._config contains (base + all stages of specific machine) configs
    # Example: If I pass machine = fish, then self._config contains all the [base.yaml + (vision,decision,action,simulation).yaml] config. 
    # And If I pass machine = fly, self._config contains [base.yaml + action.yaml] config


    #-----------------------------------------BASIC CONFIGURATIONS-------------------------------------------------------------
    
    def __init__(self, machine: str):
        self.machine = machine
        self._config: ConfigBox = load_machine_config(machine)


    def get_all_config(self) -> ConfigBox:
        return self._config
    

    # LOG FILE CONFIGURATION
    def get_log_file_paths(self) -> LogFilePaths:
        cfg = self._config.log_paths

        log_file_paths = LogFilePaths(
            mission_object_log = cfg.mission_object_log,
            mission_telemetry_log = cfg.mission_telemetry_log
        )

        return log_file_paths
    

    #-----------------------------------------VISUALIZATION CONFIGURATIONS---------------------------------------------------------------

    # 1. PERCEPTION
    def get_perception_visualization_config(self) -> PerceptionVisualization:
        cfg = self._config[self.machine].vision.visualization

        visualizer_config = PerceptionVisualization(
            enabled_gui= cfg.enabled_gui,
        )

        return visualizer_config    

    
    # 2. SIMULATION
    def get_simulation_visualization_config(self) -> SimulationVisualization:
        cfg = self._config[self.machine].simulation.visualization

        simulation_config = SimulationVisualization(
            enabled_gui= cfg.enabled_gui,
        )

        return simulation_config
    

    # ******************************************************FISH CONFIGURATION*************************************************

    
    # 1. VISION CONFIGURATIONS
    
    def get_vision_config(self) -> VisionConfig:
        vision_cfg = VisionConfig(
            visualization= self.get_perception_visualization_config(),
            io= self.get_io_config(),
            class_names= self.get_class_names(),
            training= self.get_training_config(),
            inference= self.get_inference_config(),
            tracking= self.get_tracking_config(),
            aggregation= self.get_aggregation_config(),
            categories= self.get_categories_config()
        )

        return vision_cfg

    
    def get_io_config(self) -> IOConfig:
        cfg = self._config[self.machine].vision.io

        # Mapping IO from ConfgBox ->  IOConfig object
        cfg_dict = {}
        for f in fields(IOConfig):
            cfg_dict[f.name] = cfg.get(f.name, f.default)

        model_io_cfg = IOConfig(**cfg_dict)
        return model_io_cfg


    def get_class_names(self) -> List[str]:
        cfg = self._config[self.machine].vision.class_names

        class_list = list(cfg)
        return class_list    


    def get_training_config(self) -> YOLOModelTrainerConfig:
        model_name_used: str = self._config[self.machine].vision.training.model_name
        cfg = self._config[self.machine].vision.training.model_parameters

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
        cfg = self._config[self.machine].vision.inference

        # Mapping inference from ConfgBox ->  InfernceConfig object
        cfg_dict = {}
        for f in fields(InferenceConfig):
            cfg_dict[f.name] = cfg.get(f.name, f.default)

        model_inference_cfg = InferenceConfig(**cfg_dict)
        return model_inference_cfg
    

    # Used technique = BORTSORT
    def get_tracking_config(self) -> TrackingConfig:
        cfg = self._config[self.machine].vision.tracking

        # Mapping tracking from ConfgBox ->  TrackingConfig object
        cfg_dict = {}
        for f in fields(TrackingConfig):
            cfg_dict[f.name] = cfg.get(f.name, f.default)

        model_tracking_cfg = TrackingConfig(**cfg_dict)
        return model_tracking_cfg
    

    def get_aggregation_config(self) -> AggregationConfig:
        cfg = self._config[self.machine].vision.aggregation

        # Mapping aggregation from ConfgBox ->  AggregationConfig object
        cfg_dict = {}
        for f in fields(AggregationConfig):
            cfg_dict[f.name] = cfg.get(f.name, f.default)

        model_aggregation_cfg = AggregationConfig(**cfg_dict)
        return model_aggregation_cfg
    

    def get_categories_config(self) -> Categories:
        cfg = self._config[self.machine].vision.categories

        # Mapping categories from ConfgBox ->  Categories object
        cfg_dict = {}
        for f in fields(Categories):
            cfg_dict[f.name] = cfg.get(f.name, f.default) if not None else []

        model_categories_cfg = Categories(**cfg_dict)
        return model_categories_cfg



    # 2. DECISION CONFIGURATIONS

    def get_decision_config(self) -> DecisionConfig:
        decision_cfg = DecisionConfig(
            rule_filter_cfg= self.get_rule_filter_config(),
            reasoner_cfg= self.get_reasoner_config()
        )

        return decision_cfg
    

    def get_rule_filter_config(self) -> RuleFilterConfig:
        cfg = self._config[self.machine].decision.rule_filter
        cfg_dict = {}

        for f in fields(RuleFilterConfig):
            if f.name in cfg:
                cfg_dict[f.name] = cfg.get(f.name)
            else:
                # if field has default → use it
                if f.default is not None:
                    cfg_dict[f.name] = f.default

                # if list type → fallback empty list
                elif f.type == List[str]:
                    cfg_dict[f.name] = []

                else:
                    raise ValueError(f"get_rule_filter_config(): Missing required config field: {f.name}")

        return RuleFilterConfig(**cfg_dict)
    
    
    def get_reasoner_config(self) -> PriorityReasonerConfig:
        cfg = self._config[self.machine].decision.reasoner
        cfg_dict = {}

        # Mapping categories from ConfgBox ->  PriorityReasonerConfig object
        for f in fields(PriorityReasonerConfig):
            cfg_dict[f.name] = cfg.get(f.name, f.default)

        reasoner_cfg = PriorityReasonerConfig(**cfg_dict)
        return reasoner_cfg

    

    # 3. ACTION CONFIGURATIONS

    def get_action_config(self) -> ActionConfig:
        action_config = ActionConfig(
            mission= self.get_mission_config(),
            cost_model= self.get_cost_model_config(),
            dump_location= self.get_dump_location_config()
        )

        return action_config
    

    def get_mission_config(self) -> Mission:
        cfg = self._config[self.machine].action.mission

        mission_cfg = Mission(
            start_point= parse_waypoint(cfg.start_point),
            end_point= parse_waypoint(cfg.end_point),
            hq_point= parse_waypoint(cfg.hq_point),
            depths= cfg.depths,
            navigation= self.get_navigation_config(),
            limits= cfg.limits,
            bin_manager= self.get_bin_manager_config()
        )

        return mission_cfg
    

    def get_bin_manager_config(self) -> Bin:
        cfg = self._config[self.machine].action.mission.bin_manager

        bin_cfg = Bin(
            bin_capacity= int(cfg.bin_capacity),
            alert_threshold= float(cfg.alert_threshold)
        )

        return bin_cfg
    

    def get_navigation_config(self) -> Navigation:
        cfg = self._config[self.machine].action.mission.navigation 

        nav_cfg = Navigation(
            start_point= parse_waypoint(cfg.start_point),
            end_point= parse_waypoint(cfg.end_point),
            sweep_step= cfg.sweep_step,
            reach_threshold= cfg.reach_threshold,
            speeds= cfg.speeds
        )

        return nav_cfg
    

    def get_dump_location_config(self) -> DumpLocation:
        cfg = self._config[self.machine].action

        dump_location = DumpLocation(
            d_points = parse_waypoint_list(cfg.dump_location)
        )

        return dump_location


    def get_cost_model_config(self) -> CostModel:
        cfg = self._config[self.machine].action.cost_model

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

    

    # 4. SIMULATION CONFIGURATIONS

    def get_simulation_config(self) -> SimulationConfig:
        simulation_config = SimulationConfig(
            visualization= self.get_simulation_visualization_config(),
            spawning= self.get_spawn_config(),
        )

        return simulation_config


    def get_spawn_config(self) -> SpawningConfig:
        spawning_config = SpawningConfig(
            visual= self.get_spawn_visual_config(),
            zone= self.get_spawn_zone_config()
        )

        return spawning_config
    

    def get_spawn_visual_config(self) -> Visual:
        cfg = self._config[self.machine].simulation.spawning.visual

        visual_config = Visual(
            targets= self._parse_spawn_objects(cfg.targets),
            entities= self._parse_spawn_objects(cfg.entities),
            hazards= self._parse_spawn_objects(cfg.hazards),
        )

        return visual_config

    # helper function of above function
    def _parse_spawn_objects(self, cfg_objects):
        objects = []

        for obj in cfg_objects:
            objects.append(
                SpawnObject(
                    name=obj.name,
                    shape=obj.shape,
                    size=tuple(obj.size),
                    color=tuple(obj.color),
                    count=obj.count,
                )
            )

        return objects


    def get_spawn_zone_config(self) -> SpawnZone:
        cfg = self._config[self.machine].simulation.spawning.zones

        zones_config = SpawnZone(
            targets = cfg.targets,
            entities= cfg.entities,
            hazards= cfg.hazards,
        )

        return zones_config



    # ******************************************************FLY CONFIGURATIONS*************************************************

    # 2. ACTION CONFIGURATIONS
    
    # FLIGHT CONTROLLER
    def get_controller_config(self) -> FlightControllerConfig:
        cfg = self._config[self.machine].action.controller

        controller_cfg = FlightControllerConfig(
            home= cfg.home
        )

        return controller_cfg


    # HEARTBEAT MONITOR
    def get_monitor_config(self) -> MonitorConfig:
        cfg = self._config[self.machine].action.monitor

        monitor_cfg = MonitorConfig(
            timeout_sec= cfg.timeout_sec,
            freeze_sec= cfg.freeze_sec
        )

        return monitor_cfg
