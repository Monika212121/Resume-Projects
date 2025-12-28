# Aim: REASONER / SOFT INTELLIGENCE
# The Garbage Prioritization module computes a composite priority score using multiple Decision signals. 
# These include class-specific importance weights, estimated age-based degradation weight, and model confidence score. 
# The signals are combined using a weighted scoring function to guide removal actions.

# Decision signals we used in the Reasoner subsystem are:
# 1. Class weight
# 2. Age
# 3. Confidence

from typing import List, Tuple, Optional
from src.common.logging import logger
from src.fish.stage1_vision.entity import TrackedGarbage


class PriorityReasoner:
    """
    Calculate a priority score for tracked garbages.
    """
    def __init__(self, reasoner_cfg):
        # Getting decision signals from the set Decision configuration.
        self.class_weights = reasoner_cfg.class_weights
        self.age_weight = reasoner_cfg.age_weight
        self.conf_weight = reasoner_cfg.conf_weight


    # Calculates Priority score for the tracked aggregated objects.
    def calculate_priority_score(self, tracked_objects: List[TrackedGarbage]) -> List[Tuple[Optional[TrackedGarbage], float]]:
        """
        Docstring for calculate_priority_score
        
        :param self: Belongs to class Priority Reasoner
        :param tracked_objects: List of tracked aggregated garbage from the Vision module.
        :type tracked_objects: List[TrackedGarbage]
        :return: List of calculated priority score for all the tracked objects.
        :rtype: List[Tuple(TrackedGarbage, int)]
        """
        logger.info(f"calculate_priority_score(): STARTS, Tracked objects: {len(tracked_objects)}")
        priority_scored_objects: List[Tuple[Optional[TrackedGarbage], float]]= []

        for object in tracked_objects:
            # If object is not found in the class_names dict list, assigning class_score = 0.5 (by default)
            class_score = self.class_weights.get(object.class_name, 0.5)       
            
            # Calculating Weighted Decision Signals, using formula [decision signal * weighted score]
            age_score = object.age * self.age_weight                            
            confidence_score = object.avg_confidence * self.conf_weight         

            # Decision Signals combined via weighted Scoring to produce a Priority Score.
            priority_score: int = class_score + age_score + confidence_score

            # Adding current(object, priority_score) to the final list.
            priority_scored_objects.append((object, priority_score))


        logger.info(f"calculate_priority_score(): ENDS, priority_score_list: {len(priority_scored_objects)}")
        return priority_scored_objects
