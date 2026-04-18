"""
Entities Module - Player Class
Handles player movement, physics, and rendering
"""

import pygame
import math
from settings import (
    PLAYER_SPEED, PLAYER_JUMP_FORCE, PLAYER_JETPACK_FORCE,
    PLAYER_MAX_HP, PLAYER_JETPACK_FUEL, PLAYER_JETPACK_CONSUMPTION,
    PLAYER_JETPACK_REGEN, TILE_SIZE, MATERIALS
)


class Player:
    def __init__(self, x, y):
        self.position = [float(x), float(y)]
        self.velocity = [0.0, 0.0]
        
        # Dimensions
        self.width = 24
        self.height = 32
        
        # Stats
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.jetpack_fuel = PLAYER_JETPACK_FUEL
        self.max_fuel = PLAYER_JETPACK_FUEL
        
        # State
        self.on_ground = False
        self.is_using_jetpack = False
        self.facing_right = True
        self.emits_light = True  # For lighting system
        
        # Animation
        self.animation_frame = 0
        self.animation_timer = 0
        
        # Create sprite
        self._create_sprite()
    
    def _create_sprite(self):
        """Create player sprite"""
        self.sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Body
        pygame.draw.rect(self.sprite, (100, 150, 255), (4, 8, 16, 20))
        # Head
        pygame.draw.circle(self.sprite, (255, 200, 150), (12, 6), 8)
        # Eyes
        pygame.draw.circle(self.sprite, (0, 0, 0), (10, 5), 2)
        pygame.draw.circle(self.sprite, (0, 0, 0), (14, 5), 2)
        # Jetpack
        pygame.draw.rect(self.sprite, (150, 150, 150), (0, 10, 4, 14))
    
    def get_sprite(self):
        """Get current sprite (with flip if facing left)"""
        if self.facing_right:
            return self.sprite
        else:
            return pygame.transform.flip(self.sprite, True, False)
    
    def get_position(self):
        """Get current position"""
        return self.position
    
    def handle_input(self, keys, mouse_buttons, mouse_pos):
        """Handle player input"""
        # Horizontal movement
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity[0] = -PLAYER_SPEED
            self.facing_right = False
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity[0] = PLAYER_SPEED
            self.facing_right = True
        else:
            self.velocity[0] *= 0.8  # Friction
        
        # Jump
        if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.velocity[1] = PLAYER_JUMP_FORCE
            self.on_ground = False
        
        # Jetpack
        self.is_using_jetpack = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        if self.is_using_jetpack and self.jetpack_fuel > 0:
            self.velocity[1] = max(self.velocity[1], PLAYER_JETPACK_FORCE * 0.5)
            self.jetpack_fuel -= PLAYER_JETPACK_CONSUMPTION
        elif not self.is_using_jetpack:
            self.jetpack_fuel = min(self.jetpack_fuel + PLAYER_JETPACK_REGEN, self.max_fuel)
    
    def apply_gravity(self, dt, gravity=9.8 * 50):
        """Apply gravity to player"""
        self.velocity[1] += gravity * dt
    
    def update(self, dt, world):
        """Update player physics and collision"""
        # Apply gravity
        self.apply_gravity(dt)
        
        # Update position
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        
        # World collision
        self._handle_world_collision(world)
        
        # World bounds
        self.position[0] = max(0, min(self.position[0], 2048 - self.width))
        self.position[1] = max(0, min(self.position[1], 1024 - self.height))
        
        # Check if on ground
        self.on_ground = self._check_ground(world)
        
        # Reset vertical velocity if on ground
        if self.on_ground and self.velocity[1] > 0:
            self.velocity[1] = 0
    
    def _handle_world_collision(self, world):
        """Handle collision with world terrain"""
        # Simple AABB collision with terrain
        check_points = [
            (self.position[0] + 4, self.position[1] + self.height - 2),  # Bottom left
            (self.position[0] + self.width - 4, self.position[1] + self.height - 2),  # Bottom right
            (self.position[0] + 4, self.position[1] + 4),  # Top left
            (self.position[0] + self.width - 4, self.position[1] + 4),  # Top right
            (self.position[0] - 2, self.position[1] + self.height // 2),  # Left
            (self.position[0] + self.width + 2, self.position[1] + self.height // 2),  # Right
        ]
        
        for px, py in check_points:
            if world.is_solid(int(px), int(py)):
                # Push back
                if py > self.position[1] + self.height - 10:  # Bottom collision
                    self.position[1] = py - self.height + 2
                    self.velocity[1] = 0
                elif py < self.position[1] + 10:  # Top collision
                    self.position[1] = py + 2
                    self.velocity[1] = 0
                elif px < self.position[0] + self.width // 2:  # Left collision
                    self.position[0] = px + 2
                    self.velocity[0] = 0
                else:  # Right collision
                    self.position[0] = px - self.width - 2
                    self.velocity[0] = 0
    
    def _check_ground(self, world):
        """Check if player is on ground"""
        check_y = int(self.position[1] + self.height + 2)
        check_x_left = int(self.position[0] + 4)
        check_x_right = int(self.position[0] + self.width - 4)
        
        return (world.is_solid(check_x_left, check_y) or 
                world.is_solid(check_x_right, check_y))
    
    def take_damage(self, amount):
        """Take damage"""
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            return True  # Dead
        return False
    
    def heal(self, amount):
        """Heal player"""
        self.hp = min(self.hp + amount, self.max_hp)
    
    def render_ui(self, screen, font):
        """Render player UI (HP, fuel)"""
        # HP bar
        hp_percent = self.hp / self.max_hp
        pygame.draw.rect(screen, (100, 0, 0), (10, 10, 200, 20))
        pygame.draw.rect(screen, (0, 200, 0), (10, 10, int(200 * hp_percent), 20))
        hp_text = font.render(f"HP: {int(self.hp)}/{self.max_hp}", True, (255, 255, 255))
        screen.blit(hp_text, (15, 12))
        
        # Fuel bar
        fuel_percent = self.jetpack_fuel / self.max_fuel
        pygame.draw.rect(screen, (50, 50, 100), (10, 35, 200, 15))
        pygame.draw.rect(screen, (200, 200, 0), (10, 35, int(200 * fuel_percent), 15))
        fuel_text = font.render(f"Fuel: {int(self.jetpack_fuel)}%", True, (255, 255, 255))
        screen.blit(fuel_text, (15, 37))
    
    def shoot(self, target_x, target_y):
        """Shoot a projectile toward target"""
        from systems.combat import Projectile
        
        # Calculate direction
        dx = target_x - (self.position[0] + self.width // 2)
        dy = target_y - (self.position[1] + self.height // 2)
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            dx /= distance
            dy /= distance
            
            start_x = self.position[0] + self.width // 2
            start_y = self.position[1] + self.height // 2
            
            return Projectile(start_x, start_y, dx * 400, dy * 400, MATERIALS['FIRE'])
        
        return None
