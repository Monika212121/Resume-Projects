# Aim: Project camera detections (image frame) into a robot-centric 2D world frame.
# This is an APPROXIMATION.

from typing import List, Dict, Optional, Tuple

from src.common.logging import logger
from src.common.projection.entity import FishFrameObject
from src.common.projection.convert_camera_to_fish_frame import CameraToFishFrameProjector

from src.fish.stage1_vision.entity import TrackedGarbage
from src.fish.stage2_decision.entity import ActionIntent



class FishFrameProjector:
    def __init__(self):
        self.FRAME_WIDTH = 640
        self.FRAME_HEIGHT = 480
        self.SRC_WIDTH = 1920
        self.SRC_HEIGHT = 1080   

        self.projector = CameraToFishFrameProjector(image_width= self.SRC_WIDTH, image_height= self.SRC_HEIGHT)



    def transform_to_fish_frame(self, active_objects: List[TrackedGarbage], action_intent: Optional[ActionIntent]) -> Tuple[Dict[int, FishFrameObject], Optional[FishFrameObject]]:
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
            logger.info(f"FishFrameProjector -> transform_to_fish_frame(): STARTS")
            fish_frame_objects : Dict[int, FishFrameObject] = {}
            selected_fish_frame_object: Optional[FishFrameObject] = None

            # If there are no active tracked objects, returns empty Dict and None selected world object 
            if len(active_objects) == 0:
                logger.info(f"FishFrameProjector -> transform_to_fish_frame(), No active objects are received from Vision module")
                return fish_frame_objects, selected_fish_frame_object
            
            # 1. If a valid action intent is present, then only select world object can be retrieved from world_objects dict.
            sel_object_id: Optional[int] = None
            if action_intent and action_intent.track_id:
                sel_object_id = action_intent.track_id
            
            # 2. Transforming all active objects -> fish frame objects.
            for obj in active_objects:

                # Project the image dimension(action_intent.bbox) -> fish frame dimension(x,y,z) relative to the Fish's position
                fish_frame_obj = self.projector.project_image_to_fish_frame(obj)

                # Creating dict{track_id, FishFrameObject}
                fish_frame_objects[obj.track_id] = fish_frame_obj

                # Saving the selected object, in fish frame
                if sel_object_id and (obj.track_id == sel_object_id):
                    selected_fish_frame_object = fish_frame_obj


            if len(fish_frame_objects) > 0 and selected_fish_frame_object is None:
                logger.info(f"FishFrameProjector -> transform_to_fish_frame(): There is no stable/valid tracked object")

            logger.info(f"FishFrameProjector -> transform_to_fish_frame(): ENDS, world_objects: {fish_frame_objects}, selected_world_object: {selected_fish_frame_object}")
            return (fish_frame_objects, selected_fish_frame_object)


        except Exception as e:
            logger.info(f"Error occurred in FishFrameProjector -> transform_to_fish_frame(), error: {e}")
            raise e