from typing import Set

from src.common.logging import logger
from src.common.logging.garbage_csv_logger import GarbageCSVLogger, GarbageLogEntry

from src.fish.stage2_decision.entity import ActionIntent
from src.fish.stage3_action.entity import ActionFeedback



class OutcomeLogger:
    def __init__(self):
        self.garbage_logger = GarbageCSVLogger()
        self.logged_ids: Set[int] = set()                                               # list of track_ids of objects already logged. 



    def log_action_results(self, action_intent: ActionIntent, feedback: ActionFeedback):
        """
        Logs the results from the Action module.
        
        :param self: Belongs to the MonitorAction class.
        :param action_intent: ActionIntent recieved from Decision module to execute action.
        :type action_intent: ActionIntent
        :param feedback: Action feedback passes back to Decision module after executing action.
        :type feedback: ActionFeedback
        """
        try:
            logger.info(f"OutcomeLogger -> log_action_results(): STARTS")

            # Checking through a ONE TIME LOGGING  GUARD.                               # refer ACTION_NOTES.md (3) 
            if (action_intent.track_id in self.logged_ids) or (action_intent.track_id is None):
                return          # skip logging                                                        


            # Creating a new entry.
            new_entry = GarbageLogEntry(
                track_id= action_intent.track_id,
                class_name = action_intent.class_name,
                first_seen_frame= 1,
                last_seen_frame= 10,
                final_state= feedback.status.value,
                lifecycle_state= feedback.status.value,
                age = 100,
                avg_confidence= 1.5,
                priority_score = action_intent.priority_score
            )

            # Logging into the .csv file.
            self.garbage_logger.log(new_entry)                  

            # Updating the logged_ids list with the new entry.
            self.logged_ids.add(action_intent.track_id)
            
            logger.info(f"OutcomeLogger -> create_action_results(): ENDS")
            return 
        
        
        except Exception as e:
            logger.error(f"Error occured in OutcomeLogger -> create_action_results(), error e: {e}")
            raise e
