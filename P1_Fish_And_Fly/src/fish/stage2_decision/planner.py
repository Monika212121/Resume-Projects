from typing import List, Optional, Tuple
from src.common.logging import logger
from src.fish.stage1_vision.entity import TrackedGarbage
from src.fish.stage2_decision.entity import ActionIntent


class ActionPlanner:
    """
    Builds ActionIntent only for the locked target.
    """

    def __init__(self, planner_cfg):
        self.max_targets = planner_cfg.max_targets


    def build_action_intents(self, ranked_objects: List[Tuple[Optional[TrackedGarbage], float]], locked_track_id: Optional[int]) -> Optional[ActionIntent]:
        """
        Builds action intent for the locked target.
        
        :param self: Belongs to the ActionPlanner class.
        :param ranked_objects: List of ranked tracked objects.
        :param locked_track_id: Track_id of the locked target object.
        :type locked_track_id: int
        :return: List of action intents.
        :rtype: List[ActionIntent]
        """
        logger.info(f"build_action_intents(): STARTS")
        logger.info(f"ranked_objects: {ranked_objects}, locked_id: {locked_track_id}")

        if locked_track_id is None:
            logger.info(f"No object is locked")
            return None
        
        if len(ranked_objects) == 0:
            logger.info("No objects are present")
            return None

        for object, pri_score in ranked_objects:
            if object == None:
                continue

            if object.track_id == locked_track_id:                  # When locked target is found
                action_intent = ActionIntent(
                    track_id= object.track_id,
                    class_name = object.class_name,
                    priority_score = pri_score,
                    bbox = object.bbox,
                    reason = "Selected and locked high-priority object"
                )   
            
                return action_intent                                # return action intent here


        logger.info(f"build_action_intents(): ENDS, Locked_id is not found in ranked objects: {locked_track_id}")
        return None
    

