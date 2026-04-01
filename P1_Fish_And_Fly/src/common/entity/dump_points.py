
import time
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

from src.fish.stage3_action.entity import Waypoint



@dataclass
class DumpLocation:
    d_points: List[Waypoint]        # Coordinates of the points where unloading of dustbin takes place


@dataclass
class DumpPointInfo:
    dump_point_id: int
    dump_point_position: Waypoint
    current_load: float
    max_capacity: float
    last_updated: float


    @staticmethod
    def now(dump_point_id: int, position: Waypoint, current_load: int, max_capacity: float):

        return DumpPointInfo(
            dump_point_id = dump_point_id,
            dump_point_position = position,
            current_load = current_load,
            max_capacity = max_capacity,
            last_updated = time.time()
        )