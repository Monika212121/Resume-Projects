# Aim: Domain -> Visualization bridge (FINAL, CORRECT)

from typing import List, Optional

from src.common.visualization.colors import STATUS_COLORS
from src.common.visualization.entity import VisualizationEntity, VisualObject

from src.fish.stage1_vision.entity import TrackedGarbage
from src.fish.stage2_decision.entity import ActionIntent



class VisualizationAdapter:
    """
    Converts domain tracked objects into pixel-correct visualization objects.
    """

    def __init__(
        self,
        src_width: int,
        src_height: int,
        dst_width: int,
        dst_height: int
    ):
        self.src_width = src_width
        self.src_height = src_height
        self.dst_width = dst_width
        self.dst_height = dst_height

        self.x_scale = dst_width / src_width
        self.y_scale = dst_height / src_height



    def build(
        self,
        tracked_objects: List[TrackedGarbage],
        action_intent: Optional[ActionIntent]
    ) -> VisualizationEntity:

        visuals: List[VisualObject] = []

        for obj in tracked_objects:
            x1, y1, x2, y2 = obj.bbox

            # SCALE bbox from source frame -> resized frame
            x1 = int(x1 * self.x_scale)
            x2 = int(x2 * self.x_scale)
            y1 = int(y1 * self.y_scale)
            y2 = int(y2 * self.y_scale)

            # Clamp
            x1 = max(0, min(x1, self.dst_width - 1))
            x2 = max(0, min(x2, self.dst_width - 1))
            y1 = max(0, min(y1, self.dst_height - 1))
            y2 = max(0, min(y2, self.dst_height - 1))

            if x2 <= x1 or y2 <= y1:
                continue

            # creating list of active tracked objects.
            visuals.append(
                VisualObject(
                    id=obj.track_id,
                    bbox=(x1, y1, x2, y2),
                    label=obj.class_name,
                    confidence=obj.avg_confidence,
                    status=obj.state.name,
                    color=STATUS_COLORS.get(obj.state.value, (255, 255, 255))
                )
            )

        visual_entities =  VisualizationEntity(
            objects=visuals,
            selected_id=action_intent.track_id if action_intent else None,
            action_label=None,
            grasp_threshold= 0.08
        )

        return visual_entities
