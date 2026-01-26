# Aim: Testing / debugging, Use till the Pybullet integration is done.

from src.fish.stage3_action.environment.base import EnvironmentModel
from src.fish.stage3_action.entity import Waypoint


class MockEnvironmentModel(EnvironmentModel):
    """
    Deterministic environment for testing and debugging.
    """
    def __init__(self, current: float = 0.0, risk: float = 0.0, uncertainity: float = 0.0):
        self._current = current
        self._risk = risk
        self._uncertainty = uncertainity


    def current_opposition(self, current: Waypoint, target: Waypoint) -> float: 
        return self._current
    

    def obstacle_density(self, target: Waypoint) -> float:
        return self._risk
    

    def localization_uncertainty(self) -> float:
        return self._uncertainty
    
