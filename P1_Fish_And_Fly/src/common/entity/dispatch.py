import time
from enum import Enum
from typing import Optional, List
from dataclasses import dataclass, field

from src.common.entity.position import Waypoint
from src.common.entity.dump import DumpPointState
from src.common.entity.manatee_communication import ManateeMode, DumpInfo, TaskStatus



@dataclass
class DispatchOrder:
    source: str
    operation_mode: ManateeMode                    
    timestamp: float
    
    # COLLECTION specific
    dump_info: Optional[DumpInfo] = None

    # RESCUE specific
    fish_position: Optional[Waypoint] = None

    # FINAL SWEEP specific
    all_dumps_state: List[DumpPointState] = field(default_factory=list)
 

    @staticmethod
    def create_collection_order(dump_id: int, dump_position: Waypoint, dump_load: float):
        return DispatchOrder(
            source= "Fly",
            operation_mode= ManateeMode.COLLECTION,
            timestamp= time.time(),
            dump_info= DumpInfo(dump_id= dump_id, dump_position= dump_position, dump_current_load= dump_load)
        )


    @staticmethod
    def create_rescue_order(fish_position, all_dump_points_state: List[DumpPointState]):
        return DispatchOrder(
            source= "Fly",
            operation_mode= ManateeMode.RESCUE,
            timestamp= time.time(),
            fish_position= fish_position,
            all_dumps_state= all_dump_points_state
        )
    
    @staticmethod
    def create_shadow_order(fish_position):
        return DispatchOrder(
            source= "Fly",
            operation_mode= ManateeMode.SHADOW,
            timestamp= time.time(),
            fish_position= fish_position,
        )
    
    @staticmethod
    def create_final_sweep_order(all_dump_points_state: List[DumpPointState]):
        return DispatchOrder(
            source= "Fly",
            operation_mode= ManateeMode.FINAL_SWEEP,
            timestamp= time.time(),
            all_dumps_state= all_dump_points_state
        )
    

@dataclass
class DispatchOutcome:
    dispatch_order: DispatchOrder
    task_status: TaskStatus
    issue: str
    cleaned_dump_ids: List[int] = field(default_factory=list)
