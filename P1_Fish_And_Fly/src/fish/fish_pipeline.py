# Aim: This is entry-point for Fish machine

import cv2

from src.common.logging import logger
from src.common.entity.heartbeat import SystemHeartbeat
from src.common.visualization.visualizer import Visualizer
from src.common.config.configuration import ConfigurationManager
from src.common.projection.fish_frame_projection import FishFrameProjector

from src.fish.stage1_vision.pipeline import VisionPipeline
from src.fish.stage1_vision.io.factory import build_vision_input

from src.fish.stage2_decision.command import LifeCycleAction
from src.fish.stage2_decision.pipeline import DecisionPipeline

from src.common.logging.result_logger import OutcomeLogger
from src.fish.stage3_action.mission_planner import MissionPlanner


    
class FishPipeline:
    def __init__(self, fish_cfg_mg: ConfigurationManager):

        # Loading the Fish's configurations
        self.vision_config = fish_cfg_mg.get_vision_config()

        self.decision_config = fish_cfg_mg.get_decision_config()

        self.mission_config = fish_cfg_mg.get_mission_config()
        self.bin_config = fish_cfg_mg.get_bin_manager_config()
        self.navigation_config = fish_cfg_mg.get_navigation_config()
        self.cost_model_config = fish_cfg_mg.get_cost_model_config()
        self.dump_location_config = fish_cfg_mg.get_dump_location_config()
        
        self.visualizer_config = fish_cfg_mg.get_perception_visualization_config()

        self.simulation_visualization_config = fish_cfg_mg.get_simulation_visualization_config()

        # Instantiating the pipelines
        self.vision_pipeline_obj = VisionPipeline(vision_cfg = self.vision_config)

        self.decision_pipeline_obj = DecisionPipeline(decision_cfg = self.decision_config)

        self.mission_planner_obj = MissionPlanner(
            mission_cfg = self.mission_config,
            bin_cfg = self.bin_config,
            navigation_cfg = self.navigation_config,
            cost_model_cfg = self.cost_model_config,
            dump_location_cfg = self.dump_location_config,
            sim_visualization_cfg= self.simulation_visualization_config
        )

        self.fish_frame_projector_obj = FishFrameProjector()
        self.visualization_obj = Visualizer()
        self.result_logger = OutcomeLogger()

    
    def initiate(self):
        try:
            logger.info(f"FishPipeline -> initiate(): STARTS")

            # Getting the vision input
            self.vision_input = build_vision_input(self.vision_config.io)

            # Start consuming the visual feed
            self.vision_input.start()

            logger.info(f"FishPipeline -> initiate(): ENDS")
            return
    

        except Exception as e:
            logger.info(f"Error occurred in FishPipeline -> initiate(), error: {e}")
            raise e



    def terminate(self):
        try:
            logger.info(f"FishPipeline -> terminate(): STARTS")

            # Stop consuming the visual feed
            self.vision_input.stop()
            cv2.destroyAllWindows()

            logger.info(f"FishPipeline -> terminate(): ENDS")
            return


        except Exception as e:
            logger.info(f"Error occured in FishPipeline -> terminate(), error: {e}")
            raise e



    def tick(self) -> SystemHeartbeat:
        try:
            logger.info("*********************************************FISH MODULE SYSTEM: STARTS********************************************")

            # Reading the frame of visual feed
            frame = self.vision_input.read()                             
            if frame is None:
                # If frame is not received, then abort the mission
                self.mission_planner_obj.abort_mission()

                heartbeat = SystemHeartbeat.now(
                    mission_phase= self.mission_planner_obj.phase,
                    position= self.mission_planner_obj.navigator.current_position,
                    issue= "Frame is not captured, so mission is aborted"
                )
                return heartbeat
            
            logger.info(f"Original frame shape: {frame.shape}")

            # PERCEPTION | VISION: Creating aggregated tracked objects(in Vision Aggregator)
            active_tracked_agg_objects = self.vision_pipeline_obj.run(frame)

            # REASONING | DECISION: Creating 1 action intent (Decision -> Action module) and select command (Decision -> Vision module) 
            action_intent, select_command = self.decision_pipeline_obj.run(active_tracked_agg_objects)

            # PROJECTION: Providing active_objects and selected object, after Projecting [active_objects(image frame) -> fish_frame_objects(fish frame)] 
            fish_frame_objects, selected_fish_frame_object = self.fish_frame_projector_obj.transform_to_fish_frame(active_objects= active_tracked_agg_objects, action_intent= action_intent)

            # VISUALIZATION: Viewing the tracked objects, in actual video/camera feed. 
            if self.visualizer_config.enabled_gui:
                self.visualization_obj.visualize_objects(frame = frame, active_objects= active_tracked_agg_objects, selected_world_obj= selected_fish_frame_object)

                if cv2.waitKey(1) & 0xFF == ord('q'):                                                        # Exit when 'q' is pressed
                    # If perception visualization is not interupted, then abort the mission
                    self.mission_planner_obj.abort_mission()   

                    heartbeat = SystemHeartbeat.now(
                        mission_phase= self.mission_planner_obj.phase,
                        position= self.mission_planner_obj.navigator.current_position,
                        issue= "Visualization is ended / interupted"
                    )
                    return heartbeat
    
            # Logging the LOST target object, in the `garbage.csv` file, without further applying action on it
            if select_command and select_command.action == LifeCycleAction.LOST:
                if action_intent:
                    self.result_logger.log_action_results(action_intent, None) 
                     
                    heartbeat = SystemHeartbeat.now(
                        mission_phase= self.mission_planner_obj.phase,
                        position= self.mission_planner_obj.navigator.current_position,
                        issue= "Garbage is LOST in this tick"
                    )
                    return heartbeat
            

            # IMPORTANT CHECKS FOR PIPELINE:
            navigation_only: bool = False                                                                   # refer ACTION_NOTES.md (4)

            # If active objects are not in frame.
            if len(active_tracked_agg_objects) == 0:
                logger.info("No new objects are present in frame")
                navigation_only = True
            
            # If action intent is not created.
            if action_intent is None:
                logger.info("No action intent is generated from Decision Module")
                navigation_only = True

            # If an object is not selected.
            if select_command is None:
                logger.info("No select command is generated")
                navigation_only = True

            # If selected world object is not created.
            if selected_fish_frame_object is None:
                logger.info(f"No world object is created for the action intent")
                navigation_only = True

            # Emitting select command(from Decision -> Vision Aggregator) to update the object's current status as SELECTED.
            if select_command:
                select_status_updated = self.vision_pipeline_obj.aggregator.apply_lifecycle_changes(select_command)
                if not select_status_updated:
                    logger.info("The object's status is not updated to SELECTED")
                    navigation_only = True               

            # Checking if taking action is allowed or not.
            if not self.mission_planner_obj.action_is_allowed():
                heartbeat = SystemHeartbeat.now(
                    mission_phase= self.mission_planner_obj.phase,
                    position= self.mission_planner_obj.navigator.current_position,
                    issue= "Action is not allowed, so Action module is not triggered"
                )
                return heartbeat

            # Confirmation of the nature of task, Fish is performing in this tick                           # refer ACTION_NOTE.md(8)
            if navigation_only:
                logger.info(f"Fish machine will only perform Navigation in this iteration")


            # ACTION: Execute the action intent(from Decision -> Action) to collect the target garbage, following the mission planner.
            # SIMULATION: Action and Simulation are connected together and run parallely.
            action_feedback = self.mission_planner_obj.tick(action_intent, selected_fish_frame_object, fish_frame_objects)  

            # Skip updating lifecycle changes, if there is no object, considered for pickup/picked up
            if action_intent is None:
                heartbeat = SystemHeartbeat.now(
                    mission_phase= self.mission_planner_obj.phase,
                    position= self.mission_planner_obj.navigator.current_position,
                    issue= "No action intent is present, only navigation happened in this tick"
                )
                return heartbeat
                
            # Release the locked target and generate the feedback command.
            feedback_command = self.decision_pipeline_obj.selector.handle_action_feedback(action_feedback)
            if feedback_command is None:
                heartbeat = SystemHeartbeat.now(
                    mission_phase= self.mission_planner_obj.phase,
                    position= self.mission_planner_obj.navigator.current_position,
                    issue= "No feedback command is generated from Decision module, maybe track_id mismatch."
                )
                return heartbeat

            # Emitting action feedback command(from Decision -> Vision Aggregator) to update the object's final status as DONE/LOST.
            final_status_updated = self.vision_pipeline_obj.aggregator.apply_lifecycle_changes(feedback_command)
            if not final_status_updated:
                heartbeat = SystemHeartbeat.now(
                    mission_phase= self.mission_planner_obj.phase,
                    position= self.mission_planner_obj.navigator.current_position,
                    issue= "The object's final status is not updated to DONE/LOST"
                )
                return heartbeat

            # Logging the target object's final action results in the `garbage.csv` file.
            self.result_logger.log_action_results(action_intent, action_feedback)   

            # If mission is in progress, then create and emit "No issue" heartbeat signal
            heartbeat = SystemHeartbeat.now(
                mission_phase= self.mission_planner_obj.phase,
                position= self.mission_planner_obj.navigator.current_position,
                issue= "No issue"
            )

            logger.info(f"The current heartbeat of this tick is: {heartbeat}")
            logger.info("********************************************FISH MODULE SYSTEM: ENDS**********************************************")
            return heartbeat


        except Exception as e:
            logger.info(f"Error occurred in FishPipeline -> tick(), error: {e}")
            raise e

  