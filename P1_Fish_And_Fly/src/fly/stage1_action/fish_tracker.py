import numpy as np
from typing import Tuple
from src.common.logging import logger
from src.common.logging.entity import CoverageArea

class LawnMowerCoverageTracker:
    def __init__(self, gridsize=100, mincoord=10, maxcoord=110):
        self.gridsize = gridsize
        self.mincoord = mincoord
        self.maxcoord = maxcoord
        self.lastpos = (10.0, 10.0, 0.0)
        self.total_cells = gridsize * gridsize
        self.expected_rows_covered = 0
        self.reset_all_grids()

    def reset_all_grids(self):
        self.surface_coverage_grid = np.zeros((self.gridsize, self.gridsize), dtype=np.uint8)
        self.surface_heatmap = np.zeros((self.gridsize, self.gridsize), dtype=np.uint16)
        self.underwater_coverage_grid = np.zeros((self.gridsize, self.gridsize), dtype=np.uint8)
        self.underwater_heatmap = np.zeros((self.gridsize, self.gridsize), dtype=np.uint16)
        self.expected_rows_covered = 0
        logger.info("ALL GRIDS RESET - ACTUAL: 0.0000% | EXPECTED: 0.00% (0/100 rows)")

    def get_expected_coverage(self, curr_y: int) -> float:
        if curr_y <= 10:
            return 0.0
        return min(100.0, ((curr_y - 10) / 100.0) * 100.0)

    def to_index(self, val: float) -> int:
        return max(0, min(self.gridsize - 1, int(val) - self.mincoord))

    def update_coverage_area(self, currpos: Tuple[float, float, float]):
        x1, y1 = int(self.lastpos[0]), int(self.lastpos[1])
        x2, y2, z = int(currpos[0]), int(currpos[1]), int(currpos[2])
        
        logger.info(f"TRAVEL: ({x1},{y1})→({x2},{y2}) z={z}")

        if z >= 0:
            coverage_grid, heatmap_grid, layer = self.surface_coverage_grid, self.surface_heatmap, "SURFACE"
        else:
            coverage_grid, heatmap_grid, layer = self.underwater_coverage_grid, self.underwater_heatmap, "UNDERWATER"

        newly_covered = 0
        expected_pct = self.get_expected_coverage(max(y1, y2))

        # **CRITICAL FIX: Row fill ONLY for rows 10-109, NEVER y=110**
        if y1 != y2 and y1 < 110:  # Y-CHANGE but NOT final row
            j_fill = self.to_index(y1)
            if not np.all(coverage_grid[j_fill, :] == 1):
                uncovered = np.where(coverage_grid[j_fill, :] == 0)[0]
                row_new = len(uncovered)
                coverage_grid[j_fill, uncovered] = 1
                heatmap_grid[j_fill, uncovered] += 1
                newly_covered += row_new
                self.expected_rows_covered += 1
                logger.info(f"{layer} Y-CHANGE → FILLED row y={y1}(j={j_fill}): +{row_new} cells (+{row_new/100:.2f}%)")

        # **Path marking (X, Y, or diagonal)**
        if y1 == y2 and x1 != x2:  # Pure X-MOVE
            j = self.to_index(y1)
            step = 1 if x2 > x1 else -1
            for x in range(x1, x2 + step, step):
                i = self.to_index(x)
                if coverage_grid[j, i] == 0:
                    coverage_grid[j, i] = 1
                    newly_covered += 1
                heatmap_grid[j, i] += 1
            logger.info(f"➡️  {layer} X-MOVE row{y1}(j={j}): {abs(x2-x1)} cells traversed")
            
        elif x1 == x2 and y1 != y2:  # Pure Y-MOVE
            i = self.to_index(x1)
            step = 1 if y2 > y1 else -1
            for y in range(y1, y2 + step, step):
                j = self.to_index(y)
                if coverage_grid[j, i] == 0:
                    coverage_grid[j, i] = 1
                    newly_covered += 1
                heatmap_grid[j, i] += 1
            logger.info(f"⬆️  {layer} Y-MOVE col{i}: {abs(y2-y1)} cells")
            
        else:  # DIAGONAL or mixed
            logger.info(f"{layer} MIXED PATH")
            if x1 != x2:  # X path first
                j = self.to_index(y1)
                step_x = 1 if x2 > x1 else -1
                for x in range(x1, x2 + step_x, step_x):
                    i = self.to_index(x)
                    if coverage_grid[j, i] == 0:
                        coverage_grid[j, i] = 1
                        newly_covered += 1
                    heatmap_grid[j, i] += 1
            if y1 != y2:  # Y path
                i = self.to_index(x2)
                step_y = 1 if y2 > y1 else -1
                for y in range(y1, y2 + step_y, step_y):
                    j = self.to_index(y)
                    if coverage_grid[j, i] == 0:
                        coverage_grid[j, i] = 1
                        newly_covered += 1
                    heatmap_grid[j, i] += 1

        self.lastpos = currpos
        
        total_cov = np.count_nonzero(coverage_grid)
        actual_pct = (total_cov / self.total_cells) * 100
        logger.info(f"ACTUAL: {actual_pct:06.4f}% ({total_cov:,}/{self.total_cells:,}) | "
                   f"EXPECTED: {expected_pct:06.2f}% | ROWS: {self.expected_rows_covered}/99 | "  # 99 rows + final row path
                   f"ΔNEW: +{newly_covered}")

    def log_full_status(self):
        s_total = np.count_nonzero(self.surface_coverage_grid)
        s_pct = s_total / self.total_cells * 100
        u_total = np.count_nonzero(self.underwater_coverage_grid)
        u_pct = u_total / self.total_cells * 100
        
        logger.info("="*100)
        logger.info(f"FINAL @ {self.lastpos}")
        logger.info(f"SURFACE: {s_pct:06.4f}% ({s_total:,}/{self.total_cells:,})")
        logger.info(f"EXPECTED: {self.get_expected_coverage(int(self.lastpos[1])):06.2f}%")
        logger.info(f"FILLED ROWS (10-109): {self.expected_rows_covered}/99")
        logger.info(f"FINAL ROW y=110 cells: {np.sum(self.surface_coverage_grid[self.to_index(110), :])}/100")
        logger.info("="*100)

    def get_coverage_percentages(self):
        s_pct = np.count_nonzero(self.surface_coverage_grid) / self.total_cells * 100
        u_pct = np.count_nonzero(self.underwater_coverage_grid) / self.total_cells * 100
        logger.info(f"API: S{s_pct:06.4f}% | ROWS{self.expected_rows_covered}/99 | FINAL_ROW{np.sum(self.surface_coverage_grid[self.to_index(110), :])}/100")

        self.log_full_status()
        return CoverageArea(surface_percentage=round(s_pct, 3), underwater_percentage=round(u_pct, 3))

    def get_surface_heatmap(self):
        maxval = self.surface_heatmap.max()
        return self.surface_heatmap / maxval if maxval > 0 else self.surface_heatmap

    def get_underwater_heatmap(self):
        maxval = self.underwater_heatmap.max()
        return self.underwater_heatmap / maxval if maxval > 0 else self.underwater_heatmap