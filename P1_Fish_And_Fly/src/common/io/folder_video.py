from ast import Return

import cv2
from pathlib import Path
from typing import List

from src.common.logging import logger
from src.common.io.base import VisionInput



class FolderVideoInput(VisionInput):

    def __init__(self, root_folder: str):
        self.root = Path(root_folder)

        self.surface_folder = self.root / "surface"
        self.underwater_folder = self.root / "underwater"

        self.surface_videos = self._collect_videos(self.surface_folder)
        self.underwater_videos = self._collect_videos(self.underwater_folder)

        self.current_list: List[Path] = []
        self.current_index: int = 0

        self.cap = None
        self.mode = "surface"
        self.current_video_path = None



    def _refresh_videos(self):
        try: 
            if self.mode == "surface":
                updated = self._collect_videos(self.surface_folder)
            else:
                updated = self._collect_videos(self.underwater_folder)

            if len(updated) != len(self.current_list):
                logger.info("New video detected in folder (hot-drop). Updating playlist.")
                self.current_list = updated


        except Exception as e:
            logger.error(f"Error occurred in FolderVideoInput -> refresh_videos(), error: {e}")
            raise e


    def _collect_videos(self, folder: Path):
        try:
            videos = []
            for ext in ("*.mp4","*.avi","*.mov"):
                videos.extend(folder.glob(ext))

            return sorted(videos)
        

        except Exception as e:
            logger.error(f"Error occurred in FolderVideoInput -> collect_videos(), error: {e}")
            raise e



    def start(self):
        try: 
            logger.debug("FolderVideoInput -> start()")
            self._switch_internal("surface")
            return


        except Exception as e:
            logger.error(f"Error occurred in FolderVideoInput -> start(), error: {e}")
            raise e
        


    def _switch_internal(self, mode: str):
        try:
            if mode == "surface":
                self.current_list = self.surface_videos
            else:
                self.current_list = self.underwater_videos

            if not self.current_list:
                raise RuntimeError(f"No videos found for mode: {mode}")

            self.mode = mode
            self.current_index = 0

            self._open_current_video()
            return


        except Exception as e:
            logger.error(f"Error occurred in FolderVideoInput -> switch_internal(), error: {e}")
            raise e
        


    def switch_mode(self, mode: str):
        try:
            if mode == self.mode:
                return

            logger.info(f"FolderVideoInput -> switch_mode(): switching mode to {mode}")

            if self.cap:
                self.cap.release()

            self._switch_internal(mode)
            return


        except Exception as e:
            logger.error(f"Error occurred in FolderVideoInput -> switch_mode(), error: {e}")
            raise e
        


    def _open_current_video(self):
        try:
            logger.debug(f"FolderVideoInput -> open_current_video(): STARTS")

            self.current_video_path = str(self.current_list[self.current_index])

            logger.debug(f"VideoInput -> opening video: {self.current_video_path}")

            if self.cap:
                self.cap.release()

            self.cap = cv2.VideoCapture(self.current_video_path)

            if not self.cap.isOpened():
                raise RuntimeError(f"FolderVideoInput -> open_current_video(): Unable to open video: {self.current_video_path}")

            logger.debug(f"FolderVideoInput -> open_current_video(): STARTS")
            return
        

        except Exception as e:
            logger.error(f"Error occurred in FolderVideoInput -> open_current_video(), error: {e}")
            raise e



    def read(self):
        try:
            logger.debug(f"FolderVideoInput -> read(): STARTS")

            if self.cap is None:
                return None

            ret, frame = self.cap.read()

            if ret:
                return frame

            # Video finished
            self.cap.release()

            # 🔹 Refresh folder for hot-drop videos
            self._refresh_videos()

            if not self.current_list:
                return None

            # Move to next video
            self.current_index = (self.current_index + 1) % len(self.current_list)

            self._open_current_video()

            logger.debug(f"FolderVideoInput -> read(): ENDS")
            return self.read()


        except Exception as e:
            logger.error(f"Error occurred in FolderVideoInput -> read(), error: {e}")
            raise e



    def stop(self):
        try:
            logger.debug("FolderVideoInput -> stop(): STARTS")

            if self.cap:
                self.cap.release()
                logger.info("FolderVideoInput -> stop(): camera/video is released")

            logger.debug("FolderVideoInput -> stop(): ENDS")
            return


        except Exception as e:
            logger.error(f"Error occurred in FolderVideoInput -> stop(), error: {e}")
            raise e