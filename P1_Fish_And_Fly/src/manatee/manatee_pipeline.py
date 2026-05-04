# Aim: This is entry-point for Manatee machine

import cv2

from typing import List

from src.common.logging import logger
from src.common.utils.mission import MissionPhase
from src.common.io.factory import build_vision_input
from src.common.io.folder_video import FolderVideoInput
from src.common.visualization.visualizer import Visualizer
from src.common.simulation.sim_bridge import SimulationBridge
from src.common.config.configuration import ConfigurationManager
from src.common.projection.fish_frame_projection import FishFrameProjector
from src.common.entity.manatee_communication import TaskStatus
from src.common.entity.dispatch import DispatchOrder, DispatchOutcome

from src.fly.stage3_decision.entity import DumpConfig

from src.manatee.stage1_vision.pipeline import VisionPipeline
from src.manatee.stage2_decision.pipeline import DecisionPipeline
from src.manatee.stage3_action.mission_planner import MissionPlanner



class ManateePipeline:
    def __init__(self, manatee_cfg: ConfigurationManager, dump_points: List[DumpConfig], simulation_bridge: SimulationBridge):
        self.cfg_mg = manatee_cfg
        self.dump_points = dump_points

        # Loading the Manatee's configurations
        self.vision_config = self.cfg_mg.get_vision_config()
        self.action_config = self.cfg_mg.get_manatee_action_config()

        # Instantiating the pipelines
        self.sim_bridge = simulation_bridge
        
        self.vision_pipeline_obj = VisionPipeline(vision_config = self.vision_config)
        self.mission_planner_obj = MissionPlanner(action_config = self.action_config, dump_points = self.dump_points, simulation_bridge = self.sim_bridge)
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

            # Stop recording the simulation visualization
            self.mission_planner_obj.sim_bridge.stop()

            logger.info(f"ManateePipeline -> terminate(): ENDS")
            return


        except Exception as e:
            logger.info(f"Error occured in ManateePipeline -> terminate(), error: {e}")
            raise e



    def tick(self, dispatch_order: DispatchOrder) -> DispatchOutcome:
        try:
            logger.info("********************************************* MANATEE MODULE SYSTEM: STARTS********************************************")
            logger.info(f"ManateePipeline -> tick(), dispatch_order: {dispatch_order}")
            
            dispatch_outcome: DispatchOutcome = DispatchOutcome(
                dispatch_order= dispatch_order,
                task_status = TaskStatus.FAILED,
                issue= "No issue"
            )

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
                issue: str = "Error occurred in reading camera frame"
                dispatch_outcome.issue = issue
                return dispatch_outcome
            

            # PERCEPTION | VISION: Creating list of detections and taking only navigation hazard objects
            hazard_objects = self.vision_pipeline_obj.run(frame)

            # PROJECTION: Transforming image frame(active_objects) -> fish frame(fish_frame_objects)
            fish_frame_hazard_objects = self.fish_frame_projector_obj.transform_to_fish_frame(active_objects= hazard_objects)

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
                    issue: str = "If perception visualization is interupted by user keyboard"
                    dispatch_outcome.issue = issue
                    return dispatch_outcome


            # ACTION: Execute the action intent(from Decision -> Action) to collect the target garbage, following the mission planner.
            # SIMULATION: Action and Simulation are connected together and run parallely.
            dispatch_outcome = self.mission_planner_obj.tick(dispatch_order = dispatch_order, hazard_objects = hazard_objects_list)  
                
            logger.info("********************************************MANATEE MODULE SYSTEM: ENDS**********************************************")
            return dispatch_outcome


        except Exception as e:
            logger.info(f"Error occurred in ManateePipeline -> tick(), error: {e}")
            raise e

  