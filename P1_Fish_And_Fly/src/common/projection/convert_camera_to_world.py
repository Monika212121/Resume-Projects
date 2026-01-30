# Aim: Geometric conversion of image dimension (bbox coordinates) into world coordiantes (relative postiion w.r.t Fish machine)
# This is PURELY CALCULATION and frame conversion.

from typing import Tuple
from src.common.logging import logger
from src.common.projection.entity import WorldObject
from src.fish.stage1_vision.entity import TrackedGarbage
from src.fish.stage3_action.entity import Waypoint



class CameraToWorldProjector:
    """
    Converts image-space bounding boxes into robot-centric 2D world coordinates.
    """
    def __init__(self, image_width: int, image_height: int, lateral_scale: float= 1.0, forward_scale: float = 2.0):
        """
        Args:
            image_width: width of the ORIGINAL camera frame
            image_height: height of the ORIGINAL camera frame
            lateral_scale: controls left/right spread
            forward_scale: controls depth sensitivity
        """
        self.img_w = image_width
        self.img_h = image_height
        self.lateral_scale = lateral_scale
        self.forward_scale = forward_scale

    
    
    def project_image_to_world_frame(self, tracked_obj: TrackedGarbage) -> WorldObject:
        """
        Project a bounding box into robot-centric coordinates.

        bbox format: (x1, y1, x2, y2) in ORIGINAL image space
        
        :param self: Belongs to the CameraToWorldProjector
        :param track_id: track_id of a tracked object.
        :type track_id: int
        :param bbox: Bounding box coordiantes of the tracked object
        :type bbox: Tuple[int, int, int, int]
        :return: Maintains transformed world frame dimension(x, y, z), where 'x' signals left/right positioning and 'y' signals cloneness w.r.t the Fish machine
        :rtype: WorldObject
        """
        try:
            logger.info(f"CameraToWorldProjector -> project_image_to_world_frame(): STARTS, track_id: {tracked_obj.track_id}")

            x1, y1, x2, y2 = tracked_obj.bbox

            # 1. Calculate the BBox centre (image frame)
            cx = (x1 + x2) / 2.0
            #cy = (y1 + y2) / 2.0

            # 2. Normalize to camera frame
            nx = (cx - self.img_w / 2) / (self.img_w / 2)
            #ny = 1.0 - (cy / self.img_h)

            # 3. Estimate distance proxy(bigger box -> closer object)
            bbox_height = max((y2-y1), 1)
            distance = self.forward_scale / bbox_height

            # 4. Robot-centric coordinates
            # Fish is at (0,0)
            world_x: float = nx * self.lateral_scale
            world_y: float = distance
            world_z: float = 0.0

            world_object = WorldObject(
                track_id = tracked_obj.track_id,
                class_id = tracked_obj.class_id,
                position= Waypoint(world_x, world_y, world_z),
                distance = distance,
                bbox = tracked_obj.bbox 
            )

            logger.info(f"CameraToWorldProjector -> project_image_to_world_frame(): ENDS")
            return world_object
    

        except Exception as e:
            logger.info(f"Error occurred in CameraToWorldProjector -> project_image_to_world_frame(), error: {e}")
            raise e
        

