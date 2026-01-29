import cv2
import numpy as np
from typing import List, Optional

from src.common.logging import logger
from src.common.visualization.entity import VisualizationEntity
from src.common.visualization.adapter import VisualizationAdapter
from src.common.visualization.video_overlay import GarbageVideoOverlay
from src.common.projection.entity import WorldObject
from src.common.projection.convert_camera_to_world import CameraToWorldProjector

from src.fish.stage1_vision.entity import TrackedGarbage



class Visualizer:
    def __init__(self):
        self.FRAME_WIDTH = 640
        self.FRAME_HEIGHT = 480
        self.SRC_WIDTH = 1920
        self.SRC_HEIGHT = 1080   

        self.overlay_obj = GarbageVideoOverlay()
        self.viz_adapter = VisualizationAdapter(src_width= self.SRC_WIDTH, src_height= self.SRC_HEIGHT, dst_width= self.FRAME_WIDTH, dst_height= self.FRAME_HEIGHT)
        self.viz_state: VisualizationEntity
        self.projector = CameraToWorldProjector(image_width= self.SRC_WIDTH, image_height= self.SRC_HEIGHT)



    def visualize_objects(self, frame: np.ndarray, active_objects: List[TrackedGarbage], selected_world_obj: Optional[WorldObject]) -> None:
        """
        Visualize tracked objects, selection, grasp threshold and world projection.
        """
        logger.info("Visualizer -> visualize_objects(): STARTS")

        # 1. Resize original frame to desired dimension
        frame = cv2.resize(frame, (self.FRAME_WIDTH, self.FRAME_HEIGHT))
        display_frame = frame.copy()

        # Return the normal resized frame if there is no active/selected object
        if len(active_objects)==0 or selected_world_obj is None:
            logger.info("Visualizer -> visualize_objects(): ENDS, There are no active objects or selected world object")
            cv2.imshow("My Fish machine underwater garbage tracker", display_frame)
            return

        # 2. Build visualization entities (ALL objects)
        viz_entity = self.viz_adapter.build(active_objects= active_objects, selected_track_id = selected_world_obj.track_id)

        # 3. Resize Bounding box of the selected object.
        x1, y1, x2, y2 = selected_world_obj.bbox

        scale_x = self.FRAME_WIDTH / self.SRC_WIDTH
        scale_y = self.FRAME_HEIGHT / self.SRC_HEIGHT

        resized_bbox = (int(x1 * scale_x), int(y1 * scale_y), int(x2 * scale_x), int(y2 * scale_y))

        # 4. Draw everything (pure visualization)
        display_frame = self.overlay_obj.draw(frame= display_frame, viz_entity= viz_entity, resized_bbox= resized_bbox, sel_world_object= selected_world_obj)

        # 5. Show frame
        cv2.imshow("My Fish machine underwater garbage tracker", display_frame)

        logger.info("Visualizer -> visualize_objects(): ENDS")
        return
