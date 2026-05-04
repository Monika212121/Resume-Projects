# This is core brain loop, Fly wrapper


import asyncio

from src.common.logging import logger

from src.fly.fly_pipeline import FlyPipeline

from src.system.mission_control import MissionController



async def run_fly(
        fly: FlyPipeline, 
        fish_control_signal_queue: asyncio.Queue,
        fish_heartbeat_queue: asyncio.Queue, 
        dispatch_order_queue: asyncio.Queue, 
        dispatch_outcome_queue: asyncio.Queue, 
        mission_control: MissionController
    ):

    while not mission_control.should_stop():
        try:

            logger.info(f"$$$$$$$$$$$$$$$$  run_fly(): $$$$$$$$$$$$$$$$$$$")

            # Wait for heartbeat (SYSTEM PRIMARY DRIVER)
            if not fish_heartbeat_queue.empty():
                fish_heartbeat = await fish_heartbeat_queue.get()

            logger.info(f"run_fly(): Fly received heartbeat: {fish_heartbeat}")

            dispatch_order, fish_control_signal = fly.tick(heartbeat = fish_heartbeat)

            # Send Dispatch order to Manatee
            if dispatch_order:
                await dispatch_order_queue.put(dispatch_order)

            # Send Control signal to Fish
            if fish_control_signal:
                await fish_control_signal_queue.put(fish_control_signal)

            program_terminate: bool = False

            # Process Manatee feedback (NON BLOCKING)
            while not dispatch_outcome_queue.empty():
                dispatch_order_outcome = await dispatch_outcome_queue.get()
                fly.process_manatee_action(dispatch_outcome = dispatch_order_outcome)

                # Central termination check
                if not fly.is_system_active():
                    program_terminate = True
                    break
            
            if program_terminate:
                mission_control.stop()
                break                       # exit main while loop


        except Exception as e:
            logger.error(f"Error in run_fly(), error: {e}", exc_info = True)
            raise e

        await asyncio.sleep(0.01)
