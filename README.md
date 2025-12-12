<div align="center">

# 🎲 Spinning Cube

### *3D Graphics in Your Terminal*

A beautiful terminal-based 3D renderer that brings rotating cubes to life using ASCII/Unicode characters.

**Pure Python • No Dependencies • From Scratch**

[Quick Start](#-quick-start) • [How It Works](#-how-it-works) • [Theory](#-the-math-behind-it) • [Learn More](#-learning-path)

---

</div>

## 🚀 Quick Start

```bash
# Run the spinning cube
python cube.py

# Run the simpler rotating square demo
python square.py
```

Press **Ctrl+C** to exit at any time.

> **First time?** Start with `square.py` to see 2D rotation, then move to `cube.py` for the full 3D experience!

---

## 📁 Project Structure

| File | Description |
|------|-------------|
| **`cube.py`** | Main 3D cube renderer with triple-axis rotation |
| **`graphics.py`** | Core graphics engine (rendering pipeline) |
| **`square.py`** | Simple 2D demo (perfect for beginners) |

---

## 🎨 What You'll See

Different cube faces are rendered with distinct Unicode characters for visual depth:

```
  Front:  ' ' (space)
  Right:  ▓ (dark shade)
  Back:   ▒ (medium shade)
  Left:   ░ (light shade)
  Top:    ▪ (small square)
  Bottom: █ (full block)
```

---

## 💡 How It Works

This project implements a complete 3D graphics pipeline in 5 steps:

```
3D Model → Rotation → Perspective → Depth Sort → Rasterization → Display
```

### The Pipeline

1. **Define** - Create cube vertices in 3D space
2. **Transform** - Rotate around X, Y, Z axes
3. **Project** - Apply perspective (distant = smaller)
4. **Sort** - Order faces back-to-front (Painter's Algorithm)
5. **Rasterize** - Fill polygons using scanline algorithm
6. **Render** - Display in terminal with ANSI codes

---

## 📐 The Math Behind It

### 3D Coordinate System

We use a **right-handed Cartesian system**:

```
        Y (up)
        |
        |
        |_________ X (right)
       /
      /
     Z (out of screen)
```

Each point: $`P = (x, y, z)`$

---

### 🔄 3D Transformations

#### Translation

Moving a point in space:

$$P' = P + \text{offset}$$

Simple vector addition!

---

#### Rotation Matrices

<details>
<summary><b>📘 Rotation Around X-axis</b> (pitch - nodding)</summary>

$$\begin{bmatrix} x' \\ y' \\ z' \end{bmatrix} = \begin{bmatrix} 1 & 0 & 0 \\ 0 & \cos\theta & -\sin\theta \\ 0 & \sin\theta & \cos\theta \end{bmatrix} \begin{bmatrix} x \\ y \\ z \end{bmatrix}$$

In code (`cube.py:64-69`):
```python
x' = x
y' = y·cos(θ) - z·sin(θ)
z' = y·sin(θ) + z·cos(θ)
```

</details>

<details>
<summary><b>📗 Rotation Around Y-axis</b> (yaw - shaking head)</summary>

$$\begin{bmatrix} x' \\ y' \\ z' \end{bmatrix} = \begin{bmatrix} \cos\theta & 0 & \sin\theta \\ 0 & 1 & 0 \\ -\sin\theta & 0 & \cos\theta \end{bmatrix} \begin{bmatrix} x \\ y \\ z \end{bmatrix}$$

In code (`cube.py:71-76`):
```python
x' = x·cos(θ) + z·sin(θ)
y' = y
z' = z·cos(θ) - x·sin(θ)
```

</details>

<details>
<summary><b>📙 Rotation Around Z-axis</b> (roll - tilting head)</summary>

$$\begin{bmatrix} x' \\ y' \\ z' \end{bmatrix} = \begin{bmatrix} \cos\theta & -\sin\theta & 0 \\ \sin\theta & \cos\theta & 0 \\ 0 & 0 & 1 \end{bmatrix} \begin{bmatrix} x \\ y \\ z \end{bmatrix}$$

In code (`cube.py:78-83`):
```python
x' = x·cos(θ) - y·sin(θ)
y' = x·sin(θ) + y·cos(θ)
z' = z
```

</details>

> **Note:** Rotations are applied in **Z → Y → X** order for smooth multi-axis rotation.

---

### 👁️ Perspective Projection

Makes distant objects appear smaller, just like in real life!

$$\text{scale} = \frac{f}{z}$$

$$x_{\text{screen}} = x_{3D} \times \text{scale}$$

$$y_{\text{screen}} = y_{3D} \times \text{scale}$$

Where:
- $`f`$ = focal length (field of view)
- $`z`$ = distance from camera

**Larger z → smaller scale → smaller on screen** ✨

---

### 🎨 Painter's Algorithm

How do we know which face to draw first?

1. Calculate **centroid depth** for each face:
   $$z_{\text{centroid}} = \frac{1}{4}\sum_{i=1}^{4} z_i$$

2. **Sort** faces: furthest first → nearest last

3. **Draw** in that order

Result: Near faces correctly cover far faces! 🎯

---

### 🖼️ Polygon Rasterization

**Scanline Algorithm** - The efficient way to fill polygons:

```
For each horizontal line (scanline):
  1. Find where line intersects polygon edges
  2. Fill pixels between leftmost ↔ rightmost intersection
```

**Why it's fast:** Only checks pixels inside the polygon, not the entire bounding box!

**Edge intersection formula:**

$$x = x_1 + (y - y_1) \times \frac{x_2 - x_1}{y_2 - y_1}$$

Linear interpolation finds the x-coordinate where the scanline crosses each edge.

---

### 🎯 Depth Buffering

Each pixel stores two values:

| Buffer | Stores |
|--------|--------|
| **Frame Buffer** | Character to display |
| **Depth Buffer** | Z-value (distance) |

**Drawing rule:**
```python
if new_depth <= current_depth:
    draw_pixel()  # Closer to camera, so draw it!
```

This ensures near surfaces always appear in front! 🔝

---

## 🛠️ Implementation Guide

### Core Classes

#### `Point` (`graphics.py:5-19`)

Represents a 3D point with operator overloading:

```python
p1 = Point(1, 2, 3)
p2 = Point(4, 5, 6)

p3 = p1 + p2  # Addition (translation)
p4 = p1 - p2  # Subtraction (relative position)
```

---

#### `ConvexPolygon` (`graphics.py:22-62`)

Handles efficient polygon rasterization.

**Key method:** `lattice_spans()`
- Yields `(y, x_min, x_max)` for each horizontal line
- Uses convex property: exactly 2 edge intersections per scanline

---

#### `Screen` (`graphics.py:64-160`)

The render target managing both buffers.

**Important methods:**
- `clear()` - Reset buffers for new frame
- `polygon()` - Rasterize filled polygon with depth testing
- `render()` - Convert buffers to string for terminal display

**Coordinate system:**
- Origin at center
- 2:1 horizontal scaling (compensates terminal character aspect ratio)
- Y-axis flipped (world up = terminal down)

---

### The Render Loop (`cube.py:133-175`)

```python
while True:
    screen.clear()

    # 1. Precompute trig values (optimization!)
    cos_ax, sin_ax = cos(angle_x), sin(angle_x)
    cos_ay, sin_ay = cos(angle_y), sin(angle_y)
    cos_az, sin_az = cos(angle_z), sin(angle_z)

    # 2. Transform all faces
    for face_verts, fill in faces:
        transformed = [transform(v, ...) for v in face_verts]
        depth = get_centroid_depth(transformed)
        face_data.append((depth, transformed, fill))

    # 3. Sort by depth (painter's algorithm)
    face_data.sort(key=lambda x: x[0], reverse=True)

    # 4. Rasterize back-to-front
    for depth, verts, fill in face_data:
        screen.polygon(verts, fill=fill)

    # 5. Display
    print('\033[H' + screen.render(), flush=True)

    # 6. Update angles
    angle_x += angle_step_x
    angle_y += angle_step_y
    angle_z += angle_step_z
```

---

## ⚡ Performance Tips

Despite being **pure Python**, this renders smoothly by:

✅ **Pre-computing** `cos(θ)` and `sin(θ)` once per frame
✅ **Direct attribute access** (`point.x` instead of `point[0]`)
✅ **Reusing buffers** (clear instead of allocate)
✅ **List comprehensions** (C-optimized loops)
✅ **Flat arrays** (not nested 2D lists)

**Current bottlenecks:**
- Terminal I/O (`print` operations)
- Scanline rasterization inner loops

---

## 📚 Learning Path

### Beginner → Advanced

1. **Start Here:** `square.py`
   - Understand 2D rotation
   - See basic rendering pipeline
   - Learn coordinate transformations

2. **Study Core:** `graphics.py`
   - Point operations
   - Scanline rasterization
   - Dual buffer management

3. **Master 3D:** `cube.py`
   - 3D rotations
   - Perspective projection
   - Painter's algorithm
   - Complete pipeline

---

## 🎓 Key Concepts You'll Learn

- ✨ **Linear Algebra** - Vectors, matrices, transformations
- 🔄 **3D Rotation** - Euler angles, rotation matrices
- 👁️ **Projection** - 3D to 2D conversion
- 🎨 **Rasterization** - Converting geometry to pixels
- 📊 **Depth Sorting** - Visibility algorithms
- ⚡ **Optimization** - Performance in interpreted languages

---

## 🚀 Ideas to Extend

Want to take this further? Try:

- [ ] Add more shapes (pyramid, sphere, torus)
- [ ] Implement camera controls (WASD to fly around)
- [ ] Add simple lighting (diffuse shading)
- [ ] Support terminal colors (256-color mode)
- [ ] Texture mapping with ASCII art
- [ ] Backface culling optimization
- [ ] Wireframe rendering mode
- [ ] Multiple objects in scene
- [ ] Simple physics (bouncing cubes)

---

## 📖 Mathematical Reference

### Constants Used

| Constant | Value | Purpose |
|----------|-------|---------|
| **Focal Length** | 100 units | Controls field of view |
| **Z Distance** | 300 units | Distance from camera to cube |
| **Cube Side** | 350 units | Size of the cube |
| **Angle Steps** | π/(96-768) | Rotation speed per axis |

### ANSI Escape Codes

| Code | Effect |
|------|--------|
| `\033[2J` | Clear entire screen |
| `\033[H` | Move cursor to home (0, 0) |
| `\033[?25l` | Hide cursor |
| `\033[?25h` | Show cursor |

---

## 🎯 What Makes This Special

This project demonstrates **fundamental computer graphics** concepts:

- All algorithms implemented **from scratch**
- **No external dependencies** (just Python stdlib)
- **Educational** - clear, documented code
- **Terminal-based** - creative constraint
- **Real 3D math** - not simplified or approximated

Perfect for learning how 3D graphics actually work! 🎓

---

## 📄 License

Open source - learn, modify, and extend freely!

---

<div align="center">

**Made with ❤️ and math**

*All core computer graphics concepts, implemented from scratch, running in your terminal.*

</div>
