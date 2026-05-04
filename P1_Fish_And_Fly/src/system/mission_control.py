# src/system/mission_control.py

import asyncio

from src.common.utils.mission import mission_is_active
from src.common.entity.fish_communication import SystemHeartbeat



class MissionController:
    def __init__(self):
        self.stop_event = asyncio.Event()


    def stop(self):
        self.stop_event.set()


    def should_stop(self):
        return self.stop_event.is_set()