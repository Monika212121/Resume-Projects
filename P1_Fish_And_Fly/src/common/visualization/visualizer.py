import cv2
import numpy as np
from typing import List, Optional, Tuple

from src.common.logging import logger
from src.common.visualization.video_overlay import GarbageVideoOverlay
from src.common.visualization.adapter import VisualizationAdapter
from src.common.visualization.entity import VisualizationEntity, WorldObject
from src.common.visualization.world_projection import CameraToWorldProjector

from src.fish.stage1_vision.entity import TrackedGarbage
from src.fish.stage2_decision.entity import ActionIntent



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



    def visualize_objects(self, frame: np.ndarray, active_objects: List[TrackedGarbage], action_intent: Optional[ActionIntent]) -> Optional[WorldObject]:
        """
        Visualize tracked objects, selection, grasp threshold and world projection.
        Returns projected WorldObject if available.
        """
        logger.info("Visualizer -> visualize_objects(): STARTS")
        resized_bbox: Optional[Tuple[int,int,int,int]] = None

        # 1. Resize frame
        frame = cv2.resize(frame, (self.FRAME_WIDTH, self.FRAME_HEIGHT))
        display_frame = frame.copy()

        # 2. Build visualization entities (ALL objects)
        viz_entity = self.viz_adapter.build(tracked_objects= active_objects, action_intent=action_intent)

        # 3. Project world coordinates ONLY if action exists
        world_object: Optional[WorldObject] = None
        if action_intent:
            world_object = self.projector.project(action_intent)

            logger.info(
                f"[PROJECTION] id={action_intent.track_id} "
                f"bbox={action_intent.bbox} "
                f"world_x={world_object.x:.2f} "
                f"world_y={world_object.y:.2f} "
                f"dist={world_object.distance:.4f}"
            )

            # 4. Resize Bounding box of selected object.
            x1, y1, x2, y2 = action_intent.bbox
            
            scale_x = self.FRAME_WIDTH / self.SRC_WIDTH
            scale_y = self.FRAME_HEIGHT / self.SRC_HEIGHT

            resized_bbox = (int(x1 * scale_x), int(y1 * scale_y), int(x2 * scale_x), int(y2 * scale_y))

        # 5. Draw everything (pure visualization)
        display_frame = self.overlay_obj.draw(frame= display_frame, viz_entity= viz_entity, resized_bbox= resized_bbox, world_object= world_object)

        # 5. Show frame
        cv2.imshow("My Fish machine underwater garbage tracker", display_frame)

        logger.info("Visualizer -> visualize_objects(): ENDS")
        return world_object
