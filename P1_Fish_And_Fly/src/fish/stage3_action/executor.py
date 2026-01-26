from src.common.logging import logger

from src.fish.stage2_decision.entity import ActionIntent
from src.fish.stage3_action.entity import ActionFeedback, ActionStatus
from src.fish.stage3_action.bin_manager import BinManager
from src.fish.stage3_action.manipulator import Manipulator



class ActionExecutor:
    def __init__(self, bin_manager_obj: BinManager):
        self.bin_manager = bin_manager_obj
        self.manipulator = Manipulator()


    def execute_action(self, action_intent: ActionIntent) -> ActionFeedback:
        """
        Executes the action and creates the action feedback.
        
        Returns this action feedback, back to the Decision module.
        
        :param action_intent: Action intent received from the Decision module.
        :type action_intent: ActionIntent
        :return: Action feedback like SUCCESS/FAILED.
        :rtype: ActionFeedback
        """
        try:
            logger.info(f"execute_action(): STARTS, action intent: {action_intent}")
            garbage_position = action_intent.bbox  

            # Execute the real action to collect/grasp the garbage.
            success = self.manipulator.grasp_garbage(garbage_position)

            # Case1: If the locked object is not collected.
            if not success:
                feedback = ActionFeedback(
                    status = ActionStatus.FAILED,
                    track_id = action_intent.track_id,
                    reason = "Target grasp failed"
                )

            # Case2: If the locked object is collected successfully.
            else:
                feedback = ActionFeedback(
                    status = ActionStatus.SUCCESS,
                    track_id = action_intent.track_id,
                    reason = "Target collected"
                )
                
            logger.info(f"execute_action(): ENDS, feedback: {feedback}")
            return feedback
        
        
        except Exception as e:
            logger.error(f"Error occurred in ActionExecutor -> execute_action(), error: {e}")
            raise e
        

        