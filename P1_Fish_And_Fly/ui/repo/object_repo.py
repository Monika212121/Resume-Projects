import os
import pandas as pd
from pathlib import Path



def load_objects(object_log_file_path: Path):

    if not os.path.exists(object_log_file_path):
        return pd.DataFrame(columns=[
            "timestamp",
            "track_id",
            "class_name",
            "age",
            "avg_confidence",
            "priority_score",
            "entity_role",
            "decision_status",
            "decision_reason",
            "final_action_status"
        ])

    try:
        df = pd.read_csv(object_log_file_path)

        if df.empty:
            return df

        df = df.sort_values("timestamp")

        return df

    except Exception as e:
        print("Error loading object log:", e)

        return pd.DataFrame()