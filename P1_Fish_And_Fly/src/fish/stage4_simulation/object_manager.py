import math
import time
import random
import pybullet as p
from typing import Dict, Tuple, Optional, List

from src.common.logging import logger
from src.common.projection.entity import FishFrameObject
from src.common.entity.fish_machine_info import FishNavigationInfo

from src.fish.stage1_vision.entity import EntityRole
from src.fish.stage3_action.entity import Waypoint, ActionStatus
from src.fish.stage4_simulation.entity import Metadata, Visual
from src.fish.stage4_simulation.clamper import clamp_position
from src.fish.stage4_simulation.object_factory import create_body
from src.fish.stage4_simulation.constants import SIM_GARBAGE_SPAWN_OFFSET_X, SPAWN_X_FACTOR, SPAWN_Y_FACTOR



class ObjectManager():
    def __init__(self, visual_config: Visual):
        self.object_bodyID: Dict[int, int] = {}                                                             # Dict{track_id, pybullet_body_id}
        self.objects_meta: Dict[int, Metadata] = {}                                                         # Dict{track_id, meta_data}
        
        self.visual_cfg = visual_config

        # parameters for blinking hazard objects
        self.hazard_body_ids: List[int] = []
        self._blink_state = True
        self._last_blink_time = time.time()


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



    def spawn_objects(self, objects: List[FishFrameObject], fish_info: FishNavigationInfo) -> None:
        try:
            logger.info(f"SimulationBridge -> spawn_objects(): STARTS, n(objects): {len(objects)}")

            self.fish_navigation_info = fish_info

            # Spawning all category objects
            for object in objects:
                if self.exists(object.track_id):
                    logger.info(f"SimulationBridge -> spawn_objects(): This object of track_id: {object.track_id} already exists")
                    continue

                # If the object is new in simulation, create it in simulation world
                safe_spawn_position = self.get_safe_spawn_position(object)

                # Spawn this object
                body_id = self.spawn_body(track_id = object.track_id, class_name = object.class_name, entity_role= object.entity_role, spawn_position = safe_spawn_position)


            logger.info(f"SimulationBridge -> spawn_objects(): ENDS")
            return


        except Exception as e:
            logger.info(f"Error occurred in SimulationBridge -> spawn_objects(), error: {e}")
            raise e 



    def get_safe_spawn_position(self, object: FishFrameObject) -> Tuple[float, float, float]:
        try:
            logger.info(f"ObjectManager -> get_safe_spawn_position(): STARTS, object: {object}")

            # Calculate perception mirroring based safe position
            spawn_position = self.get_spawn_position(rel_obj_pos_fish_frame = object.relative_position)

            # clamp this position to avoid spawning outside workspace
            safe_spawn_position = clamp_position(position = spawn_position)

            # NOTE: Changing position data type, because in pybullet, Spawn function takes position in tuple(float, float, float)
            safe_spawn_pos: Tuple[float, float, float] = (safe_spawn_position.x, safe_spawn_position.y, safe_spawn_position.z) 

            logger.info(f"ObjectManager -> get_safe_spawn_position(), safe_pos: {safe_spawn_position}")
            return safe_spawn_pos


        except Exception as e:
            logger.info(f"Error occurred in ObjectManager -> get_safe_spawn_position(), error: {e}")
            raise e



    def get_spawn_position(self, rel_obj_pos_fish_frame: Waypoint) -> Waypoint:
        try:

            # NOTE: We are using this formula to find the spawning position: 
            # | SPAWN POSITION = FISH POSITION + RELATIVE OBJECT POSITION + FIXED OFFSET(only in x-axis) |

            # Retrieving fish machine current position and direction
            fish_curr_pos = self.fish_navigation_info.position
            fish_curr_dir = self.fish_navigation_info.direction

            rel_obj_pos_world_frame = Waypoint(                                                             # refer SIMULATION_NOTES.md()
                x= rel_obj_pos_fish_frame.y * SPAWN_X_FACTOR,
                y= rel_obj_pos_fish_frame.x * SPAWN_Y_FACTOR * fish_curr_dir,
                z= 0
            )

            # FIXED OFFSET (in x-axis) for all targets
            gx = (SIM_GARBAGE_SPAWN_OFFSET_X * fish_curr_dir)                                     # refer SIMULATION_NOTES.md(3)

            # Spawn position in simulation world (world frame)
            spawn_world_position = Waypoint(
                x= fish_curr_pos.x + rel_obj_pos_world_frame.x + gx,
                y= fish_curr_pos.y + rel_obj_pos_world_frame.y,
                z= fish_curr_pos.z + rel_obj_pos_world_frame.z
            )

            logger.info(f"fish_curr_pos: {fish_curr_pos}, rel_pos_fish_frame: {rel_obj_pos_fish_frame}, rel_pos_world_frame: {rel_obj_pos_world_frame}")
            logger.info(f"ObjectManager -> get_spawn_position(), spawn_world_position: {spawn_world_position}")
            return spawn_world_position


        except Exception as e:
            logger.info(f"Error occurred in ObjectManager -> generate_safe_zone_position(), error: {e}")
            raise e



    def spawn_body(self, track_id: int, class_name: str, entity_role: EntityRole, spawn_position: Tuple[float, float, float]) -> int:
        try:

            # Determine appearance properties of the object to be spawned like visual, lifetime, orientation, etc.

            lifetime: float = -1                                                                            # default lifetime = eternity(always)
            obj_orientation: Optional[Tuple[float,float,float,float]] = None                                # default orientation = None

            if entity_role == EntityRole.COLLECTION_TARGET:
                visual_cfg = self.visual_cfg.targets[0]             # red sphere

            elif entity_role == EntityRole.ENVIRONMENT_ENTITY:
                visual_cfg = self.visual_cfg.entities[0]            # fish
                lifetime = 15.0
                obj_orientation = p.getQuaternionFromEuler((0, 1.57, 0))                                    # to rotate the object at 90 degree angle

            else:
                if class_name == "big_rock":
                    visual_cfg = self.visual_cfg.hazards[0]         # big rock
                else:
                    visual_cfg = self.visual_cfg.hazards[1]         # dangerous animal
                    lifetime = 15.0
                    obj_orientation = p.getQuaternionFromEuler((random.uniform(0.0,1.5), random.uniform(0.0,1.5), random.uniform(0.0, 1.5)))            # providing random orientation

            
            # Create a new body for the object (actual spawn function)
            new_body_id = create_body(body_info= visual_cfg, position= spawn_position, orientation= obj_orientation) 

            # Update the spawned objects record
            self.object_bodyID[track_id] = new_body_id

            self.objects_meta[track_id] = Metadata(
                body_id= new_body_id,
                spawn_time= time.time(),
                lifetime= lifetime,
                fade_time= 2.0,
                spawn_world_position= spawn_position
            )

            # Register hazard when spawning
            if entity_role == EntityRole.NAVIGATION_HAZARD and class_name == "dangerous_animal":
                self.hazard_body_ids.append(new_body_id)                                                # for blinking

            logger.info(f"ObjectManager -> spawn_body(): ENDS, meta_data: {self.objects_meta[track_id]}")
            return new_body_id


        except Exception as e:
            logger.info(f"Error occurred in ObjectManager -> spawn_body(), error: {e}")
            raise e
        


    def update_object_lifecycle(self):
        try:
            current_time = time.time()

            to_remove_track_ids: List[int] = []

            for track_id, obj_meta_data in self.objects_meta.items():

                # Unpacking object's metadata
                body_id, lifetime, spawn_time, fade_time = (
                    obj_meta_data.body_id, 
                    obj_meta_data.lifetime, 
                    obj_meta_data.spawn_time,  
                    obj_meta_data.fade_time
                )

                # NOTE: lifetime = -1 means, permanent object, they will be spawned for whole lifetime of the simulation
                if lifetime < 0:
                    logger.info(f"update_object_lifecycle(): This is a static object, skipped de-spawning.")
                    continue

                object_age = current_time - spawn_time

                # Start fading
                if object_age > lifetime - fade_time:
                    remaining_time = lifetime - object_age
                    if remaining_time > 0:
                        alpha = remaining_time / fade_time
                        p.changeVisualShape(body_id, -1, rgbaColor = [1, 1, 1, alpha])


                # remove object
                if object_age > lifetime:
                    p.removeBody(body_id)
                    to_remove_track_ids.append(track_id)

            
            # De-spawning objects, those exceeded their lifetime
            for track_id in to_remove_track_ids:
                del self.objects_meta[track_id]
                del self.object_bodyID[track_id]                                                            # refer SIMULATION_NOTES.md()


        except Exception as e:
            logger.info(f"Error occurred in ObjectManager -> update_object_lifecycle(), error: {e}")
            raise e
        


    def update_hazard_blinking(self):
        try:
            # If no hazard exist, leave immediately
            if not self.hazard_body_ids:
                logger.info("No hazard object is present currently")
                return
            
            now = time.time()
            if now - self._last_blink_time < 0.5:
                return
            
            self._last_blink_time = now
            self._blink_state = not self._blink_state

            color = [1, 1, 0, 1] if self._blink_state else [1, 1, 0, 0.25]

            for body_id in self.hazard_body_ids:
                p.changeVisualShape(body_id, -1, rgbaColor = color)

            return


        except Exception as e:
            logger.info(f"Error occurred in update_hazard_blinking(), error: {e}")
            raise e



    def mark_collected(self, track_id: int):
        try:
            logger.info(f"ObjectManager -> mark_collected(): STARTS, before updation: {self.objects_meta.get(track_id)}")

            garbage_meta_data = self.objects_meta.get(track_id)
            if garbage_meta_data is None:
                logger.info(f"mark_collected(): Garbage does not exist of track_id: {track_id}")
                return

            garbage_meta_data.status = ActionStatus.COLLECTED

            logger.info(f"ObjectManager -> mark_collected(): ENDS, after updation: {self.objects_meta.get(track_id)}")
            return


        except Exception as e:
            logger.info(f"Error occurred in update_hazard_blinking(), error: {e}")
            raise e