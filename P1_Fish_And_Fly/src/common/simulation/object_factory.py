import pybullet as p
from typing import Tuple, Optional

from src.common.logging import logger
from src.common.simulation.entity import SpawnObject
from src.common.simulation.constants import SHAPE_MAP


def create_body(body_info: SpawnObject, position: Tuple[float, float, float], orientation: Optional[Tuple[float,float,float,float]]) -> int:
    try:
        logger.info(f"create_body(): STARTS, body_info: {body_info}, position: {position}")

        shape, size, color = body_info.shape, body_info.size, body_info.color

        curr_orientation = orientation if orientation else (0.0, 0.0, 0.0, 1.0)

        # Retrieve shape type
        shape_type = SHAPE_MAP.get(shape)
        if shape_type is None:
            logger.info(f"Unsupported shape: {shape}")
            return -1 

        # Deceiding visual and collision according to the shape
        if shape == "sphere":
            radius = size[0]

            visual = p.createVisualShape(
                shapeType = shape_type,
                radius = radius,
                rgbaColor = color
            )

            collision = p.createCollisionShape(
                shapeType = shape_type,
                radius = radius
            )


        elif shape == "box":
            visual = p.createVisualShape(
                shapeType = shape_type,
                halfExtents = size
            )

            collision = p.createCollisionShape(
                shapeType = shape_type,
                halfExtents = size
            )

        elif shape in ["capsule", "cylinder"]:
            radius = size[0]
            height = size[1]

            visual = p.createVisualShape(
                shapeType = shape_type,
                radius = radius,
                length = height,
                rgbaColor = color
            )

            collision = p.createCollisionShape(
                shapeType = shape_type,
                radius = radius,
                height = height
            )


        else:
            logger.info(f"Shape logic not implemented: {shape}")
            return -1
        
        body_id = p.createMultiBody(
            baseMass = 0.0,
            baseCollisionShapeIndex = collision,
            baseVisualShapeIndex = visual,
            basePosition = position,
            baseOrientation = curr_orientation
        )

        logger.info(f"create_body(): ENDS,  visual:{visual}, collision: {collision}, position: {position}, body_id: {body_id}")
        return body_id


    except Exception as e:
        logger.info(f"Error occurred in create_body(), error: {e}")
        raise e