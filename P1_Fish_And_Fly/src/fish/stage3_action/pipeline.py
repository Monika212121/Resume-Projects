from typing import Optional
from src.fish.stage3_action.entity import ActionFeedback
from src.fish.stage3_action.executor import ActionExecutor
from src.fish.stage2_decision.entity import ActionIntent
from src.common.logging import logger

class ActionPipeline:
    def __init__(self):
        self.executor = ActionExecutor()


    def run(self, action_intent: Optional[ActionIntent]) -> ActionFeedback |None:
        logger.info(f"ActionPipeline-> run(): START, action_intent: {action_intent}")

        if action_intent is None:
            logger.info("No action intent is passed")
            return None
        
        action_feedback = self.executor.create_action_feedback(action_intent)

        logger.info(f"ActionPipeline-> run(): ENDS, action_feedback: {action_feedback}")

        return action_feedback