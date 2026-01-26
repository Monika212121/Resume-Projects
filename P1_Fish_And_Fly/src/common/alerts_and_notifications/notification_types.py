from enum import Enum

class NotificationType(Enum):
    MISSION_STARTED = "mission_started"
    WORKSPACE_DETECTED = "worspace_detected"
    DUMP_POINTS_SELECTED = "dump_points_selected"
    GARBAGE_UNLOADING_STARTED = "garbage_unloading_started"
    GARBAGE_UNLOADING_ENDED = "garbage_unloading_ended"
    MISSION_COMPLETED = "mission_completed"
    
    SURFACE_CLEANING_ENDED = "surface_cleaning_ended"
    MACHINE_DESCENDED = "machine_descended"
    UNDERWATER_CLEANING_ENDED = "underwater_cleaning_ended"
    MACHINE_ASCENDED = "machine_ascended"
    REACHED_HEADQUARTER = "reached_HQ"

    