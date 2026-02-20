from dataclasses import dataclass

from src.common.projection.entity import CoordinateFrame

from src.fish.stage3_action.entity import Waypoint, ActionStatus



@dataclass
class SimulationVisualization:
    enabled_gui: bool


@dataclass
class WorldObject:
    object_id: int                  # stable simulation-side id
    class_id: int                   # semantic class (garbage, etc.)
    class_name : str
    world_position: Waypoint        # (x, y, z) in WORLD frame
    state: ActionStatus = ActionStatus.ACTIVE
    frame: CoordinateFrame = CoordinateFrame.WORLD