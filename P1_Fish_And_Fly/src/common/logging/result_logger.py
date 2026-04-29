from src.common.entity.basic_paths import LogFilePaths
from src.common.logging.object_csv_logger import ObjectCSVLogger
from src.common.logging.telemetry_csv_logger import TelemetryCSVLogger



class OutcomeLogger:
    def __init__(self, log_file_paths: LogFilePaths):
        
        # Logs Fish machine's final action result
        self.object_logger = ObjectCSVLogger(reset= True, output_file_path= log_file_paths.mission_object_log)         

        # Logs Fly machine's telemetry result                   
        self.telemetry_logger = TelemetryCSVLogger(reset= True, output_file_path= log_file_paths.mission_telemetry_log)
