# Aim: RULE FILTER / HARD GATE 
# It is a filter system with a defined set of rules, to filter out the unstable detections.

# Set of rules for the Rule subsystem are:-
# 1. Rule1: Minimum Age(Number of frames apperared) of a detection.
# 2. Rule2: Minimum Confidence of a detection.
# 3. Rule3: Allowed classes of a detection.

from typing import List
from src.common.logging import logger
from src.fish.stage1_vision.entity import TrackedGarbage


class RuleFilter:
    """
    Deterministic rules to eliminate bad detections
    """
    def __init__(self, rules_cfg):
        self.min_age: int =  rules_cfg.min_age
        self.min_conf: float = rules_cfg.min_conf
        self.allowed_classes: List[str] = rules_cfg.allowed_classes
        
    
    # Applies HARD GATE(set of rules) to filter unstable detections, from the tracked aggregated detections from the Vision Module.
    def apply_hard_rules(self, tracked_objects: List[TrackedGarbage]) -> List[TrackedGarbage]:
        """
        Docstring for hard_rules_apply

        :param self: Belongs to RuleFilter class
        :param tracked_objects: List of tracked aggregated garbage from the Vision module.
        :type tracked_objects: List[TrackedGarbage]
        :return: List of filterd tracked garbage aggregations with the Hard Gate/Rule Filter. 
        :rtype: List[TrackedGarbage]
        """
        logger.info(f"apply_hard_rules(): STARTS, initial detections: {len(tracked_objects)}")

        filtered_objects: List[TrackedGarbage] = []
        
        # Filtering the tracked aggregated list of detections.
        for object in tracked_objects:

            # Rule1: If object appeared in lesser frames than the set minimum age, then ignore the detection.
            if object.age < self.min_age:
                continue

            # Rule2: If object has lesser confidence than the set minimum confidence, then ignore the detection.
            if object.avg_confidence < self.min_conf:
                continue

            # Rule3: If the object is not in the set allowed classes, then ignore the detection.
            if object.class_name not in self.allowed_classes:
                continue

            # Adding the detections to the final list, which passes all the above 3 filters (rules).
            filtered_objects.append(object)

        logger.info(f"apply_hard_rules(): ENDS, final filtered detections: {len(filtered_objects)}")
        return filtered_objects
    
