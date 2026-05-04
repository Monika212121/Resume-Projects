import asyncio

from src.common.logging import logger

from src.fly.fly_pipeline import FlyPipeline
from src.fish.fish_pipeline import FishPipeline
from src.manatee.manatee_pipeline import ManateePipeline

from src.system.fly_task import run_fly
from src.system.fish_task import run_fish
from src.system.manatee_task import run_manatee
from src.system.mission_control import MissionController
from src.system.queues import  fish_control_signal_queue, fish_heartbeat_queue, dispatch_order_queue, dispatch_outcome_queue



class AsyncOrchestrator:
    def __init__(self, fly: FlyPipeline, fish: FishPipeline, manatee: ManateePipeline):
        self.fly = fly
        self.fish = fish
        self.manatee = manatee

        self.mission_control = MissionController()



    async def start(self):

        # Inititate all machines
        self.fly.initiate()
        self.fish.initiate()
        self.manatee.initiate()
        
        logger.info(f"All machines started")

        tasks = [
            asyncio.create_task(run_fish(self.fish, fish_control_signal_queue, fish_heartbeat_queue, self.mission_control)),
            asyncio.create_task(run_fly(self.fly, fish_control_signal_queue, fish_heartbeat_queue, dispatch_order_queue, dispatch_outcome_queue, self.mission_control)),
            asyncio.create_task(run_manatee(self.manatee, dispatch_order_queue, dispatch_outcome_queue, self.mission_control)),
        ]

        # Wait until mission ends
        await self.mission_control.stop_event.wait()

        logger.info(f"Mission stopped triggered")

        # Cancel all tasks
        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions= True)

        # Graceful shutdown
        self.shutdown()
        return

    
    
    def shutdown(self):
        logger.info("SAFE SHUTDOWN INIT")

        try:
            self.fish.terminate()
        except:
            logger.warning("Fish shutdown failed")

        try:
            self.fly.terminate()
        except:
            logger.warning("Fly shutdown failed")

        try:
            self.manatee.terminate()
        except:
            logger.warning("Manatee shutdown failed")

        logger.info("SYSTEM SHUTDOWN COMPLETE")

