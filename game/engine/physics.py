"""
Engine Physics Module
Handles physics simulation using pymunk
"""

import pymunk
import pymunk.pygame_util
from settings import GRAVITY, TILE_SIZE


class PhysicsEngine:
    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = (0, GRAVITY)
        
        # Collision handlers
        self.collision_handlers = {}
        
        # Debug draw (optional)
        self.draw_options = None
        
    def create_body(self, body_type=pymunk.Body.DYNAMIC):
        """Create a new physics body"""
        body = pymunk.Body(body_type=body_type)
        return body
    
    def create_circle(self, body, radius, mass=1, collision_type=0):
        """Create a circle shape attached to a body"""
        moment = pymunk.moment_for_circle(mass, 0, radius)
        shape = pymunk.Circle(body, radius, offset=(0, 0))
        shape.mass = mass
        shape.friction = 0.5
        shape.collision_type = collision_type
        return shape
    
    def create_box(self, body, width, height, mass=1, collision_type=0):
        """Create a box shape attached to a body"""
        moment = pymunk.moment_for_box(mass, (width, height))
        shape = pymunk.Poly.create_box(body, (width, height))
        shape.mass = mass
        shape.friction = 0.7
        shape.collision_type = collision_type
        return shape
    
    def create_static_segment(self, p1, p2, collision_type=0):
        """Create a static line segment"""
        body = self.space.static_body
        shape = pymunk.Segment(body, p1, p2, TILE_SIZE // 2)
        shape.friction = 1.0
        shape.collision_type = collision_type
        return shape
    
    def add_body(self, body):
        """Add a body to the physics space"""
        self.space.add(body)
        
    def add_shape(self, shape):
        """Add a shape to the physics space"""
        self.space.add(shape)
        
    def remove_body(self, body):
        """Remove a body and its shapes from the physics space"""
        for shape in body.shapes:
            if shape in self.space.shapes:
                self.space.remove(shape)
        if body in self.space.bodies:
            self.space.remove(body)
    
    def update(self, dt):
        """Step the physics simulation"""
        # Fixed timestep for stability
        steps = 3
        sub_dt = dt / steps
        for _ in range(steps):
            self.space.step(sub_dt)
    
    def raycast(self, start, end):
        """Cast a ray and return hit information"""
        result = self.space.ray_cast(start, end)
        return result
    
    def query_point(self, point, radius=10):
        """Query shapes near a point"""
        shapes = self.space.point_query(point, radius)
        return shapes
    
    def setup_debug_render(self, surface):
        """Setup debug rendering"""
        self.draw_options = pymunk.pygame_util.DrawOptions(surface)
        
    def render_debug(self):
        """Render debug view of physics bodies"""
        if self.draw_options:
            self.space.debug_draw(self.draw_options)
