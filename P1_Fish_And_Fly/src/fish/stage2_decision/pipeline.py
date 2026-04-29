# Aim: This is entry point of the Decision Pipeline

from typing import Dict

from src.common.logging import logger
from src.common.projection.entity import FishFrameObject


from src.fish.stage2_decision.filter import Filter
from src.fish.stage2_decision.reasoner import PriorityReasoner
from src.fish.stage2_decision.planner import ActionPlanner
from src.fish.stage2_decision.selector import SelectionLock
from src.fish.stage2_decision.categorizer import Categorizer
from src.fish.stage2_decision.entity import DecisionResult
from src.fish.stage2_decision.entity import DecisionConfig, CategorizedObjects



class DecisionPipeline:
    """
    Stage2: Decision Pipeline
    - Filter stable objects
    - Applies Hard rules + Soft reasoning
    - Ranks by priority
    - Selects and locks one object
    - Emits lifecycle command
    """
    def __init__(self, decision_config: DecisionConfig):
        self.filter = Filter(rules_filter_cfg = decision_config.rule_filter_cfg)
        self.reasoner = PriorityReasoner(reasoner_config = decision_config.reasoner_cfg)
        self.planner = ActionPlanner()
        self.selector = SelectionLock()
        self.categorizer = Categorizer()



    def run(self, fish_frame_objects: Dict[int, FishFrameObject]) -> DecisionResult:
        try:
            logger.debug(f"DecisionPipeline -> run(): STARTS, fish_frame_objects: {fish_frame_objects}")

            # Default decision result
            categorized_objects = CategorizedObjects(
                collection_targets= [],
                environment_entities= [],
                navigation_hazards= []
            )

            decision_result = DecisionResult(
                categorized_objects= categorized_objects,
                action_intent= None,
                selection_commands= [],
                selected_target= None
            )

            if len(fish_frame_objects) == 0:              
                logger.error(f"DecisionPipeline-> run(): No tracked active objects are received from the Vision module")
                return decision_result

            # Stability filtering
            stable_objects = self.filter.filter_by_stability_rules(fish_frame_objects)
            if len(stable_objects) == 0:
                logger.error(f"DecisionPipeline-> run(): No stable objects")
                return decision_result

            # Hard rules filtering
            eligible_objects = self.filter.filter_by_hard_rules(stable_objects)
            if len(eligible_objects) == 0:
                logger.error(f"DecisionPipeline-> run(): No eligible objects")
                return decision_result
            
            # NOTE: Assigning priority_score and decision status for environment and hazard objects during semantic categorization

            # Semantic categorization
            categorized_objects = self.categorizer.perform_semantic_categorization(eligible_objects= eligible_objects)
            if len(categorized_objects.collection_targets) == 0:
                logger.error(f"DecisionPipeline-> run(): No collection target objects")
                decision_result.categorized_objects = categorized_objects               # updating result with categorized objects, rest of them is None
                return decision_result 

            # Hazard-aware Priority score calculation
            ranked_target_objects = self.reasoner.calculate_priority_score(target_objects = categorized_objects.collection_targets, hazard_objects= categorized_objects.navigation_hazards)
            if len(ranked_target_objects) == 0:
                logger.error(f"DecisionPipeline-> run(): No priority-scored objects")
                return decision_result
            
            # Sorting the scored target objects w.r.t priority score in descending order
            ranked_target_objects.sort(key = lambda x: x.priority_score, reverse = True)                           
            logger.debug("DecisionPipeline -> run(): Ranked objects: " + ", ".join(f"(id={obj.track_id}, score={obj.priority_score:.2f})" for obj in ranked_target_objects))

            # Hazard safety filtering 
            safe_target_objects, unsafe_target_objects = self.categorizer.perform_target_categorization(ranked_target_objects = ranked_target_objects)

            # Target selection, selects and locks 1 target
            selection_commands, selected_target = self.selector.select_target(safe_target_objects= safe_target_objects)       # refer DECISION_NOTES.md(4)
            
            # Action planning
            action_intent = self.planner.build_action_intent(safe_ranked_objects = safe_target_objects, locked_target_id = selected_target.track_id if selected_target else None)

            # Assigning Decision Status and priority_score to collection targets only 
            updated_collection_targets = self.categorizer.assign_decision_status_for_target_objects(
                all_target_objects = categorized_objects.collection_targets, 
                safe_targets = safe_target_objects,
                unsafe_targets = unsafe_target_objects, 
                selected_track_id = selected_target.track_id if selected_target else None
            )

            # Updating categorized objects with the updated collection targets
            categorized_objects.collection_targets = updated_collection_targets

            decision_result = DecisionResult(
                categorized_objects= categorized_objects,
                action_intent= action_intent,
                selection_commands= selection_commands,
                selected_target= selected_target
            )

            logger.debug(f"DecisionPipeline -> run(): ENDS, decision_result: {decision_result}")
            return decision_result


        except Exception as e:
            logger.error(f"Error occurred in DecisionPipeline -> run(), error: {e}")
            raise e