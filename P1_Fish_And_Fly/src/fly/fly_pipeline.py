# Aim: This is Fly machine entry-point

from typing import List, Tuple, Set, Optional

from src.common.logging import logger
from src.common.logging.result_logger import OutcomeLogger
from src.common.simulation.sim_bridge import SimulationBridge
from src.common.config.configuration import ConfigurationManager
from src.common.entity.dispatch import DispatchOrder, DispatchOutcome
from src.common.alerts_and_notifications.alert_types import AlertType
from src.common.alerts_and_notifications.notifier import AlertNotifier
from src.common.entity.manatee_communication import ManateeMode, TaskStatus
from src.common.entity.fish_communication import FishControlSignal, SystemHeartbeat

from src.fly.stage1_controller.flight_controller import FlightController
from src.fly.stage2_analytics.coverage_tracker import LawnMowerCoverageTracker
from src.fly.stage3_decision.entity import DumpConfig
from src.fly.stage3_decision.pipeline import DecisionPipeline



class FlyPipeline:
    def __init__(self, fly_cfg: ConfigurationManager, dump_points: List[DumpConfig], simulation_bridge: SimulationBridge):

        self.dump_points = dump_points

        # Loading the Fly's configurations
        self.log_file_paths = fly_cfg.get_log_file_paths()
        self.controller_config = fly_cfg.get_controller_config()
        self.decision_config = fly_cfg.get_fly_decision_config()

        # Instantiating the Fly's pipelines
        self.coverage_tracker_obj = LawnMowerCoverageTracker()
        self.flight_controller_obj = FlightController(self.controller_config)
        self.decision_pipeline_obj = DecisionPipeline(decision_cfg= self.decision_config, dump_points = self.dump_points)
        self.sim_bridge = simulation_bridge                                                                    # shared simulation                                            

        self.notifier = AlertNotifier()
        self.result_logger = OutcomeLogger(log_file_paths= self.log_file_paths)

        self.locked_dump_ids: Set[int] = set()

        # NOTE: This flag controls the whole project operation
        self.system_active: bool = True



    def initiate(self):
        try:
            logger.info(f"FlyPipeline -> initiate(): STARTS")

            # Takeoff + Hover
            self.flight_controller_obj.takeoff()
            self.flight_controller_obj.hover()

            logger.info(f"FlyPipeline -> initiate(): ENDS, Fly machine Hovering and Monitoring Fish")
            return


        except Exception as e:
            logger.info(f"Error occurred in FlyPipeline -> initiate(), error: {e}")
            raise e



    def terminate(self):
        try:
            logger.info(f"FlyPipeline -> terminate(): STARTS")

            # Land the machine to the HQ
            self.flight_controller_obj.return_home()

            logger.info(f"FlyPipeline -> terminate(): ENDS")
            return
        

        except Exception as e:
            logger.info(f"Error occurred in FlyPipeline -> terminate(), error: {e}")
            raise e



    def tick(self, heartbeat: SystemHeartbeat) -> Tuple[Optional[DispatchOrder], Optional[FishControlSignal]]:
        try:
            logger.info("*********************************************FLY MODULE SYSTEM: STARTS********************************************")

            dispatch_order: Optional[DispatchOrder] = None
            fish_control_signal : Optional[FishControlSignal] = FishControlSignal(locked_dump_ids= list(self.locked_dump_ids)) if len(self.locked_dump_ids) > 0 else None

            # ANALYTICS: Updating Fish machine's coverage area for current position and operation depth
            self.coverage_tracker_obj.update_coverage_area((heartbeat.position.x, heartbeat.position.y, heartbeat.position.z))

            # Retrieving Fish machine's coverage area percentages
            coverage_area_percentages = self.coverage_tracker_obj.get_coverage_percentages()

            # DECISION: Creating state deltas for telemetry visualization and Dispatch order for Manatee operation (DMS)
            state_deltas, dispatch_order = self.decision_pipeline_obj.run(heartbeat= heartbeat, coverage_area_pcts = coverage_area_percentages)

            # Creating Fish control signal, w.r.t the current dispatch order
            if dispatch_order and dispatch_order.operation_mode == ManateeMode.COLLECTION and dispatch_order.dump_info:
                self.locked_dump_ids.add(dispatch_order.dump_info.dump_id)
                fish_control_signal = FishControlSignal(locked_dump_ids= list(self.locked_dump_ids))

                logger.info(f"FlyPipeline- > tick(), locked dump_id: {dispatch_order.dump_info.dump_id}")

            # Logging the fish machine's health and state deltas w.r.t. Fly machine, in `state_delta.csv` file.
            self.result_logger.telemetry_logger.log_fish_machine_telemetry(delta= state_deltas)

            logger.info(f"FlyPipeline -> tick(), dispatch_order: {dispatch_order}, fish_control_signal: {fish_control_signal}")

            logger.info("*********************************************FLY MODULE SYSTEM: ENDS********************************************")
            return dispatch_order, fish_control_signal
        

        except Exception as e:
            logger.info(f"Error occurred in FlyPipeline -> tick(), error: {e}")
            raise e
        


    def process_manatee_action(self, dispatch_outcome: DispatchOutcome):
        try:
            logger.info(f"FlyPipeline -> process_manatee_action(): STARTS")

            dispatch_order = dispatch_outcome.dispatch_order
            manatee_action_status = dispatch_outcome.task_status

            # Releasing the target dump point, regardless of Manatee's action outcome, if failed, retry can be in next Fly's tick
            dump_info = dispatch_order.dump_info
            target_dump_id = dump_info.dump_id if dump_info else None
            
            if target_dump_id and (target_dump_id in self.locked_dump_ids):
                self.locked_dump_ids.remove(target_dump_id)
                logger.info(f"FlyPipeline- > tick(), releasing lock on dump_id: {target_dump_id}")

            # CASE1: Processing Collection dispatch order outcome
            if dispatch_order.operation_mode == ManateeMode.COLLECTION:

                if target_dump_id and manatee_action_status == TaskStatus.COMPLETED:
                    self.decision_pipeline_obj.dms.mark_unloaded(dump_id= target_dump_id)
                else:
                    # Raise alert and the same task will be retry in later tick
                    self.notifier.raise_alert(alert_type= AlertType.MACHINE_FAILURE, message= dispatch_outcome.issue, metadata= {"dump_id": target_dump_id})
                    

            logger.info(f"FlyPipeline -> process_manatee_action(): ENDS")
            return


        except Exception as e:
            logger.info(f"Error occurred in FlyPipeline -> tick(), error: {e}")
            raise e
        


    def is_system_active(self) -> bool:
        return self.system_active