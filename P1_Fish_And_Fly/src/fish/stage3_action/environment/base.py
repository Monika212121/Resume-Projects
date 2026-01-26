# Aim: Environment interface (ABC)

from abc import ABC, abstractmethod
from src.fish.stage3_action.entity import Waypoint


class EnvironmentModel(ABC):
    """
    Query-only abstraction of the environment.

    Used by:
    - cost_models
    - mission_planner
    - navigation

    Must be deterministic and fast.
    """
    @abstractmethod
    def current_opposition(self, current: Waypoint, target: Waypoint) -> float:
        """
        Returns scalar opposing current magnitude
        along path from current -> target.
        """   
        pass

    @abstractmethod
    def obstacle_density(self, target: Waypoint) -> float:
        """
        Returns collision / obstacle risk near target.
        """
        pass  

    @abstractmethod 
    def localization_uncertainty(self) -> float:
        """
        Returns current localization uncertainty.
        """
        pass   