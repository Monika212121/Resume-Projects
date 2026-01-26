# Aim: Entry point of the whole system.

import cv2
import time

from src.common.logging import logger
from src.common.config.configuration import ConfigurationManager
from src.common.visualization.visualizer import Visualizer

from src.fish.stage1_vision.io.factory import build_vision_input
from src.fish.stage1_vision.pipeline import VisionPipeline

from src.fish.stage2_decision.pipeline import DecisionPipeline

from src.fish.stage3_action.entity import MissionPhase
from src.fish.stage3_action.mission_planner import FishMissionPlanner
from src.fish.stage3_action.result_logger import OutcomeLogger


    
def main():
    try:
        logger.info("*********************************************FISH MODULE SYSTEM: STARTS********************************************")
        
        # Loading the Fish module configuration
        fish_cfg_mg = ConfigurationManager("fish")

        # Loading the Fish's configurations
        vision_config = fish_cfg_mg.get_vision_config()

        decision_config = fish_cfg_mg.get_decision_config()

        mission_config = fish_cfg_mg.get_mission_config()
        bin_config = fish_cfg_mg.get_bin_manager_config()
        navigation_config = fish_cfg_mg.get_navigation_config()
        cost_model_config = fish_cfg_mg.get_cost_model_config()
        dump_location_config = fish_cfg_mg.get_dump_location_config()


        # Instantiating the pipelines
        vision_pipeline_obj = VisionPipeline(vision_cfg = vision_config)

        decision_pipeline_obj = DecisionPipeline(decision_cfg = decision_config)

        mission_planner_obj = FishMissionPlanner(
            mission_cfg = mission_config,
            bin_cfg = bin_config,
            navigation_cfg = navigation_config,
            cost_model_cfg = cost_model_config,
            dump_location_cfg = dump_location_config
        )

        visualization_obj = Visualizer()
        result_logger = OutcomeLogger()

        
        # Getting the vision input
        vision_input = build_vision_input(vision_config.io)

        # Start consuming the visual feed
        vision_input.start()

        # ---------------------------------------------------------------------------------------------------------------------------------

        mission_start_time = time.time()

        while mission_planner_obj.mission_is_active():

            # Reading the frame of visual feed
            frame = vision_input.read()                             
            if frame is None:
                logger.info("No frame is captured.")
                break
            
            logger.info(f"Original frame shape: {frame.shape}")
        
            # PERCEPTION | VISION: Getting aggregated tracked objects(from Vision Aggregator)
            active_tracked_agg_objects = vision_pipeline_obj.run(frame)

            # REASONING | DECISION: Getting 1 action intent (Decision -> Action module) and select command (Decision -> Vision module) 
            action_intent, select_command = decision_pipeline_obj.run(active_tracked_agg_objects)

            # VISUALIZATION: Create the labelled view for the tracked detections.
            # Coverts action_intent (image frame) -> world object (world frame). 
            world_object = visualization_obj.visualize_objects(frame = frame, active_objects= active_tracked_agg_objects, action_intent= action_intent)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):                       # Exit when 'q' is pressed
                break 

            # IMPORTANT CHECKS FOR PIPELINE:
            navigation_only: bool = False                               # refer ACTION_NOTES.md (4)

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

            # If world object is not created.
            if world_object is None:
                logger.info(f"No world object is created")
                navigation_only = True

            # Emitting select command(from Decision -> Vision Aggregator) to update the object's current status as SELECTED.
            if select_command:
                select_status_updated = vision_pipeline_obj.aggregator.apply_lifecycle_changes(select_command)
                if not select_status_updated:
                    logger.info("The object's status is not updated to SELECTED")
                    navigation_only = True               

            # Checking if taking action is allowed or not.
            if not mission_planner_obj.action_is_allowed():
                logger.info("Action is not allowed, so Action module is not triggered")
                continue

            # Confirmation of the nature of task Fish is performing.                                     # refer ACTION_NOTE.md(8)
            if navigation_only:
                logger.info(f"Fish machine will only perform Navigation in this iteration")

            # ACTION: Execute the action intent(from Decision -> Action) to collect the target garbage, following the mission planner.
            action_feedback = mission_planner_obj.tick(action_intent, world_object)       
            if action_intent is None:
                logger.info("No action intent is present")
                continue

            # Release the locked target and generate the feedback command.
            feedback_command = decision_pipeline_obj.selector.handle_action_feedback(action_feedback)
            if feedback_command is None:
                logger.info("No feedback command is generted from Decision module, maybe track_id mismatch.")
                continue

            # Emitting action feedback command(from Decision -> Vision Aggregator) to update the object's final status as DONE/LOST.
            final_status_updated = vision_pipeline_obj.aggregator.apply_lifecycle_changes(feedback_command)
            if not final_status_updated:
                logger.info("The object's final status is not updated to DONE/LOST")
                continue   

            # Logging the final action results for the target in a .csv file.
            result_logger.log_action_results(action_intent, action_feedback)   
                   

        mission_end_time = time.time()

        # Final mission status.
        if mission_planner_obj.phase == MissionPhase.DONE:
            logger.info(f"Mission is completed successfully, final phase: {mission_planner_obj.phase}")
        else:
            logger.info(f"Mission is aborted and failed, final phase: {mission_planner_obj.phase}")


        # Calculating time taken in the entire mission.
        mission_time = mission_end_time - mission_start_time
        logger.info(f"MISSION STARTING TIME: {mission_start_time}, MISSION ENDING TIME: {mission_end_time}")
        logger.info(f"Total time taken in this mission is: {mission_time}")

        # ---------------------------------------------------------------------------------------------------------------------------------

        # Stop consuming the visual feed
        vision_input.stop()
        cv2.destroyAllWindows()

        logger.info("********************************************FISH MODULE SYSTEM: ENDS**********************************************")
        return


    except Exception as e:
        logger.info(f"Error occurred in FISH main(), error: {e}")
        raise e

  
main()