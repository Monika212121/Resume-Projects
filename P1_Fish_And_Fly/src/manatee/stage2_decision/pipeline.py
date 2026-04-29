# Aim: This is entry point of the Decision Pipeline

from src.common.logging import logger
from src.common.entity.dispatch import DispatchOrder

from src.fish.stage2_decision.entity import DecisionConfig



class DecisionPipeline:
    def __init__(self, decision_config: DecisionConfig):
        self.cfg = decision_config
        pass


'''
    def run(self, dispatch_order: DispatchOrder) -> OperationMode:
        try:
            logger.info(f"DecisionPipeline -> run(): STARTS, dispatch_order: {dispatch_order}")

            operation_mode: OperationMode = OperationMode.IDLE

            # Decieding operation mode for the Manatee machine
            if dispatch_order.fish_rescue_position:
                logger.info(f"Fish machine needs help")
                operation_mode = OperationMode.RESCUE

            elif len(dispatch_order.target_dump_points) > 0:
                operation_mode = OperationMode.COLLECTION
            
            logger.info(f"DecisionPipeline -> run(): ENDS, operation_mode: {operation_mode}")
            return operation_mode


        except Exception as e:
            logger.info(f"Error occurred in DecisionPipeline -> run(), error: {e}")
            raise e
'''