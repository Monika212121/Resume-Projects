import os
import pandas as pd
from pathlib import Path

from src.common.logging import logger



def load_telemetry(telemetry_log_file_path: Path):

    if not os.path.exists(telemetry_log_file_path):
        return pd.DataFrame(columns=[
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

    try:
        df = pd.read_csv(telemetry_log_file_path)
        if df.empty:
            return None

        # convert numeric values, back from string to numbers
        numeric_cols = [
            "surface_coverage_pct",
            "underwater_coverage_pct",
            "communication_delta",
            "fish_progress_delta",
            "silence_delta"
        ]

        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.sort_values("timestamp")
        return df


    except Exception as e:
        logger.info("Error loading fish machine telemetry log:", e)
        return None