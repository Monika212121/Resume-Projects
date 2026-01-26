# Aim: Implement a sub-mission of unloading garbage bin, assigned in middle of the main cleaning mission.

from src.common.logging import logger
from src.common.alerts_and_notifications.notifier import AlertNotifier, AlertType, NotificationType

from src.fish.stage3_action.navigation import PathNavigator
from src.fish.stage3_action.cost_models import CostCalculator
from src.fish.stage3_action.environment.mock_env import MockEnvironmentModel
from src.fish.stage3_action.entity import CostModel, DumpLocation, MissionCheckpoint, Depths, Waypoint


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
        


    def unload_garbage(self, checkpoint: MissionCheckpoint) -> bool:
        try:
            logger.info(f"unload_garbage(): STARTS")

            # 1. Freeze the current mission data before start UNLOADING PROCESS.
            self.mission_checkpoint = checkpoint
            self.notifier.raise_alert(AlertType.BIN_FULL, message= "Unloading phase started", metadata= {"mission_checkpoint": self.mission_checkpoint})

            # 2. Finding the best dump point after calculating cost for all the d-points.          
            best_docking_point = min(self.d_points, key= lambda d_pt : self.cost_calculator.calculate_docking_cost(target_pos = d_pt,
                                                                                                                    current_pos = self.mission_checkpoint.last_position,
                                                                                                                    env = self.env_model))
         
            logger.info(f"unload_garbage(): Best_docking_point is : {best_docking_point}")

            # 3. Approach the chosen best d_point. 
            curr_pos = self.mission_checkpoint.last_position
            curr_level = curr_pos.z

            # Case1: If currently in surface level, directly approach dump point.
            if curr_level == self.depths.surface:
                reached_D = self.navigator.move_to(target_point= best_docking_point)
                if not reached_D:
                    logger.info(f"unload_garbage(): Error occurred in reaching the best d_point.")
                    return False

            # Case2: If currently in underwater, first ascend to the surface level, then approach the dump point.
            else: 
                # first move up vertically to the surface level.
                surface_current_pos = Waypoint(curr_pos.x, curr_pos.y, self.depths.surface)

                reached_up = self.navigator.move_to(target_point= surface_current_pos)
                if not reached_up:
                    logger.info(f"unload_garbage(): Error occurred in reaching the water surface level.")
                    return False

                # then move towards the best d_point.
                reached_D = self.navigator.move_to(target_point= best_docking_point)
                if not reached_D:
                    logger.info(f"unload_garbage(): Error occurred in reaching the best d_point.")
                    return False
                
            
            logger.info(f"unload_garbage(): ENDS")
            self.notifier.raise_notification(NotificationType.GARBAGE_UNLOADING_ENDED, message= "unloading phase ended", metadata= {"resume_waypoint": self.mission_checkpoint.last_position})
            return True


        except Exception as e:
            logger.info(f"Error occurred in unload_garbage(), error: {e}")
            raise e


