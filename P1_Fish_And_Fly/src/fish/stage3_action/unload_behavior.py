# Aim: Implement a sub-mission of unloading garbage bin, assigned in middle of the main cleaning mission.
from typing import List

from src.common.logging import logger
from src.common.alerts_and_notifications.notifier import AlertNotifier

from src.fish.stage3_action.navigation import PathNavigator
from src.fish.stage3_action.cost_models import CostCalculator
from src.fish.stage3_action.environment.mock_env import MockEnvironmentModel
from src.fish.stage3_action.entity import CostModel, DumpLocation, Depths, Waypoint


# When Pybullet is ready, implement the below code.
"""
from src.fish.stage3_action.environment.pybullet_env import PyBulletEnvironmentModel

self.env_model = PyBulletEnvironmentModel(
    current_field=current_field,
    obstacle_map=obstacle_map,
    localization_estimator=localizer,
)
"""

class UnloadGarbageBehavior:
    def __init__(self, cost_cfg : CostModel, notifier_obj: AlertNotifier, navigator_obj: PathNavigator, garbage_dump: DumpLocation, depths: Depths):
        self.cost_config = cost_cfg
        self.notifier = notifier_obj
        self.navigator = navigator_obj   
        self.d_points = garbage_dump.d_points                                            # All d_points near the perimeter of the workspace
        self.depths = depths

        self.env_model = MockEnvironmentModel(current= 0.5, risk= 0.2, uncertainity= 0.1)
        self.cost_calculator = CostCalculator(cost_model_cfg= self.cost_config)
        
        self.unload_counter: int = 0
        self.dump_points_used: List[Waypoint] = []
        self.last_best_d_point: Waypoint = Waypoint(0.0, 0.0, 0.0)



    def find_best_dump_point(self, current_position: Waypoint) -> Waypoint:
        try:
            logger.info(f"UnloadGarbageBehavior -> find_best_dump_point(): STARTS")

            # Finding the best dump point after calculating cost for all the d-points.          
            best_docking_point = min(self.d_points, key= lambda d_pt : self.cost_calculator.calculate_docking_cost(target_pos = d_pt, current_pos = current_position, env = self.env_model))                                                                                                
            
            # Updating last d-point
            self.last_best_d_point = best_docking_point

            logger.info(f"UnloadGarbageBehavior -> find_best_dump_point(): ENDS, Best_docking_point is : {best_docking_point}")
            return best_docking_point


        except Exception as e:
            logger.info(f"Error occurred in UnloadGarbageBehavior -> find_best_dump_point(), error: {e}")
            raise e



    def resolve_unload_garbage(self) -> None:
        try:
            logger.info(f"UnloadGarbageBehavior -> resolve_unload_garbage(): STARTS")

            # Update the unload garbage counter
            self.unload_counter += 1

            # Updating the used dump_points list, this function is called, only when garbage unload is successful.
            # It means the last dump_point is used.
            self.dump_points_used.append(self.last_best_d_point)

            logger.info(f"UnloadGarbageBehavior -> resolve_unload_garbage(): ENDS")
            return


        except Exception as e:
            logger.info(f"Error occurred in UnloadGarbageBehavior -> resolve_unload_garbage(), error: {e}")
            raise e



    def get_all_used_dump_points(self):
        return self.dump_points_used