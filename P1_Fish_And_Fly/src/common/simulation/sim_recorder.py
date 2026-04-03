import cv2
import numpy as np
import pybullet as p

from src.common.entity.position import Waypoint
from src.common.io.video_writer import VideoWriterManager

# NOTE: I still need to fix this : speed, orientation and color issue.

class SimulationRecorder:
    def __init__(self):
        self.video_writer = VideoWriterManager(output_dir="outputs/sim", fps=10)
        self.initialized = False

        # Basic camera setup (you can tweak later)
        self.width = 640
        self.height = 480

        self.view_matrix = p.computeViewMatrixFromYawPitchRoll(
            cameraTargetPosition=[0, 0, 0],
            distance=10,
            yaw=50,
            pitch=-35,
            roll=0,
            upAxisIndex=2
        )

        self.projection_matrix = p.computeProjectionMatrixFOV(
            fov=60,
            aspect=self.width / self.height,
            nearVal=0.1,
            farVal=100
        )

        # for controlled recording
        self.frame_count = 0
        self.record_every_n = 3 



    def capture_frame2(self):
        _, _, rgb, _, _ = p.getCameraImage(
            width=self.width,
            height=self.height,
            viewMatrix=self.view_matrix,
            projectionMatrix=self.projection_matrix
        )

        frame = np.reshape(rgb, (self.height, self.width, 4))
        frame = frame[:, :, :3]  # remove alpha
        frame = frame.astype(np.uint8)

        return frame
    

    def capture_frame(self, target: Waypoint):

        if target:
            cam_target = [target.x, target.y, target.z]
        else:
            cam_target = [0, 0, 0]

        view_matrix = p.computeViewMatrixFromYawPitchRoll(
            cameraTargetPosition=cam_target,
            distance=8,
            yaw=60,
            pitch=-30,
            roll=0,
            upAxisIndex=2
        )

        projection_matrix = p.computeProjectionMatrixFOV(
            fov=75,
            aspect=self.width / self.height,
            nearVal=0.1,
            farVal=100
        )

        _, _, rgb, _, _ = p.getCameraImage(
            width=self.width,
            height=self.height,
            viewMatrix=view_matrix,
            projectionMatrix=projection_matrix
        )

        frame = np.reshape(rgb, (self.height, self.width, 4))

        # Convert to uint8 FIRST (fix crash)
        frame = frame.astype(np.uint8)

        # Remove alpha channel
        frame = frame[:, :, :3]

        # Convert RGB → BGR (fix color)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Flip vertically (fix upside-down)
        frame = frame[::-1, :, :]

        return frame



    def record(self, target: Waypoint):
        self.frame_count += 1

        if self.frame_count % self.record_every_n != 0:
            return

        frame = self.capture_frame(target= target)

        if not self.initialized:
            self.video_writer.initialize(frame)
            self.initialized = True

        self.video_writer.write(frame)



    def stop(self):
        self.video_writer.release()