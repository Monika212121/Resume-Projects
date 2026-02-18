import pandas as pd
from pathlib import Path

class LogRepository:
    def __init__(self, log_path: str):
        self.log_path = Path(log_path)

    def load(self) -> pd.DataFrame:
        if not self.log_path.exists():
            return pd.DataFrame()

        try:
            return pd.read_csv(self.log_path)
        except Exception as e:
            print(f"[LogRepository] Failed to read log: {e}")
            return pd.DataFrame()
