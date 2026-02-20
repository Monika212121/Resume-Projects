import pybullet as p
from typing import Dict, Tuple, Optional

from src.common.logging import logger
from src.common.projection.entity import FishFrameObject

from src.fish.stage3_action.entity import Waypoint, ActionStatus
from src.fish.stage5_simulation.entity import WorldObject
from src.fish.stage5_simulation.clamper import clamp_position
from src.fish.stage5_simulation.object_factory import create_garbage_body
from src.fish.stage5_simulation.constants import SIM_GARBAGE_SPAWN_OFFSET_X



class ObjectManager():
    def __init__(self):
        self.object_bodyID: Dict[int, int] = {}                                                             # Dict{track_id, pybullet_body_id}
        self.objects_spawned: Dict[int, WorldObject] = {}                                                   # Dict{track_id, world_object}
        


    def exists(self, object_id: int) -> bool:
        try:
            object_exists = object_id in self.object_bodyID
            return object_exists
        
        except Exception as e:
            logger.info(f"Error occurred in ObjectManager -> exists(), error: {e}")
            raise e
        


    def get_body_id(self, track_id: int) -> Optional[int]:
        try:
            body_id = self.object_bodyID.get(track_id)
            return body_id

        except Exception as e:
            logger.info(f"Error occurred in ObjectManager -> get_body_id(), error: {e}")
            raise e



    def create_sim_world_object_from_fish_frame(self, fish_frame_obj: FishFrameObject, fish_pos: Waypoint, fish_direction: int) -> WorldObject:
        try:
            logger.info(f"ObjectManager -> create_sim_world_object_from_fish_frame(): STARTS, fish direction: {fish_direction}")

            # Simulation-only: applies forward offset and workspace clamping

            # Applies forward OFFSET, only in x_direction
            gx = fish_pos.x + (SIM_GARBAGE_SPAWN_OFFSET_X * fish_direction)                                 # refer SIMULATION_NOTES.md(3)
            garbage_world_position = Waypoint(gx, fish_pos.y, fish_pos.z)

            # Clamp the new position, to give a safe position for garbage spawning
            safe_garbage_position = clamp_position(position= garbage_world_position)

            # Create world object of the garbage, recieved in fish_frame format
            # This world object will be only used in Simulation
            garbage_world_object = WorldObject(
                object_id= fish_frame_obj.track_id,
                class_id= fish_frame_obj.class_id,
                class_name= fish_frame_obj.class_name,
                world_position= safe_garbage_position
            )

            logger.info(f"ObjectManager -> create_sim_world_object_from_fish_frame(): fish_pos: {fish_pos}, garbage_pos: {garbage_world_position}")

            logger.info(f"ObjectManager -> create_sim_world_object_from_fish_frame(): ENDS, world_obj pos: {garbage_world_object.world_position}")
            return garbage_world_object
        
        
        except Exception as e:
            logger.info(f"Error occurred in ObjectManager -> create_sim_world_object_from_fish_frame(), error: {e}")
            raise e      
        


    def spawn_garbage(self, world_obj: WorldObject) -> None:
        try:
            logger.info(f"ObjectManager -> spawn_garbage(): STARTS")
                        
            # Spawn a new garbage
            pos = world_obj.world_position
            spawn_pos: Tuple[float, float, float] = (pos.x, pos.y, pos.z)                                   # Spawn function takes position in tuple(float)

            garbage_body_id = create_garbage_body(position= spawn_pos)

            # Updating the object spawned memory
            self.objects_spawned[world_obj.object_id] = world_obj
            self.object_bodyID[world_obj.object_id] = garbage_body_id

            logger.info(f"ObjectManager -> spawn_garbage(): ENDS, created garbage_body_id: {garbage_body_id}")
            return
        

        except Exception as e:
            logger.info(f"Error occurred in ObjectManager -> spawn_garbage(), error: {e}")
            raise e
            
        

    def mark_collected(self, track_id: int):
        try:
            logger.info(f"ObjectManager -> mark_collected(): STARTS, before updation: {self.objects_spawned.get(track_id)}")

            garbage_world_object = self.objects_spawned.get(track_id)
            if garbage_world_object is None:
                logger.info(f"mark_collected(): Garbage does not exist of track_id: {track_id}")
                return

            garbage_world_object.state = ActionStatus.COLLECTED

            logger.info(f"ObjectManager -> mark_collected(): ENDS, after updation: {self.objects_spawned.get(track_id)}")
            return


        except Exception as e:
            logger.info(f"Error occurred in ObjectManager -> mark_collected(), error: {e}")
            raise e
        


'''
    def remove_garbage(self, object_id: int) -> None:
        try:
            logger.info(f"ObjectManager -> remove_garbage(): STARTS")

            # Retrieve the body_id of the given garbage
            garbage_body_id = self.object_bodyID.get(object_id)
            if garbage_body_id is None:
                return
            
            # Remove from simulation
            p.removeBody(garbage_body_id)

            # Deleting the garbage record, from both the dictionaries
            del self.object_bodyID[object_id]
            del self.objects_spawned[object_id]

            logger.info(f"ObjectManager -> remove_garbage(): ENDS, deleted garbage_body_id: {garbage_body_id}")
            return
        

        except Exception as e:
            logger.info(f"Error occurred in ObjectManager -> remove_garbage(), error: {e}")
            raise e
'''