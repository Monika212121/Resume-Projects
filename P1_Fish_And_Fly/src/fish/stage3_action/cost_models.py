# AIM: Implementing Cost-based Deterministic Minimizaton function to find the nearest docking / d-point. 
import math
from src.common.logging import logger
from src.fish.stage3_action.entity import Waypoint, CostModel
from src.fish.stage3_action.environment.mock_env import MockEnvironmentModel



class CostCalculator:
    def __init__(self, cost_model_cfg: CostModel):
       self.cost_model_cfg = cost_model_cfg
       
       self.weights = self.cost_model_cfg.cost_weigths
       self.vehicle = self.cost_model_cfg.vehicle_model
       self.norm_limits = self.cost_model_cfg.normalization_limits

    # ---------------------------------------------------       | Utilities |           -------------------------------------------------------------

    def planar_distance(self, current: Waypoint, target: Waypoint) -> float:
        logger.info(f"CostCalculator -> planner_distance(): STARTS")

        planar_distance = math.hypot(target.x - current.x, target.y - current.y)

        logger.info(f"CostCalculator -> planner_distance(): ENDS, distance: {planar_distance}")
        return planar_distance
    

    def normalize(self, value: float, max_value: float) -> float:
        logger.info(f"CostCalculator -> normalize(): STARTS")

        normalized_val = value / max_value

        logger.info(f"CostCalculator -> normalize(): ENDS, norm value: {normalized_val}")
        return min(normalized_val, 1.0) 



    # ---------------------------------------------------       | Main cost |           -------------------------------------------------------------

    def calculate_docking_cost(self, target_pos: Waypoint, current_pos: Waypoint, env: MockEnvironmentModel) -> float:
        try:
            logger.info(f"CostCalculator -> calculate_docking_cost(): STARTS, calculating for d_point: {target_pos}")
      
            # distance and time
            distance = self.planar_distance(current_pos, target_pos)
            travel_time = distance / self.vehicle.cruise_speed

            # current opposition
            current_cost = env.current_opposition(current_pos, target_pos)

            # drag and energy
            relative_speed = self.vehicle.cruise_speed + current_cost
            energy = self.vehicle.drag_coeff * (relative_speed ** 2) * distance
            drag = self.vehicle.avg_drag_force * distance

            # safety 
            risk = env.obstacle_density(target_pos)
            uncertainty = env.localization_uncertainty()

            # normalize
            travel_time_n = self.normalize(distance, self.norm_limits.max_distance)           # time = distance/speed, norm(time) = norm(ditance) as speed will be nullify in division. 
            current_n = self.normalize(current_cost, self.norm_limits.max_current)
            energy_n = self.normalize(energy, self.norm_limits.max_energy)
            risk_n = self.normalize(risk, self.norm_limits.max_risk)
            uncertainty_n = self.normalize(uncertainty, self.norm_limits.max_uncertainty)

            # weighted sum
            total_cost = (
                self.weights.travel_time * travel_time_n +
                self.weights.current * current_n +
                self.weights.energy * energy_n +
                self.weights.drag * drag +
                self.weights.risk * risk_n +
                self.weights.uncertainty * uncertainty_n
            )

            logger.info(f"CostCalculator -> calculate_docking_cost(): ENDS, cost: {total_cost}")
            return total_cost


        except Exception as e:
            logger.info(f"Error occurred in CostCalculator -> calculate_docking_cost(), error: {e}")
            raise e