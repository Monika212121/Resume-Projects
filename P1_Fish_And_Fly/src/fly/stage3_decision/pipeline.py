from typing import List, Optional, Tuple, Set

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

        self.processed_dump_eventIDs= set()                                                  # to avoid creating dispatch order of same event_id / dump_event
        self.active_dispatch_keys = set()                                                    # to avoid returning same disaptch order

        self.dispatch_counter = 1                                                            # to create unique dispatch id



    def run(self, heartbeat: SystemHeartbeat, coverage_area_pcts: CoverageArea) -> Tuple[StateDeltas, Optional[DispatchOrder]]:
        try:
            logger.info(f"DecisionPipeline -> run(): STARTS")

            state_deltas: StateDeltas
            dispatch_order: Optional[DispatchOrder] = None

            # Creating state deltas, from its current heartbeat, to monitor Fish machine's health
            state_deltas = self.monitor.calculate_fish_state_deltas(heartbeat= heartbeat, coverage_area_pcts= coverage_area_pcts)

            # Creating dispatch order for Manatee machine
            dispatch_id = self.dispatch_counter
            
            # CASE1: RESCUE ORDER -> If Fish machine is DEAD or asekd help or FAIELD/ABORTED executing mission, extract Fish machine safely to the HQ
            if heartbeat.need_help or (heartbeat.mission_phase in [MissionPhase.FAILED, MissionPhase.ABORT]):
                logger.info(f"INSIDE RESCUE ORDER CREATION")
                dispatch_key = "RESCUE"
                if dispatch_key in self.active_dispatch_keys:                                               # avoid duplicate rescue orders
                    logger.info(f"DecisionPipeline -> run(), dispatch_id: {dispatch_id} already created RESCUE order")
                    return (state_deltas, dispatch_order)                                                               # (SD, None)
                
                dispatch_order = DispatchOrder.create_rescue_order(
                    dispatch_id= dispatch_id,
                    fish_position= heartbeat.position,
                    all_dump_points_state= self.dms.get_all_dumps()
                )

                self.active_dispatch_keys.add(dispatch_key)
                self.dispatch_counter += 1

                logger.info(f"DecisionPipeline -> run(), RESCUE ORDER CREATED, Fish machine state: {state_deltas.fish_state}, heartbeat: {heartbeat}")
                return (state_deltas, dispatch_order)

          
            # Processing Dump event once, Updating DMS, in case any dump event (unloading of fish's bin) took place
            event = heartbeat.dump_event
            if event and (event.event_id not in self.processed_dump_eventIDs):                              # consuming only unique dump event
                self.dms.mark_loaded(dump_event= event)
                self.processed_dump_eventIDs.add(event.event_id)


            # CASE2: COLLECTION ORDER -> If a dump point exceeds its capacity threshold, empty the filled dump point            # refer ACTION.MD()
            target_dump = self.dms.get_most_urgent_filled_dump()
            if target_dump:
                logger.info(f"DecisionPipeline -> run(), INSIDE COLLECTION ORDER CREATION, filled target dump: {target_dump}")

                dispatch_key = f"COLLECTION:{target_dump.dump_id}"

                if dispatch_key in self.active_dispatch_keys:                                              # avoid duplicate collection orders
                    logger.info(f"DecisionPipeline -> run(), dispatch_id: {dispatch_id} already created for collection")
                    return (state_deltas, dispatch_order)                                                                    # (SD, None)

                dispatch_order = DispatchOrder.create_collection_order(
                    dispatch_id= dispatch_id,
                    dump_id= target_dump.dump_id,
                    dump_position= target_dump.position,
                    dump_load= target_dump.current_load
                )

                self.active_dispatch_keys.add(dispatch_key)
                self.dispatch_counter += 1

                logger.info(f"DecisionPipeline -> run(), COLLECTION ORDER CREATED, Fish machine state: {state_deltas.fish_state}, heartbeat: {heartbeat}")
                return (state_deltas, dispatch_order)
            

            # CASE3: RETURN ORDER -> If Fish machine returned to HQ, after successfully completing the mission
            if heartbeat.mission_phase == MissionPhase.DONE:
                logger.info(f"DecisionPipeline -> run(), INSIDE RETURN_HQ ORDER CREATION")

                dispatch_key = f"RETURN_HQ"

                if dispatch_key in self.active_dispatch_keys:                                              # avoid duplicate collection orders
                    logger.info(f"DecisionPipeline -> run(), dispatch_id: {dispatch_id} already created for RETURN_HQ")
                    return (state_deltas, dispatch_order)  
                
                dispatch_order = DispatchOrder.create_return_order(dispatch_id= dispatch_id)

                self.active_dispatch_keys.add(dispatch_key)
                self.dispatch_counter += 1

                logger.info(f"DecisionPipeline -> run(), RETURN ORDER CREATED, Fish machine state: {state_deltas.fish_state}, heartbeat: {heartbeat}")
                return (state_deltas, dispatch_order)
            

            logger.info(f"DecisionPipeline -> run(): ENDS, dispatch_order: {dispatch_order}")
            return (state_deltas, dispatch_order)


        except Exception as e:
            logger.error(f"Error occurred in DecisionPipeline -> run(), error: {e}", exc_info= True)
            raise e