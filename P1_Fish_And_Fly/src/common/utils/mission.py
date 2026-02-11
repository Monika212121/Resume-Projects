from src.common.logging import logger

from src.fish.stage3_action.entity import MissionPhase



def mission_is_active(curr_phase: MissionPhase) -> bool:
    try:
        logger.info(f"mission_is_active(): STARTS")

        # Mission is not active when its current phase is completed, aborted or failed.
        if curr_phase in {MissionPhase.DONE, MissionPhase.ABORT, MissionPhase.FAILED}:
            logger.info(f"misssion_is_active(): Mission is not active, current phase: {curr_phase}")
            return False

        logger.info(f"misssion_is_active(): ENDS")
        return True


    except Exception as e:
        logger.info(f"Error occurred in mission_is_active(), error: {e}")
        raise e
    
