import os
import csv
from pathlib import Path
from typing import Set, List
from datetime import datetime, timezone

from src.common.logging import logger
from src.common.logging.entity import ObjectLogEntry
from src.common.projection.entity import FishFrameObject
from src.common.entity.decision_types import DecisionStatus
from src.common.logging.object_csv_logger import ObjectLogEntry

from src.fish.stage1_vision.entity import TrackedGarbage, EntityRole
from src.fish.stage2_decision.entity import CategorizedObjects, LifeCycleAction, LifeCycleCommand
from src.fish.stage3_action.entity import ActionStatus



class ObjectCSVLogger:
    """
    Persistent garbage CSV for garbage lifecycle outcomes.
    """
    def __init__(self, output_file_path: Path, reset: bool = False):                                       # add output_dir and file_path as parameters
        self.file_path = Path(output_file_path)

        # create parent directory if not exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        if reset and self.file_path.exists():
            self.file_path.unlink()

        self._init_csv()
        
        self.logged_ids: Set[int] = set()                                                                   # list of track_ids of objects already logged. 
        self.counter: int = 0           # REMOVE LATER



    def _init_csv(self):
        """
        Creates a new csv file with the mentioned column names.
        
        :param self: Belongs to ObjectCSVLogger class.
        
        """
        if not os.path.exists(self.file_path):
            with open(self.file_path, mode = "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp",
                    "track_id",
                    "class_name",
                    "age",
                    "avg_confidence",
                    "priority_score",
                    "entity_role",
                    "decision_status",
                    "decision_reason",
                    "final_action_status"
                ])


    def log_object(self, new_entry: ObjectLogEntry):
        """
        Logs the attended/actioned item into the csv file.
        
        :param self: Belong to the ObjectCSVLogger class.
        """
        try:
            with open(self.file_path, mode= "a", newline= "") as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now(timezone.utc).isoformat(),
                    new_entry.track_id,
                    new_entry.class_name,
                    new_entry.age,
                    new_entry.avg_confidence,
                    new_entry.priority_score,
                    new_entry.entity_role,
                    new_entry.decision_status,
                    new_entry.decision_reason,
                    new_entry.final_action_status
                ])

            logger.info(f"ObjectCSVLogger -> log(), Recorded successfully: {new_entry.track_id}")   


        except Exception as e:
            logger.info(f"ObjectCSVLogger -> log(), Error occurred for new entry: {new_entry}, received error: {e}")
            raise e



    def log_lost_object(self, lost_objects: List[TrackedGarbage]):
        try:
            logger.info(f"ObjectCSVLogger -> log_lost_object(): STARTS, lost_objects: {lost_objects}")
                                                                                                                                         
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
                
                new_entry = ObjectLogEntry(
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
                self.log_object(new_entry)                  

                # Updating the logged_ids list with the new entry.
                self.logged_ids.add(obj.track_id)
            
            logger.info(f"ObjectCSVLogger -> log_lost_object(): ENDS")
            return 
        
        
        except Exception as e:
            logger.error(f"Error occured in ObjectCSVLogger -> log_lost_object(), error e: {e}")
            raise e
        


    def log_non_selectable_objects(self, categorized_objects: CategorizedObjects):
        try:
            logger.info(f"ObjectCSVLogger -> log_non_selectable_objects(): STARTS")
            
            # Log unsafe targets (target near hazard objects)
            for object in categorized_objects.collection_targets:
                # If already logged, then skip
                if object.track_id in self.logged_ids:
                    continue

                if object.decision_status == DecisionStatus.TARGET_AVOIDED:
                    new_entry = ObjectLogEntry(
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
                    self.log_object(new_entry)                  

                    # Updating the logged_ids list with the new entry.
                    self.logged_ids.add(object.track_id)


            # Log environment entities
            for object in categorized_objects.environment_entities:
                # If already logged, then skip
                if object.track_id in self.logged_ids:
                    continue

                new_entry = ObjectLogEntry(
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
                self.log_object(new_entry)                  

                # Updating the logged_ids list with the new entry.
                self.logged_ids.add(object.track_id)

            # Log navigation hazards
            for object in categorized_objects.navigation_hazards:
                # If already logged, then skip
                if object.track_id in self.logged_ids:
                    continue

                new_entry = ObjectLogEntry(
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
                self.log_object(new_entry)                  

                # Updating the logged_ids list with the new entry.
                self.logged_ids.add(object.track_id)
            

            logger.info(f"ObjectCSVLogger -> log_non_selectable_objects(): ENDS")
            return 
        

        except Exception as e:
            logger.error(f"Error occured in ObjectCSVLogger -> log_non_selectable_objects(), error: {e}")
            raise e



    def log_selected_target(self, selected_object: FishFrameObject, feedback_command: LifeCycleCommand):
        try:
            logger.info(f"ObjectCSVLogger -> log_selected_target(): STARTS")

            # Checking through a ONE TIME LOGGING GUARD, if so, skip logging.                               # refer ACTION_NOTES.md (3) 
            if selected_object.track_id in self.logged_ids:
                logger.info(f"ObjectCSVLogger -> log_selected_target(), This object is already logged, track_id: {selected_object.track_id}")
                return                                                                                                                                              
            
            # If the target is unattempted, then skip logging, as it is yet to be handled
            if feedback_command.action == LifeCycleAction.UNATTEMPTED:
                logger.info(f"ObjectCSVLogger -> log_selected_target(), Skip logging as this object is unattempted till now")
                return

            # Determining the target object's final status, according to the feedback command received.
            if feedback_command.action == LifeCycleAction.DONE:
                final_status = ActionStatus.COLLECTED
            elif feedback_command.action == LifeCycleAction.LOST:
                final_status = ActionStatus.LOST
            else:
                final_status = ActionStatus.FAILED
              
            # Creating a new entry.
            new_entry = ObjectLogEntry(
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
            self.log_object(new_entry)                  

            # Updating the logged_ids list with the new entry.
            self.logged_ids.add(selected_object.track_id)
            
            logger.info(f"ObjectCSVLogger -> log_selected_target(): ENDS")
            return 


        except Exception as e:
            logger.error(f"Error occured in ObjectCSVLogger -> log_selected_target(), error e: {e}")
            raise e