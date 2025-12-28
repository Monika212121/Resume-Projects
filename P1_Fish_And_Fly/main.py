import cv2
from src.common.logging import logger
from src.common.config.configuration import ConfigurationManager
from src.fish.stage1_vision.io.factory import build_vision_input

from src.fish.stage1_vision.pipeline import VisionPipeline
from src.fish.stage2_decision.pipeline import DecisionPipeline
from src.fish.stage3_action.pipeline import ActionPipeline

from src.fish.stage3_action.entity import ActionFeedback, ActionStatus

class DecisionEngine:
    def should_stop(self, tracked_objects):
        for obj in tracked_objects:
            if obj.age >= 10 and obj.avg_confidence >= 0.5:
                return True
        return False
    
    
def main():
    try:
        logger.info("*********************************************MAIN FILE: STARTS********************************************")
        
        # Loading the Fish module configuration
        fish_cfg_mg = ConfigurationManager("fish")

        # Loading the Fish's configurations
        vision_config = fish_cfg_mg.get_vision_config()
        decision_config = fish_cfg_mg.get_decision_config()
        #action_config = fish_cfg_mg.get_action_config()

        # Getting the vision input
        vision_input = build_vision_input(vision_config.io)

        # Instantiating the pipelines
        vision_pipeline_obj = VisionPipeline(vision_cfg = vision_config)
        decision_pipeline_obj = DecisionPipeline(decision_cfg = decision_config)
        action_pipeline_obj = ActionPipeline()

        # Start consuming the visual feed
        vision_input.start()

        decision_engine = DecisionEngine()      # to stop the camera/video feed

        while True:
            # Reading the frame of visual feed
            frame = vision_input.read()                             
            if frame is None:
                break
            
            # Getting aggregated tracked objects(from Vision Aggregator)
            tracked_aggregated_objects = vision_pipeline_obj.run(frame)
            if len(tracked_aggregated_objects) == 0:
                logger.info("No objects are aggregated")
                continue

            # Getting action intents(will be passed to Action module) and select command(will be passed back to Vision module) 
            action_intent, select_command = decision_pipeline_obj.run(tracked_aggregated_objects)
            if select_command is None:
                logger.info("No select command is generated")
                continue

            # Emitting select command(from Decision -> Vision Aggregator) to update the object's status to be SELECTED/DONE.
            vision_pipeline_obj.aggregator.apply_lifecycle_changes(select_command)

            if action_intent is None:
                logger.info("No action intent is generated from Decision Module")
                continue

            # Emitting action intent(from Decision -> Action module) to carry out the action(collection).
            action_feedback = action_pipeline_obj.run(action_intent)           
            if action_feedback is None:
                logger.info("No action feedback is generated from Action module")
                continue

            # Getting action feedback(from Action -> Decision) to release lock of the target.
            feedback_command = decision_pipeline_obj.selector.handle_action_feedback(action_feedback)
            if feedback_command is None:
                logger.info("No feedback command is generted from Decision module")
                continue

            # Emitting action feedback command(from Decision -> Vision Aggregator) to update the object's status to be DONE/LOST.
            vision_pipeline_obj.aggregator.apply_lifecycle_changes(feedback_command)


            # Stopping detections
            if decision_engine.should_stop(tracked_aggregated_objects):
                logger.info("Decision: Garbage confirmed. Stopping vision.")
                break

            # Visualizing the tracked objects
            for tracked_obj in tracked_aggregated_objects:
                logger.info(tracked_obj)
            


        # Stop consuming the visual feed
        vision_input.stop()

        logger.info("*********************************************MAIN FILE: ENDS**********************************************")


    except Exception as e:
        logger.info(f"Error occurred in main(): {e}")
        raise e
    
main()



