# Aim: REASONER / SOFT INTELLIGENCE

import math
from typing import List

from src.common.logging import logger
from src.common.projection.entity import FishFrameObject

from src.fish.stage2_decision.entity import PriorityReasonerConfig



class PriorityReasoner:
    """
    Calculate a priority score for tracked garbages.
    """
    def __init__(self, reasoner_config: PriorityReasonerConfig):
        self.hazard_radius = reasoner_config.hazard_radius               # adjust it later



    # Hazard Proximity Check
    def is_hazard_near_target(self, target_object: FishFrameObject, hazard_objects: List[FishFrameObject]) -> bool:
        try:
            logger.info(f"PriorityReasoner -> is_hazard_near_target(): ENDS, target: {target_object}, hazard_objects: {hazard_objects}")

            for hazard_obj in hazard_objects:
                # Calculating distance between the target and this hazard object
                dx = target_object.relative_position.x - hazard_obj.relative_position.x
                dy = target_object.relative_position.y - hazard_obj.relative_position.y
                dz = target_object.relative_position.z - hazard_obj.relative_position.z           

                distance = math.sqrt(dx*dx + dy*dy + dz*dz)
                logger.info(f"PriorityReasoner -> is_hazard_near_target(), distance: {distance}")

                # Checking if hazard is near to the target object
                if distance < self.hazard_radius:
                    logger.info(f"PriorityReasoner -> is_hazard_near_target(), hazard_near: True")
                    return True


            logger.info(f"PriorityReasoner -> is_hazard_near_target(): ENDS, hazard_near: False")
            return False


        except Exception as e:
            logger.info(f"Error occurred in PriorityReasoner -> is_hazard_near_target(), error: {e}")
            raise e
        


    # Hazard-Aware Priority Scoring
    def calculate_priority_score(self, target_objects: List[FishFrameObject], hazard_objects: List[FishFrameObject]) -> List[FishFrameObject]:
        try:
            logger.info(f"PriorityReasoner -> rank_targets(): STARTS, target_objects: {target_objects}, hazard_objects: {hazard_objects}")

            # Calculate priority score for all target objects
            for obj in target_objects:

                # Calculate base priority score, using formula [base_score = 1 / distance of target w.r.t fish machine]
                base_score = 1 / (obj.relative_distance + 1e-6)

                # Penalize heavily in case any hazard objects is near to this target object
                priority_score = base_score
                hazard_is_near = self.is_hazard_near_target(target_object= obj, hazard_objects= hazard_objects)
                if hazard_is_near:
                    priority_score = base_score * -1        # penalize base score
                
                obj.priority_score = priority_score


            logger.info(f"PriorityReasoner -> rank_targets(): ENDS, ranked_objects: {target_objects}")
            return target_objects


        except Exception as e:
            logger.info(f"Error occurred in PriorityReasoner -> rank_targets(), error: {e}")
            raise e