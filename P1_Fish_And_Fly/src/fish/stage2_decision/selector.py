# NOTE: This is pure decision memory, not vision memory.
from typing import Optional, List, Tuple

from src.common.logging import logger

from src.fish.stage1_vision.entity import TrackedGarbage
from src.fish.stage2_decision.command import LifeCycleCommand, LifeCycleAction
from src.fish.stage3_action.entity import ActionFeedback, ActionStatus



class SelectionLock:
    """
    Maintains a single active target lock.
    Responsible Only for selection and release.
    """
    def __init__(self):
        self.active_track_id : Optional[int] = None
        self.selection_counter = 1


    def select_target(self, ranked_objects: List[Tuple[Optional[TrackedGarbage], float]]) -> Optional[LifeCycleCommand]:
        """
        Selects highest priority object if no active lock exists.
        
        :param self: Belongs to the SelectionLock class.
        :param ranked_objects: List of tracked objects, sorted w.r.t priority score.
        :return: Command to make Lifecycle state transitions (state -> SELECTED) in Vision Aggregator.
        :rtype: LifeCycleCommand | None
        """
        logger.info(f"SelectionLock -> select_target(): STARTS, ranked objects: {len(ranked_objects)}")
        
        # 1. If there is no tracked stable objects in frame.
        if len(ranked_objects) == 0:
            logger.info("No stable candidates present now")
            return None

        # 2. Selecting highest priority object.
        selected_object, _ = ranked_objects[0]
        if selected_object is None:
            return None
        
        # 3. Creating the selection command, locking the suitable target

        # Case1: OLD TARGET: If a target is already locked
        if self.active_track_id:

            # CaseA: If the locked target is still present in current frame, then reselect it again 
            if self.active_track_id == selected_object.track_id:
                self.selection_counter += 1                                                                 # give another chance for its collection                                                  
                command = LifeCycleCommand(                                     
                    action = LifeCycleAction.SELECT,
                    track_id = self.active_track_id,
                    selection_count= self.selection_counter
                )

            # CaseB: If the locked target is not present, in current frame anymore, then mark it as LOST and release it
            else:
                command = LifeCycleCommand(                                     
                    action = LifeCycleAction.LOST,
                    track_id = self.active_track_id,
                    selection_count= self.selection_counter
                )

                # Release the locked target, as it is LOST
                self.active_track_id = None


        # Case2: NEW TARGET: If no target is locked at present
        else:
            # Locking the highest priority object as target
            self.active_track_id = selected_object.track_id
            self.selection_counter = 1

            # New command generation.
            command = LifeCycleCommand(                                     
                action = LifeCycleAction.SELECT,
                track_id = self.active_track_id,
                selection_count= self.selection_counter
            )

        logger.info(f"SelectionLock -> select_target(): ENDS, SELECT COMMAND: {command}")
        return command
    

    def release_target(self) -> None:
        """
        Releases the currently locked target.
        
        :param self: Belongs to the SelectionLock class.
        """
        logger.info(f"SelectorLock -> release(): STARTS, before releasing track_id = {self.active_track_id}")

        self.active_track_id = None                                                                         # triggered only when action_feedback status = SUCCESS / FAILED

        logger.info(f"SelectorLock -> release(): ENDS, after releasing track_id = {self.active_track_id}")
        return


    def get_locked_target(self) -> Optional[int]:
        """
        Provides the locked object's id.
        
        :param self: Belongs to the SelectionLock class.
        """
        return self.active_track_id



    def handle_action_feedback(self, feedback: ActionFeedback) -> Optional[LifeCycleCommand]:
        """
        Converts Action feedback into Lifecycle command.

        Receives Action feedback from Action pipeline (status = SUCESS / FAILED / MOVED_FORWARD / NONE).
        
        Passes Lifecycle command to the Vision pipeline(aggregation) to update the target's lifecycle status (MARK_DONE / FAILED / LOST).
        
        :param self: Belongs to the SelectionLock class.
        :param feedback: Action feedback from the Action module.
        :type feedback: ActionFeedback
        :return: Life cycle command for the Vision module (status = MARK_DONE / FAILED / UNATTEMPTED)
        :rtype: LifeCycleCommand | None
        """
        logger.info(f"handle_action_feedback(): STARTS, feedback status: {feedback.status}")

        locked_target_id = self.active_track_id

        # If selector locked_id and feedback track_id is mismatched.
        if locked_target_id != feedback.track_id:
            logger.info(f"Received object is not locked. locked object id: {locked_target_id}, feedback object id: {feedback.track_id}")
            return None
        
        # Creating Lifcycle command for the locked object to pass to Vision aggregation.

        # Case1: TARGET ATTEMPTED: When locked object is collected (SUCCESS).
        if feedback.status == ActionStatus.COLLECTED:
            command = LifeCycleCommand(
                action = LifeCycleAction.MARK_DONE,
                track_id = feedback.track_id,
                selection_count= self.selection_counter
            )
        
        # Case2: TARGET ATTEMPTED: When locked object is not collected (FAILED).
        elif feedback.status == ActionStatus.FAILED:
            command = LifeCycleCommand(
                action = LifeCycleAction.FAILED,
                track_id = feedback.track_id,
                selection_count= self.selection_counter
            )
        
        # Case3: TARGET UNATTEMPTED: When objects are tracked at a far location (MOVED_FORWARD / NONE).           
        else:
            command = LifeCycleCommand(
                action = LifeCycleAction.UNATTEMPTED,
                track_id = feedback.track_id,
                selection_count= self.selection_counter
            )
            logger.info(f"The locked target is far from Fish machine and hence UNATTEMPTED.")


        # Releasing lock after command creation.
        self.release_target()

        logger.info(f"handle_action_feedback(): ENDS, command: {command}")
        return command
    
