# 🎮 Noita-like Physics Game

Game 2D pixel physics sandbox lấy cảm hứng từ Noita, được viết bằng Python với pygame và pymunk.

## 📋 Tính năng

### Core Gameplay (Giống Noita)
- ✅ **Pixel-based world**: Mỗi pixel là một vật liệu với tính chất riêng
- ✅ **Falling sand simulation**: Cát rơi, nước chảy, lửa lan
- ✅ **Terrain destructible**: Có thể phá hủy từng pixel
- ✅ **Material reactions**: 
  - Nước + Lava = Obsidian
  - Lửa + Gỗ = Tro
- ✅ **Physics interactions**: Trọng lực, dòng chảy, cháy

### Player System
- ✅ Di chuyển WASD
- ✅ Nhảy (Space/W)
- ✅ Jetpack (Shift)
- ✅ HP system
- ✅ Combat với wand/projectile

### Combat System
- ✅ 3 loại vũ khí: Fireball, Water Bolt, Acid Blob
- ✅ Projectile physics
- ✅ Particle effects
- ✅ Explosion damage

### Enemy AI
- ✅ Basic và Strong enemy types
- ✅ AI state machine (wander, chase, attack)
- ✅ Pathfinding đơn giản
- ✅ Tấn công player

### World System
- ✅ Procedural generation với noise
- ✅ Chunk system cho optimization
- ✅ Camera follow player + shake effect
- ✅ Lighting system (2D radial light)

## 🏗️ Cấu trúc Project

```
game/
├── main.py                 # Entry point, game loop
├── settings.py             # Configuration constants
├── engine/
│   ├── physics.py          # Pymunk physics engine
│   ├── renderer.py         # Rendering, camera, lighting
│   └── world.py            # World generation, chunk system
├── entities/
│   ├── player.py           # Player class
│   └── enemy.py            # Enemy AI classes
├── systems/
│   ├── combat.py           # Combat, projectiles, particles
│   └── sand_simulation.py  # Pixel physics simulation
└── assets/
    ├── tiles/              # Tile sprites (optional)
    └── sprites/            # Entity sprites (optional)
```

## 🛠️ Thư viện sử dụng

### Bắt buộc
- `pygame` - Render và input handling
- `pymunk` - Physics engine 2D
- `numpy` - Xử lý grid pixel nhanh
- `noise` - Procedural generation (Perlin noise)

### Tùy chọn (nâng cao)
- `numba` - Tăng tốc simulation với JIT
- `moderngl` - GPU rendering

## 🚀 Hướng dẫn cài đặt

### 1. Cài đặt dependencies

```bash
pip install pygame pymunk numpy noise
```

### 2. Chạy game

```bash
cd game
python main.py
```

## 🎮 Điều khiển

| Phím | Chức năng |
|------|-----------|
| **WASD / Mũi tên** | Di chuyển |
| **Space / W** | Nhảy |
| **Shift** | Jetpack (giữ) / Phá terrain (với click) |
| **Left Click** | Đặt vật liệu |
| **Right Click** | Bắn fireball |
| **1 / 2 / 3** | Đổi vũ khí (Fireball / Water / Acid) |
| **S / W / L / T** | Chọn vật liệu (Sand / Water / Lava / Stone) |
| **P** | Pause |
| **F1** | Toggle debug mode |
| **ESC** | Thoát game |
| **R** | Restart (khi game over) |

## 🔬 Vật liệu

| Material | ID | Tính chất |
|----------|-----|-----------|
| Air | 0 | Trong suốt |
| Sand | 1 | Rơi xuống, tích tụ |
| Water | 2 | Chảy, lan ngang |
| Stone | 3 | Rắn, không di chuyển |
| Lava | 4 | Chảy, nóng, cháy |
| Fire | 5 | Bay lên, lan sang gỗ |
| Wood | 6 | Rắn, dễ cháy |
| Ash | 7 | Nhẹ, bay |
| Acid | 8 | Chảy, ăn mòn |
| Smoke | 9 | Bay lên, tan dần |
| Steam | 10 | Bay lên từ nước nóng |
| Obsidian | 11 | Cứng (water + lava) |

## ⚙️ Optimization

### Chunk System
- World chia thành chunks 64x64 tiles
- Chỉ update chunks gần player (UPDATE_RADIUS = 300px)
- Render caching cho mỗi chunk

### Numpy Arrays
- Sử dụng numpy thay vì list cho grid
- Batch processing cho pixel updates

### Update Optimization
- Alternating scan direction (tránh bias)
- Chỉ simulate pixels trong tầm nhìn
- Early exit cho AIR materials

## 🎨 Customization

### Thêm vật liệu mới

1. Thêm vào `settings.py`:
```python
MATERIALS['NEW_MAT'] = 13
MATERIAL_COLORS[13] = (255, 0, 255, 255)  # RGBA
MATERIAL_PROPS[13] = {'solid': False, 'liquid': True, 'gas': False, 'flammable': False, 'density': 1}
```

2. Thêm logic simulation trong `sand_simulation.py`:
```python
elif material == MATERIALS['NEW_MAT']:
    self._update_new_material(x, y)
```

### Thêm vũ khí mới

Thêm vào `CombatSystem.__init__()` trong `combat.py`:
```python
self.weapons['ice_bolt'] = {
    'damage': 15,
    'speed': 450,
    'cooldown': 0.25
}
```

## 🐛 Troubleshooting

### Game chạy chậm
- Giảm `UPDATE_RADIUS` trong `settings.py`
- Giảm `CHUNK_SIZE` để ít pixel cần update hơn
- Tắt debug mode (F1)

### Không thấy hình
- Kiểm tra terminal có display không
- Thử chạy với `SDL_VIDEODRIVER=dummy python main.py`

### Lỗi import
```bash
pip install --upgrade pygame pymunk numpy noise
```

## 📝 Demo Features

Khi chạy game, bạn sẽ thấy:

1. **Player** với jetpack ở giữa màn hình
2. **Terrain** được sinh procedural với stone và sand
3. **Enemies** đỏ và tím di chuyển xung quanh
4. **Physics**:
   - Bắn fireball (right-click) → nổ terrain
   - Đặt sand (left-click) → cát rơi
   - Đặt water → nước chảy xuống và lan
   - Shift + click → phá terrain

## 🔮 Future Enhancements

- [ ] Multi-threading cho simulation
- [ ] GPU acceleration với moderngl
- [ ] Thêm biomes (forest, desert, ice)
- [ ] Wand crafting system
- [ ] Save/Load world
- [ ] More particle effects
- [ ] Sound effects và music
- [ ] Boss enemies

## 📄 License

MIT License - Tự do sử dụng và modify

## 👨‍💻 Credits

Inspired by **Noita** by Nolla Games
Asset suggestions từ OpenGameArt và Kenney.nl

---

**Enjoy coding and playing! 🎉**
