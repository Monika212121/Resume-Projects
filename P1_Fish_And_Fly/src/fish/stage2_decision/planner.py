from typing import List, Optional

from src.common.logging import logger
from src.common.projection.entity import FishFrameObject

from src.fish.stage2_decision.entity import ActionIntent



class ActionPlanner:
    """
    Builds ActionIntent only for the locked target.
    """

    def __init__(self):
        pass


    # Action Planner Hazard Reaction: Planner must react to hazards around selected target.
    def build_action_intent(self, safe_ranked_objects: List[FishFrameObject], locked_target_id: Optional[int]) -> Optional[ActionIntent]:
        try: 
            logger.info(f"ActionPlanner -> build_action_intent(): STARTS, ranked_objects: {safe_ranked_objects}, locked_id: {locked_target_id}")

            action_intent: Optional[ActionIntent] = None
            if len(safe_ranked_objects) == 0 or locked_target_id is None:
                logger.info(f"ActionPlanner -> build_action_intent(), There are no safe ranked object")
                return action_intent

            # Creating an action intent, for the selected safe target object
            for object in safe_ranked_objects:
                
                # When locked target is found
                if object.track_id == locked_target_id:                  
                    action_intent = ActionIntent(
                        track_id = object.track_id,
                        class_name = object.class_name,
                        priority_score = object.priority_score,
                        reason = "Selected and locked high-priority safe object"
                    )  

            logger.info(f"ActionPlanner -> build_action_intent(): ENDS, action_intent: {action_intent}")
            return action_intent


        except Exception as e:
            logger.info(f"Error occurred in ActionPlanner -> build_action_intent(), error: {e}")
            raise e