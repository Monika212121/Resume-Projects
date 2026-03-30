# Aim: To visualize the tracked garbages in water body.
# CHANGE: This file now ACTUALLY DRAWS bounding boxes and text.

import cv2                                 
import numpy as np
from typing import Optional, Tuple, List

from src.fish.stage1_vision.entity import TrackedGarbage
from src.common.projection.entity import FishFrameObject
from src.common.visualization.entity import VisualizationEntity, VisualObject



class GarbageVideoOverlay:
    """
    Dumb renderer.
    - NO logic
    - NO decisions
    - ONLY draws what VisualizationState tells it to draw
    """

    def __init__(self):
        self.threshold_distance = 0.08


    def draw(self, frame: np.ndarray, viz_entity: VisualizationEntity, resized_bbox: Optional[Tuple[int, int, int, int]], selected_object: Optional[FishFrameObject]) -> np.ndarray:
        """
        Draw all visual objects and selection highlight.
        """

        # Draw all active objects
        for obj in viz_entity.objects:
            frame = self._draw_box(frame, obj)

        # Draw coords(rel_x, rel_y) w.r.t fish machine (YELLOW)
        if selected_object and resized_bbox:
            frame = self._draw_fish_frame_coords(frame, resized_bbox, selected_object)

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

        # Bounding box
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), obj.color, 2)

        # Label text
        label = f" {obj.id} | {obj.label} | {obj.confidence:.2f} | {obj.status}"

        cv2.putText(frame, label, (int(x1), max(int(y1) - 7, 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, obj.color, 1, cv2.LINE_AA)
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


    def _draw_fish_frame_coords(self, frame: np.ndarray, resized_bbox: Tuple[int, int, int, int], world_obj: FishFrameObject) -> np.ndarray:
           
        # NOTE: These coordinates are already resized w.r.t. resized frame.
        x1, y1, x2, y2 = resized_bbox

        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        text = f"x={world_obj.relative_position.x:.2f}, y={world_obj.relative_position.y:.3f}"

        cv2.putText(frame, text, (cx, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)                                 # YELLOW
        return frame

