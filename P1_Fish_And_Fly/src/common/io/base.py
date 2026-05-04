# AIM: Abstract interface (CORE ABSTRACTION)

from abc import ABC, abstractmethod

class VisionInput(ABC):
    """
    Abstract base class for all vision input sources
    """

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def read(self):
        """
        Returns:
            frame (np.ndarray) or None if stream ended    

        """
        pass

    @abstractmethod
    def stop(self):
        pass