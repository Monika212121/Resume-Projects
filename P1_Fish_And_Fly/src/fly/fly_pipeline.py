# Aim: This is Fly machine entry-point

from src.common.logging import logger
from src.common.entity.heartbeat import SystemHeartbeat
from src.common.logging.result_logger import OutcomeLogger
from src.common.config.configuration import ConfigurationManager
from src.common.alerts_and_notifications.notifier import AlertNotifier, AlertType

from src.fly.stage2_action.entity import FishStatus
from src.fly.stage2_action.flight_controller import FlightController
from src.fly.stage2_action.heartbeat_monitor import HeartbeatMonitor



class FlyPipeline:
    def __init__(self, fly_cfg_mg: ConfigurationManager):

        # Loading the Fly's configurations
        #self.vision_config = fly_cfg_mg.get_vision_config()

        self.controller_config = fly_cfg_mg.get_controller_config()
        self.monitor_config = fly_cfg_mg.get_monitor_config()

        # Instantiating the Fly's pipelines
        self.flight = FlightController(self.controller_config)
        self.monitor = HeartbeatMonitor(self.monitor_config)                                                   

        self.notifier = AlertNotifier()
        self.state_delta_logger = OutcomeLogger()



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

            # Monitoring of Fish machine
            fish_health = self.monitor.calculate_fish_state_deltas(heartbeat = heartbeat)
            
            # Raising alert according to the Fish's state deltas, calculated above                                                                           
            if not fish_health.alive:
                self.notifier.raise_alert(AlertType.MACHINE_LOST, "Fish heartbeat lost", metadata= {})

                # Return the Fly machine to HQ
                self.flight.return_home()


            elif fish_health.status == FishStatus.FROZEN:
                self.notifier.raise_alert(AlertType.MACHINE_STUCK,"Fish execution frozen", metadata={})

                # Hold Fly machine at the hover height
                self.flight.hold_position()


            elif fish_health.status == FishStatus.LAGGING:
                self.notifier.raise_alert(AlertType.MACHINE_LAGGING, "Fish responding slowly", metadata={})

                # Hover the Fly machine
                self.flight.hover()


            # Logging the fish machine's health and state deltas w.r.t. Fly machine, in `state_delta.csv` file.
            self.state_delta_logger.log_fly_state_delta(delta= fish_health)
            logger.info("*********************************************FLY MODULE SYSTEM: ENDS********************************************")
            return
        

        except Exception as e:
            logger.info(f"Error occurred in FlyPipeline -> tick(), error: {e}")
            raise e
