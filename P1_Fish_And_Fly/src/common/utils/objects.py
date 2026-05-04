from typing import List, Dict, Set

from src.common.logging import logger
from src.common.projection.entity import FishFrameObject

from src.fish.stage2_decision.entity import CategorizedObjects



def get_all_tracked_objects(active_objects: Dict[int, FishFrameObject], categorized_objects: CategorizedObjects) -> List[FishFrameObject]:
    try:
        all_tracked_objects: List[FishFrameObject] = []

        # NOTE: This list of object doesn't contain objects with state = NEW, it filtered out in Stability filter (in Decision Module)
        # fish frame_objects = active objects (projected in fish frame)
        # categorized objects = subset of fish_frame_objects/active objects, filtered and categorized
        # total tracked objects = categorized objects + filtered out fish_fram_objects/active objects(eg: state = NEW)
        # Reason we can't use just fish_frame_objects is because we need decision_status of objects to correctly visualize them, 
        # which is received as categorized objects (from Decision module)
        
        # Flatten categorized objects
        all_categorized_objects: List[FishFrameObject] = (
            [obj for obj in categorized_objects.collection_targets] + 
            [obj for obj in categorized_objects.environment_entities] + 
            [obj for obj in categorized_objects.navigation_hazards]
        )

        # Build a set of track_ids (O(n), fastest lookup)
        categorized_objects_ids: Set[int] = {obj.track_id for obj in all_categorized_objects}

        # Merge efficiently
        # - keep categorized objects (they have decision_status)
        # - append only missing ones from fish_frame_objects
        all_tracked_objects = (
            all_categorized_objects +
            [obj for track_id, obj in active_objects.items() if track_id not in categorized_objects_ids]
        )
        
        logger.debug(f"get_all_tracked_objects(), all_tracked objects: {all_tracked_objects}")
        return all_tracked_objects


    except Exception as e:
        logger.error(f"Error occurred in get_all_tracked_objects(), error: {e}")
        raise e