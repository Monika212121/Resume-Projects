from enum import Enum

class AlertType(Enum):
    BIN_FULL = "bin_full"
    HQ_RETURN_FAIL = "hq_return_failed"
    SURFACE_CLEANUP_FAIL = "surface_cleanup_fail"
    UNDERWATER_CLEANUP_FAIL = "underwater_cleanup_fail"
    DESCEND_FAIL = "descending fail"
    ASCEND_FAIL = "ascending fail"
    UNLOADING_FAIL = "unloading_fail"
    MACHINE_LOST = "machine_lost"
    MACHINE_FAILURE = "machine_failure"
    MACHINE_DAMAGE = "machine_damage"
    HARD_ABORT = "hard_abort"
    MACHINE_STUCK = "machine_frozen"
    MACHINE_LAGGING = "machine_lagging"
    #OBSTACLE_ALERT = "obstacle_alert"
    #THREAT_DETECTED = "threat_detected"


class ErrorType(Enum):
    EXECUTION_ERROR = "execution_error"
    TIMEOUT_ERROR = "timeout_error"
    TECHNICAL_ERROR = "technical_error"