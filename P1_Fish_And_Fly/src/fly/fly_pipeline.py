# Aim: This is Fly machine entry-point

from src.common.logging import logger
from src.common.entity.heartbeat import SystemHeartbeat
from src.common.logging.result_logger import OutcomeLogger
from src.common.config.configuration import ConfigurationManager
from src.common.alerts_and_notifications.notifier import AlertNotifier, AlertType

from src.fly.stage1_action.entity import FishStatus
from src.fly.stage1_action.flight_controller import FlightController
from src.fly.stage1_action.heartbeat_monitor import HeartbeatMonitor
from src.fly.stage1_action.fish_tracker import LawnMowerCoverageTracker



class FlyPipeline:
    def __init__(self, fly_cfg_mg: ConfigurationManager):

        # Loading the Fly's configurations
        self.log_file_paths = fly_cfg_mg.get_log_file_paths()
        self.controller_config = fly_cfg_mg.get_controller_config()
        self.monitor_config = fly_cfg_mg.get_monitor_config()

        # Instantiating the Fly's pipelines
        self.flight = FlightController(self.controller_config)
        self.monitor = HeartbeatMonitor(self.monitor_config)                                                   

        self.notifier = AlertNotifier()
        self.result_logger = OutcomeLogger(log_file_paths= self.log_file_paths)
        self.coverage_tracker = LawnMowerCoverageTracker()



    def initiate(self):
        try:
            logger.info(f"FlyPipeline -> initiate(): STARTS")

            # Takeoff + Hover
            self.flight.takeoff()
            self.flight.hover()

            logger.info(f"FlyPipeline -> initiate(): ENDS, Fly machine Hovering and Monitoring Fish")
            return


        except Exception as e:
            logger.info(f"Error occurred in FlyPipeline -> initiate(), error: {e}")
            raise e


    def terminate(self):
        try:
            logger.info(f"FlyPipeline -> terminate(): STARTS")

            # Land the machine to the HQ
            self.flight.return_home()

            logger.info(f"FlyPipeline -> terminate(): ENDS")
            return
        

        except Exception as e:
            logger.info(f"Error occurred in FlyPipeline -> terminate(), error: {e}")
            raise e
    


    def tick(self, heartbeat: SystemHeartbeat) -> None:
        try:
            logger.info("*********************************************FLY MODULE SYSTEM: STARTS********************************************")

            # Updating Fish machine's coverage area for current position and operation depth
            self.coverage_tracker.update_coverage_area((heartbeat.position.x, heartbeat.position.y, heartbeat.position.z))

            # Retrieving Fish machine's coverage area percentages
            coverage_area_percentages = self.coverage_tracker.get_coverage_percentages()

            # Calculating Fish machine's state deltas
            state_deltas = self.monitor.calculate_fish_state_deltas(heartbeat = heartbeat, coverage_area_pcts = coverage_area_percentages)

            # Raising alert according to the Fish's state deltas, calculated above                                                                           
            if state_deltas.fish_state != FishStatus.ALIVE.name:
                self.notifier.raise_alert(AlertType.MACHINE_LOST, "Fish heartbeat lost", metadata= {})

                # Return the Fly machine to HQ
                self.flight.return_home()


            elif state_deltas.fish_state == FishStatus.FROZEN.name:
                self.notifier.raise_alert(AlertType.MACHINE_STUCK,"Fish execution frozen", metadata={})

                # Hold Fly machine at the hover height
                self.flight.hold_position()


            elif state_deltas.fish_state == FishStatus.LAGGING.name:
                self.notifier.raise_alert(AlertType.MACHINE_LAGGING, "Fish responding slowly", metadata={})

                # Hover the Fly machine
                self.flight.hover()


            # Logging the fish machine's health and state deltas w.r.t. Fly machine, in `state_delta.csv` file.
            self.result_logger.telemetry_logger.log_fish_machine_telemetry(delta= state_deltas)
            logger.info("*********************************************FLY MODULE SYSTEM: ENDS********************************************")
            return
        

        except Exception as e:
            logger.info(f"Error occurred in FlyPipeline -> tick(), error: {e}")
            raise e