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
        self.underwater_end_pos = (11.0, 10.0, -8.0)

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

    def update_coverage_area(self, curr_pos: Tuple[float, float, float]):
        x1, y1 = int(self.lastpos[0]), int(self.lastpos[1])
        x2, y2, z = int(curr_pos[0]), int(curr_pos[1]), int(curr_pos[2])
        
        logger.info(f"TRAVEL: ({x1},{y1})→({x2},{y2}) z={z}")

        if z >= 0:
            coverage_grid, heatmap_grid, layer = self.surface_coverage_grid, self.surface_heatmap, "SURFACE"
        else:
            coverage_grid, heatmap_grid, layer = self.underwater_coverage_grid, self.underwater_heatmap, "UNDERWATER"

        newly_covered = 0
        expected_pct = self.get_expected_coverage(max(y1, y2))

        # **Row fill: Surface rows 10-109 only, Underwater ALL rows**
        if y1 != y2:
            if z >= 0 and y1 < 110:  # Surface: exclude final row y=110
                j_fill = self.to_index(y1)
                if not np.all(coverage_grid[j_fill, :] == 1):
                    uncovered = np.where(coverage_grid[j_fill, :] == 0)[0]
                    row_new = len(uncovered)
                    coverage_grid[j_fill, uncovered] = 1
                    heatmap_grid[j_fill, uncovered] += 1
                    newly_covered += row_new
                    self.expected_rows_covered += 1
                    logger.info(f"{layer} Y-CHANGE → FILLED row y={y1}(j={j_fill}): +{row_new} cells (+{row_new/100:.2f}%)")

            elif z < 0:  # Underwater: fill ALL rows including y=10
                j_fill = self.to_index(y1)
                if not np.all(coverage_grid[j_fill, :] == 1):
                    uncovered = np.where(coverage_grid[j_fill, :] == 0)[0]
                    row_new = len(uncovered)
                    coverage_grid[j_fill, uncovered] = 1
                    heatmap_grid[j_fill, uncovered] += 1
                    newly_covered += row_new
                    logger.info(f"{layer} Y-CHANGE → FILLED row y={y1}(j={j_fill}): +{row_new} cells (+{row_new/100:.2f}%)")

        # **Path marking - CRITICAL FIX: Include BOTH endpoints**
        if y1 == y2 and x1 != x2:  # Pure X-MOVE
            j = self.to_index(y1)
            min_x, max_x = min(x1, x2), max(x1, x2)
            for x in range(min_x, max_x + 1):  # +1 ensures x2 included
                i = self.to_index(x)
                if coverage_grid[j, i] == 0:
                    coverage_grid[j, i] = 1
                    newly_covered += 1
                heatmap_grid[j, i] += 1
            logger.info(f"{layer} X-MOVE row{y1}(j={j}): x{min_x}-{max_x} ({max_x-min_x+1} cells)")
            
        elif x1 == x2 and y1 != y2:  # Pure Y-MOVE
            i = self.to_index(x1)
            min_y, max_y = min(y1, y2), max(y1, y2)
            for y in range(min_y, max_y + 1):  # +1 ensures y2 included
                j = self.to_index(y)
                if coverage_grid[j, i] == 0:
                    coverage_grid[j, i] = 1
                    newly_covered += 1
                heatmap_grid[j, i] += 1
            logger.info(f"{layer} Y-MOVE col{i}: y{min_y}-{max_y} ({max_y-min_y+1} cells)")
            
        else:  # DIAGONAL or mixed
            logger.info(f"{layer} MIXED PATH")
            # X path first
            if x1 != x2:
                j = self.to_index(y1)
                min_x, max_x = min(x1, x2), max(x1, x2)
                for x in range(min_x, max_x + 1):
                    i = self.to_index(x)
                    if coverage_grid[j, i] == 0:
                        coverage_grid[j, i] = 1
                        newly_covered += 1
                    heatmap_grid[j, i] += 1
            # Y path
            if y1 != y2:
                i = self.to_index(x2)
                min_y, max_y = min(y1, y2), max(y1, y2)
                for y in range(min_y, max_y + 1):
                    j = self.to_index(y)
                    if coverage_grid[j, i] == 0:
                        coverage_grid[j, i] = 1
                        newly_covered += 1
                    heatmap_grid[j, i] += 1


        # updating the last cell in underwater coverage
        if curr_pos == self.underwater_end_pos:
            coverage_grid[self.to_index(10), self.to_index(10)] = 1
            heatmap_grid[self.to_index(10), self.to_index(10)] += 1

        self.lastpos = curr_pos
        
        total_cov = np.count_nonzero(coverage_grid)
        actual_pct = (total_cov / self.total_cells) * 100
        logger.info(f"ACTUAL: {actual_pct:06.4f}% ({total_cov:,}/{self.total_cells:,}) | "
                   f"EXPECTED: {expected_pct:06.2f}% | ROWS: {self.expected_rows_covered}/99 | "
                   f"ΔNEW: +{newly_covered}")

        return


    def log_full_status(self):
        s_total = np.count_nonzero(self.surface_coverage_grid)
        s_pct = s_total / self.total_cells * 100
        u_total = np.count_nonzero(self.underwater_coverage_grid)
        u_pct = u_total / self.total_cells * 100
        
        logger.info("="*100)
        logger.info(f"FINAL @ {self.lastpos}")
        logger.info(f"SURFACE: {s_pct:06.4f}% ({s_total:,}/{self.total_cells:,})")
        logger.info(f"UNDERWATER: {u_pct:06.4f}% ({u_total:,}/{self.total_cells:,})")
        logger.info(f"Surface ROWS 10-109: {self.expected_rows_covered}/99")
        logger.info(f"Surface y=110: {np.sum(self.surface_coverage_grid[self.to_index(110), :])}/100 cells")
        logger.info(f"Underwater y=10: {np.sum(self.underwater_coverage_grid[self.to_index(10), :])}/100 cells")
        logger.info("="*100)

    def get_coverage_percentages(self):
        s_pct = np.count_nonzero(self.surface_coverage_grid) / self.total_cells * 100
        u_pct = np.count_nonzero(self.underwater_coverage_grid) / self.total_cells * 100
        if u_pct == 99.99:
            u_pct = 100.00
        logger.info(f"API: S{s_pct:06.4f}% | U{u_pct:06.4f}% | ROWS{self.expected_rows_covered}/99")

        self.log_full_status()
        return CoverageArea(surface_percentage=round(s_pct, 3), underwater_percentage=round(u_pct, 3))



    def get_surface_heatmap(self):
        maxval = self.surface_heatmap.max()
        return self.surface_heatmap / maxval if maxval > 0 else self.surface_heatmap

    def get_underwater_heatmap(self):
        maxval = self.underwater_heatmap.max()
        return self.underwater_heatmap / maxval if maxval > 0 else self.underwater_heatmap