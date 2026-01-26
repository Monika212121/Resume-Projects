from typing import Optional, Tuple

from src.common.logging import logger



class Manipulator:
    def __init__(self):
        pass


    def grasp_garbage(self, bbox: Optional[Tuple[int, int, int, int]]) -> bool:
        try:
            logger.info(f"Manipulation -> grasp_garbage(): STARTS, position of garbage : {bbox}")

            if not bbox:
                logger.info(f"Manipulation -> grasp_garbage(), No position is passed.")
                return False

            # TODO: Simulation stub
            
            logger.info(f"Manipulation -> grasp_garbage(): ENDS")
            return True


        except Exception as e:
            logger.info(f"Error occurred in Manipulation -> grasp_garbage(), error: {e}")
            raise e

