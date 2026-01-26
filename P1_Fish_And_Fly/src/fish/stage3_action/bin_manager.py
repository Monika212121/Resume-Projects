from src.common.logging import logger
from src.common.alerts_and_notifications.notifier import AlertNotifier
from src.common.alerts_and_notifications.alert_types import AlertType

from src.fish.stage3_action.entity import Bin, Waypoint



class BinManager:
    """
    Manages the bin operations.
    """
    def __init__(self, bin_cfg: Bin):
        self.capacity: int = bin_cfg.bin_capacity
        self.alert_threshold: float = bin_cfg.alert_threshold

        self.current_load: int = 0
        self.paused_position: Waypoint = Waypoint(0.0, 0.0, 0.0)

        self.notifier = AlertNotifier()


    
    def add_garbage(self):
        """
        Adds 1 garbage in the dustbin, after collecting 1 locked item.
        
        :param self: Belongs to the BinManager class
        :return: Status of garbage whther its added or not in the dustbin.
        :rtype: bool
        """
        try: 
            logger.info(f"BinManager -> add_garbage(): STARTS, curr load: {self.current_load}")

            self.current_load += 1

            logger.info(f"BinManager -> add_garbage(): ENDS, curr load: {self.current_load}")
            return
            
     
        except Exception as e:
            logger.info(f"Error occurred in BinManager -> add_garbage(), error: {e}")
            raise e



    def usage_ratio(self) -> float:
        """
        Provides the used volume(in ratio) of the dustbin container.
        
        :param self: Belongs to the BinManager class.
        :return: Usage ratio
        :rtype: float
        """
        try: 
            logger.info(f"BinManager -> usage_ratio(): STARTS")

            usage_ratio = self.current_load / self.capacity

            logger.info(f"BinManager -> usage_ratio(): ENDS, usage_ratio: {usage_ratio}")
            return usage_ratio


        except Exception as e:
            logger.info(f"Error occurred in BinManager -> usage_ratio(), error: {e}")
            raise e

        
    
    def bin_is_full(self) -> bool:
        """
        Provides the status of dustbin's volume, whether it is 100% full or not.
        
        :param self: Belongs tot he BinManager class.   
        :return: Status of dustbin.
        :rtype: bool
        """
        try: 
            logger.info(f"BinManager -> is_full(): STARTS, current load: {self.current_load}")

            reached_max_capacity = self.usage_ratio() >= self.alert_threshold
            if reached_max_capacity:
                self.notifier.raise_alert(AlertType.BIN_FULL, "dustbin is full", {"current_usage_ratio": self.usage_ratio()})
                logger.info(f"BinMananger -> bin_is_full(), Bin reached its max capacity. Needs to unload.")

            logger.info(f"BinManager -> is_full(): ENDS")
            return reached_max_capacity


        except Exception as e:
            logger.info(f"Error occurred in BinManager -> is_full(), error: {e}")
            raise e
        

    
    def reset_bin(self) -> bool:
        """
        Resets dustbin's laod after unloading it.
        
        :param self: Belongs to the BinManager class.
        :return: Confirmation that bin is unloaded completely.
        :rtype: bool
        """
        try:
            logger.info(f"BinManager -> reset_bin(): STARTS, before load: {self.current_load}")
            self.current_load = 0
            logger.info(f"BinManager -> reset_bin(): ENDS, after load: {self.current_load}")
            return True


        except Exception as e:
            logger.info(f"Error occurred in BinManager -> reset_bin(), error: {e}")
            raise e