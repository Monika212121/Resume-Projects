import time

from src.common.logging import logger
from src.common.entity.position import Waypoint

from src.fly.stage1_controller.entity import FlightControllerConfig, FlightMode



class FlightController:
    def __init__(self, controller_config: FlightControllerConfig):
        self.controller_cfg = controller_config
        self.pose = self.controller_cfg.hover_position                                                                # Pose: x, y, z(hover_height)
                                                                       
        self.mode = FlightMode.IDLE
        self.last_cmd_ts = time.time()

    
    def takeoff(self) -> Waypoint:
        try:
            logger.info(f"FlightController -> takeoff(): STARTS")

            if self.mode != FlightMode.IDLE:
                return self.pose

            self.mode = FlightMode.TAKEOFF

            logger.info(f"FlightController -> takeoff(): ENDS, mode: {self.mode}")
            return self.pose
            

        except Exception as e:
            logger.error(f"Error occurred in FlightController -> takeoff(), error: {e}")
            raise e
    

    def hover(self):
        try:
            logger.info(f"FlightController -> hover(): STARTS")

            self.mode = FlightMode.HOVER

            logger.info(f"FlightController -> hover(): ENDS, mode: {self.mode}")
            return self.pose


        except Exception as e:
            logger.error(f"Error occurred in FlightController -> hover(), error: {e}")
            raise e
    


    def hold_position(self):
        try:
            logger.info(f"FlightController -> hold_position(): STARTS")

            self.mode = FlightMode.HOLD

            logger.info(f"FlightController -> hold_position(): ENDS, mode: {self.mode}")
            return self.pose


        except Exception as e:
            logger.error(f"Error occurred in FlightController -> hold_position(), error: {e}")
            raise e
        

    def return_home(self):
        try:
            logger.info(f"FlightController -> return_home(): STARTS")

            self.mode = FlightMode.RETURN_HOME

            logger.info(f"FlightController -> return_home(): ENDS, mode: {self.mode}")
            return self.pose


        except Exception as e:
            logger.error(f"Error occurred in FlightController -> return_home(), error: {e}")
            raise e
