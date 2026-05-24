import time
from enum import Enum
from typing import Optional, List
from dataclasses import dataclass, field

from src.common.entity.position import Waypoint
from src.common.entity.dump import DumpPointState
from src.common.entity.manatee_communication import ManateeMode, DumpInfo, TaskStatus



@dataclass
class DispatchOrder:
    dispatch_id: int
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
    def create_collection_order(dispatch_id: int, dump_id: int, dump_position: Waypoint, dump_load: float):
        return DispatchOrder(
            dispatch_id= dispatch_id,
            source= "Fly",
            operation_mode= ManateeMode.COLLECTION,
            timestamp= time.time(),
            dump_info= DumpInfo(dump_id= dump_id, dump_position= dump_position, dump_current_load= dump_load)
        )


    @staticmethod
    def create_rescue_order(dispatch_id: int, fish_position, all_dump_points_state: List[DumpPointState]):
        return DispatchOrder(
            dispatch_id= dispatch_id,
            source= "Fly",
            operation_mode= ManateeMode.RESCUE,
            timestamp= time.time(),
            fish_position= fish_position,
            all_dumps_state= all_dump_points_state
        )
        
    @staticmethod
    def create_patrol_order(dispatch_id: int, fish_position):
        return DispatchOrder(
            dispatch_id= dispatch_id,
            source= "Fly",
            operation_mode= ManateeMode.PATROL,
            timestamp= time.time(),
            fish_position= fish_position,
        )
        
    @staticmethod
    def create_return_order(dispatch_id: int):
        return DispatchOrder(
            dispatch_id= dispatch_id,
            source= "Fly",
            operation_mode= ManateeMode.RETURN_HQ,
            timestamp= time.time()
        )  


@dataclass
class DispatchOutcome:
    dispatch_order: Optional[DispatchOrder]
    task_status: TaskStatus
    issue: str
    cleaned_dump_ids: List[int] = field(default_factory=list)
