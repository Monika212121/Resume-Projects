# Aim: To visualize the tracked garbages in water body.
# CHANGE: This file now ACTUALLY DRAWS bounding boxes and text.

import cv2                                 
import numpy as np
from typing import Optional, Tuple

from src.common.visualization.entity import VisualizationEntity, VisualObject
from src.common.projection.entity import WorldObject



class GarbageVideoOverlay:
    """
    Dumb renderer.
    - NO logic
    - NO decisions
    - ONLY draws what VisualizationState tells it to draw
    """

    def __init__(self):
        self.threshold_distance = 0.08


    def draw(self, frame: np.ndarray, viz_entity: VisualizationEntity, resized_bbox: Optional[Tuple[int, int, int, int]], sel_world_object: WorldObject) -> np.ndarray:
        """
        Draw all visual objects and selection highlight.
        """

        # 1. Draw all objects (WHITE)
        for obj in viz_entity.objects:
            frame = self._draw_box(frame, obj)

        # 2. Draw selected object, highlight (ORANGE)
        if viz_entity.selected_id:
            frame = self._draw_selected(frame, viz_entity)

        # 3. Draw grasp threshold line (BLUE)
        frame = self._draw_grasp_threshold(frame = frame, threshold_distance = self.threshold_distance)

        # 4. Draw world coords(world_x, world_y) (YELLOW)
        if resized_bbox and sel_world_object:
            frame = self._draw_world_coords(frame, resized_bbox, sel_world_object)

        return frame

    # ============================ INTERNAL DRAW HELPERS ============================

    def _draw_box(self, frame: np.ndarray, obj: VisualObject) -> np.ndarray:
        """
        Draw bounding box + label for one object
        """

        # CHANGE: Expect bbox in (x1, y1, x2, y2) format
        x1, y1, x2, y2 = obj.bbox

        # SAFETY CHECK (helps catch silent bugs)
        if x2 <= x1 or y2 <= y1:
            return frame

        color = obj.color

        # Bounding box
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)

        # Label text
        label = f" {obj.id} | {obj.label} | {obj.confidence:.2f} | {obj.status}"

        cv2.putText(frame, label, (int(x1), max(int(y1) - 7, 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
        return frame


    def _draw_selected(self, frame: np.ndarray, viz_state: VisualizationEntity):
        """
        Draw thicker highlight for selected object
        """

        for obj in viz_state.objects:
            if obj.id == viz_state.selected_id:
                x1, y1, x2, y2 = obj.bbox

                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 255),  3)         # Yellow highlight
                break

        return frame


    def _draw_grasp_threshold(self, frame: np.ndarray, threshold_distance: float) -> np.ndarray:
        """
        Draws a horizontal line indicating grasp trigger zone.
        This is an APPROXIMATION for visual debugging.
        """

        h, w, _ = frame.shape

        # Map distance threshold to image Y (heuristic)
        # Smaller distance => lower in image
        y = int(h * (1.0 - min(threshold_distance * 8.0, 1.0)))

        cv2.line(frame, (0, y), (w, y), (255, 0, 0), 2)                                                 # BLUE line

        cv2.putText(frame, "GRASP THRESHOLD", (10, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        return frame


    def _draw_world_coords(self, frame: np.ndarray, resized_bbox: Tuple[int, int, int, int], world_obj: WorldObject) -> np.ndarray:
           
        # NOTE: These coordinates are already resized w.r.t. resized frame.
        x1, y1, x2, y2 = resized_bbox

        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        text = f"x={world_obj.x:.2f}, y={world_obj.y:.3f}"

        cv2.putText(frame, text, (cx, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)                                 # YELLOW
        return frame

