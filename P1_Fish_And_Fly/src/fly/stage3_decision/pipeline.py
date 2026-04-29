from typing import List, Optional, Tuple

from src.common.logging import logger
from src.common.utils.mission import MissionPhase
from src.common.logging.entity import CoverageArea
from src.common.entity.dispatch import DispatchOrder
from src.common.entity.fish_communication import SystemHeartbeat

from src.fly.stage3_decision.agent_monitor import HeartbeatMonitor
from src.fly.stage3_decision.dump_management_system import DumpManagementSystem
from src.fly.stage3_decision.entity import DumpConfig, FlyDecisionConfig, FishStatus, StateDeltas



class DecisionPipeline:
    """
    Pure decision-making brain of Fly.

    Responsibilities:
    - Monitor Fish health
    - Update DMS from heartbeat
    - Decide Manatee dispatch
    """

    def __init__(self, decision_cfg: FlyDecisionConfig, dump_points: List[DumpConfig]):
        self.cfg = decision_cfg
        self.dump_points = dump_points

        self.monitor = HeartbeatMonitor(monitor_config= self.cfg.monitor)
        self.dms = DumpManagementSystem(dms_config= self.cfg.dms, dump_points = self.dump_points)



    def run(self, heartbeat: SystemHeartbeat, coverage_area_pcts: CoverageArea) -> Tuple[StateDeltas, Optional[DispatchOrder]]:
        try:
            logger.info(f"DecisionPipeline -> run(): STARTS")

            state_deltas: StateDeltas
            dispatch_order: Optional[DispatchOrder] = None

            # Creating state deltas, from its current heartbeat, to monitor Fish machine's health
            state_deltas = self.monitor.calculate_fish_state_deltas(heartbeat= heartbeat, coverage_area_pcts= coverage_area_pcts)

            # Creating dispatch order for Manatee machine
            
            # CASE1: If Fish machine is DEAD or asekd help or FAIELD/ABORTED executing mission, creating Fish rescue order, to extract Fish machine safely to the HQ
            if (state_deltas.fish_state != FishStatus.ALIVE.name) or heartbeat.need_help or (heartbeat.mission_phase in [MissionPhase.FAILED, MissionPhase.ABORT]):

                dispatch_order = DispatchOrder.create_rescue_order(
                    fish_position= heartbeat.position,
                    all_dump_points_state= self.dms.get_all_dumps()
                )

                logger.info(f"DecisionPipeline -> run(), RESCUE ORDER CREATED, Fish machine state: {state_deltas.fish_state}, heartbeat: {heartbeat}")
                return (state_deltas, dispatch_order)

          
            # Updating DMS from Heartbeat, in case any dump event (unloading of fish's bin) took place
            if heartbeat.dump_event:
                self.dms.mark_loaded(dump_event= heartbeat.dump_event)

            # CASE2: If a dump point exceeds its capacity threshold, creating collection order, to unload the filled dump point
            target_dump = self.dms.get_most_urgent_filled_dump()
            if target_dump:
                logger.info(f"DecisionPipeline -> run(), filled target dump: {target_dump}")

                dispatch_order = DispatchOrder.create_collection_order(
                    dump_id= target_dump.dump_id,
                    dump_position= target_dump.position,
                    dump_load= target_dump.current_load
                )

            logger.info(f"DecisionPipeline -> run(): ENDS, dispatch_order: {dispatch_order}")
            return (state_deltas, dispatch_order)


        except Exception as e:
            logger.error(f"Error occurred in DecisionPipeline -> run(), error: {e}", exc_info= True)
            raise e