import numpy as np
from enum import IntEnum
from src.common.logging import logger

from src.fish.stage3_action.entity import Waypoint


class CellState(IntEnum):
    """
    Sequential pollution-remediation stages.
    """
    POLLUTED = 0                # dark orange
    SURFACE_TRAVERSED = 1       # light orange
    UNDERWATER_TRAVERSED = 2    # light blue
    CLEANED = 3                 # dark blue


class CoverageGrid:
    def __init__(self, size: int = 100):
        self.size = size

        # Entire water body starts polluted
        self.grid = np.full(
            (size, size),
            CellState.POLLUTED,
            dtype=np.int8
        )

    # -------------------------------------------------
    # CORE UPDATE LOGIC
    # -------------------------------------------------
    def update_cell(self, curr_position: Waypoint):
        """
        Updates grid cell state based on Fish depth.

        z >= 0  : surface traversal
        z < 0   : underwater traversal
        """

        gx = int(np.clip(curr_position.x, 0, self.size - 1))
        gy = int(np.clip(curr_position.y, 0, self.size - 1))

        current = CellState(self.grid[gx, gy])

        # Surface pass
        if curr_position.z >= 0:
            if current == CellState.POLLUTED:
                self.grid[gx, gy] = CellState.SURFACE_TRAVERSED

        # Underwater pass
        else:
            if current == CellState.SURFACE_TRAVERSED:
                self.grid[gx, gy] = CellState.UNDERWATER_TRAVERSED
            elif current == CellState.UNDERWATER_TRAVERSED:
                self.grid[gx, gy] = CellState.CLEANED
            elif current == CellState.POLLUTED:
                # Direct underwater cleaning if surface was skipped
                self.grid[gx, gy] = CellState.CLEANED

        logger.info(
            f"CoverageGrid -> update_cell(): ({gx}, {gy}, z={curr_position.z}) -> "
            f"{CellState(self.grid[gx, gy]).name}"
        )

        logger.info(f"grid : {self.grid}")
        return

    # -------------------------------------------------
    # STATS FOR MISSION UI
    # -------------------------------------------------
    def coverage_stats(self):
        """
        Returns mission progress metrics.
        """

        total = self.size * self.size

        surface = np.count_nonzero(self.grid == CellState.SURFACE_TRAVERSED)
        underwater = np.count_nonzero(self.grid == CellState.UNDERWATER_TRAVERSED)
        cleaned = np.count_nonzero(self.grid == CellState.CLEANED)

        progress = surface + underwater + cleaned

        return {
            "progress_pct": round((progress / total) * 100, 2),
            "cleaned_pct": round((cleaned / total) * 100, 2),
            "remaining_polluted_pct": round(
                (np.count_nonzero(self.grid == CellState.POLLUTED) / total) * 100,
                2
            ),
        }

    # -------------------------------------------------
    # OPTIONAL
    # -------------------------------------------------
    def reset(self):
        self.grid.fill(CellState.POLLUTED)
