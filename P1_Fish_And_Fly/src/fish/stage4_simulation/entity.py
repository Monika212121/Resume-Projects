from enum import Enum
from typing import List, Tuple
from dataclasses import dataclass

from src.fish.stage3_action.entity import ActionStatus



@dataclass
class SimulationVisualization:
    enabled_gui: bool


@dataclass
class Metadata:
    body_id: int                    # pybullet id
    spawn_time: float               # time of spawning
    lifetime: float                 # time duration of spawn
    fade_time: float                # time for which object disappear
    spawn_world_position: Tuple[float, float, float]    # position of object spawned in sim world frame
    status: ActionStatus = ActionStatus.ACTIVE


@dataclass
class SpawnObject:
    name: str
    shape: str
    size: Tuple[float, ...]
    color: Tuple[float, float, float, float]
    count: int

@dataclass
class Visual:
    targets: List[SpawnObject]
    entities: List[SpawnObject]
    hazards: List[SpawnObject]



@dataclass
class Zone:
    x_range: Tuple[float, float]
    y_range: Tuple[float, float]
    z: float
    min_distance: float

@dataclass
class SpawnZone:
    targets: Zone
    entities: Zone
    hazards: Zone

@dataclass
class SpawningConfig:
    visual: Visual
    zone: SpawnZone



@dataclass
class SimulationConfig:
    visualization: SimulationVisualization
    spawning: SpawningConfig