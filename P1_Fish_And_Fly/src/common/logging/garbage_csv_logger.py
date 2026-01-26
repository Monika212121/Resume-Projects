import os
import csv
from datetime import datetime, timezone

from src.common.logging import logger
from src.common.logging.entity import GarbageLogEntry


class GarbageCSVLogger:
    """
    Persistent garbage CSV for garbage lifecycle outcomes.
    """
    def __init__(self):                         # add output_dir and file_path as parameters
        output_dir = "artifacts/logs"           # later pass in config 
        file_path = "garbage_log.csv"
        os.makedirs(output_dir, exist_ok= True)
        self.file_path = os.path.join(output_dir, file_path)

        self._init_csv()        # call to create a new csv file


    def _init_csv(self):
        """
        Creates a new csv file with the mentioned column names.
        
        :param self: Belongs to GarbageCSVLogger class.
        
        """
        if not os.path.exists(self.file_path):
            with open(self.file_path, mode = "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp",
                    "track_id",
                    "class_name",
                    "final_state",
                    "lifecycle_state",
                    "priority_score",
                    "first_seen_frame",
                    "selected_at",
                    "completed_at",
                    "age",
                    "avg_confidence",
                    "failure_reason",
                    "ignore_reason"
                ])


    def log(self, new_entry: GarbageLogEntry):
        """
        Logs the attended/actioned item into the csv file.
        
        :param self: Belong to the GarbageCSVLogger class.
        """
        try:
            with open(self.file_path, mode= "a", newline= "") as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now(timezone.utc).isoformat(),
                    new_entry.track_id,
                    new_entry.class_name,
                    new_entry.final_state,
                    new_entry.lifecycle_state,
                    new_entry.priority_score,
                    new_entry.first_seen_frame,
                    new_entry.selected_at,
                    new_entry.completed_at,
                    new_entry.age,
                    new_entry.avg_confidence,
                    new_entry.failure_reason,
                    new_entry.ignore_rason
                ])

            logger.info(f"GarbageCSVLogger -> log(), Recorded successfully: {new_entry.track_id}")   


        except Exception as e:
            logger.info(f"GarbageCSVLogger -> log(), Error occurred for new entry: {new_entry}, received error: {e}")
            raise e
