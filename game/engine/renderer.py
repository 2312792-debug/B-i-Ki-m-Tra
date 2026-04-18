"""
Engine Renderer Module
Handles all rendering operations with batch rendering and camera
"""

import pygame
import numpy as np
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, 
    MATERIAL_COLORS, WORLD_WIDTH, WORLD_HEIGHT,
    CAMERA_SMOOTHING, CAMERA_SHAKE_DECAY
)


class Camera:
    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        self.shake_x = 0
        self.shake_y = 0
        self.shake_intensity = 0
        
    def follow(self, target_x, target_y, dt):
        """Smoothly follow a target position"""
        target_cam_x = target_x - self.width // 2
        target_cam_y = target_y - self.height // 2
        
        # Smooth camera movement
        self.x += (target_cam_x - self.x) * CAMERA_SMOOTHING
        self.y += (target_cam_y - self.y) * CAMERA_SMOOTHING
        
        # Clamp to world bounds
        self.x = max(0, min(self.x, WORLD_WIDTH - self.width))
        self.y = max(0, min(self.y, WORLD_HEIGHT - self.height))
        
        # Apply shake decay
        if self.shake_intensity > 0.5:
            self.shake_x = (np.random.random() - 0.5) * self.shake_intensity
            self.shake_y = (np.random.random() - 0.5) * self.shake_intensity
            self.shake_intensity *= CAMERA_SHAKE_DECAY
        else:
            self.shake_x = 0
            self.shake_y = 0
            self.shake_intensity = 0
    
    def add_shake(self, intensity):
        """Add camera shake effect"""
        self.shake_intensity = max(self.shake_intensity, intensity)
    
    def apply(self):
        """Get the camera offset including shake"""
        return int(self.x + self.shake_x), int(self.y + self.shake_y)
    
    def world_to_screen(self, wx, wy):
        """Convert world coordinates to screen coordinates"""
        cam_x, cam_y = self.apply()
        return wx - cam_x, wy - cam_y
    
    def screen_to_world(self, sx, sy):
        """Convert screen coordinates to world coordinates"""
        cam_x, cam_y = self.apply()
        return sx + cam_x, sy + cam_y
    
    def get_visible_rect(self):
        """Get the visible world rectangle"""
        cam_x, cam_y = self.apply()
        return pygame.Rect(cam_x, cam_y, self.width, self.height)


class Renderer:
    def __init__(self, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Noita-like Physics Game")
        self.clock = pygame.time.Clock()
        
        self.camera = Camera(screen_width, screen_height)
        
        # Batch rendering surfaces
        self.world_surface = None
        self.entity_surface = None
        self.effect_surface = None
        
        # Lighting
        self.light_surface = None
        
        self._init_surfaces()
    
    def _init_surfaces(self):
        """Initialize rendering surfaces"""
        # Create world surface for terrain
        self.world_surface = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT), depth=32)
        self.world_surface.set_colorkey((0, 0, 0))
        
        # Entity surface for sprites
        self.entity_surface = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT), depth=32, flags=pygame.SRCALPHA)
        
        # Effect surface for particles and effects
        self.effect_surface = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT), depth=32, flags=pygame.SRCALPHA)
        
        # Lighting overlay
        self.light_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), depth=32, flags=pygame.SRCALPHA)
    
    def clear_world(self):
        """Clear the world surface"""
        self.world_surface.fill((0, 0, 0))
    
    def draw_pixel(self, x, y, material_id):
        """Draw a single pixel/tile"""
        if material_id not in MATERIAL_COLORS:
            return
            
        color = MATERIAL_COLORS[material_id]
        if color[3] == 0:  # Transparent
            return
            
        screen_x, screen_y = self.camera.world_to_screen(x, y)
        
        # Only draw if on screen
        if -TILE_SIZE <= screen_x < SCREEN_WIDTH and -TILE_SIZE <= screen_y < SCREEN_HEIGHT:
            rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
            
            if color[3] < 255:  # Semi-transparent
                s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                s.fill(color)
                self.screen.blit(s, rect)
            else:
                pygame.draw.rect(self.screen, color[:3], rect)
    
    def draw_pixels_batch(self, pixels_array, offset=(0, 0)):
        """Draw multiple pixels from a numpy array efficiently"""
        # This is optimized for chunk-based rendering
        pass  # Implemented in World class
    
    def draw_entity(self, entity):
        """Draw an entity (player, enemy, etc.)"""
        sprite = entity.get_sprite()
        pos = entity.get_position()
        screen_x, screen_y = self.camera.world_to_screen(pos[0], pos[1])
        
        # Only draw if on screen
        if (-sprite.get_width() <= screen_x < SCREEN_WIDTH and 
            -sprite.get_height() <= screen_y < SCREEN_HEIGHT):
            self.screen.blit(sprite, (screen_x, screen_y))
    
    def draw_particle(self, x, y, color, size=4, alpha=255):
        """Draw a particle effect"""
        screen_x, screen_y = self.camera.world_to_screen(x, y)
        
        if -size <= screen_x < SCREEN_WIDTH and -size <= screen_y < SCREEN_HEIGHT:
            s = pygame.Surface((size, size), pygame.SRCALPHA)
            color_with_alpha = (*color[:3], alpha)
            pygame.draw.circle(s, color_with_alpha, (size//2, size//2), size//2)
            self.screen.blit(s, (screen_x, screen_y))
    
    def draw_projectile(self, projectile):
        """Draw a projectile"""
        pos = projectile.position
        screen_x, screen_y = self.camera.world_to_screen(pos[0], pos[1])
        
        # Draw fireball or other projectile
        color = projectile.color if hasattr(projectile, 'color') else (255, 100, 0)
        radius = projectile.radius if hasattr(projectile, 'radius') else 8
        
        pygame.draw.circle(self.screen, color, (int(screen_x), int(screen_y)), radius)
    
    def setup_lighting(self):
        """Setup lighting system"""
        self.light_surface.fill((0, 0, 0, 200))  # Dark overlay
    
    def add_light(self, x, y, radius, intensity=255):
        """Add a light source"""
        screen_x, screen_y = self.camera.world_to_screen(x, y)
        
        # Create radial gradient for light
        gradient = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        center = (radius, radius)
        
        for r in range(radius, 0, -2):
            alpha = int(intensity * (r / radius))
            color = (255, 255, 200, alpha)
            pygame.draw.circle(gradient, color, center, r)
        
        # Cut hole in dark overlay
        self.light_surface.blit(gradient, (screen_x - radius, screen_y - radius), 
                               special_flags=pygame.BLEND_RGBA_SUB)
    
    def render_lighting(self):
        """Render lighting overlay"""
        self.screen.blit(self.light_surface, (0, 0))
    
    def render(self, world, entities, particles, projectiles):
        """Main render function"""
        # Clear screen
        self.screen.fill((20, 20, 40))  # Dark background
        
        # Render world terrain
        world.render(self)
        
        # Render entities
        for entity in entities:
            self.draw_entity(entity)
        
        # Render projectiles
        for proj in projectiles:
            self.draw_projectile(proj)
        
        # Render particles
        for particle in particles:
            self.draw_particle(particle.x, particle.y, particle.color, 
                             particle.size, particle.alpha)
        
        # Setup and render lighting
        self.setup_lighting()
        for entity in entities:
            if hasattr(entity, 'emits_light') and entity.emits_light:
                self.add_light(entity.position[0], entity.position[1], 60)
        for proj in projectiles:
            if proj.material_id == 5:  # Fire
                self.add_light(proj.position[0], proj.position[1], 40)
        self.render_lighting()
        
        # Update display
        pygame.display.flip()
    
    def tick(self, fps=60):
        """Control frame rate"""
        self.clock.tick(fps)
    
    def get_delta_time(self):
        """Get time since last frame in seconds"""
        return self.clock.get_time() / 1000.0
    
    def quit(self):
        """Cleanup"""
        pygame.quit()
