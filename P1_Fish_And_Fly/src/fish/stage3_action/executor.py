from src.common.logging import logger
from src.fish.stage2_decision.entity import ActionIntent
from src.fish.stage3_action.entity import ActionFeedback, ActionStatus



class ActionExecutor:
    def __init__(self):
        pass

    def create_action_feedback(self, action_intent: ActionIntent) -> ActionFeedback:
        """
        Creates the action feedback, according to the action execution.
        
        Returns back this action feedback to the Decision module.
        
        :param action_intent: Action intent received from the Decision module.
        :type action_intent: ActionIntent
        :return: Action feedback according to the action executed, i.e. either DONE/LOST.
        :rtype: ActionFeedback
        """
        logger.info(f"create_action_feedback(): STARTS, action intent: {action_intent}")

        # SIMULATED EXECUTION LATER
        success = True

        # Case1: If the locked object is collected successfully
        if success:
            feedback = ActionFeedback(
                track_id = action_intent.track_id,
                status = ActionStatus.SUCCESS,
                reason = "Target collected"
            )
        
        # Case2: If the locked object is not collected
        else:
            feedback = ActionFeedback(
                track_id = action_intent.track_id,
                status = ActionStatus.FAILED,
                reason = "Target lost"
            )

        logger.info(f"create_action_feedback(): ENDS, feedback: {feedback}")
        return feedback