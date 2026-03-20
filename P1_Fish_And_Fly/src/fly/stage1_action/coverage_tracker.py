from typing import Tuple, Optional, List
from collections import defaultdict
import numpy as np

from src.common.logging import logger
from src.common.logging.entity import CoverageArea


class CoverageTracker:
    """
    Tracks:
    - Coverage using unique visited cells
    - Heatmap using density accumulation
    - Supports interpolation + jitter-safe updates
    """

    def __init__(self, grid_size: int = 100):
        self.grid_size = grid_size

        # Unique coverage tracking
        self.surface_visited = set()
        self.underwater_visited = set()
        self.total_visited = set()

        # Density tracking (for heatmap)
        self.surface_density = defaultdict(int)
        self.underwater_density = defaultdict(int)

        self.prev_position: Optional[Tuple[float, float, float]] = None



    # -----------------------------
    # INTERNAL UTILITIES
    # -----------------------------

    def _clamp(self, val: float) -> int:
        try:
            return max(0, min(self.grid_size - 1, int(float(val))))
        
        except Exception as e:
            logger.warning(f"CoverageTracker -> Clamp failed for value={val}, error={e}")
            return 0



    def _interpolate_cells(self, x1: int, y1: int, x2: int, y2: int) -> List[Tuple[int, int]]:
        try:
            cells = []

            dx = x2 - x1
            dy = y2 - y1
            steps = max(abs(dx), abs(dy))

            if steps == 0:
                return [(x1, y1)]

            for i in range(steps + 1):
                x = int(round(x1 + dx * (i / steps)))
                y = int(round(y1 + dy * (i / steps)))

                x = self._clamp(x)
                y = self._clamp(y)

                cells.append((x, y))

            return cells

        except Exception as e:
            logger.error(f"CoverageTracker -> interpolate_cells(), Interpolation error: {e}")
            return [(x1, y1)]

    # -----------------------------
    # CORE UPDATE METHOD
    # -----------------------------

    def update_coverage_area(self, position: Tuple[float, float, float]) -> None:
        try:
            x, y, z = position

            x = self._clamp(x)
            y = self._clamp(y)

            current_pos = (x, y, z)

            # First update
            if self.prev_position is None:
                self._mark_cell(x, y, z)
                self.prev_position = current_pos
                return

            px, py, _ = self.prev_position
            px = self._clamp(px)
            py = self._clamp(py)

            # Interpolate path
            cells = self._interpolate_cells(px, py, x, y)

            for cx, cy in cells:
                self._mark_cell(cx, cy, z)

            self.prev_position = current_pos

            logger.info(
                f"[CoverageTracker] Update | Pos=({x},{y},{z}) | "
                f"Surface={len(self.surface_visited)} | "
                f"Underwater={len(self.underwater_visited)} | "
                f"Total={len(self.total_visited)}"
            )

        except Exception as e:
            logger.error(f"CoverageTracker -> Update failed, error: {e}")

    # -----------------------------
    # CELL MARKING
    # -----------------------------

    def _mark_cell(self, x: int, y: int, z: float) -> None:
        try:
            cell = (x, y)

            # Unique tracking
            self.total_visited.add(cell)

            if z >= 0:
                self.surface_visited.add(cell)
                self.surface_density[cell] += 1
            else:
                self.underwater_visited.add(cell)
                self.underwater_density[cell] += 1

        except Exception as e:
            logger.warning(f"CoverageTracker -> Mark cell failed, error: {e}")

    # -----------------------------
    # METRICS
    # -----------------------------

    def get_coverage_percentages(self):
        try:
            total_cells = self.grid_size * self.grid_size

            # Lawn mower → expected full grid coverage
            surface_pct = (len(self.surface_visited) / total_cells) * 1000
            underwater_pct = (len(self.underwater_visited) / total_cells) * 1000

            return CoverageArea(
                surface_percentge=round(surface_pct, 3),
                underwater_percentage=round(underwater_pct, 3)
            )

        except Exception as e:
            logger.error(f"Coverage calc failed: {e}", exc_info=True)
            raise e


    # -----------------------------
    # HEATMAP (DENSITY)
    # -----------------------------

    def get_density_heatmap(self, underwater: bool = False):
        try:
            heatmap = np.zeros((self.grid_size, self.grid_size))

            # fallback: if density not implemented yet
            if hasattr(self, "surface_density"):

                density = (
                    self.underwater_density if underwater
                    else self.surface_density
                )

                for (x, y), count in density.items():
                    heatmap[y][x] = count

            else:
                # fallback to visited cells (binary heatmap)
                visited = (
                    self.underwater_visited if underwater
                    else self.surface_visited
                )

                for (x, y) in visited:
                    heatmap[y][x] = 1

            # normalize
            if heatmap.max() > 0:
                heatmap = heatmap / heatmap.max()

            logger.info(f"CoverageTracker -> get_density_heatmap(), heatmap: {heatmap}")
            return heatmap


        except Exception as e:
            logger.error(f"[CoverageTracker] Heatmap failed: {e}", exc_info=True)
            return None

    # -----------------------------
    # RESET
    # -----------------------------

    def reset(self):
        try:
            self.surface_visited.clear()
            self.underwater_visited.clear()
            self.total_visited.clear()

            self.surface_density.clear()
            self.underwater_density.clear()

            self.prev_position = None

            logger.info("[CoverageTracker] Reset complete")
            return


        except Exception as e:
            logger.error(f"[CoverageTracker] Reset failed: {e}")