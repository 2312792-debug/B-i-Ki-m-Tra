"""
Main Game File - Noita-like Physics Game
A 2D pixel physics sandbox game inspired by Noita
"""

import pygame
import sys
import random
import math

# Import game modules
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    WORLD_WIDTH, WORLD_HEIGHT, TILE_SIZE,
    MATERIALS, MATERIAL_COLORS
)
from engine.renderer import Renderer
from engine.world import World
from engine.physics import PhysicsEngine
from entities.player import Player
from entities.enemy import Enemy
from systems.combat import CombatSystem
from systems.sand_simulation import SandSimulation


class Game:
    def _spawn_player(self):
        """Spawn player at a safe position"""
        # Tìm vị trí an toàn để spawn player
        spawn_x = 100
        spawn_y = 0
        
        # Tìm mặt đất từ trên xuống
        for y in range(0, WORLD_HEIGHT - 50):
            if self.world.is_solid(spawn_x, y) and self.world.is_solid(spawn_x + 20, y):
                spawn_y = y - 40  # Spawn phía trên mặt đất
                break
        
        # Nếu không tìm thấy, spawn ở vị trí mặc định an toàn
        if spawn_y == 0:
            spawn_y = 400
        
        self.player = Player(spawn_x, spawn_y)
    
    def __init__(self):
        # Initialize renderer
        self.renderer = Renderer(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Create world
        self.world = World()
        
        # Create physics engine
        self.physics = PhysicsEngine()
        
        # Create player at safe position
        self._spawn_player()
        
        # Create combat system
        self.combat = CombatSystem()
        
        # Create enemies
        self.enemies = []
        self._spawn_enemies()
        
        # Font for UI
        self.font = pygame.font.Font(None, 36)
        
        # Game state
        self.running = True
        self.paused = False
        self.game_over = False
        
        # Debug mode
        self.debug_mode = False
        
        # Mouse state
        self.mouse_held = False
        self.current_material = MATERIALS['SAND']
    
    def _spawn_enemies(self):
        """Spawn some enemies in the world"""
        enemy_positions = [
            (400, 500),
            (600, 450),
            (800, 500),
            (1000, 400),
        ]
        
        for x, y in enemy_positions:
            enemy_type = random.choice(['basic', 'basic', 'strong'])
            self.enemies.append(Enemy(x, y, enemy_type))
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                
                elif event.key == pygame.K_F1:
                    self.debug_mode = not self.debug_mode
                
                # Weapon switching
                elif event.key == pygame.K_1:
                    self.combat.switch_weapon('fireball')
                elif event.key == pygame.K_2:
                    self.combat.switch_weapon('water_bolt')
                elif event.key == pygame.K_3:
                    self.combat.switch_weapon('acid_blob')
                
                # Material selection for sandbox mode
                elif event.key == pygame.K_s:
                    self.current_material = MATERIALS['SAND']
                elif event.key == pygame.K_w:
                    self.current_material = MATERIALS['WATER']
                elif event.key == pygame.K_l:
                    self.current_material = MATERIALS['LAVA']
                elif event.key == pygame.K_t:
                    self.current_material = MATERIALS['STONE']
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.mouse_held = True
                    self._handle_mouse_click()
                elif event.button == 3:  # Right click
                    # Shoot projectile
                    mx, my = pygame.mouse.get_pos()
                    wx, wy = self.renderer.camera.screen_to_world(mx, my)
                    
                    px, py = self.player.get_position()
                    self.combat.shoot(
                        px + self.player.width // 2,
                        py + self.player.height // 2,
                        wx, wy
                    )
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_held = False
    
    def _handle_mouse_click(self):
        """Handle left mouse click - place material or destroy terrain"""
        mx, my = pygame.mouse.get_pos()
        wx, wy = self.renderer.camera.screen_to_world(mx, my)
        
        # Check if holding shift - destroy terrain
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            # Destroy terrain
            self.world.create_explosion(wx, wy, 10)
            self.renderer.camera.add_shake(3)
        else:
            # Place material
            radius = 5 if self.current_material == MATERIALS['WATER'] else 3
            self.world.set_pixel(wx, wy, self.current_material)
            
            # Place multiple pixels for better effect
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if dx * dx + dy * dy <= radius * radius:
                        self.world.set_pixel(int(wx + dx), int(wy + dy), self.current_material)
    
    def update(self, dt):
        """Update game logic"""
        if self.paused or self.game_over:
            return
        
        # Update player
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        
        self.player.handle_input(keys, mouse_buttons, mouse_pos)
        self.player.update(dt, self.world)
        
        # Update camera to follow player
        px, py = self.player.get_position()
        self.renderer.camera.follow(px + self.player.width // 2, 
                                    py + self.player.height // 2, dt)
        
        # Update active chunks
        self.world.update_active_chunks(px, py)
        
        # Update world simulation
        self.world.simulate_pixels(dt, px, py)
        
        # Update combat system
        self.combat.update(dt, self.world)
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update(dt, self.world, self.player)
        
        # Remove dead enemies
        self.enemies = [e for e in self.enemies if e.is_alive]
        
        # Spawn new enemies occasionally
        if random.random() < 0.001 and len(self.enemies) < 10:
            angle = random.random() * 3.14159 * 2
            dist = random.uniform(200, 400)
            ex = px + int(math.cos(angle) * dist)
            ey = py + int(math.sin(angle) * dist)
            ex = max(0, min(ex, WORLD_WIDTH - 50))
            ey = max(0, min(ey, WORLD_HEIGHT - 50))
            self.enemies.append(Enemy(ex, ey))
        
        # Continuous mouse placement
        if self.mouse_held:
            self._handle_mouse_click()
        
        # Check game over
        if self.player.hp <= 0:
            self.game_over = True
    
    def render(self):
        """Render the game"""
        self.renderer.render(
            self.world,
            [self.player] + self.enemies,
            self.combat.particles,
            self.combat.projectiles
        )
        
        # Render UI
        self.player.render_ui(self.renderer.screen, self.font)
        
        # Render weapon info
        weapon_info = self.combat.get_weapon_info()
        weapon_text = self.font.render(
            f"Weapon: {self.combat.current_weapon}", 
            True, (255, 255, 255)
        )
        self.renderer.screen.blit(weapon_text, (10, SCREEN_HEIGHT - 40))
        
        # Render material info
        mat_name = [k for k, v in MATERIALS.items() if v == self.current_material][0]
        mat_text = self.font.render(f"Material: {mat_name}", True, (255, 255, 255))
        self.renderer.screen.blit(mat_text, (10, SCREEN_HEIGHT - 70))
        
        # Render debug info
        if self.debug_mode:
            fps = self.renderer.clock.get_fps()
            debug_texts = [
                f"FPS: {fps:.1f}",
                f"Player: ({int(px)}, {int(py)})",
                f"Enemies: {len(self.enemies)}",
                f"Projectiles: {len(self.combat.projectiles)}",
                f"Particles: {len(self.combat.particles)}",
            ]
            for i, text in enumerate(debug_texts):
                surf = self.font.render(text, True, (0, 255, 0))
                self.renderer.screen.blit(surf, (SCREEN_WIDTH - 200, 10 + i * 25))
        
        # Render game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.renderer.screen.blit(overlay, (0, 0))
            
            go_text = self.font.render("GAME OVER", True, (255, 0, 0))
            restart_text = self.font.render("Press R to restart", True, (255, 255, 255))
            
            self.renderer.screen.blit(go_text, 
                                     (SCREEN_WIDTH // 2 - go_text.get_width() // 2, 
                                      SCREEN_HEIGHT // 2 - 30))
            self.renderer.screen.blit(restart_text,
                                     (SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                                      SCREEN_HEIGHT // 2 + 10))
        
        # Render pause screen
        if self.paused and not self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            self.renderer.screen.blit(overlay, (0, 0))
            
            pause_text = self.font.render("PAUSED", True, (255, 255, 255))
            self.renderer.screen.blit(pause_text,
                                     (SCREEN_WIDTH // 2 - pause_text.get_width() // 2,
                                      SCREEN_HEIGHT // 2))
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        
        while self.running:
            dt = clock.tick(FPS) / 1000.0
            
            # Handle restart
            if self.game_over:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_r]:
                    self.__init__()
                    continue
            
            self.handle_events()
            self.update(dt)
            self.render()
        
        self.renderer.quit()


def main():
    """Entry point"""
    print("=" * 50)
    print("Noita-like Physics Game")
    print("=" * 50)
    print("\nControls:")
    print("  WASD/Arrows - Move")
    print("  Space/W - Jump")
    print("  Shift - Jetpack / Destroy terrain (with mouse)")
    print("  Left Click - Place material")
    print("  Right Click - Shoot fireball")
    print("  1/2/3 - Switch weapons")
    print("  S/W/L/T - Select material (Sand/Water/Lava/Stone)")
    print("  P - Pause")
    print("  F1 - Toggle debug mode")
    print("  ESC - Quit")
    print("=" * 50)
    
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
