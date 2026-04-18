"""
Systems Module - Combat System
Handles projectiles, weapons, and combat mechanics
"""

import pygame
import math
from settings import (
    FIREBALL_SPEED, FIREBALL_DAMAGE, FIREBALL_LIFETIME,
    MATERIALS, MATERIAL_COLORS, TILE_SIZE
)


class Projectile:
    def __init__(self, x, y, vx, vy, material_id=MATERIALS['FIRE']):
        self.position = [float(x), float(y)]
        self.velocity = [float(vx), float(vy)]
        self.material_id = material_id
        self.lifetime = FIREBALL_LIFETIME
        self.max_lifetime = FIREBALL_LIFETIME
        self.damage = FIREBALL_DAMAGE
        self.radius = 8
        self.is_active = True
        
        # Set color based on material
        if material_id == MATERIALS['FIRE']:
            self.color = (255, 100, 0)
        elif material_id == MATERIALS['WATER']:
            self.color = (64, 164, 223)
        elif material_id == MATERIALS['ACID']:
            self.color = (124, 252, 0)
        else:
            self.color = (255, 255, 255)
    
    def update(self, dt, world):
        """Update projectile physics"""
        # Apply gravity slightly
        self.velocity[1] += 50 * dt
        
        # Update position
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        
        # Decrease lifetime
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.is_active = False
            return
        
        # Check collision with terrain
        px, py = int(self.position[0]), int(self.position[1])
        
        # Check multiple points around projectile
        for dx in [-self.radius, 0, self.radius]:
            for dy in [-self.radius, 0, self.radius]:
                if world.is_solid(px + dx, py + dy):
                    self.on_hit(world, px, py)
                    return
    
    def on_hit(self, world, x, y):
        """Handle projectile hitting terrain"""
        self.is_active = False
        
        # Create explosion or effect based on material
        if self.material_id == MATERIALS['FIRE']:
            # Fire explosion
            world.create_explosion(x, y, 15)
            # Maybe ignite nearby flammable materials
        elif self.material_id == MATERIALS['WATER']:
            # Water splash
            world.create_explosion(x, y, 8)
            # Add water particles
        elif self.material_id == MATERIALS['ACID']:
            # Acid腐蚀
            world.create_explosion(x, y, 12)
    
    def render(self, renderer):
        """Render projectile"""
        renderer.draw_projectile(self)


class Particle:
    def __init__(self, x, y, vx, vy, color, size=4, lifetime=1.0):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.alpha = 255
        self.is_active = True
    
    def update(self, dt):
        """Update particle"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 20 * dt  # Gravity
        
        self.lifetime -= dt
        self.alpha = int(255 * (self.lifetime / self.max_lifetime))
        
        if self.lifetime <= 0:
            self.is_active = False
    
    def render(self, renderer):
        """Render particle"""
        renderer.draw_particle(self.x, self.y, self.color, self.size, self.alpha)


class CombatSystem:
    def __init__(self):
        self.projectiles = []
        self.particles = []
        
        # Weapon types
        self.weapons = {
            'fireball': {'damage': 25, 'speed': 400, 'cooldown': 0.3},
            'water_bolt': {'damage': 10, 'speed': 500, 'cooldown': 0.2},
            'acid_blob': {'damage': 35, 'speed': 300, 'cooldown': 0.5},
        }
        
        self.current_weapon = 'fireball'
        self.weapon_cooldown = 0
    
    def spawn_projectile(self, x, y, vx, vy, material_id):
        """Spawn a new projectile"""
        proj = Projectile(x, y, vx, vy, material_id)
        self.projectiles.append(proj)
        return proj
    
    def spawn_particles(self, x, y, count, color, speed_range=(50, 150)):
        """Spawn particle effects"""
        import random
        for _ in range(count):
            angle = random.random() * 3.14159 * 2
            speed = random.uniform(*speed_range)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            particle = Particle(x, y, vx, vy, color, 
                              size=random.randint(2, 5),
                              lifetime=random.uniform(0.5, 1.5))
            self.particles.append(particle)
    
    def shoot(self, x, y, target_x, target_y, weapon_type=None):
        """Shoot from position toward target"""
        if weapon_type is None:
            weapon_type = self.current_weapon
        
        if self.weapon_cooldown > 0:
            return None
        
        weapon = self.weapons.get(weapon_type, self.weapons['fireball'])
        
        # Calculate direction
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            dx /= distance
            dy /= distance
            
            # Determine material based on weapon
            if weapon_type == 'fireball':
                material = MATERIALS['FIRE']
            elif weapon_type == 'water_bolt':
                material = MATERIALS['WATER']
            elif weapon_type == 'acid_blob':
                material = MATERIALS['ACID']
            else:
                material = MATERIALS['FIRE']
            
            speed = weapon['speed']
            proj = self.spawn_projectile(
                x, y, 
                dx * speed, dy * speed,
                material
            )
            
            self.weapon_cooldown = weapon['cooldown']
            
            # Spawn muzzle flash particles
            self.spawn_particles(x, y, 5, (255, 200, 50), speed_range=(100, 200))
            
            return proj
        
        return None
    
    def update(self, dt, world):
        """Update all projectiles and particles"""
        # Update cooldown
        if self.weapon_cooldown > 0:
            self.weapon_cooldown -= dt
        
        # Update projectiles
        for proj in self.projectiles[:]:
            proj.update(dt, world)
            if not proj.is_active:
                self.projectiles.remove(proj)
        
        # Update particles
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.is_active:
                self.particles.remove(particle)
    
    def render(self, renderer):
        """Render all combat elements"""
        for proj in self.projectiles:
            proj.render(renderer)
        
        for particle in self.particles:
            particle.render(renderer)
    
    def switch_weapon(self, weapon_name):
        """Switch current weapon"""
        if weapon_name in self.weapons:
            self.current_weapon = weapon_name
            return True
        return False
    
    def get_weapon_info(self):
        """Get current weapon info"""
        return self.weapons.get(self.current_weapon, {})
