"""
Entities Module - Enemy Class
Handles enemy AI and behavior
"""

import pygame
import math
from settings import TILE_SIZE, MATERIALS


class Enemy:
    def __init__(self, x, y, enemy_type='basic'):
        self.position = [float(x), float(y)]
        self.velocity = [0.0, 0.0]
        self.enemy_type = enemy_type
        
        # Dimensions
        self.width = 24
        self.height = 28
        
        # Stats
        self.hp = 50 if enemy_type == 'basic' else 100
        self.max_hp = self.hp
        self.damage = 10
        self.speed = 80 if enemy_type == 'basic' else 120
        
        # State
        self.on_ground = False
        self.facing_right = True
        self.is_alive = True
        self.attack_cooldown = 0
        
        # AI state
        self.state = 'wander'  # wander, chase, attack
        self.wander_timer = 0
        self.target = None
        
        # Create sprite
        self._create_sprite()
    
    def _create_sprite(self):
        """Create enemy sprite"""
        self.sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        if self.enemy_type == 'basic':
            # Basic enemy - red creature
            pygame.draw.rect(self.sprite, (200, 50, 50), (2, 6, 20, 22))
            pygame.draw.circle(self.sprite, (255, 100, 100), (12, 8), 10)
            # Angry eyes
            pygame.draw.circle(self.sprite, (255, 255, 0), (8, 7), 3)
            pygame.draw.circle(self.sprite, (255, 255, 0), (16, 7), 3)
            pygame.draw.circle(self.sprite, (0, 0, 0), (8, 7), 1)
            pygame.draw.circle(self.sprite, (0, 0, 0), (16, 7), 1)
        else:
            # Strong enemy - purple creature
            pygame.draw.rect(self.sprite, (150, 50, 200), (2, 6, 20, 22))
            pygame.draw.circle(self.sprite, (200, 100, 255), (12, 8), 10)
            pygame.draw.circle(self.sprite, (255, 0, 255), (8, 7), 3)
            pygame.draw.circle(self.sprite, (255, 0, 255), (16, 7), 3)
    
    def get_sprite(self):
        """Get current sprite"""
        if self.facing_right:
            return self.sprite
        else:
            return pygame.transform.flip(self.sprite, True, False)
    
    def get_position(self):
        """Get current position"""
        return self.position
    
    def update(self, dt, world, player=None):
        """Update enemy AI and physics"""
        if not self.is_alive:
            return
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        # AI behavior
        self._update_ai(dt, player, world)
        
        # Apply gravity
        self.velocity[1] += 9.8 * 50 * dt
        
        # Update position
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        
        # Collision
        self._handle_collision(world)
        
        # Check ground
        self.on_ground = self._check_ground(world)
        if self.on_ground and self.velocity[1] > 0:
            self.velocity[1] = 0
    
    def _update_ai(self, dt, player, world):
        """Update AI behavior"""
        if player is None or not player.is_alive if hasattr(player, 'is_alive') else False:
            self.state = 'wander'
            self._wander(dt, world)
            return
        
        # Calculate distance to player
        dx = player.position[0] - self.position[0]
        dy = player.position[1] - self.position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        # State machine
        if distance < 40:
            self.state = 'attack'
            self._attack(dt, player)
        elif distance < 300:
            self.state = 'chase'
            self._chase(dt, player, world)
        else:
            self.state = 'wander'
            self._wander(dt, world)
    
    def _wander(self, dt, world):
        """Wander behavior"""
        self.wander_timer -= dt
        
        if self.wander_timer <= 0:
            # Choose new direction
            self.wander_timer = 2.0 + (hash(str(self.position)) % 100) / 100.0
            direction = 1 if (hash(str(self.position)) % 2) == 0 else -1
            self.velocity[0] = direction * self.speed * 0.3
            self.facing_right = direction > 0
            
            # Random jump
            if (hash(str(self.wander_timer)) % 3) == 0 and self.on_ground:
                self.velocity[1] = -200
    
    def _chase(self, dt, player, world):
        """Chase player"""
        dx = player.position[0] - self.position[0]
        
        if abs(dx) > 10:
            direction = 1 if dx > 0 else -1
            self.velocity[0] = direction * self.speed
            self.facing_right = direction > 0
        
        # Jump over obstacles
        if not self.on_ground:
            # Check if should jump
            check_x = int(self.position[0] + (20 if self.facing_right else -20))
            check_y = int(self.position[1] + self.height)
            if world.is_solid(check_x, check_y):
                self.velocity[1] = -250
    
    def _attack(self, dt, player):
        """Attack player"""
        if self.attack_cooldown <= 0:
            # Deal damage to player
            if player.take_damage(self.damage):
                pass  # Player died
            
            self.attack_cooldown = 1.0
    
    def _handle_collision(self, world):
        """Handle world collision"""
        check_points = [
            (self.position[0] + 4, self.position[1] + self.height - 2),
            (self.position[0] + self.width - 4, self.position[1] + self.height - 2),
            (self.position[0] - 2, self.position[1] + self.height // 2),
            (self.position[0] + self.width + 2, self.position[1] + self.height // 2),
        ]
        
        for px, py in check_points:
            if world.is_solid(int(px), int(py)):
                if px < self.position[0] + self.width // 2:
                    self.position[0] = px + 2
                    self.velocity[0] = 0
                else:
                    self.position[0] = px - self.width - 2
                    self.velocity[0] = 0
    
    def _check_ground(self, world):
        """Check if on ground"""
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
            self.is_alive = False
            return True  # Died
        return False
    
    def render_ui(self, screen, font):
        """Render enemy HP bar"""
        if self.hp < self.max_hp:
            hp_percent = self.hp / self.max_hp
            x, y = self.position
            pygame.draw.rect(screen, (100, 0, 0), (int(x), int(y) - 10, self.width, 5))
            pygame.draw.rect(screen, (200, 0, 0), (int(x), int(y) - 10, int(self.width * hp_percent), 5))
