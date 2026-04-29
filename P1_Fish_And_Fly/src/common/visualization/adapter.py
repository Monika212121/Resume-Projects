# Aim: Domain -> Visualization bridge (FINAL, CORRECT)

from typing import List, Optional, Dict, Tuple

from src.common.logging import logger
from src.common.entity.decision_types import DecisionStatus
from src.common.projection.entity import FishFrameObject
from src.common.visualization.colors import STATUS_COLORS
from src.common.visualization.entity import VisualizationEntity, VisualObject
from src.common.vision.entity import EntityRole, TrackedObject, TrackedState



class VisualizationAdapter:
    """
    Converts domain tracked objects into pixel-correct visualization objects.
    """

    def __init__(self, src_width: int, src_height: int, dsp_width: int, dsp_height: int):
        self.src_width = src_width
        self.src_height = src_height
        self.dst_width = dsp_width
        self.dst_height = dsp_height

        self.x_scale = dsp_width / src_width
        self.y_scale = dsp_height / src_height

        self.selection_counter: Dict[int, int] = {}         # [track_id, selection_count], Used to display whether an object's status is SELECTED | UNATTEMPTED

        self.collected_display_memory: Dict[int, int] = {}  # [track_id, frame_appeared], Used to disappear COLLECTED object's bounding boxes, after sometime
        self.lost_display_memory: Dict[int, int] = {}       # [track_id, frame_appeared], Used to disappear LOST object's bounding boxes, after sometime
        self.max_display_count = 5



    def build_visual_entity(self, all_objects: List[FishFrameObject], selected_track_id: Optional[int], collected_objects: List[TrackedObject], lost_objects: List[TrackedObject]) -> VisualizationEntity:

        visuals: List[VisualObject] = []

        # Updating selection counter's memory with the new selected object's id.
        if selected_track_id and (selected_track_id not in self.selection_counter):
            self.selection_counter[selected_track_id] = 1                                                    # refer VISION_NOTES.md()

        # Building visual bodies for active objects
        for obj in all_objects:

            # SCALE bbox from source frame -> resized frame
            x1, y1, x2, y2 = self.clamp_bounding_box(obj.original_bbox)
            if x2 <= x1 or y2 <= y1:
                continue

            # Determining state and color, from both the entiy role(assigned in Vision module) and decision status (assigned in Decision module)
            status = obj.state

            if obj.entity_role == EntityRole.COLLECTION_TARGET:
                if obj.decision_status == DecisionStatus.TARGET_AVOIDED:
                    status = TrackedState.AVOIDED

                # NOTE: # As selected object can get unattempted in same tick, to differentiate these 2 states, I am marking first unattempted state as selected
                elif obj.state == TrackedState.UNATTEMPTED:
                    if self.selection_counter[obj.track_id] == 1:
                        status = TrackedState.SELECTED                             
                        self.selection_counter[obj.track_id] += 1
            
            elif obj.entity_role == EntityRole.ENVIRONMENT_ENTITY:
                status = TrackedState.IGNORED

            elif obj.entity_role == EntityRole.NAVIGATION_HAZARD:
                status = TrackedState.AVOIDED

            # creating list of visual objects, for each active tracked object, to display in perception frame.
            visuals.append(
                VisualObject(
                    id= obj.track_id,
                    bbox= (x1, y1, x2, y2),
                    label= obj.class_name,
                    confidence= obj.avg_confidence,
                    status= status.name,
                    color= STATUS_COLORS.get(status.value, (255, 255, 255))
                )
            )

        # Building visual bodies for already collected objects
        for obj in collected_objects:
            if obj.track_id not in self.collected_display_memory:
                self.collected_display_memory[obj.track_id] = 1
            
            if self.collected_display_memory[obj.track_id] > self.max_display_count:
                continue

            x1, y1, x2, y2 = self.clamp_bounding_box(obj.bbox)
            if x2 <= x1 or y2 <= y1:
                continue

            visuals.append(
                VisualObject(
                    id= obj.track_id,
                    bbox= (x1, y1, x2, y2),
                    label= obj.class_name,
                    confidence= obj.avg_confidence,
                    status= obj.state.name,
                    color= STATUS_COLORS.get(obj.state.value, (255, 255, 255))
                )
            )

            self.collected_display_memory[obj.track_id] += 1


        # Building visual bodies for LOST objects
        for obj in lost_objects:
            if obj.track_id not in self.lost_display_memory:
                self.lost_display_memory[obj.track_id] = 1
            
            if self.lost_display_memory[obj.track_id] > self.max_display_count:
                continue

            x1, y1, x2, y2 = self.clamp_bounding_box(obj.bbox)
            if x2 <= x1 or y2 <= y1:
                continue

            visuals.append(
                VisualObject(
                    id= obj.track_id,
                    bbox= (x1, y1, x2, y2),
                    label= obj.class_name,
                    confidence= obj.avg_confidence,
                    status= obj.state.name,
                    color= STATUS_COLORS.get(obj.state.value, (255, 255, 255))
                )
            )

            self.lost_display_memory[obj.track_id] += 1


        # Creating final visual entity
        visual_entities =  VisualizationEntity(
            objects= visuals,
            selected_id= selected_track_id,
            action_label= None,
            grasp_threshold= 0.08
        )

        logger.debug(f"visual objects: {visuals}")
        return visual_entities



    def clamp_bounding_box(self, bbox: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        try:
            x1, y1, x2, y2 = bbox

            x1 = int(x1 * self.x_scale)
            x2 = int(x2 * self.x_scale)
            y1 = int(y1 * self.y_scale)
            y2 = int(y2 * self.y_scale)

            # Clamp original bounding box
            x1 = max(0, min(x1, self.dst_width - 1))
            x2 = max(0, min(x2, self.dst_width - 1))
            y1 = max(0, min(y1, self.dst_height - 1))
            y2 = max(0, min(y2, self.dst_height - 1))

            return x1, y1, x2, y2


        except Exception as e:
            logger.error(f"Error occured in VisualizationAdapter -> clamp_bounding_box(), error: {e}")
            raise e