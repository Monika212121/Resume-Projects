# Aim: RULE FILTER / HARD GATE 
# It is a filter system with a defined set of rules, to filter out the unstable detections.

# Set of rules for the Rule subsystem are:-
# 1. Rule1: Minimum Age(Number of frames apperared) of a detection.
# 2. Rule2: Minimum Confidence of a detection.
# 3. Rule3: Allowed classes of a detection.

from typing import List, Dict

from src.common.logging import logger
from src.common.projection.entity import FishFrameObject

from src.fish.stage1_vision.aggregator import TrackedState

from src.fish.stage2_decision.entity import RuleFilterConfig



class Filter:
    """
    Deterministic rules to eliminate bad detections
    """
    def __init__(self, rules_filter_cfg: RuleFilterConfig):
        self.min_age: int =  rules_filter_cfg.min_age
        self.min_conf: float = rules_filter_cfg.min_conf
        self.allowed_classes: List[str] = rules_filter_cfg.allowed_classes
    


    def filter_by_stability_rules(self, fish_frame_objects: Dict[int, FishFrameObject]) -> List[FishFrameObject]:
        try:
            logger.info(f"Filter -> filter_by_stability_rules(): STARTS, before filtering n(objects): {len(fish_frame_objects)}")

            # NOTE: If an object is UNATTEMPTED, it means that its already beeen considered, it means it was stable
            # Object lifecycle = NEW -> STABLE -> UNATTEMPTED -> DONE | FAILED | LOST | AVOIDED | IGNORED
            allowed_phases = [TrackedState.STABLE, TrackedState.SELECTED, TrackedState.UNATTEMPTED, TrackedState.AVOIDED, TrackedState.IGNORED]

            stable_fish_frame_objects = [obj for obj in fish_frame_objects.values() if obj.state in allowed_phases]

            logger.info(f"Filter -> filter_by_stability_rules(): ENDS, after filtering n(objects): {len(stable_fish_frame_objects)}")
            return stable_fish_frame_objects
        

        except Exception as e:
            logger.info(f"Error occurred in Filter -> filter_by_stability_rules(), error: {e}")
            raise e
    


    # Applies HARD GATE(set of rules) to filter unstable detections, from the tracked aggregated detections from the Vision Module.
    def filter_by_hard_rules(self, tracked_objects: List[FishFrameObject]) -> List[FishFrameObject]:
        """
        Docstring for hard_rules_apply

        :param self: Belongs to RuleFilter class
        :param tracked_objects: List of tracked aggregated garbage from the Vision module.
        :type tracked_objects: List[TrackedGarbage]
        :return: List of filterd tracked garbage aggregations with the Hard Gate/Rule Filter. 
        :rtype: List[TrackedGarbage]
        """
        try:
            logger.info(f"Filter -> filter_by_hard_rules(): STARTS, initial detections: {len(tracked_objects)}")

            filtered_objects: List[FishFrameObject] = []
            
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

            logger.info(f"Filter -> filter_by_hard_rules(): ENDS, final filtered detections: {len(filtered_objects)}")
            return filtered_objects

    
        except Exception as e:
            logger.info(f"Error occurred in Filter -> filter_by_hard_rules(), error: {e}")
            raise e