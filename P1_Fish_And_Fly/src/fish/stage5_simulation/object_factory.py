
import pybullet as p

from src.common.logging import logger
#from src.common.projection.entity import WorldObject



def create_garbage(position, radius=0.15, color=(1, 0, 0, 1)) -> int:
    logger.info(f"create_garbage(): STARTS, position: {position}")

    visual = p.createVisualShape(
        p.GEOM_SPHERE,
        radius=radius,
        rgbaColor=color             # (1,0,0,1) -> red
    )

    collision = p.createCollisionShape(
        p.GEOM_SPHERE,
        radius=radius
    )

    body_id = p.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=collision,
        baseVisualShapeIndex=visual,
        basePosition=position
    )

    logger.info(f"create_garbage(): ENDS, body_id: {body_id}")
    return body_id

