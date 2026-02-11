# Aim: Entry point of the whole system.
import time

from src.common.logging import logger
from src.common.utils.mission import mission_is_active
from src.common.config.configuration import ConfigurationManager

from src.fly.fly_pipeline import FlyPipeline

from src.fish.fish_pipeline import FishPipeline
from src.fish.stage3_action.entity import MissionPhase



def main():
    try:
        logger.info("*********************************************MAIN SYSTEM: STARTS********************************************")

        # Loading the Fish and Fly modules configuration
        fly_cfg_manager = ConfigurationManager("fly")
        fish_cfg_manager = ConfigurationManager("fish")

        # Instantiating the main pipelines
        fly_machine = FlyPipeline(fly_cfg_mg= fly_cfg_manager)
        fish_machine = FishPipeline(fish_cfg_mg= fish_cfg_manager)

        # Noting mission's start time
        mission_start_time = time.time()

        # This whole system runs in 3 phases:

        # PHASE1: Initiates both machines: Fish and Fly.
        fly_machine.initiate()
        fish_machine.initiate()

        
        # PHASE2: Implementing water body cleaning mission. 
        while True:

            # 1. Garbage collection is done, on surface and underwater level, by the Fish machine.
            curr_fish_heartbeat = fish_machine.tick()

            # 2. Monitoring the cleaning operation, from above the water body, by the Fly machine.
            fly_machine.tick(heartbeat= curr_fish_heartbeat)

            # 3. If the mission is DONE/ABORTED/FAILED, then stop the system.
            if not mission_is_active(curr_fish_heartbeat.mission_phase):
                break
        
        # Logging the final status of the cleaning operation.
        if curr_fish_heartbeat.mission_phase == MissionPhase.DONE:
            logger.info(f"main(): MISSION IS COMPLETED SUCCESSFULLY")
        else:
            logger.info("main(): Mission is ABORTED/FAILED")

        # Noting mission's end time
        mission_end_time = time.time()

        total_time_taken = mission_end_time - mission_start_time
        logger.info(f"main(): Total time taken in this mission is: {total_time_taken}")


        # PHASE3: Terminates both machines: Fish and Fly.
        fish_machine.terminate()
        fly_machine.terminate()

        logger.info("********************************************MAIN MODULE SYSTEM: ENDS**********************************************")
        return


    except Exception as e:
        logger.info(f"Error occurred in main(), error: {e}")
        raise e

  
main()