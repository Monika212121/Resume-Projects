# Aim: This is entry-point for Manatee machine

import cv2

from src.common.logging import logger
from src.common.entity.dispatch_order import DispatchOrder
from src.common.visualization.visualizer import Visualizer
from src.common.config.configuration import ConfigurationManager
from src.common.projection.fish_frame_projection import FishFrameProjector
from src.common.logging.result_logger import OutcomeLogger
from src.common.io.factory import build_vision_input
from src.common.io.folder_video import FolderVideoInput

from src.manatee.stage1_vision.pipeline import VisionPipeline
from src.manatee.stage2_decision.pipeline import DecisionPipeline
from src.manatee.stage3_action.pipeline import MissionPlanner

from src.fish.stage3_action.entity import MissionPhase


    
class ManateePipeline:
    def __init__(self, manatee_cfg_mg: ConfigurationManager):
        self.cfg_mg = manatee_cfg_mg

        # Loading the Manatee's configurations
        self.log_file_paths = self.cfg_mg.get_log_file_paths()
        self.vision_config = self.cfg_mg.get_vision_config()
        self.decision_config = self.cfg_mg.get_decision_config()
        self.action_config = self.cfg_mg.get_action_config()
        self.simulation_config = self.cfg_mg.get_simulation_config() 

        # Instantiating the pipelines
        self.result_logger = OutcomeLogger(log_file_paths = self.log_file_paths)
        self.vision_pipeline_obj = VisionPipeline(vision_config = self.vision_config)

        self.decision_pipeline_obj = DecisionPipeline(decision_config = self.decision_config)
        self.mission_planner_obj = MissionPlanner(action_config = self.action_config, simulation_config= self.simulation_config, telemetry_logger = self.result_logger.telemetry_logger)
        self.fish_frame_projector_obj = FishFrameProjector()
        self.visualization_obj = Visualizer(io_config= self.vision_config.io)



    def initiate(self):
        try:
            logger.info(f"ManateePipeline -> initiate(): STARTS")

            # Getting the vision input
            self.vision_input = build_vision_input(self.vision_config.io)

            # Start consuming the visual feed
            self.vision_input.start()

            logger.info(f"ManateePipeline -> initiate(): ENDS")
            return
    

        except Exception as e:
            logger.info(f"Error occurred in ManateePipeline -> initiate(), error: {e}")
            raise e



    def terminate(self):
        try:
            logger.info(f"ManateePipeline -> terminate(): STARTS")

            # Stop consuming the visual feed
            self.vision_input.stop()
            cv2.destroyAllWindows()

            # Stop recording the perception visualization
            if self.video_writer:
                self.video_writer.release()

            logger.info(f"ManateePipeline -> terminate(): ENDS")
            return


        except Exception as e:
            logger.info(f"Error occured in ManateePipeline -> terminate(), error: {e}")
            raise e



    def tick(self, dispatch_order: DispatchOrder) -> bool:
        try:
            logger.info("********************************************* MANATEE MODULE SYSTEM: STARTS********************************************")

            # Mode switching based on mission phase                                                         # refer VISION_NOTE.md(5)
            if isinstance(self.vision_input, FolderVideoInput):
                if self.mission_planner_obj.phase == MissionPhase.SURFACE:
                    self.vision_input.switch_mode("surface")

                elif self.mission_planner_obj.phase == MissionPhase.UNDERWATER:
                    self.vision_input.switch_mode("underwater")


            # Reading the frame of visual feed
            frame = self.vision_input.read()                             
            if frame is None:
                logger.info(f"Frame is not captured")
                
                # If frame is not received, then return false
                return False
            

            # PERCEPTION | VISION: Creating list of detections and taking only naviagtion hazard objects
            hazard_objects = self.vision_pipeline_obj.run(frame)

            # PROJECTION: Transforming image frame(active_objects) -> fish frame(fish_frame_objects)
            fish_frame_hazard_objects = self.fish_frame_projector_obj.transform_to_fish_frame(active_objects= hazard_objects)

            # REASONING | DECISION: Creating 1 action intent (Decision -> Action module) 
            dispatch_order.operation_mode = self.decision_pipeline_obj.run(dispatch_order = dispatch_order)

            hazard_objects_list = [obj for obj in fish_frame_hazard_objects.values()]
            
            # VISUALIZATION: Viewing the tracked objects, in actual video/camera feed. 
            if self.vision_config.visualization.enabled_gui:
                self.video_writer = self.visualization_obj.visualize_objects(
                    frame = frame, 
                    all_objects= hazard_objects_list, 
                    selected_obj= None, 
                    collected_objects = [],
                    lost_objects= []
                )

                if cv2.waitKey(1) & 0xFF == ord('q'):                                                        # Exit when 'q' is pressed
                    # If perception visualization is interupted, then return False
                    return False


            # ACTION: Execute the action intent(from Decision -> Action) to collect the target garbage, following the mission planner.
            # SIMULATION: Action and Simulation are connected together and run parallely.
            action_feedback = self.mission_planner_obj.tick(dispatch_order = dispatch_order, hazard_objects = hazard_objects_list)  
            if not action_feedback:
                logger.info(f"Action module is failed to perform current dispatch order")
                return False

            # Logging target object's final action result, in the `garbage.csv` file.
            #self.result_logger.object_logger.log_selected_target(selected_object= selected_target, feedback_command = feedback_command)   

            # If mission is in progress, then create and emit "No issue" heartbeat signal
            logger.info(f"The current result of this tick is: {True}")
            logger.info("********************************************MANATEE MODULE SYSTEM: ENDS**********************************************")
            return True


        except Exception as e:
            logger.info(f"Error occurred in ManateePipeline -> tick(), error: {e}")
            raise e

  