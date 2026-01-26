# Aim: PyBullet-backed implementation

import numpy as np
from typing import List
from src.fish.stage3_action.entity import Waypoint
from src.fish.stage3_action.environment.base import EnvironmentModel


class PyBulletEnvironmentModel(EnvironmentModel):
    """
    Environment model backed by PyBullet simulation.

    This file is the ONLY place where PyBullet logic lives.
    """

    def __init__(self, current_field, obstacle_map, localization_estimator):
        self.current_field = current_field
        self.obstacle_map = obstacle_map
        self.localization_estimator = localization_estimator


    def current_opposition(self, current: Waypoint, target: Waypoint) -> float:
        path_vec = np.array([target.x - current.x, target.y - current.y])
        norm = np.linalg.norm(path_vec) + 1e-6
        direction = path_vec / norm
        current_vec = self.current_field(current.x, current.y, current.z)
        opposition = float(np.dot(current_vec[:2], direction))
        return max(0.0, opposition)
    
    
    def obstacle_density(self, target: Waypoint) -> float:
        density = float(self.obstacle_map.local_density(target.x, target.y, target.z))
        return density
    

    def localization_uncertainty(self) -> float:
        uncertainty = float(self.localization_estimator.position_uncertainty())
        return uncertainty