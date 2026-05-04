# Aim: Project camera detections (image frame) into a robot-centric 2D world frame.
# This is an APPROXIMATION.

from typing import List, Dict

from src.common.logging import logger
from src.common.vision.entity import TrackedObject
from src.common.projection.entity import FishFrameObject
from src.common.projection.convert_camera_to_fish_frame import CameraToFishFrameProjector



class FishFrameProjector:
    def __init__(self):                             # convert to config driven rendering
        self.FRAME_WIDTH = 640
        self.FRAME_HEIGHT = 480
        self.SRC_WIDTH = 1920
        self.SRC_HEIGHT = 1080   

        self.projector = CameraToFishFrameProjector(image_width= self.SRC_WIDTH, image_height= self.SRC_HEIGHT)



    def transform_to_fish_frame(self, active_objects: List[TrackedObject]) -> Dict[int, FishFrameObject]:
        """
        Transforms active_objects(image_frame) to fish_frame_objects(fish frame).

        Returns Dict{track_id, FishFrameObject} and Selected Fish Frame object
        
        :param self: Belongs to the FishFrameProjector
        :param active_objects: List of active tracked objects
        :type active_objects: List[TrackedGarbage]
        :param action_intent: Information of selected target object
        :type action_intent: Optional[ActionIntent]
        :return: Both Dict{track-id, World_objects} and selected world object
        :rtype: Tuple[Dict[int, FishFrameObject], FishFrameObject | None]
        """
        try:
            logger.debug(f"FishFrameProjector -> transform_to_fish_frame(): STARTS, active_objects: {active_objects}")

            fish_frame_objects : Dict[int, FishFrameObject] = {}

            # If there are no active tracked objects, returns empty Dict
            if len(active_objects) == 0:
                logger.error(f"FishFrameProjector -> transform_to_fish_frame(), No active objects are received from Vision module")
                return fish_frame_objects
            
            # Apply frame transformation(image_frame -> fish_frame) to all active tracked objects
            for obj in active_objects:

                # Project the image dimension(action_intent.bbox) -> fish frame dimension(x,y,z) relative to the Fish's position
                fish_frame_obj = self.projector.project_image_to_fish_frame(obj)

                # Creating dict{track_id, FishFrameObject}
                fish_frame_objects[obj.track_id] = fish_frame_obj


            logger.debug(f"FishFrameProjector -> transform_to_fish_frame(): ENDS, fish_frame_objects: {fish_frame_objects}")
            return fish_frame_objects


        except Exception as e:
            logger.error(f"Error occurred in FishFrameProjector -> transform_to_fish_frame(), error: {e}")
            raise e