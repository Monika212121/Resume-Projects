

import pybullet as p
from typing import Optional

from src.common.logging import logger
from src.common.entity.position import Waypoint
from src.common.simulation.entity import CameraMode



class CameraManager:
    def __init__(self):
        self.mode = CameraMode.OVERVIEW
            


    def update_keyboard_controls(self):
        """
        Handle runtime keyboard camera switching.
        """
        try:
            keys = p.getKeyboardEvents()

            # OVERVIEW CAMERA
            if ord('1') in keys and keys[ord('1')] & p.KEY_WAS_TRIGGERED:
                self.mode = CameraMode.OVERVIEW
                logger.info("Camera switched -> OVERVIEW")


            # FISH FOLLOW CAMERA
            elif ord('2') in keys and keys[ord('2')] & p.KEY_WAS_TRIGGERED:
                self.mode = CameraMode.FISH_FOLLOW
                logger.info("Camera switched -> FISH_FOLLOW")


            # MANATEE FOLLOW CAMERA
            elif ord('3') in keys and keys[ord('3')] & p.KEY_WAS_TRIGGERED:
                self.mode = CameraMode.MANATEE_FOLLOW
                logger.info("Camera switched -> MANATEE_FOLLOW")


            # CINEMATIC CAMERA
            elif ord('4') in keys and keys[ord('4')] & p.KEY_WAS_TRIGGERED:
                self.mode = CameraMode.CINEMATIC
                logger.info("Camera switched -> CINEMATIC")


            # TOP VIEW CAMERA
            elif ord('5') in keys and keys[ord('5')] & p.KEY_WAS_TRIGGERED:
                self.mode = CameraMode.TOP_VIEW
                logger.info("Camera switched -> TOP_VIEW")


        except Exception as e:
            logger.error(f"Error occurred in CameraManager -> update_keyboard_controls(), error: {e}")
            raise e



    def update_camera(
        self,
        fish_pose: Optional[Waypoint] = None,
        manatee_pose: Optional[Waypoint] = None
    ):
        """
        Update active camera mode every simulation frame.
        """

        try:

            if self.mode == CameraMode.OVERVIEW:
                self.set_overview_camera()


            elif self.mode == CameraMode.FISH_FOLLOW and fish_pose is not None:
                self.follow_fish(fish_pose)


            elif self.mode == CameraMode.MANATEE_FOLLOW and manatee_pose is not None:
                self.follow_manatee(manatee_pose)


            elif self.mode == CameraMode.CINEMATIC:

                # Prefer manatee for cinematic shots
                target_pose = manatee_pose if manatee_pose is not None else fish_pose

                if target_pose is not None:
                    self.cinematic_side_view(target_pose)


            elif self.mode == CameraMode.TOP_VIEW:
                self.top_view()


        except Exception as e:
            logger.error(f"Error occurred in CameraManager -> update_camera(), error: {e}")
            raise e



    def set_overview_camera(self):
        """
        Best for:
        - Multi-agent orchestration
        - System overview
        - Mission coordination
        """

        try:

            p.resetDebugVisualizerCamera(
                cameraDistance=85,
                cameraYaw=45,
                cameraPitch=-55,
                cameraTargetPosition=[60, 60, 0],
            )

        except Exception as e:
            logger.error(f"Error occurred in CameraManager -> set_overview_camera(), error: {e}")
            raise e



    def follow_fish(self, pose: Waypoint):
        """
        Best for:
        - Fish garbage collection
        - Hazard avoidance
        - Underwater traversal
        """

        try:

            p.resetDebugVisualizerCamera(
                cameraDistance=14,
                cameraYaw=45,
                cameraPitch=-25,
                cameraTargetPosition=[
                    pose.x + 3,
                    pose.y + 2,
                    pose.z
                ],
            )

        except Exception as e:
            logger.error(f"Error occurred in CameraManager -> follow_fish(), error: {e}")
            raise e



    def follow_manatee(self, pose: Waypoint):
        """
        Best for:
        - Dump collection
        - HQ unloading
        - Rescue operations
        """

        try:

            p.resetDebugVisualizerCamera(
                cameraDistance=20,
                cameraYaw=120,
                cameraPitch=-30,
                cameraTargetPosition=[
                    pose.x + 4,
                    pose.y,
                    pose.z
                ],
            )

        except Exception as e:
            logger.error(f"Error occurred in CameraManager -> follow_manatee(), error: {e}")
            raise e



    def cinematic_side_view(self, pose: Waypoint):
        """
        Best for:
        - Hero shots
        - Trailer shots
        - Cinematic moments
        """

        try:

            p.resetDebugVisualizerCamera(
                cameraDistance=28,
                cameraYaw=90,
                cameraPitch=-18,
                cameraTargetPosition=[
                    pose.x,
                    pose.y,
                    pose.z
                ],
            )

        except Exception as e:
            logger.error(f"Error occurred in CameraManager -> cinematic_side_view(), error: {e}")
            raise e



    def top_view(self):
        """
        Best for:
        - Tactical orchestration
        - Dispatcher visualization
        - Multi-agent coordination
        """

        try:

            p.resetDebugVisualizerCamera(
                cameraDistance=75,
                cameraYaw=0,
                cameraPitch=-89,
                cameraTargetPosition=[60, 60, 0],
            )

        except Exception as e:
            logger.error(f"Error occurred in CameraManager -> top_view(), error: {e}")
            raise e