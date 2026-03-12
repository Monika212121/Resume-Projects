from typing import Set, List

from src.common.logging import logger
from src.common.entity.decision_types import DecisionStatus
from src.common.projection.entity import FishFrameObject
from src.common.logging.garbage_csv_logger import GarbageCSVLogger, GarbageLogEntry

from src.fish.stage1_vision.entity import TrackedGarbage, EntityRole

from src.fish.stage2_decision.entity import CategorizedObjects, LifeCycleAction, LifeCycleCommand

from src.fish.stage3_action.entity import ActionStatus



class OutcomeLogger:
    def __init__(self):
        self.garbage_logger = GarbageCSVLogger()
        self.logged_ids: Set[int] = set()                                                                   # list of track_ids of objects already logged. 



    def log_lost_object(self, lost_objects: List[TrackedGarbage]):
        try:
            logger.info(f"OutcomeLogger -> log_lost_object(): STARTS, lost_objects: {lost_objects}")
                                                                                                                                         
            for obj in lost_objects:
                # If already logged, then skip
                if obj.track_id in self.logged_ids:
                    logger.info(f"log_lost_object(): **********************SKIPPED")
                    continue

                # Determining decision result
                decision_status = DecisionStatus.TARGET_IGNORED
                if obj.entity_role == EntityRole.ENVIRONMENT_ENTITY:
                    decision_status = DecisionStatus.ENVIRONMENT_OBJECT_IGNORED
                
                elif obj.entity_role == EntityRole.NAVIGATION_HAZARD:
                    decision_status = DecisionStatus.HAZARD_OBJECT_AVOIDED
                
                new_entry = GarbageLogEntry(
                    track_id= obj.track_id,
                    class_name= obj.class_name,
                    age = obj.age,
                    avg_confidence= obj.avg_confidence,
                    priority_score= 0.0,
                    entity_role= obj.entity_role.name,
                    decision_status= decision_status.name,
                    decision_reason= decision_status.value,
                    final_action_status= ActionStatus.LOST.name
                )

                logger.info(f"log_lost_object(): new_entry: {new_entry}")
                # Logging into the `garbage.csv` file.
                self.garbage_logger.log(new_entry)                  

                # Updating the logged_ids list with the new entry.
                self.logged_ids.add(obj.track_id)
            
            logger.info(f"OutcomeLogger -> log_lost_object(): ENDS")
            return 
        
        
        except Exception as e:
            logger.error(f"Error occured in OutcomeLogger -> log_lost_object(), error e: {e}")
            raise e
        


    def log_non_selectable_objects(self, categorized_objects: CategorizedObjects):
        try:
            logger.info(f"OutcomeLogger -> log_non_selectable_objects(): STARTS")
            
            # Log unsafe targets (target near hazard objects)
            for object in categorized_objects.collection_targets:
                # If already logged, then skip
                if object.track_id in self.logged_ids:
                    continue

                if object.decision_status == DecisionStatus.TARGET_AVOIDED:
                    new_entry = GarbageLogEntry(
                        track_id= object.track_id,
                        class_name= object.class_name,
                        age = object.age,
                        avg_confidence= object.avg_confidence,
                        priority_score=object.priority_score,
                        entity_role= object.entity_role.name,
                        decision_status= object.decision_status.name,
                        decision_reason= object.decision_status.value,
                        final_action_status= ActionStatus.AVOIDED.name
                    )

                    # Logging into the `garbage.csv` file.
                    self.garbage_logger.log(new_entry)                  

                    # Updating the logged_ids list with the new entry.
                    self.logged_ids.add(object.track_id)


            # Log environment entities
            for object in categorized_objects.environment_entities:
                # If already logged, then skip
                if object.track_id in self.logged_ids:
                    continue

                new_entry = GarbageLogEntry(
                    track_id= object.track_id,
                    class_name= object.class_name,
                    age = object.age,
                    avg_confidence= object.avg_confidence,
                    priority_score= object.priority_score,
                    entity_role= object.entity_role.name,
                    decision_status= object.decision_status.name,
                    decision_reason= object.decision_status.value,
                    final_action_status= ActionStatus.IGNORED.name
                )

                # Logging into the `garbage.csv` file.
                self.garbage_logger.log(new_entry)                  

                # Updating the logged_ids list with the new entry.
                self.logged_ids.add(object.track_id)

            # Log navigation hazards
            for object in categorized_objects.navigation_hazards:
                # If already logged, then skip
                if object.track_id in self.logged_ids:
                    continue

                new_entry = GarbageLogEntry(
                    track_id= object.track_id,
                    class_name= object.class_name,
                    age = object.age,
                    avg_confidence= object.avg_confidence,
                    priority_score= object.priority_score,
                    entity_role= object.entity_role.name,
                    decision_status= object.decision_status.name,
                    decision_reason= object.decision_status.value,
                    final_action_status= ActionStatus.AVOIDED.name
                )

                # Logging into the `garbage.csv` file.
                self.garbage_logger.log(new_entry)                  

                # Updating the logged_ids list with the new entry.
                self.logged_ids.add(object.track_id)
            

            logger.info(f"OutcomeLogger -> log_non_selectable_objects(): ENDS")
            return 
        

        except Exception as e:
            logger.error(f"Error occured in OutcomeLogger -> log_non_selectable_objects(), error: {e}")
            raise e



    def log_selected_target(self, selected_object: FishFrameObject, feedback_command: LifeCycleCommand):
        try:
            logger.info(f"OutcomeLogger -> log_selected_target(): STARTS")

            # Checking through a ONE TIME LOGGING GUARD, if so, skip logging.                               # refer ACTION_NOTES.md (3) 
            if selected_object.track_id in self.logged_ids:
                logger.info(f"OutcomeLogger -> log_selected_target(), This object is already logged, track_id: {selected_object.track_id}")
                return                                                                                                                                              
            
            # If the target is unattempted, then skip logging, as it is yet to be handled
            if feedback_command.action == LifeCycleAction.UNATTEMPTED:
                logger.info(f"OutcomeLogger -> log_selected_target(), Skip logging as this object is unattempted till now")
                return

            # Determining the target object's final status, according to the feedback command received.
            if feedback_command.action == LifeCycleAction.DONE:
                final_status = ActionStatus.COLLECTED
            elif feedback_command.action == LifeCycleAction.LOST:
                final_status = ActionStatus.LOST
            else:
                final_status = ActionStatus.FAILED
              
            # Creating a new entry.
            new_entry = GarbageLogEntry(
                track_id= selected_object.track_id,
                class_name= selected_object.class_name,
                age = selected_object.age,
                avg_confidence= selected_object.avg_confidence,
                priority_score= selected_object.priority_score,
                entity_role= selected_object.entity_role.name,
                decision_status= selected_object.decision_status.name,
                decision_reason= selected_object.decision_status.value,
                final_action_status= final_status.name
            )

            # Logging into the `garbage.csv` file.
            self.garbage_logger.log(new_entry)                  

            # Updating the logged_ids list with the new entry.
            self.logged_ids.add(selected_object.track_id)
            
            logger.info(f"OutcomeLogger -> log_selected_target(): ENDS")
            return 


        except Exception as e:
            logger.error(f"Error occured in OutcomeLogger -> log_selected_target(), error e: {e}")
            raise e