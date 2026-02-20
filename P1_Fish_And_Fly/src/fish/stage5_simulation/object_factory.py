
import pybullet as p
from src.common.logging import logger


def create_garbage_body(position, radius = 0.30, color = (0.8, 0.2, 0.2, 1.0)) -> int:
    logger.info(f"create_garbage_body(): position: {position}, radius: {radius}, color: {color}")


    visual = p.createVisualShape(
        p.GEOM_SPHERE,
        radius=radius,
        rgbaColor=color,
    )

    collision = p.createCollisionShape(
        p.GEOM_SPHERE,
        radius=radius,
    )

    body_id = p.createMultiBody(
        baseMass=0.0,
        baseCollisionShapeIndex=collision,
        baseVisualShapeIndex=visual,
        basePosition=position,
    )

    logger.info(f"create_garbage_body(), visual: {visual}, collision: {collision}, body_id: {body_id}")
    return body_id

