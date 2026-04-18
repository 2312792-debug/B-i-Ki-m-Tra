"""
Game Settings and Configuration
Noita-like 2D Physics Game
"""

# Screen settings
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
TITLE = "Noita-like Physics Game"

# World settings
WORLD_WIDTH = 2048  # Total world width in pixels
WORLD_HEIGHT = 1024  # Total world height in pixels
TILE_SIZE = 4  # Size of each pixel/tile
CHUNK_SIZE = 64  # Chunk size in tiles
CHUNK_PIXEL_SIZE = CHUNK_SIZE * TILE_SIZE

# Physics
GRAVITY = 9.8 * 50  # Scaled gravity
PLAYER_SPEED = 200
PLAYER_JUMP_FORCE = -400
PLAYER_JETPACK_FORCE = -300

# Materials (pixel types)
MATERIALS = {
    'AIR': 0,
    'SAND': 1,
    'WATER': 2,
    'STONE': 3,
    'LAVA': 4,
    'FIRE': 5,
    'WOOD': 6,
    'ASH': 7,
    'ACID': 8,
    'SMOKE': 9,
    'STEAM': 10,
    'OBSIDIAN': 11,
    'PLAYER': 12,
}

# Material colors (RGB)
MATERIAL_COLORS = {
    MATERIALS['AIR']: (0, 0, 0, 0),
    MATERIALS['SAND']: (235, 200, 115, 255),
    MATERIALS['WATER']: (64, 164, 223, 200),
    MATERIALS['STONE']: (128, 128, 128, 255),
    MATERIALS['LAVA']: (207, 16, 32, 255),
    MATERIALS['FIRE']: (255, 69, 0, 220),
    MATERIALS['WOOD']: (139, 69, 19, 255),
    MATERIALS['ASH']: (80, 80, 80, 255),
    MATERIALS['ACID']: (124, 252, 0, 200),
    MATERIALS['SMOKE']: (100, 100, 100, 150),
    MATERIALS['STEAM']: (200, 200, 220, 180),
    MATERIALS['OBSIDIAN']: (40, 20, 60, 255),
    MATERIALS['PLAYER']: (255, 200, 100, 255),
}

# Material properties
MATERIAL_PROPS = {
    MATERIALS['AIR']: {'solid': False, 'liquid': False, 'gas': False, 'flammable': False, 'density': 0},
    MATERIALS['SAND']: {'solid': True, 'liquid': False, 'gas': False, 'flammable': False, 'density': 2},
    MATERIALS['WATER']: {'solid': False, 'liquid': True, 'gas': False, 'flammable': False, 'density': 1},
    MATERIALS['STONE']: {'solid': True, 'liquid': False, 'gas': False, 'flammable': False, 'density': 3},
    MATERIALS['LAVA']: {'solid': False, 'liquid': True, 'gas': False, 'flammable': True, 'density': 3, 'heat': 100},
    MATERIALS['FIRE']: {'solid': False, 'liquid': False, 'gas': True, 'flammable': False, 'density': 0, 'heat': 80},
    MATERIALS['WOOD']: {'solid': True, 'liquid': False, 'gas': False, 'flammable': True, 'density': 1},
    MATERIALS['ASH']: {'solid': True, 'liquid': False, 'gas': False, 'flammable': False, 'density': 0.5},
    MATERIALS['ACID']: {'solid': False, 'liquid': True, 'gas': False, 'flammable': False, 'density': 1.2},
    MATERIALS['SMOKE']: {'solid': False, 'liquid': False, 'gas': True, 'flammable': False, 'density': 0},
    MATERIALS['STEAM']: {'solid': False, 'liquid': False, 'gas': True, 'flammable': False, 'density': 0},
    MATERIALS['OBSIDIAN']: {'solid': True, 'liquid': False, 'gas': False, 'flammable': False, 'density': 4},
    MATERIALS['PLAYER']: {'solid': True, 'liquid': False, 'gas': False, 'flammable': False, 'density': 1},
}

# Camera
CAMERA_SMOOTHING = 0.1
CAMERA_SHAKE_DECAY = 0.9

# Player
PLAYER_MAX_HP = 100
PLAYER_JETPACK_FUEL = 100
PLAYER_JETPACK_CONSUMPTION = 0.5
PLAYER_JETPACK_REGEN = 0.2

# Combat
FIREBALL_SPEED = 400
FIREBALL_DAMAGE = 25
FIREBALL_LIFETIME = 3.0

# Update distance (optimization)
UPDATE_RADIUS = 300  # Only update pixels within this distance from player
