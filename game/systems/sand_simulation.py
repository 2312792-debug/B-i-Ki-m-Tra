"""
Systems Module - Sand Simulation
Handles pixel-based physics simulation (falling sand, liquids, gases)
Optimized with numpy for performance
"""

import numpy as np
from settings import MATERIALS, MATERIAL_PROPS, UPDATE_RADIUS


class SandSimulation:
    """
    Optimized falling sand simulation using numpy arrays
    Supports multiple material types with different behaviors
    """
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Main grid storing material IDs
        self.grid = np.zeros((height, width), dtype=np.uint8)
        
        # Temperature grid for heat simulation
        self.temperature = np.zeros((height, width), dtype=np.float32)
        
        # Update counter for alternating updates
        self.update_frame = 0
    
    def set_pixel(self, x, y, material_id):
        """Set a pixel's material"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y, x] = material_id
    
    def get_pixel(self, x, y):
        """Get a pixel's material"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y, x]
        return MATERIALS['AIR']
    
    def clear_region(self, x, y, radius):
        """Clear a circular region (for explosions)"""
        y_min = max(0, int(y - radius))
        y_max = min(self.height, int(y + radius) + 1)
        x_min = max(0, int(x - radius))
        x_max = min(self.width, int(x + radius) + 1)
        
        for py in range(y_min, y_max):
            for px in range(x_min, x_max):
                if (px - x) ** 2 + (py - y) ** 2 <= radius ** 2:
                    self.grid[py, px] = MATERIALS['AIR']
    
    def update(self, player_x=None, player_y=None):
        """
        Update the entire simulation
        Only updates pixels near player if coordinates provided
        """
        self.update_frame += 1
        
        # Determine update region
        if player_x is not None and player_y is not None:
            x_min = max(0, int(player_x - UPDATE_RADIUS))
            x_max = min(self.width, int(player_x + UPDATE_RADIUS))
            y_min = max(0, int(player_y - UPDATE_RADIUS))
            y_max = min(self.height, int(player_y + UPDATE_RADIUS))
        else:
            x_min, x_max = 0, self.width
            y_min, y_max = 0, self.height
        
        # Process from bottom to top, alternating left-right direction
        start_y = y_max - 1
        end_y = y_min - 1
        
        for y in range(start_y, end_y, -1):
            # Alternate direction each row to prevent bias
            if self.update_frame % 2 == 0:
                x_range = range(x_min, x_max)
            else:
                x_range = range(x_max - 1, x_min - 1, -1)
            
            for x in x_range:
                material = self.grid[y, x]
                
                if material == MATERIALS['AIR']:
                    continue
                
                props = MATERIAL_PROPS.get(material, {})
                
                # Simulate based on material type
                if props.get('liquid', False):
                    self._update_liquid(x, y, material)
                elif props.get('gas', False):
                    self._update_gas(x, y, material)
                elif material == MATERIALS['SAND']:
                    self._update_sand(x, y)
                elif props.get('heat', 0) > 0:
                    self._update_heat_source(x, y, material)
    
    def _update_sand(self, x, y):
        """Update falling sand behavior"""
        if y + 1 >= self.height:
            return
        
        # Try to fall straight down
        if self.grid[y + 1, x] == MATERIALS['AIR']:
            self.grid[y, x] = MATERIALS['AIR']
            self.grid[y + 1, x] = MATERIALS['SAND']
        # Try to fall diagonally
        elif y + 1 < self.height:
            dir_offset = 1 if (x + y) % 2 == 0 else -1
            for dx in [dir_offset, -dir_offset]:
                nx = x + dx
                if 0 <= nx < self.width:
                    if self.grid[y + 1, nx] == MATERIALS['AIR']:
                        self.grid[y, x] = MATERIALS['AIR']
                        self.grid[y + 1, nx] = MATERIALS['SAND']
                        return
                    # Fall through water
                    elif self.grid[y + 1, nx] == MATERIALS['WATER']:
                        self.grid[y, x] = MATERIALS['WATER']
                        self.grid[y + 1, nx] = MATERIALS['SAND']
                        return
    
    def _update_liquid(self, x, y, material):
        """Update liquid flow behavior"""
        if y + 1 >= self.height:
            return
        
        below = self.grid[y + 1, x]
        below_props = MATERIAL_PROPS.get(below, {})
        
        # Try to fall down
        if below == MATERIALS['AIR']:
            self.grid[y, x] = MATERIALS['AIR']
            self.grid[y + 1, x] = material
            return
        # Displace less dense liquids
        elif below_props.get('density', 0) < MATERIAL_PROPS.get(material, {}).get('density', 0):
            self.grid[y, x] = below
            self.grid[y + 1, x] = material
            return
        
        # Try to spread horizontally
        dir_offset = 1 if (x + y + self.update_frame) % 2 == 0 else -1
        for dx in [dir_offset, -dir_offset]:
            nx = x + dx
            if 0 <= nx < self.width:
                if self.grid[y, nx] == MATERIALS['AIR']:
                    self.grid[y, x] = MATERIALS['AIR']
                    self.grid[y, nx] = material
                    return
    
    def _update_gas(self, x, y, material):
        """Update gas rising behavior"""
        if y <= 0:
            return
        
        above = self.grid[y - 1, x]
        
        # Try to rise
        if above == MATERIALS['AIR']:
            self.grid[y, x] = MATERIALS['AIR']
            self.grid[y - 1, x] = material
            
            # Decrease lifetime for temporary gases
            if material in [MATERIALS['FIRE'], MATERIALS['SMOKE'], MATERIALS['STEAM']]:
                # Small chance to dissipate
                if (x + y + self.update_frame) % 100 == 0:
                    self.grid[y - 1, x] = MATERIALS['AIR']
            return
        
        # Spread horizontally
        for dx in [-1, 1]:
            nx = x + dx
            if 0 <= nx < self.width:
                if self.grid[y, nx] == MATERIALS['AIR']:
                    self.grid[y, x] = MATERIALS['AIR']
                    self.grid[y, nx] = material
                    return
    
    def _update_heat_source(self, x, y, material):
        """Update heat propagation from heat sources"""
        heat_level = MATERIAL_PROPS.get(material, {}).get('heat', 0)
        self.temperature[y, x] = max(self.temperature[y, x], heat_level)
        
        # Check for flammable materials nearby
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbor = self.grid[ny, nx]
                    neighbor_props = MATERIAL_PROPS.get(neighbor, {})
                    
                    if neighbor_props.get('flammable', False):
                        # Chance to ignite
                        if (x + y + self.update_frame) % 20 == 0:
                            if neighbor == MATERIALS['WOOD']:
                                self.grid[ny, nx] = MATERIALS['FIRE']
    
    def check_reactions(self):
        """Check for material reactions across the grid"""
        # This could be optimized further with numpy operations
        changes = []
        
        for y in range(self.height):
            for x in range(self.width):
                material = self.grid[y, x]
                
                # Water + Lava = Obsidian
                if material == MATERIALS['WATER']:
                    for dy, dx in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            if self.grid[ny, nx] == MATERIALS['LAVA']:
                                changes.append((x, y, MATERIALS['OBSIDIAN']))
                                changes.append((nx, ny, MATERIALS['OBSIDIAN']))
                                break
                
                # Fire + Wood = Ash (handled in heat update)
        
        # Apply changes
        for x, y, new_material in changes:
            self.grid[y, x] = new_material
    
    def add_material(self, x, y, material_id, radius=5):
        """Add material in a circular area"""
        y_min = max(0, int(y - radius))
        y_max = min(self.height, int(y + radius) + 1)
        x_min = max(0, int(x - radius))
        x_max = min(self.width, int(x + radius) + 1)
        
        for py in range(y_min, y_max):
            for px in range(x_min, x_max):
                if (px - x) ** 2 + (py - y) ** 2 <= radius ** 2:
                    if self.grid[py, px] == MATERIALS['AIR']:
                        self.grid[py, px] = material_id
    
    def get_grid(self):
        """Get the full grid array"""
        return self.grid
