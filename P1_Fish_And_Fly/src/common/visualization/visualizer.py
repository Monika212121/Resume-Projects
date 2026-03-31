import cv2
import numpy as np
from typing import List, Optional

from src.common.logging import logger
from src.common.io.entity import IOConfig
from src.common.io.video_writer import VideoWriterManager 
from src.common.projection.entity import FishFrameObject
from src.common.visualization.entity import VisualizationEntity
from src.common.visualization.adapter import VisualizationAdapter
from src.common.visualization.video_overlay import GarbageVideoOverlay
from src.common.projection.convert_camera_to_fish_frame import CameraToFishFrameProjector
from src.common.vision.entity import TrackedObject



class Visualizer:
    def __init__(self, io_config: IOConfig):
        self.io_config = io_config
        self.screen_dim = self.io_config.screen_dimensions

        self.SOURCE_WIDTH = self.screen_dim.source_width
        self.SOURCE_HEIGHT = self.screen_dim.source_height
        self.DISPLAY_FRAME_WIDTH = self.screen_dim.display_width
        self.DISPLAY_FRAME_HEIGHT = self.screen_dim.display_height

        self.viz_state: VisualizationEntity

        self.overlay_obj = GarbageVideoOverlay()
        self.viz_adapter = VisualizationAdapter(src_width= self.SOURCE_WIDTH, src_height= self.SOURCE_HEIGHT, dsp_width= self.DISPLAY_FRAME_WIDTH, dsp_height= self.DISPLAY_FRAME_HEIGHT)
        self.projector = CameraToFishFrameProjector(image_width= self.SOURCE_WIDTH, image_height= self.SOURCE_HEIGHT)

        self.video_writer = VideoWriterManager(fps=15) if self.io_config.record_output else None



    def visualize_objects(
            self, 
            frame: np.ndarray,
            all_objects: List[FishFrameObject],
            selected_obj: Optional[FishFrameObject], 
            collected_objects: List[TrackedObject], 
            lost_objects: List[TrackedObject]
        ) -> Optional[VideoWriterManager]:
        """
        Visualize tracked objects, selection, grasp threshold and world projection.
        """
        try:
            logger.info(f"Visualizer -> visualize_objects(): STARTS, all_objects: {all_objects}, selected_obj: {selected_obj}")

            # 1. Resize original frame to desired dimension
            frame = cv2.resize(frame, (self.DISPLAY_FRAME_WIDTH, self.DISPLAY_FRAME_HEIGHT))
            display_frame = frame.copy()
            
            # Return the normal resized frame if there is no active object
            if len(all_objects) == 0 and len(collected_objects) == 0 and len(lost_objects) == 0:
                logger.info("Visualizer -> visualize_objects(): ENDS, There is no tracked object in current frame")
                cv2.imshow("Fish Module: Real-Time Aquatic Perception", display_frame)

                # Record perception visualization video
                if self.video_writer:
                    self.video_writer.write(display_frame)

                return self.video_writer

            # 2. Build visualization entities (ALL objects)
            selected_track_id = selected_obj.track_id if selected_obj else None
            viz_entity = self.viz_adapter.build_visual_entity(
                all_objects= all_objects, 
                selected_track_id= selected_track_id, 
                collected_objects= collected_objects,
                lost_objects= lost_objects
            )

            # 3. Resize Bounding box of the selected object.
            resized_bbox = None
            if selected_obj:
                x1, y1, x2, y2 = selected_obj.original_bbox

                scale_x = self.DISPLAY_FRAME_WIDTH / self.SOURCE_WIDTH
                scale_y = self.DISPLAY_FRAME_HEIGHT / self.SOURCE_HEIGHT

                resized_bbox = (int(x1 * scale_x), int(y1 * scale_y), int(x2 * scale_x), int(y2 * scale_y))

            # 4. Draw everything (pure visualization)
            display_frame = self.overlay_obj.draw(frame= display_frame, viz_entity= viz_entity, resized_bbox= resized_bbox, selected_object= selected_obj)

            # 5. Show frame
            cv2.imshow("Fish Module: Real-Time Aquatic Perception", display_frame)

            # Record perception visulization video
            if self.video_writer:
                self.video_writer.write(display_frame)

            logger.info(f"Visualizer -> visualize_objects(): ENDS")
            return self.video_writer
        

        except Exception as e:
            logger.info(f"Error occurred in Visualizer -> visualize_objects(), error: {e}")
            raise e
