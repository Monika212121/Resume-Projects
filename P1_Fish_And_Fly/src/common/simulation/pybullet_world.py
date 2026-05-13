import pybullet as p
from typing import List, Tuple, Dict

from src.common.logging import logger
from src.common.entity.position import Waypoint
from src.common.simulation.entity import SpawnObject
from src.common.simulation.constants import WORKSPACE_BOUNDS
from src.common.simulation.object_factory import create_body
from src.common.simulation.sim_recorder import SimulationRecorder

from src.fly.stage3_decision.entity import DumpConfig



class PyBulletWorld:
    def __init__(self, dump_points_info: List[DumpConfig], gui: bool = True):
        self.gui = gui
        self.connected = False
        self.workspace_ids = []

        self.physics_client_id = None
        self.dump_points: List[DumpConfig] = dump_points_info
        self.dump_point_body_IDs: Dict[int, int] = {}
        self.recorder = SimulationRecorder()

        self.last_filled_dump_bodyID = -1
        self.dump_blink_state = False



    def connect(self, enable_GUI: bool = False):
        try: 
            logger.debug(f"PybulletWorld -> connect(): STARTS")

            if self.connected:
                return

            if enable_GUI:
                self.physics_client_id = p.connect(p.GUI)
            else:
                self.physics_client_id = p.connect(p.DIRECT)

            
            p.setGravity(0, 0, 0)

            # Create water body workspace
            self.create_water_cuboid()

            # Optional: hide noisy GUI panels
            p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
            p.configureDebugVisualizer(p.COV_ENABLE_RGB_BUFFER_PREVIEW, 0)
            p.configureDebugVisualizer(p.COV_ENABLE_DEPTH_BUFFER_PREVIEW, 0)
            p.configureDebugVisualizer(p.COV_ENABLE_SEGMENTATION_MARK_PREVIEW, 0)

            # Create Head Quarter(H.Q.) of the workspace
            self.spawn_headquarter(position= (0.0, 60.0, 0.0))

            # Create dump points on the boundary of the workspace
            self.spawn_dump_points()

            self.connected = True

            logger.debug(f"PybulletWorld -> connect(): ENDS")
            return

        
        except Exception as e:
            logger.error(f"Error occurred in PybulletWorld -> connect(), error: {e}")
            raise e



    def update_camera_follow_fish(self, fish_pose: Waypoint):
        try: 
            logger.debug(f"PybulletWorld -> update_camera_follow_fish(): STARTS")

            fx, fy, fz = fish_pose.x, fish_pose.y, fish_pose.z

            p.resetDebugVisualizerCamera(
                cameraDistance=30,                                                                              # wide enough to see garbage
                cameraYaw=45,
                cameraPitch=-35,
                cameraTargetPosition=[fx, fy, fz],
            )

            logger.debug(f"PybulletWorld -> update_camera_follow_fish(): ENDS")
            return


        except Exception as e:
            logger.error(f"Error occurred in PybulletWorld -> update_camera_follow_fish(), error: {e}")
            raise e


        

    def shutdown(self):
        try: 
            if self.connected:
                p.disconnect()
                self.connected = False
            
            return
        

        except Exception as e:
            logger.error(f"Error occurred in PybulletWorld -> update_camera_follow_fish(), error: {e}")
            raise e
        


    def create_water_cuboid(self):
        try: 
            logger.debug(f"PyBulletWorld -> create_water_cuboid(): STARTS")

            thickness = 0.1

            X_MIN, X_MAX = WORKSPACE_BOUNDS["x_min"], WORKSPACE_BOUNDS["x_max"]
            Y_MIN, Y_MAX = WORKSPACE_BOUNDS["y_min"], WORKSPACE_BOUNDS["y_max"]
            Z_MIN, Z_MAX = WORKSPACE_BOUNDS["z_min"], WORKSPACE_BOUNDS["z_max"]

            x_mid = (X_MIN + X_MAX) / 2
            y_mid = (Y_MIN + Y_MAX) / 2
            z_mid = (Z_MIN + Z_MAX) / 2

            x_half = (X_MAX - X_MIN) / 2
            y_half = (Y_MAX - Y_MIN) / 2
            z_half = (Z_MAX - Z_MIN) / 2

            # Bottom
            self.create_wall(
                [x_half, y_half, thickness],
                [x_mid, y_mid, Z_MIN - thickness]
            )

            # Top
            self.create_wall(
                [x_half, y_half, thickness],
                [x_mid, y_mid, Z_MAX + thickness]
            )

            # X min
            self.create_wall(
                [thickness, y_half, z_half],
                [X_MIN - thickness, y_mid, z_mid]
            )

            # X max
            self.create_wall(
                [thickness, y_half, z_half],
                [X_MAX + thickness, y_mid, z_mid]
            )

            # Y min
            self.create_wall(
                [x_half, thickness, z_half],
                [x_mid, Y_MIN - thickness, z_mid]
            )

            # Y max
            self.create_wall(
                [x_half, thickness, z_half],
                [x_mid, Y_MAX + thickness, z_mid]
            )

            logger.debug(f"PyBulletWorld -> create_water_cuboid(): ENDS")
            return
        
        
        except Exception as e:
            logger.error(f"Error occurred in PybulletWorld -> create_water_cuboid(), error: {e}")
            raise e



    def create_wall(self, half_extents: List[float], position: List[float]):
        try: 
            logger.debug(f"PyBulletWorld -> create_wall(): STARTS")

            visual = p.createVisualShape(
                p.GEOM_BOX,
                halfExtents=half_extents,
                rgbaColor=[0, 0.5, 1, 0.15],                                                                    # transparent water blue
            )

            collision = p.createCollisionShape(
                p.GEOM_BOX,
                halfExtents=half_extents,
            )

            p.createMultiBody(
                baseMass=0,
                baseCollisionShapeIndex=collision,
                baseVisualShapeIndex=visual,
                basePosition=position,
            )

            logger.debug(f"PyBulletWorld -> create_wall(): ENDS")
            return



        except Exception as e:
            logger.error(f"Error occurred in PybulletWorld -> create_wall(), error: {e}")
            raise e



    def spawn_headquarter(self, position: Tuple[float,float,float]):
        try: 
            logger.debug(f"PybulletWorld -> spawn_headquarter(): STARTS")
            
            # base platform
            base_info = SpawnObject(
                name= "HQ",
                shape= "cylinder",
                size= (1.8, 0.6),
                color= (1.0, 0.0, 0.0, 1.0),
                count= 1
            )
            base_id = create_body(body_info= base_info, position= position, orientation = None)

            # pole
            pole_pos = (position[0], position[1], position[2] + 0.6)
            pole_info = SpawnObject(
                name= "HQ",
                shape= "cylinder",
                size= (0.15, 5.0),
                color= (0.1, 0.5, 1.0, 1.0),
                count= 2
            )
            pole_id = create_body(body_info= pole_info, position= pole_pos, orientation = None)

            # top marker
            marker_pos = (position[0], position[1], position[2] + 1.2)
            marker_info = SpawnObject(
                name= "HQ",
                shape= "sphere",
                size= (0.36,),
                color= (1.0, 1.0, 1.0, 0.9),
                count= 3
            )
            marker_id = create_body(body_info= marker_info, position= marker_pos, orientation = None)

            self.hq_body_ids = [base_id, pole_id, marker_id]

            logger.debug(f"PybulletWorld -> spawn_headquarter(): ENDS")
            return


        except Exception as e:
            logger.error(f"Error occurred in PybulletWorld -> spawn_headquarter(), error: {e}")
            raise e



    def spawn_dump_points(self):
        """
        Spawn dump point stations in the buffer area.
        Each dump point is a static colored box.
        """
        try: 
            logger.debug(f"PybulletWorld -> spawn_dump_points(): STARTS")

            # Dump points are taken from `action.yaml` config file
            dump_points = self.dump_points

            # Cube shaped stations
            half_extents = [1.8, 1.8, 0.8]                     # 2x2x0.5 box

            collision_shape = p.createCollisionShape(
                shapeType=p.GEOM_BOX,
                halfExtents=half_extents,
                physicsClientId=self.physics_client_id
            )

            visual_shape = p.createVisualShape(
                shapeType=p.GEOM_BOX,
                halfExtents=half_extents,
                rgbaColor=[1.0, 0.6, 0.0, 1.0],                 # orange
                physicsClientId=self.physics_client_id
            )


            for idx, dump_point in enumerate(dump_points):
                dp = dump_point.position
                body_id = p.createMultiBody(
                    baseMass=0.0,                               # static
                    baseCollisionShapeIndex=collision_shape,
                    baseVisualShapeIndex=visual_shape,
                    basePosition=[dp.x, dp.y, dp.z + 0.50],     # sits on surface
                    physicsClientId=self.physics_client_id
                )

                p.changeVisualShape(
                    body_id,
                    -1,
                    rgbaColor=[1.0, 0.7, 0.2, 1.0],
                    physicsClientId=self.physics_client_id
                )

                self.dump_point_body_IDs[dump_point.dump_id] = body_id

                logger.debug(f"PybulletWorld -> spawn_dump_points(): Spawned Dump Point {idx} at ({dp.x}, {dp.y}, {dp.z})")


            logger.debug(f"PybulletWorld -> spawn_dump_points(): ENDS, Total dump points spawned: {len(self.dump_point_body_IDs)}")
            return
        

        except Exception as e:
            logger.error(f"Error occurred in PybulletWorld -> spawn_dump_points(), error: {e}")
            raise e
        


    def update_dump_blinking(self, dump_id: int):
        try:
            target_dump_body_ID: int

            # If there is filled dump point, mark it mud brown
            if dump_id > 0:
                target_dump_body_ID = self.dump_point_body_IDs[dump_id]
                self.last_filled_dump_bodyID = target_dump_body_ID

                self.dump_blink_state = not self.dump_blink_state
                color = [0.38, 0.25, 0.12, 1.0] if self.dump_blink_state else [0.55, 0.35, 0.15, 1.0]           # mud brown, light brown
            

            # If there is no filled dump point, then restore the orignal orange color of last marked dump point
            else:
                target_dump_body_ID = self.last_filled_dump_bodyID
                color = [1.0, 0.7, 0.2, 1.0]                                                                    # orange


            p.changeVisualShape(
                target_dump_body_ID,
                -1,
                rgbaColor= color
            )

            return
        

        except Exception as e:
            logger.error(f"Error occurred in PybulletWorld -> update_dump_blinking(), error: {e}")
            raise e        