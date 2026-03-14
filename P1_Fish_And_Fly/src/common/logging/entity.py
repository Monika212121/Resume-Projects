from dataclasses import dataclass



@dataclass
class GarbageLogEntry:
    track_id: int
    class_name: str
    age: int
    avg_confidence: float
    priority_score: float
    entity_role: str                                        # target / enviornment / hazard
    decision_status: str
    decision_reason: str
    final_action_status: str                                # collected / lost / ignored / failed  
