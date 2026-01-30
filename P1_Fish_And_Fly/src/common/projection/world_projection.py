# Aim: Project camera detections (image frame) into a robot-centric 2D world frame.
# This is an APPROXIMATION.

from typing import List, Dict, Optional, Tuple

from src.common.logging import logger
from src.common.projection.entity import WorldObject
from src.common.projection.convert_camera_to_world import CameraToWorldProjector

from src.fish.stage1_vision.entity import TrackedGarbage
from src.fish.stage2_decision.entity import ActionIntent



class WorldProjector:
    def __init__(self):
        self.FRAME_WIDTH = 640
        self.FRAME_HEIGHT = 480
        self.SRC_WIDTH = 1920
        self.SRC_HEIGHT = 1080   

        self.projector = CameraToWorldProjector(image_width= self.SRC_WIDTH, image_height= self.SRC_HEIGHT)



    def transform_to_world_frame(self, active_objects: List[TrackedGarbage], action_intent: Optional[ActionIntent]) -> Tuple[Dict[int, WorldObject], Optional[WorldObject]]:
        """
        Transforms active_objects(image_frame) to world_objects(world frame).

        Returns Dict{track_id, WorldObject} and Selected World object
        
        :param self: Belongs to the WorldProjector
        :param active_objects: List of active tracked objects
        :type active_objects: List[TrackedGarbage]
        :param action_intent: Information of selected target object
        :type action_intent: Optional[ActionIntent]
        :return: Both Dict{track-id, World_objects} and selected world object
        :rtype: Tuple[Dict[int, WorldObject], WorldObject | None]
        """
        try:
            logger.info(f"WorldProjector -> transform_to_world_frame(): STARTS")
            world_objects : Dict[int, WorldObject] = {}
            selected_world_object: Optional[WorldObject] = None

            # If there are no active tracked objects, returns empty Dict and None selected world object 
            if len(active_objects) == 0:
                logger.info(f"WorldProjector -> transform_to_world_frame(), No active objects are received from Vision module")
                return world_objects, selected_world_object
            
            # 1. If a valid action intent is present, then only select world object can be retrieved from world_objects dict.
            sel_object_id: Optional[int] = None
            if action_intent and action_intent.track_id:
                sel_object_id = action_intent.track_id
            
            # 2. Transforming all active objects -> world objects.
            for obj in active_objects:

                # Project the image dimension(action_intent.bbox) -> world dimension(x,y,z) relative to the Fish's position
                world_obj = self.projector.project_image_to_world_frame(obj)

                # Creating dict{track_id, WorldObject}
                world_objects[obj.track_id] = world_obj

                # Retrieve world object for the selected object
                if sel_object_id and (obj.track_id == sel_object_id):
                    selected_world_object = world_obj


            if len(world_objects) > 0 and selected_world_object is None:
                logger.info(f"WorldProjector -> transform_to_world_frame(): There is no stable/valid tracked object")

            logger.info(f"WorldProjector -> transform_to_world_frame(): ENDS, world_objects: {world_objects}, selected_world_object: {selected_world_object}")
            return (world_objects, selected_world_object)


        except Exception as e:
            logger.info(f"Error occurred in WorldProjector -> transform_to_world_frame(), error: {e}")
            raise e