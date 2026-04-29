from pathlib import Path
from dataclasses import dataclass



@dataclass
class LogFilePaths:
    mission_object_log: Path
    mission_telemetry_log: Path


@dataclass
class RecordInfo:
   record_path: Path
   fps: int

@dataclass
class VideoWriterConfig:
  perception: RecordInfo
  simulation: RecordInfo
