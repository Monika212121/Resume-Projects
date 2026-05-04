from dataclasses import dataclass



@dataclass(frozen= True)
class CostWeights:
    travel_time: float
    energy: float
    current: float
    drag: float
    risk: float
    uncertainty: float


@dataclass(frozen= True)
class VehicleModel:
    cruise_speed: float
    drag_coeff: float
    avg_drag_force: float


@dataclass(frozen= True)
class NormalizationLimits:
    max_distance: float
    max_energy: float
    max_current: float
    max_risk: float
    max_uncertainty: float


@dataclass
class CostModel:
    cost_weigths: CostWeights
    vehicle_model: VehicleModel
    normalization_limits: NormalizationLimits