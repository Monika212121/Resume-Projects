import cv2
from pathlib import Path
from datetime import datetime

from src.common.logging import logger


class VideoWriterManager:

    def __init__(self, output_dir: str = "outputs", fps: int = 20):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.fps = fps
        self.writer = None
        self.frame_size = None
        logger.info("video_writer_manager init")

    def _generate_filename(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return str(self.output_dir / f"fish_fly_output_{timestamp}.mp4")

    def initialize(self, frame):
        h, w = frame.shape[:2]
        self.frame_size = (w, h)

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")            # type:ignore
        filename = self._generate_filename()

        self.writer = cv2.VideoWriter(filename, fourcc, self.fps, self.frame_size)

    def write(self, frame):
        logger.info(f"*********VideoWriterMananger -> write()")
        if self.writer is None:
            self.initialize(frame)

        if frame.shape[1::-1] != self.frame_size:
            frame = cv2.resize(frame, self.frame_size)

        self.writer.write(frame)                            # type: ignore

    def release(self):
        if self.writer:
            self.writer.release()