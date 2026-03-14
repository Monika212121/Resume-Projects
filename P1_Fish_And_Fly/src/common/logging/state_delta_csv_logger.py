import os
import csv
from datetime import datetime, timezone

from src.common.logging import logger

from src.fly.stage2_action.entity import StateDeltas



class StateDeltaCSVLogger:
    """
    Persistent CSV logger for Fly machine monitoring deltas.
    """
    def __init__(self, reset: bool = False):
        output_dir = "artifacts/logs"              # later pass via config
        file_path = "fly_state_deltas.csv"

        os.makedirs(output_dir, exist_ok=True)
        self.file_path = os.path.join(output_dir, file_path)

        if reset and os.path.exists(self.file_path):
            os.remove(self.file_path)      

        self._init_csv()



    def _init_csv(self):
        """
        Initialize CSV with monitoring schema.
        """
        if not os.path.exists(self.file_path):
            with open(self.file_path, mode="w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp",
                    "alive",
                    "status",
                    "communication_delta",
                    "fish_progress_delta",
                    "silence_delta"
                ])

    def log(self, delta: StateDeltas):
        """
        Append a new monitoring snapshot.
        """
        try:
            with open(self.file_path, mode="a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now(timezone.utc).isoformat(),
                    delta.alive,
                    delta.status.name,
                    delta.communication_delta,
                    delta.fish_progress_delta,
                    delta.silence_delta
                ])

            logger.info("StateDeltaCSVLogger -> log(): Fly state delta recorded")

        except Exception as e:
            logger.error(f"StateDeltaCSVLogger -> log(): Failed to log state delta, error: {e}")
            raise e
