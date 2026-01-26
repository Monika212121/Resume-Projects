from typing import List, Iterable, Protocol

from src.fish.stage3_action.entity import Waypoint


# NOTE: This means: “Any object with attributes x, y, z of type float is acceptable.”
class WaypointConfig(Protocol):
    x: float
    y: float
    z: float


def parse_waypoint(cfg: WaypointConfig) -> Waypoint:
    point = Waypoint(
        x = float(cfg.x),
        y = float(cfg.y),
        z = float(cfg.z)
    )
    return point


def parse_waypoint_list(cfg_list: Iterable[WaypointConfig]) -> List[Waypoint]:
    if not isinstance(cfg_list, (list, tuple)):
        raise TypeError("Expected a list of waypoints")

    list_of_points = [parse_waypoint(p) for p in cfg_list]
    return list_of_points