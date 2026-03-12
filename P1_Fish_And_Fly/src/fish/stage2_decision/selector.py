# NOTE: This is pure decision memory, not vision memory.

from typing import Optional, List, Tuple

from src.common.logging import logger
from src.common.projection.entity import FishFrameObject

from src.fish.stage2_decision.entity import LifeCycleCommand, LifeCycleAction

from src.fish.stage3_action.entity import ActionFeedback, ActionStatus



class SelectionLock:
    """
    Maintains a single active target lock.
    Responsible Only for selection and release.
    """
    def __init__(self):
        self.active_track_id : Optional[int] = None
        self.selection_counter = 1
        self.last_priority_score = 0.0



    def select_target(self, safe_target_objects: List[FishFrameObject]) -> Tuple[List[LifeCycleCommand], Optional[FishFrameObject]]:
        """
        Responsible for target locking and lifecycle management.

        Emits lifecycle commands:
        - SELECT  : target is selected or re-selected
        - LOST    : previously locked target disappeared
        """
        try:
            logger.info(f"SelectionLock -> select_target(): STARTS, ranked objects: {safe_target_objects}, active_track_id: {self.active_track_id}")

            selection_commands: List[LifeCycleCommand] = []

            if len(safe_target_objects) == 0:
                logger.info("No safe ranked objects are present")
                return selection_commands, None

            # Selecting highest priority safe object
            highest_priority_target = safe_target_objects[0]

            # Creating the selection commands, releasing lost target(if any) and locking suitable target

            # Case1: OLD TARGET: If a target is already locked
            if self.active_track_id:

                # CaseA: If the locked target is still present in current frame, then reselect it again 
                if self.active_track_id == highest_priority_target.track_id:                                # Locked target still highest priority
                    self.selection_counter += 1                                                             # give another chance for its collection                                                  
                    selection_command = LifeCycleCommand(                                     
                        action = LifeCycleAction.SELECT,
                        track_id = self.active_track_id,
                        selection_count = self.selection_counter,
                        priority_score = highest_priority_target.priority_score
                    )
                    selection_commands.append(selection_command)

                # CaseB: If the locked target is not present, in current frame anymore, then mark it as LOST and release it
                else:
                    lost_command = LifeCycleCommand(                                     
                        action = LifeCycleAction.LOST,
                        track_id = self.active_track_id,
                        selection_count = self.selection_counter,
                        priority_score = self.last_priority_score
                    )
                    selection_commands.append(lost_command)

                    # Release the previously locked target, in LOST case
                    self.release_target()

                    # Lock new target
                    self.active_track_id = highest_priority_target.track_id
                    selection_command = LifeCycleCommand(                                     
                        action = LifeCycleAction.SELECT,
                        track_id = self.active_track_id,
                        selection_count = self.selection_counter,                                           # already reset to 1 during release of last target 
                        priority_score = highest_priority_target.priority_score
                    )
                    selection_commands.append(selection_command)


            # Case2: NEW TARGET: If no target is locked at present
            else:
                # Locking the highest priority object as target
                self.active_track_id = highest_priority_target.track_id
                selection_command = LifeCycleCommand(                                     
                    action = LifeCycleAction.SELECT,
                    track_id = self.active_track_id,
                    selection_count = self.selection_counter,                                                # already reset to 1 during release of last target
                    priority_score = highest_priority_target.priority_score
                )
                selection_commands.append(selection_command)
                
                self.last_priority_score = highest_priority_target.priority_score                           # maintaining last priority_score for logging LOST object


            logger.info(f"SelectionLock -> select_target(): ENDS, SELECTION COMMANDS: {selection_commands}, selected_obj: {highest_priority_target}")
            return selection_commands, highest_priority_target


        except Exception as e:
            logger.info(f"Error occurred in SelectionLock -> select_target(), error: {e}")
            raise e



    def release_target(self) -> None:
        """
        Releases the currently locked target.
        
        :param self: Belongs to the SelectionLock class.
        """
        try:
            logger.info(f"SelectionLock -> release_target(): STARTS, before releasing track_id = {self.active_track_id}")

            # NOTE: Release will be triggered, when action_feedback
            # status = SUCCESS / FAILED / LOST, not when status = SELECT / UNATTEMPTED
            self.active_track_id = None

            # Reset selection counter  
            self.selection_counter = 1                

            logger.info(f"SelectionLock -> release_target(): ENDS, after releasing track_id = {self.active_track_id}")
            return


        except Exception as e:
            logger.info(f"Error occurred in SelectionLock -> release_target(), error: {e}")
            raise e     



    def handle_action_feedback(self, feedback: ActionFeedback) -> LifeCycleCommand:
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
        try: 
            logger.info(f"SelectionLock -> handle_action_feedback(): STARTS, feedback status: {feedback.status}")
          
            # Creating Lifcycle command for the locked object, to pass back to Vision aggregation.

            # Case1: TARGET ATTEMPTED: When locked object is collected (SUCCESS).
            if feedback.status == ActionStatus.COLLECTED:
                feedback_command = LifeCycleCommand(
                    action = LifeCycleAction.DONE,
                    track_id = feedback.track_id,
                    selection_count= self.selection_counter,
                    priority_score = 0.0                                                                    # After action is taken on a target, its priority_score becomes 0
                )
            
            # Case2: TARGET ATTEMPTED: When locked object is not collected (FAILED).
            elif feedback.status == ActionStatus.FAILED:
                feedback_command = LifeCycleCommand(
                    action = LifeCycleAction.FAILED,
                    track_id = feedback.track_id,
                    selection_count= self.selection_counter,
                    priority_score = 0.0
                )
            
            # Case3: TARGET UNATTEMPTED: When objects are tracked at a far location (MOVED_FORWARD / NONE).           
            else:
                feedback_command = LifeCycleCommand(
                    action = LifeCycleAction.UNATTEMPTED,
                    track_id = feedback.track_id,
                    selection_count= self.selection_counter,
                    priority_score = 0.0
                )
                logger.info(f"SelectionLock -> handle_action_feedback(), The locked target is far from Fish machine and hence UNATTEMPTED.")


            # Releasing lock after command creation.
            if feedback.status in [ActionStatus.COLLECTED, ActionStatus.FAILED]:
                self.release_target()

            logger.info(f"SelectionLock -> handle_action_feedback(): ENDS, feedback command: {feedback_command}")
            return feedback_command


        except Exception as e:
            logger.info(f"Error occurred in SelectionLock -> handle_action_feedback(), error: {e}")
            raise e