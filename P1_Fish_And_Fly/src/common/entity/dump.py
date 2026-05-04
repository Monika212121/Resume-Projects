import time
from enum import Enum
from typing import Optional, List
from dataclasses import dataclass, field

from src.common.entity.position import Waypoint


@dataclass
class DumpPointState:
    dump_id: int
    position: Waypoint  # (x, y, z)
    capacity: float

    current_load: float = 0.0
    last_updated_ts: Optional[float] = field(default_factory=time.time)
    last_serviced_ts: Optional[float] = field(default_factory=time.time)


    # --- Update from Fish ---
    def add_load(self, amount: float) -> None:
        self.current_load = self.current_load if self.current_load else 0.0

        self.current_load = min(self.capacity, self.current_load + amount)
        self.last_updated_ts = time.time()
        return

    # --- After Manatee unload ---
    def clear_load(self) -> None:
        self.current_load = 0.0
        self.last_serviced_ts = time.time()
        return


    # --- Metrics ---
    @property
    def fill_pct(self) -> float:
        self.current_load = self.current_load if self.current_load else 0.0

        return self.current_load / self.capacity if self.capacity else 0.0


    def time_since_service(self) -> float:
        self.last_serviced_ts = self.last_serviced_ts if self.last_serviced_ts else time.time()

        return time.time() - self.last_serviced_ts


    def is_recently_serviced(self, cooldown: float = 60.0) -> bool:
        self.last_serviced_ts = self.last_serviced_ts if self.last_serviced_ts else time.time()

        return (time.time() - self.last_serviced_ts) < cooldown


    def urgency_score(self) -> float:
        """
        Smart but simple heuristic:
        - 70% weight: fill level
        - 30% weight: waiting time (capped)
        """
        time_factor = min(self.time_since_service(), 300.0) / 300.0
        return (self.fill_pct * 0.7) + (time_factor * 0.3)
    
