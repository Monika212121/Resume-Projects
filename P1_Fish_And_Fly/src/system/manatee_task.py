# Stateful execution

import asyncio
from typing import Optional

from src.common.entity.manatee_communication import ManateeMode
from src.common.logging import logger
from src.common.entity.dispatch import DispatchOrder, DispatchOutcome

from src.manatee.manatee_pipeline import ManateePipeline

from src.system.mission_control import MissionController



async def run_manatee(manatee: ManateePipeline, dispatch_order_queue: asyncio.Queue, dispatch_outcome_queue: asyncio.Queue, mission_control: MissionController):

    while not mission_control.should_stop():
        try:
            logger.info(f"$$$$$$$$$$$$$$$$  run_manatee(): $$$$$$$$$$$$$$$$$$$")

            logger.info(f"run_manatee(), Dispatch_order Queue size: {dispatch_order_queue.qsize()}")
            logger.info(f"run_manatee(), Dispatch_order Queue: {dispatch_order_queue}")        
            
            active_dispatch_order = manatee.mission_planner_obj.active_dispatch_order
            incoming_dispatch_order: Optional[DispatchOrder] = None
            dispatch_order_outcome: Optional[DispatchOutcome] = None

            if not dispatch_order_queue.empty():
                candidate_order = await dispatch_order_queue.get()

                # CASE1: Rescue order -> Always interupts
                if candidate_order.operation_mode == ManateeMode.RESCUE:
                    logger.warning("RESCUE received -> interrupting current mission")

                    manatee.mission_planner_obj.active_dispatch_order = candidate_order
                    incoming_dispatch_order = candidate_order

                # CASE2: No active task -> Accept task
                elif active_dispatch_order is None:
                    manatee.mission_planner_obj.active_dispatch_order = candidate_order
                    incoming_dispatch_order = candidate_order

                # CASE3: Busy and just sequential incoming task-> Put back in queue
                else:
                    await dispatch_order_queue.put(candidate_order)


            # Execute task continuously
            logger.info(f"run_manatee(), Dispatch order: {incoming_dispatch_order}")
            dispatch_order_outcome = manatee.tick(dispatch_order = incoming_dispatch_order)

            if dispatch_order_outcome:
                await dispatch_outcome_queue.put(dispatch_order_outcome)


        except Exception as e:
            logger.error(f"Error in run_manatee(), error: {e}", exc_info= True)
            raise e

        await asyncio.sleep(0.1)