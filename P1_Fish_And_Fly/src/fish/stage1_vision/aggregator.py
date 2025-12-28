from typing import List, Dict, Tuple

from src.common.logging import logger
from src.fish.stage1_vision.entity import Detection, TrackedGarbage, TrackedState
from src.fish.stage2_decision.command import LifeCycleCommand, LifeCycleAction


class GarbageAggregator:
    """
    Aggregates detections over time using track_id
    """
    def __init__(self, aggregator_cfg):
        self.max_history = aggregator_cfg.max_history
        self.stable_age = aggregator_cfg.stable_age
        self.max_idle_frames = aggregator_cfg.max_idle_frames

        self.frame_count = 0
        self.memory: Dict[int, TrackedGarbage] = {}                             # lifecycle memory


    def _cleanup_memory(self):
        """
        Remove collected(DONE) and long lost(LOST) objects from memory.
        
        :param self: Belongs to GarbageAggregator class.
        """
        logger.info(f"cleanup_memory(): STARTS, before memory cleanup n(items): {len(self.memory.items())}")

        ids_to_remove = []

        for track_id, tracked_object in self.memory.items():
            if tracked_object.state == TrackedState.DONE:
                ids_to_remove.append(track_id)

            elif tracked_object.state == TrackedState.LOST:
                idle_frame = self.frame_count - tracked_object.last_seen_frame
                if idle_frame > self.max_idle_frames * 2:                       # Gives tracker time to re-identify
                    ids_to_remove.append(track_id)

        # Removing the collected / lost objects from the memory
        for track_id in ids_to_remove:
            del self.memory[track_id]

        logger.info(f"cleanup_memory(): IDS_TO_REMOVE: : {ids_to_remove}")
        logger.info(f"cleanup_memory(): ENDS, after memory cleanup n(intems): {len(self.memory.items())}")
        return
    


    def create_garbage_aggregations(self, detections: List[Detection]) -> List[TrackedGarbage]:
        """
        Create garbage aggregations from raw object detections, received from YOLO.

        Update tracked garbage memory with new detections.

        Handles lifecycle transitions except states: SELECTED and DONE.
        
        :param self: Belongs to GarbageAggregator class
        :param detections: List of tracked garbage detections, received from YOLO.
        :type detections: List[Detection]
        :return: List of Tracked Garbage aggregations, created from detections(I/P)
        :rtype: List[TrackedGarbage]
        """
        logger.info(f"GarbageAggregator -> create_garbage_aggregations(): STARTS, initial detections: {detections}")

        self.frame_count += 1

        active_track_ids = set()

        # ----------------------------------Create / Update tracked objects-----------------------------
        for det in detections:
            track_id: int = det.track_id
            det_bbox: Tuple[int, int, int, int] = tuple(det.bbox)
            active_track_ids.add(track_id)                                          # to keep track of active objects

            # Creating a new object
            if track_id not in self.memory:
                tracked_object = TrackedGarbage(
                    track_id = track_id,
                    class_id = det.class_id,
                    class_name = det.class_name,
                    avg_confidence = det.confidence,
                    bbox = det_bbox,
                    age = 1,
                    last_seen_frame = self.frame_count,
                    state = TrackedState.NEW
                )

                self.memory[track_id] = tracked_object
                continue

            # Updating stats for old object
            tracked_object = self.memory[track_id]
            tracked_object.age += 1
            tracked_object.last_seen_frame = self.frame_count
            tracked_object.bbox = det_bbox
            tracked_object.avg_confidence = ( (tracked_object.avg_confidence*(tracked_object.age - 1)) + det.confidence ) / tracked_object.age

            # State transforamtion: [NEW -> STABLE] Promotion
            if tracked_object.state == TrackedState.NEW and tracked_object.age >= self.stable_age:
                tracked_object.state = TrackedState.STABLE

        logger.info(f"create_garbage_aggregations(): , tracked_objects= {len(self.memory)}")

        # --------------------------------------Handle missing objects--------------------------------
        for track_id, tracked_object in list(self.memory.items()):
            if track_id in active_track_ids:
               continue

            # finding for how long the object is missing, using formula (current frame - last seen frame)
            idle_frame = self.frame_count - tracked_object.last_seen_frame
            
            # State transformation: [any state -> LOST]
            if idle_frame > self.max_idle_frames:
                # Vision can mark the state to LOST
                if tracked_object.state != TrackedState.DONE:                       # the object is not collected yet.
                    tracked_object.state = TrackedState.LOST
                    logger.info(f"marked lost: track_id: {track_id}")
                
        
        # ----------------Cleanup of collected(state = DONE) and old lost(state = LOST) objects-------
        self._cleanup_memory()

        # Taking active objects from the memory.
        active_objects = [obj for obj in self.memory.values() if obj.state not in (TrackedState.DONE, TrackedState.LOST)]

        logger.info(f"GarbageAggregator -> create_garbage_aggregations() -> Active tracked garbage: {len(active_objects)}")
        logger.info("GarbageAggregator -> create_garbage_aggregations(): ENDS")

        for obj in self.memory.values():
            logger.info(
                f"[TRACK {obj.track_id}] "
                f"state={obj.state.value}, "
                f"age={obj.age}, "
                f"last_seen={obj.last_seen_frame}"
            )

        return active_objects


    def apply_lifecycle_changes(self, command: LifeCycleCommand):
        """
        Applies lifecycle changes to the tracked garbage aggregations, according to the command from Decision module.
        
        Marks object's state as SELECTED or DONE. 

        :param self: Belongs to the GarbageAggregator class.
        :param command: Command received from Decision module to make lifecycle state transitions in Vision module.
        :type command: LifeCycleCommand {action:LifeCycleAction, track_id: int}
        """
        logger.info(f"GarbageAggregator -> apply_lifecycle_changes(): STARTS, command recieved: {command}")

        if command is None:
            return

        track_id = command.track_id

        # if the selected target is not present in the aggregation memory(i.e. the object is LOST/DONE)
        if track_id not in self.memory:
            logger.info(f"locked object is not present in the aggregation memory(LOST/DONE)")
            return
        
        selected_object = self.memory[track_id]

        if command.action == LifeCycleAction.SELECT:
            selected_object.state = TrackedState.SELECTED                           # automatically updated in aggregation memory(pass by reference)
            logger.info(f"track_id: {track_id} set to SELECTED")

        elif command.action == LifeCycleAction.MARK_DONE:
            selected_object.state = TrackedState.DONE
            logger.info(f"track_id: {track_id} set to DONE")

        elif command.action == LifeCycleAction.LOST:
            selected_object.state = TrackedState.LOST
            logger.info(f"track_id: {track_id} set to LOST")
            
        # NOTE: No need to update the memory with selected object's state bcz `Objects in Python are passed by reference, not by value`.
        logger.info(f"GarbageAggregator -> apply_lifecycle_changes(): ENDS, checking memory updation: {self.memory[track_id].state}")
        return


