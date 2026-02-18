import time
import pandas as pd
from typing import Dict
from ui.grid.coverage_grid import CoverageGrid



class StatsAdapter:
    """
    Central statistics adapter for Fish–Fly dashboard.

    Responsibilities:
    - Hold raw logs (df)
    - Own CoverageGrid object
    - Expose clean, UI-safe stats
    - Centralize mission & heartbeat logic
    """

    HEARTBEAT_TIMEOUT_SEC = 5.0

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._now = time.time()

        # SINGLE source of truth for coverage
        self.coverage_grid_obj = CoverageGrid()

    # ======================================================
    # 🐟 FISH OBJECT STATS
    # ======================================================
    def final_state_stats(self) -> Dict[str, int]:
        if self.df.empty or "final_state" not in self.df.columns:
            return {}
        return self.df["final_state"].value_counts().to_dict()

    def collected_class_stats(self) -> Dict[str, int]:
        if self.df.empty:
            return {}

        required = {"final_state", "class_name"}
        if not required.issubset(self.df.columns):
            return {}

        collected = self.df[self.df["final_state"] == "COLLECTED"]
        return collected["class_name"].value_counts().to_dict()

    # ======================================================
    # 🩺 HEARTBEAT / FLY MONITORING
    # ======================================================

    def _get_last_timestamp_sec(self) -> float | None:
        if self.df.empty or "timestamp" not in self.df.columns:
            return None

        last_ts = self.df["timestamp"].iloc[-1]

        # Case 1: already numeric (epoch seconds)
        if isinstance(last_ts, (int, float)):
            return float(last_ts)

        # Case 2: pandas / string datetime
        try:
            return pd.to_datetime(last_ts).timestamp()
        except Exception:
            return None


    def is_fish_alive(self) -> bool:
        last_ts_sec = self._get_last_timestamp_sec()
        if last_ts_sec is None:
            return False

        return (time.time() - last_ts_sec) < self.HEARTBEAT_TIMEOUT_SEC


    def silence_delta(self) -> float:
        last_ts_sec = self._get_last_timestamp_sec()
        if last_ts_sec is None:
            return float("inf")

        return time.time() - last_ts_sec


    # ======================================================
    # 🚦 MISSION PHASE
    # ======================================================
    @property
    def mission_phase(self) -> str:
        if self.df.empty:
            return "BOOTING"

        if not self.is_fish_alive():
            return "ERROR"

        if self.coverage_stats["cleaned_pct"] >= 99.0:
            return "COMPLETED"

        return "RUNNING"

    # ======================================================
    # 🧭 COVERAGE (AREA-BASED)
    # ======================================================
    @property
    def coverage_stats(self) -> Dict[str, float]:
        """
        UI-safe coverage stats.
        Always derived from CoverageGrid.
        """
        return self.coverage_grid_obj.coverage_stats()
