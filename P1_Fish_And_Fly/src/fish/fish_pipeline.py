# Aim: This is entry-point for Fish machine

import cv2

from src.common.logging import logger
from src.common.logging.result_logger import OutcomeLogger
from src.common.io.factory import build_vision_input
from src.common.io.folder_video import FolderVideoInput
from src.common.io.video_writer import VideoWriterManager 
from src.common.utils.mission import action_is_allowed
from src.common.utils.objects import get_all_tracked_objects
from src.common.visualization.visualizer import Visualizer
from src.common.entity.heartbeat import SystemHeartbeat
from src.common.config.configuration import ConfigurationManager
from src.common.projection.fish_frame_projection import FishFrameProjector

from src.fish.stage1_vision.pipeline import VisionPipeline
from src.fish.stage2_decision.pipeline import DecisionPipeline
from src.fish.stage2_decision.entity import LifeCycleAction, LifeCycleCommand
from src.fish.stage3_action.entity import MissionPhase
from src.fish.stage3_action.mission_planner import MissionPlanner

    
class FishPipeline:
    def __init__(self, fish_cfg_mg: ConfigurationManager):
        self.cfg_mg = fish_cfg_mg

        # Loading the Fish's configurations
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
        self.video_writer = VideoWriterManager(output_dir= "outputs/fish", fps= 20) if self.vision_config.io.record_output else None
        self.recording_enabled = self.vision_config.visualization.enabled_gui



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

            # Stop recording the perception visualization
            if self.video_writer:
                self.video_writer.release()

            # Stop recording the simulation visualization
            if self.mission_planner_obj.sim_bridge.world.recorder:
                self.mission_planner_obj.sim_bridge.stop()

            logger.info(f"FishPipeline -> terminate(): ENDS")
            return


        except Exception as e:
            logger.info(f"Error occured in FishPipeline -> terminate(), error: {e}")
            raise e



    def tick(self) -> SystemHeartbeat:
        try:
            logger.info("*********************************************FISH MODULE SYSTEM: STARTS********************************************")

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
                
                # If frame is not received, then abort the mission
                self.mission_planner_obj.abort_mission()

                heartbeat = SystemHeartbeat.now(
                    mission_phase= self.mission_planner_obj.phase,
                    position= self.mission_planner_obj.navigator.current_position,
                    issue= "Frame is not captured, so mission is aborted"
                )
                return heartbeat
            
            #logger.info(f"Original frame shape: {frame.shape}")

            # PERCEPTION | VISION: Creating aggregated tracked objects(in Vision Aggregator)
            active_objects, collected_objects, lost_objects = self.vision_pipeline_obj.run(frame)

            # PROJECTION: Transforming image frame(active_objects) -> fish frame(fish_frame_objects)
            fish_frame_objects = self.fish_frame_projector_obj.transform_to_fish_frame(active_objects= active_objects)

            # REASONING | DECISION: Creating 1 action intent (Decision -> Action module) and 1 select command (Decision -> Vision module) 
            decision_result = self.decision_pipeline_obj.run(fish_frame_objects = fish_frame_objects)

            # Unpacking decision result
            categorized_objects = decision_result.categorized_objects
            action_intent = decision_result.action_intent
            selection_commands = decision_result.selection_commands
            selected_target = decision_result.selected_target

            # VISUALIZATION: Viewing the tracked objects, in actual video/camera feed. 
            if self.vision_config.visualization.enabled_gui:
                all_active_objects = get_all_tracked_objects(active_objects= fish_frame_objects, categorized_objects= categorized_objects)

                display_frame = self.visualization_obj.visualize_objects(
                    frame = frame, 
                    all_objects= all_active_objects, 
                    selected_obj= selected_target, 
                    collected_objects = collected_objects, 
                    lost_objects= lost_objects
                )

                # Record perception video
                if self.video_writer:
                    self.video_writer.write(display_frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):                                                        # Exit when 'q' is pressed
                    # If perception visualization is not interupted, then abort the mission
                    self.mission_planner_obj.abort_mission()   

                    heartbeat = SystemHeartbeat.now(
                        mission_phase= self.mission_planner_obj.phase,
                        position= self.mission_planner_obj.navigator.current_position,
                        issue= "Visualization is ended / interupted"
                    )
                    return heartbeat

            
            # Updating lifecycle states for non-selectable objects[Unsafe targets + Env + Hazard]
            self.vision_pipeline_obj.aggregator.apply_lifecycle_changes_for_non_selectable_objects(categorized_objects= categorized_objects)

            # Logging non-selectable objects[Unsafe targets + Env + Hazard]
            self.result_logger.object_logger.log_non_selectable_objects(categorized_objects= categorized_objects)

            # Processing selection commands one by one
            for command in selection_commands:    
                # Logging the LOST target object(which lost after getting selected)
                if command.action == LifeCycleAction.LOST:
                    logger.info("The object's status is LOST")
                    if selected_target and selected_target.track_id == command.track_id:
                        feedback_command = LifeCycleCommand(
                            action= LifeCycleAction.LOST,
                            track_id= command.track_id,
                            selection_count= command.selection_count,
                            priority_score= 0.0
                        )
                        self.result_logger.object_logger.log_selected_target(selected_object= selected_target, feedback_command = feedback_command)

                # Emitting select command(from Decision -> Vision Aggregator) to update the object's current status as SELECTED.
                elif command.action == LifeCycleAction.SELECT:
                    logger.info("The object's status is SELECT")
                    select_status_updated = self.vision_pipeline_obj.aggregator.apply_lifecycle_changes(command)
                    if not select_status_updated:
                        logger.info("The object's status is not updated to SELECTED")


            # IMPORTANT CHECKS FOR PIPELINE:
            navigation_only: bool = False                                                                   # refer ACTION_NOTES.md (4)

            # If active objects are not in frame.
            if len(active_objects) == 0:
                logger.info("No new objects are present in frame")
                navigation_only = True
            
            # If action intent is not created.
            if action_intent is None:
                logger.info("No action intent is generated from Decision Module")
                navigation_only = True

            # If selected world object is not created.
            if selected_target is None:
                logger.info(f"No world object is created for the action intent")
                navigation_only = True

            # Checking if taking action is allowed or not.
            if not action_is_allowed(current_mission_phase= self.mission_planner_obj.phase):
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
            logger.info(f"**********************simualtion config:***************,{self.simulation_config}")
            action_feedback = self.mission_planner_obj.tick(action_intent= action_intent, selected_target= selected_target, categorized_objects= categorized_objects)  

            # Skip updating lifecycle changes, if there is no object, considered for pickup/picked up
            if action_intent is None or selected_target is None:
                heartbeat = SystemHeartbeat.now(
                    mission_phase= self.mission_planner_obj.phase,
                    position= self.mission_planner_obj.navigator.current_position,
                    issue= "No action intent is present, only navigation happened in this tick"
                )
                return heartbeat
                
            # Release the locked target and generate the feedback command.
            feedback_command = self.decision_pipeline_obj.selector.handle_action_feedback(action_feedback)

            # Emitting action feedback command(from Decision -> Vision Aggregator) to update the object's final status as DONE/LOST.
            final_status_updated = self.vision_pipeline_obj.aggregator.apply_lifecycle_changes(feedback_command)
            if not final_status_updated:
                heartbeat = SystemHeartbeat.now(
                    mission_phase= self.mission_planner_obj.phase,
                    position= self.mission_planner_obj.navigator.current_position,
                    issue= "The object's final status is not updated to DONE/LOST"
                )
                return heartbeat

            # Logging target object's final action result, in the `garbage.csv` file.
            self.result_logger.object_logger.log_selected_target(selected_object= selected_target, feedback_command = feedback_command)   

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

  