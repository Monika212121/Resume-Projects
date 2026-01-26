from typing import List, Set

from src.common.logging import logger
from src.fish.stage1_vision.entity import TrackedGarbage
from src.fish.stage1_vision.aggregator import TrackedState


class StableObjectFilter:
    """
    Filters only STABLE tracked objects, for decision making. 
    """
    def filter_detections(self, tracked_objects: List[TrackedGarbage]) -> List[TrackedGarbage]:
        logger.info(f"StableObjectFilter-> filter_detections() STARTS: before filtering n(objects): {len(tracked_objects)}")

        stable_objects = [obj for obj in tracked_objects if obj.state == TrackedState.STABLE]

        logger.info(f"StableObjectFilter-> filter_detections() ENDS: after filtering n(objects): {len(stable_objects)}")
        return stable_objects
    


    '''
    def filter_done_objects(self, tracked_objects: List[TrackedGarbage], done_ids: Set[int]) -> List[TrackedGarbage]:
        logger.info(f"StableObjectFilter-> filter_done_objects() STARTS: before filtering n(all tracked_objects): {len(tracked_objects)}")

        new_objects = [obj for obj in tracked_objects if obj.track_id not in done_ids]

        logger.info(f"StableObjectFilter-> filter_done_objects() ENDS: after filtering n(new_objects): {len(new_objects)}")
        return new_objects
    '''