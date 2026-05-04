# Aim: Entry point of the whole system.
# I made some changes here, now only bootstrapping is done in main.py file, all logic moved to orchestrator.

import time
import asyncio

from src.common.logging import logger
from src.common.simulation.sim_bridge import SimulationBridge
from src.common.config.configuration import ConfigurationManager

from src.fly.fly_pipeline import FlyPipeline

from src.fish.fish_pipeline import FishPipeline

from src.manatee.manatee_pipeline import ManateePipeline

from src.system.orchestrator import AsyncOrchestrator



async def main_async():
    try:
        logger.info("*********************************************MAIN SYSTEM: STARTS********************************************")

        # Loading configurations
        common_config = ConfigurationManager("common")
        fly_config = ConfigurationManager("fly")
        fish_config = ConfigurationManager("fish")
        manatee_config = ConfigurationManager("manatee")

        dump_points = common_config.get_dump_points_config()
        simulation_config = common_config.get_simulation_config()

        # Instantiating the main pipelines
        simulation_obj = SimulationBridge(simulation_config= simulation_config, dump_points_info= dump_points)
        
        fly_machine = FlyPipeline(fly_cfg= fly_config, dump_points = dump_points, simulation_bridge = simulation_obj)
        fish_machine = FishPipeline(fish_cfg= fish_config, dump_points = dump_points, simulation_bridge = simulation_obj)
        manatee_machine = ManateePipeline(manatee_cfg= manatee_config, dump_points = dump_points, simulation_bridge = simulation_obj)

        # Start project's simulation
        simulation_obj.start()

        # Noting mission's start time
        mission_start_time = time.time()

        # System orchestrator
        orchestrator = AsyncOrchestrator(
            fly = fly_machine,
            fish = fish_machine,
            manatee = manatee_machine
        )

        # Starts system(Block until mission ends)
        await orchestrator.start()


    except Exception as e:
        logger.error(f"[FATAL ERROR] {e}", exc_info=True)

    finally:
        logger.info("========== MAIN SYSTEM END ==========")
        mission_end_time = time.time()

        #logger.info(f"Total time taken in this mission is: {mission_end_time - mission_start_time}")



def main():
    """
    Entry point for the entire system.
    """
    try:
        asyncio.run(main_async())

    except KeyboardInterrupt:
        logger.warning("SYSTEM INTERRUPTED BY USER")

    except Exception as e:
        logger.error(f"[MAIN FAILURE] {e}", exc_info=True)


if __name__ == "__main__":
    main()