import math
import pybullet as p
from typing import Dict, Tuple

from src.common.logging import logger
from src.common.projection.entity import WorldObject

from src.fish.stage3_action.entity import Waypoint
from src.fish.stage5_simulation.object_factory import create_garbage
from src.fish.stage5_simulation.constants import WORKSPACE_BOUNDS



class ObjectManager():
    def __init__(self):
        self.objects_done: Dict[int, int] = {}                                # track_id -> body_id


    def clamp_garbage_position(self, pos: Waypoint):
        x = min(max(pos.x, WORKSPACE_BOUNDS["x_min"]), WORKSPACE_BOUNDS["x_max"])
        y = min(max(pos.y, WORKSPACE_BOUNDS["y_min"]), WORKSPACE_BOUNDS["y_max"])
        z = min(max(pos.z, WORKSPACE_BOUNDS["z_min"]), WORKSPACE_BOUNDS["z_max"])

        garbage_position = Waypoint(x, y, z)

        logger.info(f"ObjectManager -> clamp_garbage_position(), garbage_position: {garbage_position}")
        return garbage_position
        
    
    def spawn_garbage_objects(self, obj: WorldObject, fish_pos: Waypoint):

        logger.info(f"ObjectManager -> spawn_garbage_objects(): STARTS, obj: {obj}, self.objects_done: {self.objects_done}")

        # Objects already spawned, NEVER respawn or move 
        if obj.track_id in self.objects_done:
            logger.info(f"ObjectManager -> spawn_garbage_objects(), track_id: {obj.track_id} is already spawned")
            return
        
        #  --- PROJECT IN FRONT OF FISH (CORRECT AXIS) ---                                                  # refer SIMULATION_NOTES.md(3)

        # 1. Getting Fish machine position and distance of garbage, in front of it
        fx, fy, fz = fish_pos.x, fish_pos.y, fish_pos.z
        d = obj.distance

        # 2. Calculate the garbage object position, in front of Fish machine (fish_pse + distance projection)
        OFFSET = 0.5 * (obj.track_id % 10)

        gx = fx + OFFSET                                                                               # distance projection in x-axis
        gy = fy                                                                                             # distance projection in y-axis
        gz = fz                                                                                             # same depth as fish for now
        garbage_position = Waypoint(gx, gy, gz)

        logger.info(f"ObjectManager -> spawn_garbage_objects(): OFFSET= {OFFSET:.2f}, fish= ({fx:.2f}, {fy:.2f}, {fz:.2f}), garbage= ({gx:.2f}, {gy:.2f}, {gz:.2f})")

        # 3. Getting safe position, to spawn garbage objects within the defined workspace
        safe_garbage_pos = self.clamp_garbage_position(pos= garbage_position)
        logger.info(f"ObjectManager -> spawn_garbage_objects(): safe_garbage_pos: {safe_garbage_pos}")

        # 4. Create garbage objects at the safe(clamped) position
        body_id = create_garbage(safe_garbage_pos)

        # 5. Update the dict{track_id, body_id} with the garbage objects already spawned
        self.objects_done[obj.track_id] = body_id
        
        logger.info(f"ObjectManager -> spawn_garbage_objects(): ENDS")
        return


    def get_body(self, track_id: int):
        return self.objects_done.get(track_id)
