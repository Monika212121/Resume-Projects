from typing import Tuple, List, Optional, Dict

from src.common.logging import logger
from src.common.projection.entity import FishFrameObject
from src.common.entity.decision_types import DecisionStatus
from src.common.vision.entity import EntityRole

from src.fish.stage2_decision.entity import CategorizedObjects



class Categorizer:
    def __init__(self):
        pass


    def perform_semantic_categorization(self, eligible_objects: List[FishFrameObject]) -> CategorizedObjects:
        try:
            logger.debug(f"Categorizer -> perform_semantic_categorization(): STARTS, eligible_objects: {eligible_objects}")

            target_list: List[FishFrameObject] = []
            environment_list: List[FishFrameObject] = []
            hazard_list: List[FishFrameObject] = []

            # Categorizing eligible objects into 3 semantic categories: target, environment entitiy, navigation hazard
            for obj in eligible_objects:

                # Case1: Collection target(garbage)
                if obj.entity_role == EntityRole.COLLECTION_TARGET:
                    target_list.append(obj)                                                                 # priority_score and decision status will be assigned later

                # Case2: Environment entity(harmless marine life)
                elif obj.entity_role == EntityRole.ENVIRONMENT_ENTITY:
                    obj.priority_score = 0.0                                                                # object ignored
                    obj.decision_status = DecisionStatus.ENVIRONMENT_OBJECT_IGNORED
                    environment_list.append(obj)
                
                # Case3: Navigation Hazard(dangerous animal & rock)
                else:
                    obj.priority_score = -1.0                                                               # object avoided
                    obj.decision_status = DecisionStatus.HAZARD_OBJECT_AVOIDED
                    hazard_list.append(obj)

            # Creating categorized list, adding all 3 categories
            categorized_objects_list = CategorizedObjects(
                collection_targets= target_list,
                environment_entities= environment_list,
                navigation_hazards= hazard_list
            )

            logger.debug(f"Categorizer -> perform_semantic_categorization(): ENDS, categorized_list: {categorized_objects_list}")
            return categorized_objects_list


        except Exception as e:
            logger.error(f"Error occured in Categorizer -> perform_semantic_categorization(), error: {e}")
            raise e



    def perform_target_categorization(self, ranked_target_objects: List[FishFrameObject]) -> Tuple[List[FishFrameObject], List[FishFrameObject]]:
        try:
            logger.debug(f"Categorizer -> perform_target_categorization(): STARTS, ranked_objects: {ranked_target_objects}")
            
            safe_target_objects: List[FishFrameObject] = []
            unsafe_target_objects: List[FishFrameObject] = []

            # Categorizing targets into 2 categories: safe and unsafe
            for obj in ranked_target_objects:

                # Case1: UNSAFE: When hazard object is near to this target object
                if obj.priority_score <= 0:   
                    obj.decision_status = DecisionStatus.TARGET_AVOIDED                                                                 # refer DECISION_NOTES.md(3)                                   
                    unsafe_target_objects.append(obj)
                
                # Case2: SAFE: When hazard object is not near to this target
                else:
                    safe_target_objects.append(obj)

            logger.debug(f"Categorizer -> perform_target_categorization(): ENDS, safe_target_objects: {safe_target_objects}, unsafe_objects: {unsafe_target_objects}")
            return (safe_target_objects, unsafe_target_objects)


        except Exception as e:
            logger.error(f"Error occured in Categorizer -> perform_target_categorization(), error: {e}")
            raise e
        


    def assign_decision_status_for_target_objects(self, all_target_objects: List[FishFrameObject], safe_targets: List[FishFrameObject], unsafe_targets: List[FishFrameObject], selected_track_id: Optional[int]) -> List[FishFrameObject]:
        try:
            logger.debug(f"Categorizer -> assign_decision_status_for_target_objects(): STARTS, SAFE: {safe_targets}, UNSAFE: {unsafe_targets}, SEL_ID: {selected_track_id}")
            
            # Creating a dict of {track_id, priority_score}
            id_score_dict: Dict[int, float] = {}
            for obj in safe_targets:
                id_score_dict[obj.track_id] = obj.priority_score 

            for obj in unsafe_targets:
                id_score_dict[obj.track_id] = obj.priority_score

            unsafe_object_ids = [obj.track_id for obj in unsafe_targets]

            # NOTE: Environment and hazard objects are already updated with, priority_score and decision status, during semantic categorization
            
            # Assigning decision status and priority_score to target objects 
            for obj in all_target_objects:
                if selected_track_id and obj.track_id == selected_track_id:
                    obj.decision_status = DecisionStatus.TARGET_SELECTED
                
                elif obj.track_id in unsafe_object_ids:
                    obj.decision_status = DecisionStatus.TARGET_AVOIDED

                else:
                    obj.decision_status = DecisionStatus.TARGET_IGNORED
                
                obj.priority_score = id_score_dict[obj.track_id]


            logger.debug(f"Categorizer -> assign_decision_status_for_target_objects(): ENDS, all_target_objects: {all_target_objects}")
            return all_target_objects


        except Exception as e:
            logger.error(f"Error occurred in Categorizer -> assign_decision_status_for_target_objects(), error: {e}")
            raise e