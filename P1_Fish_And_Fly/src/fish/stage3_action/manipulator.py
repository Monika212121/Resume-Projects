# Aim: update backend grasp state and produce semantic feedback

from src.common.logging import logger

from src.fish.stage3_action.entity import ActionFeedback, ActionStatus



class Manipulator:
    """
    Given simulation result, update backend grasp state and produce semantic feedback
    """
    def __init__(self):
        self.garbage_grasped: bool = False



    def resolve_garbage_collection(self, garbage_track_id: int, sim_collected: bool) -> ActionFeedback:
        try:
            logger.debug(f"Manipulator -> resolve_garbage_collection(): STARTS, track_id: {garbage_track_id}") 

            # 1. Update the garbage collection status, based on the result of real action/simulation(here)
            self.update_garbage_grasp(sim_collected)

            # 2. Create action feedback, based on the simulation's result
            # Case1: If the locked object is not collected
            if not sim_collected:
                feedback = ActionFeedback(
                    status = ActionStatus.FAILED,
                    track_id = garbage_track_id,
                    need_manatee_help= False,
                    reason = "Target grasp failed",
                    dump_event= None
                )
            # Case2: If the locked object is collected successfully
            else:
                feedback = ActionFeedback(
                    status = ActionStatus.COLLECTED,
                    track_id = garbage_track_id,
                    need_manatee_help= False,
                    reason = "Target collected",
                    dump_event= None
                )
                
            logger.debug(f"Manipulator -> resolve_garbage_collection(): ENDS, feedback: {feedback}")
            return feedback
        
        
        except Exception as e:
            logger.error(f"Error occurred in Manipulator ->  resolve_garbage_collection(), error: {e}")
            raise e
        


    # Just for maintaining internal record of collection targets
    def update_garbage_grasp(self, sim_collected: bool):
        try:
            # Updating garbage grasp status, based on the Simulation's result.
            if sim_collected:
                logger.debug(f"Manipulator -> update_garbage_grasp(): Garbage is grasped")
                self.garbage_grasped = True
                return

            logger.debug(f"Manipulator -> update_garbage_grasp(): ENDS, Garbage is not grasped.")
            return


        except Exception as e:
            logger.error(f"Error occurred in Manipulator -> update_garbage_grasp(), error: {e}")
            raise e

