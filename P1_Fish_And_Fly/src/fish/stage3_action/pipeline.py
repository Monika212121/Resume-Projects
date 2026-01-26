from typing import Optional
from src.common.logging import logger

from src.fish.stage3_action.entity import ActionFeedback
from src.fish.stage3_action.executor import ActionExecutor
from src.fish.stage2_decision.entity import ActionIntent



class ActionPipeline:
    def __init__(self, executor_obj: ActionExecutor):
        self.executor = executor_obj


    def run(self, action_intent: ActionIntent) -> ActionFeedback:
        """
        Executes 1 action intent for a locked object.
        
        :param self: Belongs to the Action Pipeline.
        :param action_intent: Action intent needs to be performed.
        :type action_intent: Optional[ActionIntent]
        :return: Action feedback, returned to Decision layer back.(status = SUCCESS/FAILED)
        :rtype: ActionFeedback | None
        """
        try:
            logger.info(f"ActionPipeline-> run(): START, action_intent: {action_intent}")
            
            # Executing the action and creating action feedback accordingly.
            action_feedback = self.executor.execute_action(action_intent)

            logger.info(f"ActionPipeline-> run(): ENDS, action_feedback: {action_feedback}")

            # Returning generated action feedback (Action -> Decision module).
            return action_feedback
        

        except Exception as e:
            logger.error(f"Error occured in ActionPipeline -> run(), error: {e}")
            raise e
        

# FOR TESTING AND DEBUGGING
"""
# Loading the Fish module configuration
fish_cfg_mg = ConfigurationManager("fish")

bin_config = fish_cfg_mg.get_bin_manager_config()
executor = ActionExecutor(bin_cfg= bin_config)
action_pipeline_obj = ActionPipeline(executor= executor)


first_action_intent = ActionIntent(
    track_id= 1,
    class_name= "plastic",
    priority_score= 0.80,
    bbox= (1544, 65, 1918, 593),
    reason = "high priority garbage"
)

action_pipeline_obj.run(action_intent= first_action_intent)
"""