# src/fly/decision/dms/dump_management_system.py

from typing import Dict, List, Optional

from src.common.logging import logger
from src.common.entity.dump import DumpPointState
from src.common.entity.fish_communication import DumpEvent

from src.fly.stage3_decision.entity import DumpConfig, DMSConfig



class DumpManagementSystem:
    """
    Dump Management System (DMS)

    Responsibilities:
    - Maintain in-memory state of all dump points
    - Update load state from Fish heartbeat
    - Update unload state from Manatee actions
    - Provide intelligence for dispatch decisions
    """

    def __init__(self, dms_config: DMSConfig, dump_points: List[DumpConfig]):
        self.dms_config = dms_config

        self.capacity_threshold: float = self.dms_config.threshold
        self.cooldown_period: float = self.dms_config.cooldown
        self.dump_points = dump_points

        self.dump_memory: Dict[int, DumpPointState] = {
            d.dump_id: DumpPointState(
                dump_id= d.dump_id,
                position= d.position,
                capacity= d.capacity,
            )
            for d in self.dump_points
        }


    # -----------------------------
    # UPDATE (from Fish heartbeat)
    # -----------------------------
    def mark_loaded(self, dump_event: DumpEvent) -> None:
        try:
            logger.info(f"DMS -> mark_loaded(): STARTS, dump_event: {dump_event}")

            dump_id: int = dump_event.dump_id
            load_added: float = dump_event.load_added

            dump = self.dump_memory.get(dump_id)
            if dump is None:
                logger.error(f"DMS -> mark_loaded(): Invalid dump_id= {dump_id}")
                return

            dump.add_load(load_added)

            logger.info(f"DMS -> mark_loaded(): ENDS, Dump {dump_id} loaded +{load_added} | fill={dump.fill_pct:.2f}")
            return
        

        except Exception as e:
            logger.error(f"Error occurred in DMS -> mark_loaded(), error: {e}", exc_info=True)
            raise

    # -----------------------------
    # AFTER MANATEE ACTION
    # -----------------------------
    def mark_unloaded(self, dump_id: int) -> None:
        try:
            logger.info(f"DMS -> mark_unloaded(): STARTS, dump_id: {dump_id}")

            dump = self.dump_memory.get(dump_id)
            if dump is None:
                logger.error(f"DMS -> mark_unloaded(): Invalid dump_id= {dump_id}")
                return

            dump.clear_load()

            logger.info(f"DMS -> mark_unloaded(): Dump {dump_id} unloaded successfully")
            return
        

        except Exception as e:
            logger.error(f"Error occurred in DMS -> mark_unloaded(), error: {e}", exc_info=True)
            raise

    # -----------------------------
    # QUERY
    # -----------------------------
    def get_dump(self, dump_id: int) -> Optional[DumpPointState]:
        return self.dump_memory.get(dump_id)

    def get_all_dumps(self) -> List[DumpPointState]:
        return list(self.dump_memory.values())


    # -----------------------------
    # CORE INTELLIGENCE
    # -----------------------------
    def get_filled_dump_points(self) -> List[DumpPointState]:
        try:
            filled = [
                d for d in self.dump_memory.values()
                if d.fill_pct >= self.capacity_threshold
                and not d.is_recently_serviced(self.cooldown_period)
            ]

            if filled:
                logger.info(f"DMS -> get_filled_dump_points(), Filled dumps: {[d.dump_id for d in filled]}")

            return filled


        except Exception as e:
            logger.error(f"DMS -> get_filled_dump_points(), error: {e}", exc_info=True)
            raise



    def get_most_urgent_filled_dump(self) -> Optional[DumpPointState]:
        try:
            filled = self.get_filled_dump_points()
            if not filled:
                logger.info(f"DMS -> get_most_urgent_filled_dump(), No dump point is filled yet")
                return None

            # urgency_score() should internally consider:
            # - fill percentage
            # - time since last serviced
            most_urgent = max(filled, key=lambda d: d.urgency_score())

            logger.info(f"DMS -> get_most_urgent_filled_dump(), Selected dump: {most_urgent.dump_id}, (fill={most_urgent.fill_pct:.2f})")
            return most_urgent


        except Exception as e:
            logger.error(f"Error occurred in DMS -> get_most_urgent_filled_dump(), error: {e}", exc_info=True)
            raise