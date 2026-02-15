import pybullet as p
import pybullet_data
from typing import List

from src.common.logging import logger

from src.fish.stage3_action.entity import Waypoint

X_MIN, X_MAX = 0, 100
Y_MIN, Y_MAX = 0, 100
Z_MIN, Z_MAX = -8, 0



class PyBulletWorld:
    def __init__(self, gui: bool = True):
        self.gui = gui
        self.connected = False
        self.workspace_ids = []


    def connect(self, enable_GUI: bool = False):
        if self.connected:
            return

        if enable_GUI:
            p.connect(p.GUI)
        else:
            p.connect(p.DIRECT)

        
        p.setGravity(0, 0, 0)

        
        # Create water body workspace
        self.create_water_cuboid()
        '''
        # 🔒 Lock camera ONCE
        p.resetDebugVisualizerCamera(
            cameraDistance=12,
            cameraYaw=45,
            cameraPitch=-30,
            cameraTargetPosition=[0, 0, 0],
        )
        '''

        # Optional: hide noisy GUI panels
        p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
        p.configureDebugVisualizer(p.COV_ENABLE_RGB_BUFFER_PREVIEW, 0)
        p.configureDebugVisualizer(p.COV_ENABLE_DEPTH_BUFFER_PREVIEW, 0)
        p.configureDebugVisualizer(p.COV_ENABLE_SEGMENTATION_MARK_PREVIEW, 0)

        self.connected = True
        return



    def update_camera_follow_fish(self, fish_pose: Waypoint):
        fx, fy, fz = fish_pose.x, fish_pose.y, fish_pose.z

        p.resetDebugVisualizerCamera(
            cameraDistance=30,                                                                              # wide enough to see garbage
            cameraYaw=45,
            cameraPitch=-35,
            cameraTargetPosition=[fx, fy, fz],
        )

        return
        


    def shutdown(self):
        if self.connected:
            p.disconnect()
            self.connected = False
        
        return



    def create_wall(self, half_extents: List[float], position: List[float]):
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



    def create_water_cuboid(self):
        logger.info(f"PyBulletWorld -> create_water_cuboid(): STARTS")

        thickness = 0.1
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

        logger.info(f"PyBulletWorld -> create_water_cuboid(): ENDS")
        return