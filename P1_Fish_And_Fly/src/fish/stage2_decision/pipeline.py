from typing import List, Optional, Tuple
from src.common.logging import logger

from src.fish.stage2_decision.filter import StableObjectFilter
from src.fish.stage2_decision.rules import RuleFilter
from src.fish.stage2_decision.reasoner import PriorityReasoner
from src.fish.stage2_decision.planner import ActionPlanner
from src.fish.stage2_decision.selector import SelectionLock

from src.fish.stage1_vision.entity import TrackedGarbage
from src.fish.stage2_decision.entity import ActionIntent
from src.fish.stage2_decision.command import LifeCycleCommand


class DecisionPipeline:
    """
    Stage2: Decision Pipeline
    - Filter stable objects
    - Applies Hard rules + Soft reasoning
    - Ranks by priority
    - Selects and locks one object
    - Emits lifecycle command
    """

    def __init__(self, decision_cfg):
        self.filter = StableObjectFilter()
        self.rule_filter = RuleFilter(decision_cfg.rules)
        self.reasoner = PriorityReasoner(decision_cfg.reasoner)
        self.planner = ActionPlanner(decision_cfg.planner)
        self.selector = SelectionLock()


    def run(self, tracked_agg_objects: List[TrackedGarbage]) -> Tuple[Optional[ActionIntent], Optional[LifeCycleCommand]]:
        logger.info(f"DecisionPipeline -> run(): STARTS, tracked objects: {len(tracked_agg_objects)}")

        # Step1: Filtering out only STABLE objects.
        stable_tracked_objects = self.filter.filter_detections(tracked_agg_objects)

        # Step2: Applying Hard Gate / Rule-based Filtering
        valid_objects = self.rule_filter.hard_rules_apply(stable_tracked_objects)
        if not valid_objects:
            logger.info(f"DecisionPipeline-> run(): No eligible objects")
            return None, None

        # Step3: Applying Soft Intelligence / Reasoning
        # returns List[(TrackedGarbage, priority_score)]
        ranked_objects = self.reasoner.calculate_priority_score(valid_objects)             
        if not ranked_objects:
            logger.info(f"DecisionPipeline-> run(): No priority-scored objects")
            return None, None
        
        # Step4: Sorting the (tracked object,priority_score) dictionary w.r.t priority score in descending order
        ranked_objects.sort(key = lambda x: x[1], reverse = True)                           
        logger.info(
            "DecisionPipeline -> Ranked objects: " + ", ".join(
                f"(id={obj.track_id}, score={score:.2f})" for obj, score in ranked_objects if obj is not None
            )
        )

        # Step5: Selects and locks 1 target, generating a lifecycle command
        select_command = self.selector.select_target(ranked_objects)
        locked_id = self.selector.get_locked_target()

        # Step6: Decision Making / Action Planning
        action_intent = self.planner.build_action_intents(ranked_objects, locked_id)

        logger.info(f"DecisionPipeline -> run(): ENDS, action intent: {action_intent}, select_command: {select_command}")
        return action_intent, select_command
