"""
Engine World Module
Handles world generation, chunk system, and pixel-based terrain
"""

import pygame
import numpy as np
import random
import math
from settings import (
    WORLD_WIDTH, WORLD_HEIGHT, TILE_SIZE, CHUNK_SIZE,
    MATERIALS, MATERIAL_PROPS, UPDATE_RADIUS, MATERIAL_COLORS
)


class SimpleNoise:
    """Simple permutation-based noise generator - thay thế cho thư viện noise"""
    
    def __init__(self, seed: int = 0):
        self.seed = seed
        random.seed(seed)
        # Tạo permutation table
        self.perm = list(range(256))
        random.shuffle(self.perm)
        self.perm = np.array(self.perm + self.perm)  # Double for wrapping
    
    def _fade(self, t: float) -> float:
        """Smoothstep function"""
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def _lerp(self, a: float, b: float, t: float) -> float:
        """Linear interpolation"""
        return a + t * (b - a)
    
    def _grad(self, hash_val: int, x: float, y: float) -> float:
        """Calculate gradient"""
        h = hash_val & 3
        if h == 0:
            return x + y
        elif h == 1:
            return -x + y
        elif h == 2:
            return x - y
        else:
            return -x - y
    
    def noise2d(self, x: float, y: float) -> float:
        """Generate 2D noise value at (x, y)"""
        # Grid coordinates
        X = int(np.floor(x)) & 255
        Y = int(np.floor(y)) & 255
        
        # Relative position in grid
        x -= np.floor(x)
        y -= np.floor(y)
        
        # Fade curves
        u = self._fade(x)
        v = self._fade(y)
        
        # Hash coordinates of corners
        A = self.perm[X] + Y
        B = self.perm[X + 1] + Y
        
        # Get gradients for 4 corners
        g1 = self._grad(self.perm[A], x, y)
        g2 = self._grad(self.perm[B], x - 1, y)
        g3 = self._grad(self.perm[A + 1], x, y - 1)
        g4 = self._grad(self.perm[B + 1], x - 1, y - 1)
        
        # Interpolate
        return self._lerp(
            self._lerp(g1, g2, u),
            self._lerp(g3, g4, u),
            v
        )
    
    def octave_noise(self, x: float, y: float, octaves: int = 4, persistence: float = 0.5) -> float:
        """Multi-octave noise for more natural terrain"""
        total = 0.0
        frequency = 1.0
        amplitude = 1.0
        max_value = 0.0
        
        for _ in range(octaves):
            total += self.noise2d(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= 2.0
        
        return total / max_value


class Chunk:
    def __init__(self, chunk_x, chunk_y, chunk_size=CHUNK_SIZE):
        self.chunk_x = chunk_x
        self.chunk_y = chunk_y
        self.chunk_size = chunk_size
        
        # Pixel data: 2D numpy array storing material IDs
        self.pixels = np.zeros((chunk_size, chunk_size), dtype=np.uint8)
        
        # Modified flag for efficient rendering
        self.modified = True
        
        # Cache for rendered surface
        self.surface = None
    
    def get_pixel(self, x, y):
        """Get material at local coordinates"""
        if 0 <= x < self.chunk_size and 0 <= y < self.chunk_size:
            return self.pixels[y, x]
        return MATERIALS['AIR']
    
    def set_pixel(self, x, y, material_id):
        """Set material at local coordinates"""
        if 0 <= x < self.chunk_size and 0 <= y < self.chunk_size:
            self.pixels[y, x] = material_id
            self.modified = True
    
    def get_world_pos(self, local_x, local_y):
        """Convert local chunk coordinates to world coordinates"""
        world_x = self.chunk_x * self.chunk_size + local_x
        world_y = self.chunk_y * self.chunk_size + local_y
        return world_x, world_y
    
    def get_local_pos(self, world_x, world_y):
        """Convert world coordinates to local chunk coordinates"""
        local_x = world_x % self.chunk_size
        local_y = world_y % self.chunk_size
        return local_x, local_y
    
    def generate_terrain(self, seed=0):
        """Generate procedural terrain using noise"""
        noise_gen = SimpleNoise(seed)
        
        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                world_x = self.chunk_x * self.chunk_size + x
                world_y = self.chunk_y * self.chunk_size + y
                
                # Generate noise value
                nx = world_x / 200.0
                ny = world_y / 200.0
                noise_val = noise_gen.octave_noise(nx, ny, octaves=3, persistence=0.5)
                
                # Determine material based on noise and height
                if noise_val > 0.5:
                    self.pixels[y, x] = MATERIALS['STONE']
                elif noise_val > 0.3:
                    self.pixels[y, x] = MATERIALS['SAND']
                elif world_y > WORLD_HEIGHT - 100:
                    self.pixels[y, x] = MATERIALS['STONE']
                else:
                    self.pixels[y, x] = MATERIALS['AIR']
        
        self.modified = True


class World:
    def __init__(self):
        self.width = WORLD_WIDTH // TILE_SIZE
        self.height = WORLD_HEIGHT // TILE_SIZE
        
        # Calculate number of chunks
        self.num_chunks_x = (WORLD_WIDTH + CHUNK_SIZE * TILE_SIZE - 1) // (CHUNK_SIZE * TILE_SIZE)
        self.num_chunks_y = (WORLD_HEIGHT + CHUNK_SIZE * TILE_SIZE - 1) // (CHUNK_SIZE * TILE_SIZE)
        
        # Chunk storage
        self.chunks = {}
        
        # Initialize chunks
        self._init_chunks()
        
        # Active chunks (near player)
        self.active_chunks = set()
    
    def _init_chunks(self):
        """Initialize all chunks"""
        for cy in range(self.num_chunks_y):
            for cx in range(self.num_chunks_x):
                chunk = Chunk(cx, cy)
                chunk.generate_terrain(seed=cx * 1000 + cy)
                self.chunks[(cx, cy)] = chunk
    
    def get_chunk(self, world_x, world_y):
        """Get chunk containing world position"""
        chunk_x = world_x // (CHUNK_SIZE * TILE_SIZE)
        chunk_y = world_y // (CHUNK_SIZE * TILE_SIZE)
        return self.chunks.get((chunk_x, chunk_y))
    
    def get_pixel(self, world_x, world_y):
        """Get material at world position (in pixels)"""
        chunk = self.get_chunk(world_x, world_y)
        if chunk:
            local_x, local_y = chunk.get_local_pos(world_x, world_y)
            return chunk.get_pixel(local_x, local_y)
        return MATERIALS['AIR']
    
    def set_pixel(self, world_x, world_y, material_id):
        """Set material at world position"""
        if 0 <= world_x < WORLD_WIDTH and 0 <= world_y < WORLD_HEIGHT:
            chunk = self.get_chunk(world_x, world_y)
            if chunk:
                local_x, local_y = chunk.get_local_pos(world_x, world_y)
                chunk.set_pixel(local_x, local_y, material_id)
    
    def is_solid(self, world_x, world_y):
        """Check if a position is solid"""
        material = self.get_pixel(world_x, world_y)
        if material in MATERIAL_PROPS:
            return MATERIAL_PROPS[material].get('solid', False)
        return False
    
    def create_explosion(self, center_x, center_y, radius):
        """Create an explosion crater"""
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy <= radius * radius:
                    px = int(center_x + dx)
                    py = int(center_y + dy)
                    self.set_pixel(px, py, MATERIALS['AIR'])
    
    def update_active_chunks(self, player_x, player_y):
        """Update which chunks are active (near player)"""
        chunk_radius = (UPDATE_RADIUS // (CHUNK_SIZE * TILE_SIZE)) + 1
        
        player_chunk_x = player_x // (CHUNK_SIZE * TILE_SIZE)
        player_chunk_y = player_y // (CHUNK_SIZE * TILE_SIZE)
        
        new_active = set()
        for dy in range(-chunk_radius, chunk_radius + 1):
            for dx in range(-chunk_radius, chunk_radius + 1):
                cx = player_chunk_x + dx
                cy = player_chunk_y + dy
                if (cx, cy) in self.chunks:
                    new_active.add((cx, cy))
        
        self.active_chunks = new_active
    
    def render(self, renderer):
        """Render the world"""
        visible_rect = renderer.camera.get_visible_rect()
        
        # Calculate visible chunk range
        start_cx = max(0, visible_rect.left // (CHUNK_SIZE * TILE_SIZE))
        end_cx = min(self.num_chunks_x, visible_rect.right // (CHUNK_SIZE * TILE_SIZE) + 1)
        start_cy = max(0, visible_rect.top // (CHUNK_SIZE * TILE_SIZE))
        end_cy = min(self.num_chunks_y, visible_rect.bottom // (CHUNK_SIZE * TILE_SIZE) + 1)
        
        # Render visible chunks
        for cy in range(start_cy, end_cy):
            for cx in range(start_cx, end_cx):
                chunk = self.chunks.get((cx, cy))
                if chunk and (cx, cy) in self.active_chunks:
                    self._render_chunk(chunk, renderer)
    
    def _render_chunk(self, chunk, renderer):
        """Render a single chunk efficiently"""
        chunk_pixel_size = CHUNK_SIZE * TILE_SIZE
        base_x = chunk.chunk_x * chunk_pixel_size
        base_y = chunk.chunk_y * chunk_pixel_size
        
        # Only render modified chunks or cache
        if chunk.modified:
            chunk.surface = pygame.Surface((chunk_pixel_size, chunk_pixel_size), depth=32)
            chunk.surface.set_colorkey((0, 0, 0))
            
            for y in range(CHUNK_SIZE):
                for x in range(CHUNK_SIZE):
                    material = chunk.pixels[y, x]
                    if material != MATERIALS['AIR']:
                        color = MATERIAL_COLORS.get(material)
                        if color and color[3] > 0:
                            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                            if color[3] < 255:
                                s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                                s.fill(color)
                                chunk.surface.blit(s, rect)
                            else:
                                pygame.draw.rect(chunk.surface, color[:3], rect)
            
            chunk.modified = False
        
        # Blit chunk to screen
        if chunk.surface:
            screen_x, screen_y = renderer.camera.world_to_screen(base_x, base_y)
            renderer.screen.blit(chunk.surface, (screen_x, screen_y))
    
    def simulate_pixels(self, dt, player_x, player_y):
        """Simulate pixel physics (falling sand, liquids, etc.)"""
        # Only simulate active chunks near player
        for chunk_key in self.active_chunks:
            chunk = self.chunks.get(chunk_key)
            if chunk:
                self._simulate_chunk(chunk, dt, player_x, player_y)
    
    def _simulate_chunk(self, chunk, dt, player_x, player_y):
        """Simulate physics for a single chunk"""
        # Create a copy to avoid modifying while iterating
        new_pixels = chunk.pixels.copy()
        
        # Process from bottom to top for falling materials
        for y in range(CHUNK_SIZE - 1, -1, -1):
            for x in range(CHUNK_SIZE):
                material = chunk.pixels[y, x]
                
                if material == MATERIALS['AIR']:
                    continue
                
                props = MATERIAL_PROPS.get(material, {})
                
                # Check distance to player for optimization
                world_x, world_y = chunk.get_world_pos(x, y)
                dist_to_player = ((world_x - player_x) ** 2 + (world_y - player_y) ** 2) ** 0.5
                if dist_to_player > UPDATE_RADIUS:
                    continue
                
                if props.get('liquid', False):
                    # Liquid behavior (water, lava, acid)
                    self._simulate_liquid(chunk, new_pixels, x, y, material, props)
                elif props.get('gas', False):
                    # Gas behavior (fire, smoke, steam)
                    self._simulate_gas(chunk, new_pixels, x, y, material, props)
                elif props.get('solid', False) and not props.get('liquid', False):
                    # Solid that can fall (sand)
                    if material == MATERIALS['SAND']:
                        self._simulate_falling_solid(chunk, new_pixels, x, y, material)
        
        # Apply changes
        chunk.pixels = new_pixels
    
    def _simulate_liquid(self, chunk, new_pixels, x, y, material, props):
        """Simulate liquid flow"""
        # Try to fall down
        if y + 1 < CHUNK_SIZE:
            below = chunk.pixels[y + 1, x]
            below_props = MATERIAL_PROPS.get(below, {})
            
            if below == MATERIALS['AIR'] or (below_props.get('density', 0) < props.get('density', 0)):
                new_pixels[y, x] = MATERIALS['AIR']
                new_pixels[y + 1, x] = material
                return
        
        # Try to spread horizontally
        direction = 1 if (x + y) % 2 == 0 else -1
        for dx in [direction, -direction]:
            nx = x + dx
            if 0 <= nx < CHUNK_SIZE:
                neighbor = chunk.pixels[y, nx]
                if neighbor == MATERIALS['AIR']:
                    new_pixels[y, x] = MATERIALS['AIR']
                    new_pixels[y, nx] = material
                    return
    
    def _simulate_gas(self, chunk, new_pixels, x, y, material, props):
        """Simulate gas rising"""
        if y > 0:
            above = chunk.pixels[y - 1, x]
            if above == MATERIALS['AIR']:
                new_pixels[y, x] = MATERIALS['AIR']
                new_pixels[y - 1, x] = material
                return
        
        # Also spread horizontally
        for dx in [-1, 1]:
            nx = x + dx
            if 0 <= nx < CHUNK_SIZE:
                neighbor = chunk.pixels[y, nx]
                if neighbor == MATERIALS['AIR']:
                    new_pixels[y, x] = MATERIALS['AIR']
                    new_pixels[y, nx] = material
                    return
    
    def _simulate_falling_solid(self, chunk, new_pixels, x, y, material):
        """Simulate falling solid (sand)"""
        if y + 1 < CHUNK_SIZE:
            below = chunk.pixels[y + 1, x]
            if below == MATERIALS['AIR']:
                new_pixels[y, x] = MATERIALS['AIR']
                new_pixels[y + 1, x] = material
                return
            
            # Try diagonal
            for dx in [-1, 1]:
                nx = x + dx
                if 0 <= nx < CHUNK_SIZE:
                    diag = chunk.pixels[y + 1, nx]
                    if diag == MATERIALS['AIR']:
                        new_pixels[y, x] = MATERIALS['AIR']
                        new_pixels[y + 1, nx] = material
                        return
    
    def check_reactions(self, x, y, material):
        """Check for material reactions"""
        # Water + Lava = Obsidian
        if material == MATERIALS['WATER']:
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                neighbor = self.get_pixel(nx, ny)
                if neighbor == MATERIALS['LAVA']:
                    self.set_pixel(x, y, MATERIALS['OBSIDIAN'])
                    self.set_pixel(nx, ny, MATERIALS['OBSIDIAN'])
                    return True
        
        # Fire + Wood = Ash
        if material == MATERIALS['FIRE']:
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                neighbor = self.get_pixel(nx, ny)
                if neighbor == MATERIALS['WOOD']:
                    self.set_pixel(nx, ny, MATERIALS['ASH'])
                    return True
        
        return False
