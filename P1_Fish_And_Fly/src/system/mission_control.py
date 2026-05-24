import asyncio



class MissionController:
    def __init__(self):
        self.stop_event = asyncio.Event()


    def stop(self):
        self.stop_event.set()


    def should_stop(self):
        return self.stop_event.is_set()