import os
import numpy as np
from enum import IntEnum
from typing import Tuple, List

from src.fish.stage3_action.entity import Waypoint


class CellState(IntEnum):
    POLLUTED = 0            # dark orange (initial)
    SURFACE_TRAVERSED = 1   # light orange
    CLEANED = 2             # dark blue


class CoverageGrid:
    def __init__(self, size: int= 100, world_size:float= 100.0):
        """
        size: grid resolution (size x size)
        world_size: physical size of environment (meters)
        """
        self.size = size
        self.world_size = world_size
        self.cell_size = world_size / size

        self.grid = np.full((size, size), CellState.POLLUTED, dtype=np.int8)

        self._last_cell = None  # stores last grid index

    # --------------------------------------------------
    # World → Grid mapping
    # --------------------------------------------------
    def world_to_grid(self, curr_pos: Waypoint):
        gx = int(np.clip(curr_pos.x / self.cell_size, 0, self.size - 1))
        gy = int(np.clip(curr_pos.y / self.cell_size, 0, self.size - 1))
        return gx, gy

    # --------------------------------------------------
    # Bresenham-style line fill
    # --------------------------------------------------
    def _cells_between(self, start: Tuple[int,int], end: Tuple[int,int]):
        x0, y0 = start
        x1, y1 = end

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1

        err = dx - dy

        cells: List[Tuple[int,int]] = []

        while True:
            cells.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

        return cells

    # --------------------------------------------------
    # MAIN UPDATE API (this is what backend calls)
    # --------------------------------------------------
    def _to_cell(self, curr_pos: Waypoint):
        gx = int(np.clip(curr_pos.x, 0, self.size - 1))
        gy = int(np.clip(curr_pos.y, 0, self.size - 1))
        return gx, gy


    def update_from_pose(self, curr_pos: Waypoint):
        current_cell = self._to_cell(curr_pos)

        if self._last_cell is None:
            self._last_cell = current_cell

        path_cells = self._cells_between(self._last_cell, current_cell)

        for gx, gy in path_cells:
            self._update_cell(gx, gy, curr_pos.z)

        self._last_cell = current_cell

    # --------------------------------------------------
    # Cell state transition
    # --------------------------------------------------
    def _update_cell(self, gx: int, gy: int, z: float):
        state = CellState(self.grid[gx, gy])

        # Surface pass
        if z >= 0:
            if state == CellState.POLLUTED:
                self.grid[gx, gy] = CellState.SURFACE_TRAVERSED     # surface (light orange)

        # Underwater pass
        else:
            if state != CellState.CLEANED:
                self.grid[gx, gy] = CellState.CLEANED               # underwater (dark blue)

    # --------------------------------------------------
    # Stats
    # --------------------------------------------------
    def coverage_stats(self):
        total = self.size * self.size
        cleaned = np.count_nonzero(self.grid == CellState.CLEANED)
        surface = np.count_nonzero(self.grid == CellState.SURFACE_TRAVERSED)

        return {
            "cleaned_pct": round((cleaned / total) * 100, 2),
            "surface_pct": round((surface / total) * 100, 2),
        }

    # --------------------------------------------------
    # Persistence (atomic)
    # --------------------------------------------------

    def save(self, path:str ="artifacts/logs/coverage_grid.npy"):
        os.makedirs(os.path.dirname(path), exist_ok=True)

        np.save(path, self.grid)
