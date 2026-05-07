import math
from turtle import distance
from typing import List, Optional

from src.common.logging import logger
from src.common.entity.position import Waypoint

from src.manatee.stage3_action.entity import ManateeNavigation



class BoundaryNavigator:
    """
    Intelligent boundary navigator for Manatee.

    Features:
    - Continuous boundary patrol
    - Shortest-path traversal (CW / CCW)
    - Target-based navigation on boundary
    """

    def __init__(self, navigation_config: ManateeNavigation):
        self.cfg = navigation_config

        self.start_position = self.cfg.start_point
        self.end_position = self.cfg.end_point

        self.min_x, self.min_y = 8, 8
        self.max_x, self.max_y = 112, 112
        self.z = 0

        self.speed = 2.0
        self.dt = 1.0
        self.reach_threshold = 1.0
        self.step_distance = self.speed * self.dt

        self.corners: List[Waypoint] = self.generate_boundary_loop()

        self.current_position = self.corners[0]
        self.edge_index = 0                                                                                 # current edge



    def generate_boundary_loop(self) -> List[Waypoint]:
        try:
            logger.debug(f"BoundaryNavigator -> generate_boundary_loop(): STARTS")

            path = [
                Waypoint(self.min_x, self.min_y, self.z),
                Waypoint(self.max_x, self.min_y, self.z),
                Waypoint(self.max_x, self.max_y, self.z),
                Waypoint(self.min_x, self.max_y, self.z)
            ]

            logger.debug(f"BoundaryNavigator -> generate_boundary_loop(): ENDS")
            return path


        except Exception as e:
            logger.error(f"Error occurred in BoundaryNavigator -> generate_boundary_loop(), error: {e}")
            raise e



    def step_boundary_edge(self):
        try:
            start_point = self.corners[self.edge_index]
            end_point = self.corners[(self.edge_index + 1) % 4]

            next_position = self.get_next_position_in_boundary_path(target_corner = end_point)

            # Change boundary edge, if Manatee reaches the current edge's end point(corner).
            if self.is_close(a= next_position, b= end_point):

                # Updating current boundary edge
                self.edge_index = (self.edge_index + 1) % 4

                # Snapping to the last corner point
                next_position = end_point

            logger.info(f"BoundaryNavigator -> step_boundary_edge(): ENDS, new_position: {next_position}")
            return next_position


        except Exception as e:
            logger.error(f"Error occurred in BoundaryNavigator -> step_boundary_edge(), error: {e}")
            raise e



    def get_next_position_in_boundary_path(self, target_corner: Waypoint):
        try:
            logger.info(f"BoundaryNavigator -> get_next_position_in_boundary_path(): STARTS, before pos: {self.current_position}")

            target_corner = self.corners[self.edge_index]

            dx = target_corner.x - self.current_position.x
            dy = target_corner.y - self.current_position.y
            
            distance = math.sqrt(dx*dx + dy*dy)

            # Snap to corner
            if distance <= self.step_distance:
                self.current_position = target_corner

                # Move to next edge
                self.edge_index = (self.edge_index+1) % len(self.corners)

                logger.info(f"Reached corner -> Switching to edge: {self.edge_index}")
                return self.current_position
            

            # Move only along axis (no diagonal)
            if abs(dx) > 0:
                step_x = self.step_distance if dx > 0 else -self.step_distance
                new_x = self.current_position.x + step_x
                new_y = self.current_position.y

            elif abs(dy) > 0:
                step_y = self.step_distance if dy > 0 else -self.step_distance
                new_x = self.current_position.x
                new_y = self.current_position.y + step_y

            else:
                return self.current_position                                                                # already at point
            

            new_pos = Waypoint(x= new_x, y= new_y, z= self.current_position.z)

            #self.current_position = new_pos

            logger.info(f"BoundaryNavigator -> get_next_position_in_boundary_path(): ENDS, new position: {new_pos}")
            return new_pos


        except Exception as e:
            logger.error(f"Error occurred in BoundaryNavigator -> get_next_position_in_boundary_path(), error: {e}")
            raise e



    def is_reached_destination(self, target_position: Waypoint) -> bool:
        try:
            is_reached = False
            if self.current_position == target_position:
                is_reached = True
            
            logger.info(f"BoundaryNavigator -> is_reached_destination(): ENDS, is_reached: {is_reached}") 
            return is_reached


        except Exception as e:
            logger.error(f"Error occurred in BoundaryNavigator -> is_reached_destination(), error: {e}")
            raise e
        
    

    def get_boundary_projection(self, point: Waypoint) -> Waypoint:
        """
        Project point to nearest boundary edge.
        """
        try:
            x, y = point.x, point.y
            projected_point: Waypoint

            dist_left = abs(x - self.min_x)
            dist_right = abs(x - self.max_x)
            dist_bottom = abs(y - self.min_y)
            dist_top = abs(y - self.max_y)

            min_dist = min(dist_left, dist_right, dist_bottom, dist_top)

            if min_dist == dist_left:
                projected_point = Waypoint(self.min_x, y, self.z)

            elif min_dist == dist_right:
                projected_point = Waypoint(self.max_x, y, self.z)

            elif min_dist == dist_bottom:
                projected_point = Waypoint(x, self.min_y, self.z)

            else:
                projected_point = Waypoint(x, self.max_y, self.z)
         
            logger.debug(f"BoundaryNavigator -> get_boundary_projection(), projected_point: {projected_point}")
            return projected_point


        except Exception as e:
            logger.error(f"Error occurred in BoundaryNavigator -> get_boundary_projection(), error: {e}")
            raise e
        


    def is_close(self, a: Waypoint, b: Waypoint):
        return math.hypot(a.x - b.x, a.y - b.y) <= self.reach_threshold
    


    def get_linear_step_to_destination(self, destination: Waypoint) -> Waypoint:
        try:
            logger.debug(f"BoundaryNavigator -> get_linear_step_to_destination(): STARTS")

            # Calculate direction vectors (3D), for DIRECT destination
            dx = destination.x - self.current_position.x
            dy = destination.y - self.current_position.y
            dz = destination.z - self.current_position.z

            # Distance between current position and the destination
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            logger.info(f"BoundaryNavigator -> get_linear_step_to_destination(): Distance between current position and the destination: {distance}")

            # If already reached very close to target waypoint and might overshoot in stepping, then snap to target waypoint and then approach next waypoint.
            if distance <= self.step_distance:
                
                # Snap to the current target first
                self.current_position = destination   
                
                logger.debug(f"BoundaryNavigator -> get_linear_step_to_destination(): Destination reached") 
                return destination                                                                                        
    
            # Normalize directions
            ux = dx / distance
            uy = dy / distance
            uz = dz / distance

            # Incremental motion
            new_x = self.current_position.x + ux * self.step_distance
            new_y = self.current_position.y + uy * self.step_distance
            new_z = self.current_position.z + uz * self.step_distance

            # New position for Fish machine
            new_position = Waypoint(new_x, new_y, new_z)            

            logger.debug(f"BoundaryNavigator -> get_linear_step_to_destination(): ENDS, new_position: {new_position}")
            return new_position


        except Exception as e:
            logger.error(f"Error occurred in BoundaryNavigator -> get_linear_step_to_destination(), error: {e}")
            raise e