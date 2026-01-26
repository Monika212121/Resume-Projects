# Aim: Project camera detections (image frame) into a robot-centric 2D world frame.
# This is an APPROXIMATION but a correct and standard one for early robotics systems.

from src.common.visualization.entity import WorldObject
from src.fish.stage2_decision.entity import ActionIntent




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

    
    def project(self, action_intent: ActionIntent) -> WorldObject:
        """
        Project a bounding box into robot-centric coordinates.

        bbox format: (x1, y1, x2, y2) in ORIGINAL image space
        """   
        x1, y1, x2, y2 = action_intent.bbox

        # 1. BBox centre (image frame)
        cx = (x1 + x2) / 2.0
        #cy = (y1 + y2) / 2.0

        # 2. Normalize to camera frame.
        nx = (cx - self.img_w / 2) / (self.img_w / 2)
        #ny = 1.0 - (cy / self.img_h)

        # 3. Estimate distance proxy(bigger box -> closer object)
        bbox_height = max((y2-y1), 1)
        distance = self.forward_scale / bbox_height

        # 4. Robot-centric coordinates
        # Fish is at (0,0)
        world_x = nx * self.lateral_scale
        world_y = distance

        world_obj = WorldObject(
            track_id = action_intent.track_id,
            x = world_x,
            y = world_y,
            distance = distance,
            bbox = action_intent.bbox
        )

        return world_obj

