from dataclasses import dataclass



@dataclass
class Speeds:
    surface: float
    underwater: float


@dataclass
class Depths:
    surface: float
    underwater: float


@dataclass
class Limits:
    max_operation_retries: int
    max_mission_time_sec : int
    max_target_loss_ignore: int
    max_step_retry_ignore: int


@dataclass
class Bin:
    bin_capacity: int               # Number of items dustbin can contain
    alert_threshold: float          # Percentage of bin, allowed to filled before unloading