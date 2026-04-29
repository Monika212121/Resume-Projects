# This is just a wrapper for fish pipeline

import asyncio
from typing import Optional

from src.common.logging import logger
from src.common.entity.fish_communication import FishControlSignal

from src.fish.fish_pipeline import FishPipeline

from src.system.mission_control import MissionController



async def run_fish(fish: FishPipeline, fish_control_signal_queue: asyncio.Queue, fish_heartbeat_queue: asyncio.Queue, mission_control: MissionController):

    latest_signal: Optional[FishControlSignal] = None                                                # stores last signal

    while not mission_control.should_stop():
        try:
            logger.info(f"$$$$$$$$$$$$$$$$  run_fish(): $$$$$$$$$$$$$$$$$$$")

            # Non blocking update of control signal
            if not fish_control_signal_queue.empty():
                latest_signal = await fish_control_signal_queue.get()

            # Always run Fish machine
            heartbeat = fish.tick(operation_instruction= latest_signal)
            logger.info(f"run_fish(), Fish heartbeat: {heartbeat}")

            if heartbeat:
                await fish_heartbeat_queue.put(heartbeat)


        except Exception as e:
            logger.error(f"Error in run_fish(), error: {e}", exc_info= True)
            raise e


        await asyncio.sleep(0.5)            # control rate