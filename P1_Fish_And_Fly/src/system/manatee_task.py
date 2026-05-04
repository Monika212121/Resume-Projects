# Stateful execution

import asyncio

from src.common.logging import logger

from src.manatee.manatee_pipeline import ManateePipeline

from src.system.mission_control import MissionController



async def run_manatee(manatee: ManateePipeline, dispatch_order_queue: asyncio.Queue, dispatch_outcome_queue: asyncio.Queue, mission_control: MissionController):

    while not mission_control.should_stop():
        try:
            logger.info(f"$$$$$$$$$$$$$$$$  run_manatee(): $$$$$$$$$$$$$$$$$$$")

            logger.info(f"Dispatch_order Queue: {dispatch_order_queue.qsize()}")
            
            # Pick task if there is any dispatch order
            if not dispatch_order_queue.empty():
                dispatch_order = await dispatch_order_queue.get()

            # Exexute task continuously
            if dispatch_order:
                logger.info(f"Manatee executing Dispatch order: {dispatch_order}")
                dispatch_order_outcome = manatee.tick(dispatch_order = dispatch_order)

            if dispatch_order_outcome:
                await dispatch_outcome_queue.put(dispatch_order_outcome)


        except Exception as e:
            logger.error(f"Error in run_manatee(), error: {e}", exc_info= True)
            raise e

        await asyncio.sleep(0.1)