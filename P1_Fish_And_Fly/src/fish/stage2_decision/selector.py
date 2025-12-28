# NOTE: This is pure decision memory, not vision memory.
from typing import Optional, List, Tuple
from src.common.logging import logger
from src.fish.stage2_decision.command import LifeCycleCommand, LifeCycleAction
from src.fish.stage3_action.entity import ActionFeedback, ActionStatus
from src.fish.stage1_vision.entity import TrackedGarbage


class SelectionLock:
    """
    Maintains a single active target lock.
    Responsible Only for selection and release.
    """
    def __init__(self):
        self.active_track_id : Optional[int] = None


    def select_target(self, ranked_objects: List[Tuple[Optional[TrackedGarbage], float]]) -> Optional[LifeCycleCommand]:
        """
        Selects highest priority object if no active lock exists.
        
        :param self: Belongs to the SelectionLock class.
        :param ranked_objects: List of tracked objects, sorted w.r.t priority score.
        :return: Command to make Lifecycle state transitions (state -> SELECTED) in Vision Aggregator.
        :rtype: LifeCycleCommand | None
        """
        logger.info(f"SelectionLock -> select_target(): STARTS, ranked objects: {len(ranked_objects)}")

        # If target is already locked, do nothing
        if self.active_track_id is not None:
            logger.info(f"An object is already locked of track_id: {self.active_track_id}")
            return None
        
        # if no tracked stable objects
        if not ranked_objects:
            logger.info("No stable candidates present now")
            return None

        # Selecting highest priority object
        selected_object, _ = ranked_objects[0]
        self.active_track_id = selected_object.track_id

        logger.info(f"Selecting object of track_id: {selected_object.track_id}")

        command = LifeCycleCommand(
            action = LifeCycleAction.SELECT,
            track_id = self.active_track_id
        )

        logger.info(f"SelectionLock -> select_target(): ENDS, command: {command}")
        return command
    

    def release_target(self) -> None:
        """
        Releases the currently locked target.
        
        :param self: Belongs to the SelectionLock class.
        """
        logger.info(f"SelectorLock -> release(): releasing track_id = {self.active_track_id}")
        self.active_track_id = None
        return


    def get_locked_target(self) -> Optional[int]:
        """
        Provides the locked object's id.
        
        :param self: Belongs to the SelectionLock class.
        """
        return self.active_track_id




    def handle_action_feedback(self, feedback: ActionFeedback) -> Optional[LifeCycleCommand]:
        """
        Converts Action feedback into lifecycle command.

        Receives Action feedback from Action and converts into lifecycle command to pass to the Vision aggregation to update the lifecycle status of the locked object (DONE/LOST).
        
        :param self: Belongs to the SelectionLock class.
        :param feedback: Action feedback from the Action module.
        :type feedback: ActionFeedback
        :return: Life cycle comamnd for the Vision module.
        :rtype: LifeCycleCommand
        """
        logger.info(f"handle_action_feetback(): STARTS, feedback status: {feedback.status}")

        locked_target_id = self.active_track_id

        if locked_target_id != feedback.track_id:
            logger.info(f"Received object is not locked. locked object id: {locked_target_id}, feedback object id: {feedback.track_id}")
            return None
        
        # Creating lifcycle command for the locked object to pass to Vision aggregation.
        # Case1: When locked object is collected successfully.
        if feedback.status == ActionStatus.SUCCESS:
            command = LifeCycleCommand(
                action = LifeCycleAction.MARK_DONE,
                track_id = feedback.track_id
            )
        
        # Case2: When locked object is not collected(LOST).
        else:
            command = LifeCycleCommand(
                action = LifeCycleAction.LOST,
                track_id = feedback.track_id
            )

        # Releasing lock after command creation
        self.release_target()

        logger.info(f"BOTH MUST BE SAME: released id: {locked_target_id}, TO VERIFY: {self.active_track_id}")

        logger.info(f"handle_action_feetback(): ENDS, command: {command}")
        return command
        

