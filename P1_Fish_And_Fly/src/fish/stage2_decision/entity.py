from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

from src.common.projection.entity import FishFrameObject



@dataclass
class RuleFilterConfig:
   min_age: int
   min_conf: float
   allowed_classes: List[str]


@dataclass
class PriorityReasonerConfig:
   hazard_radius: float


@dataclass
class DecisionConfig:
   rule_filter_cfg: RuleFilterConfig
   reasoner_cfg: PriorityReasonerConfig


class LifeCycleAction(Enum):
   SELECT = "select"
   DONE = "done"
   LOST = "lost"
   FAILED = "failed"
   UNATTEMPTED = "unattempted"
   AVOIDED = "avoid intentionally"


@dataclass
class LifeCycleCommand:
   action: LifeCycleAction
   track_id: int
   selection_count: int
   priority_score: float


@dataclass
class ActionIntent:
   """
   High-level decision output for Action layer
   """
   track_id: int
   class_name: str
   priority_score: float
   reason: str


@dataclass 
class CategorizedObjects:
   collection_targets: List[FishFrameObject]
   environment_entities: List[FishFrameObject]
   navigation_hazards: List[FishFrameObject]


@dataclass
class DecisionResult:
   categorized_objects: CategorizedObjects
   action_intent: Optional[ActionIntent]
   selection_commands: List[LifeCycleCommand]
   selected_target: Optional[FishFrameObject]