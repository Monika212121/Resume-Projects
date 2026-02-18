from typing import Set, Optional

from src.common.logging import logger
from src.common.logging.state_delta_csv_logger import StateDeltaCSVLogger
from src.common.logging.garbage_csv_logger import GarbageCSVLogger, GarbageLogEntry

from src.fish.stage2_decision.entity import ActionIntent
from src.fish.stage3_action.entity import ActionFeedback, ActionStatus

from src.fly.stage2_action.entity import StateDeltas


class OutcomeLogger:
    def __init__(self):
        self.garbage_logger = GarbageCSVLogger(reset= True)                                                            # logs Fish result
        self.state_delta_logger = StateDeltaCSVLogger(reset= True)                                                     # logs Fly result

        self.logged_ids: Set[int] = set()                                                                   # list of track_ids of objects already logged. 
        self.counter: int = 0           # REMOVE LATER



    def log_action_results(self, action_intent: ActionIntent, feedback: Optional[ActionFeedback]):
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

            # 1. Checking through a ONE TIME LOGGING GUARD, if so, skip logging.                               # refer ACTION_NOTES.md (3) 
            if (action_intent.track_id in self.logged_ids) or (action_intent.track_id is None):
                return                                                                                                                                              

            # NOTE: When object is LOST, it wouldn't pass to the fish_pipeline(only ACTIVE objects will be passed in fish pipeline), 
            # So I am logging LOST objects in `aggregator.py` file, and hence no feedback will be produced for them.
            # 2. Determining the target object's final status, according to the feedback received.
            final_state: ActionStatus

            if feedback is None:         
                final_state = ActionStatus.LOST
            else:
                final_state = feedback.status

            # TODO: REMOVE LATER
            class_name = "organic"
            if self.counter%2 == 0:
                class_name = "plastic"
            elif self.counter%3 == 0:
                class_name = "metal"
            else:
                class_name = "cloth"
              
            # 3. Creating a new entry.
            new_entry = GarbageLogEntry(
                track_id= action_intent.track_id,
                class_name = class_name,
                first_seen_frame= 1,
                last_seen_frame= 10,
                final_state= final_state.name,
                age = 100,
                avg_confidence= 0.80,
                priority_score = action_intent.priority_score
            )

            # 4. Logging into the `garbage.csv` file.
            self.garbage_logger.log(new_entry)                  

            # 5. Updating the logged_ids list with the new entry.
            self.logged_ids.add(action_intent.track_id)
            
            logger.info(f"OutcomeLogger -> create_action_results(): ENDS")
            self.counter += 1               # remove later
            return 
        
        
        except Exception as e:
            logger.error(f"Error occured in OutcomeLogger -> create_action_results(), error e: {e}")
            raise e



    def log_fly_state_delta(self, delta: StateDeltas):
        """
        Logs Fly machine monitoring data.
        """
        try:
            self.state_delta_logger.log(delta)


        except Exception as e:
            logger.error(f"Error occurred in OutcomeLogger -> log_fly_state_delta(): error: {e}")
            raise e
