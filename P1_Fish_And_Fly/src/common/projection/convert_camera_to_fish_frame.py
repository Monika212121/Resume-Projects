# Aim: Geometric conversion of image dimension (bbox coordinates) into fish relative coordiantes
# This is PURELY CALCULATION and frame conversion [IMAGE -> FISH] FRAME

from src.common.logging import logger
from src.common.vision.entity import TrackedObject
from src.common.projection.entity import FishFrameObject

from src.fish.stage3_action.entity import Waypoint



class CameraToFishFrameProjector:
    """
    Converts image-space bounding boxes into fish robot-centric 2D coordinates.
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

    
    
    def project_image_to_fish_frame(self, tracked_obj: TrackedObject) -> FishFrameObject:
        """
        Project a bounding box into fish robot-centric coordinates.

        bbox format: (x1, y1, x2, y2) in ORIGINAL image space
        
        :param self: Belongs to the CameraToFishFrameProjector
        :param track_id: track_id of a tracked object.
        :type track_id: int
        :param bbox: Bounding box coordiantes of the tracked object
        :type bbox: Tuple[int, int, int, int]
        :return: Maintains transformed fish frame dimension(x, y, z), where 'x' signals left/right positioning and 'y' signals closeness w.r.t the Fish machine
        :rtype: FishFrameObject
        """
        try:
            logger.info(f"CameraToFishFrameProjector -> project_image_to_fish_frame(): STARTS, track_id: {tracked_obj.track_id}")

            x1, y1, x2, y2 = tracked_obj.bbox

            # 1. Calculate the BBox centre (image frame)
            cx = (x1 + x2) / 2.0
            #cy = (y1 + y2) / 2.0

            # 2. Normalize to camera frame
            nx = (cx - self.img_w / 2) / (self.img_w / 2)
            #ny = 1.0 - (cy / self.img_h)

            # 3. Estimate distance proxy[bigger box = closer object, smaller box = farther object]
            bbox_height = max((y2-y1), 1)
            relative_distance = self.forward_scale / bbox_height

            # 4. Robot-centric coordinates
            # Fish is at (0,0)
            x_rel_fish: float = nx * self.lateral_scale
            y_rel_fish: float = relative_distance
            z_rel_fish: float = 0.0                                 # will be populated later in mission_planner.py/tick/apply_depth_to_fish_frame_objects()

            fish_frame_object = FishFrameObject(
                track_id = tracked_obj.track_id,
                class_id = tracked_obj.class_id,
                class_name = tracked_obj.class_name,
                age = tracked_obj.age,
                state = tracked_obj.state,
                avg_confidence = tracked_obj.avg_confidence,
                entity_role = tracked_obj.entity_role,
                relative_position = Waypoint(x_rel_fish, y_rel_fish, z_rel_fish),
                relative_distance = relative_distance,
                original_bbox = tracked_obj.bbox
            )

            logger.info(f"CameraToFishFrameProjector -> project_image_to_fish_frame(): ENDS")
            return fish_frame_object
    

        except Exception as e:
            logger.info(f"Error occurred in CameraToFishFrameProjector -> project_image_to_fish_frame(), error: {e}")
            raise e
        

