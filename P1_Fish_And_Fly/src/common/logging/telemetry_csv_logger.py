import os
import csv
from pathlib import Path
from datetime import datetime, timezone

from src.common.logging import logger

from src.fly.stage3_decision.entity import StateDeltas



class TelemetryCSVLogger:
    """
    Persistent CSV logger for Fly machine monitoring deltas.
    """
    def __init__(self, output_file_path: Path | str, reset: bool = False):
        self.file_path = Path(output_file_path)

        # create parent directory if not exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        if reset and self.file_path.exists():
            self.file_path.unlink()

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
                    "mission_phase",
                    "fish_state",
                    "fish_x",
                    "fish_y",
                    "fish_z",
                    "surface_coverage_pct",
                    "underwater_coverage_pct",
                    "communication_delta",
                    "fish_progress_delta",
                    "silence_delta"
                ])



    def log_fish_machine_telemetry(self, delta: StateDeltas):
        """
        Append a new monitoring snapshot.
        """
        try:
            with open(self.file_path, mode="a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now(timezone.utc).isoformat(),
                    delta.mission_phase,
                    delta.fish_state,
                    delta.fish_x,
                    delta.fish_y,
                    delta.fish_z,
                    delta.surface_coverage_pct,
                    delta.underwater_coverage_pct,
                    delta.communication_delta,
                    delta.fish_progress_delta,
                    delta.silence_delta
                ])

            logger.info("TelemetryCSVLogger -> log_fish_fly_delta(): Fly state delta recorded")


        except Exception as e:
            logger.error(f"TelemetryCSVLogger -> log_fish_fly_delta(): Failed to log state delta, error: {e}")
            raise e