# Spinning Cube 🎲

A terminal-based 3D graphics engine that renders a rotating cube using ASCII/Unicode characters. This project demonstrates fundamental 3D computer graphics concepts implemented in pure Python.

## Overview

This project renders a 3D spinning cube directly in your terminal using text characters. It implements core computer graphics algorithms from scratch, including 3D transformations, perspective projection, and polygon rasterization.

## Quick Start

```bash
# Run the spinning cube
python cube.py

# Run the simpler 2D square demo
python square.py
```

Press `Ctrl+C` to exit.

## Files

- **`cube.py`** - Main 3D cube renderer with triple-axis rotation
- **`graphics.py`** - Core graphics engine (Point, ConvexPolygon, Screen)
- **`square.py`** - Simple 2D rotating square demo

## Theory

### 1. 3D Coordinate System

The engine uses a right-handed Cartesian coordinate system:
- **X-axis**: Left (-) to Right (+)
- **Y-axis**: Down (-) to Up (+)
- **Z-axis**: Into screen (-) to Out of screen (+)

Each point in 3D space is represented as `(x, y, z)`.

### 2. 3D Transformations

#### Translation
Moving a point in 3D space:
```
P' = P + offset
```

#### Rotation
Rotation matrices transform points around each axis:

**Rotation around X-axis** (pitch):
```
x' = x
y' = y·cos(θ) - z·sin(θ)
z' = y·sin(θ) + z·cos(θ)
```

**Rotation around Y-axis** (yaw):
```
x' = x·cos(θ) + z·sin(θ)
y' = y
z' = z·cos(θ) - x·sin(θ)
```

**Rotation around Z-axis** (roll):
```
x' = x·cos(θ) - y·sin(θ)
y' = x·sin(θ) + y·cos(θ)
z' = z
```

The code applies rotations in Z → Y → X order to achieve smooth 3D rotation.

### 3. Perspective Projection

Perspective projection creates the illusion of depth by making distant objects appear smaller.

**Formula**:
```
scale = focal_length / z
x_screen = x_3d × scale
y_screen = y_3d × scale
```

- **Focal length**: Controls field of view (smaller = wider angle)
- **Z-distance**: Objects further away (larger z) appear smaller

This mimics how the human eye perceives depth.

### 4. Painter's Algorithm

To correctly render overlapping faces:
1. Calculate the **centroid depth** (average z-coordinate) of each face
2. Sort faces from **furthest to nearest**
3. Draw in that order (far faces first, near faces last)

This ensures nearer faces correctly occlude distant ones.

### 5. Polygon Rasterization

The engine uses **scanline rasterization** to fill polygons efficiently:

1. For each horizontal scanline (y-coordinate):
   - Find where the scanline intersects polygon edges
   - Fill pixels between the leftmost and rightmost intersection

This is more efficient than checking every pixel in the bounding box.

**Key algorithm** (`ConvexPolygon.find_intercept_pair`):
- Iterates through polygon edges
- Finds exactly 2 intersections per scanline (convex property)
- Uses linear interpolation to compute intersection x-coordinates

### 6. Depth Buffering

Each screen pixel has:
- **Frame buffer**: Character to display
- **Depth buffer**: Z-value of nearest surface

Before drawing a pixel, check if its depth is nearer than the current depth buffer value. Only draw if it's closer.

### 7. Terminal Rendering

**Coordinate transformation**:
- Origin at screen center
- 2:1 horizontal scaling (terminal characters are taller than wide)
- Y-axis flipped (world up = screen down)

**ANSI escape codes**:
- `\033[2J` - Clear screen
- `\033[H` - Move cursor to home
- `\033[?25l` - Hide cursor
- `\033[?25h` - Show cursor

## Implementation Details

### Core Classes (`graphics.py`)

#### `Point`
Represents a 3D point with `x`, `y`, `z` coordinates.

**Operations**:
- Addition: `P1 + P2` → translate
- Subtraction: `P1 - P2` → relative position

#### `ConvexPolygon`
Handles polygon rasterization using scanline algorithm.

**Key method**: `lattice_spans()`
- Yields `(y, x_min, x_max)` for each scanline
- Optimized for convex polygons (exactly 2 edge intersections)

#### `Screen`
Manages the render target with dual buffers.

**Features**:
- Frame buffer: Stores characters to display
- Depth buffer: Z-values for depth testing
- `polygon()`: Rasterizes filled polygons with depth
- `render()`: Converts buffers to terminal string with borders

### Cube Rendering (`cube.py`)

**Setup**:
1. Define 8 vertices forming a cube
2. Group into 6 faces (4 vertices each)
3. Assign unique fill characters for visual distinction

**Render loop**:
1. **Transform**: For each vertex:
   - Translate to origin (relative to cube center)
   - Rotate around X, Y, Z axes
   - Translate back
   - Apply perspective projection

2. **Sort**: Calculate centroid depth per face, sort back-to-front

3. **Rasterize**: Draw each polygon using scanline fill

4. **Display**: Print frame buffer to terminal

5. **Update**: Increment rotation angles for next frame

**Performance optimizations**:
- Pre-compute `cos(θ)` and `sin(θ)` once per frame
- Direct attribute access (`point.x` vs `point[0]`)
- Manual loop unrolling for centroid calculation
- Flat buffer arrays instead of 2D nested lists

### Square Demo (`square.py`)

A simpler 2D demonstration:
- 4 vertices in the XY plane (Z=0)
- Single Z-axis rotation
- No perspective (orthographic projection)
- Rotates to π/2 and displays FPS statistics

## Mathematical Constants

- **Angle steps**: Control rotation speed per axis
- **Focal length**: 100 units (affects perspective strength)
- **Z-distance**: 300 units (distance from camera to cube)
- **Side length**: 350 units (cube size)

## Character Set

Different faces use distinct Unicode block characters for depth perception:
- ` ` (space) - Front face
- `▓` - Dark shade (right)
- `▒` - Medium shade (back)
- `░` - Light shade (left)
- `▪` - Small square (top)
- `█` - Full block (bottom)

## Performance Considerations

**Why Python?**
Despite being interpreted, Python can render smooth animations by:
- Minimizing allocations (reuse buffers)
- Using list comprehensions (C-optimized)
- Avoiding function call overhead in tight loops
- Pre-computing trigonometric values

**Bottlenecks**:
- Terminal I/O (print operations)
- Scanline rasterization (inner loops)

## Learning Path

1. **Start with `square.py`**: Understand 2D rotation and rendering
2. **Study `graphics.py`**: Learn rasterization and screen management
3. **Explore `cube.py`**: See full 3D pipeline in action

## Extensions

Ideas to expand the project:
- Add more shapes (pyramid, sphere, torus)
- Implement camera controls (WASD movement)
- Add lighting and shading
- Support colored terminal output
- Texture mapping with ASCII art
- Backface culling optimization
- Wireframe rendering mode

## Key Takeaways

This project demonstrates:
- **3D mathematics**: Rotation matrices and perspective projection
- **Graphics algorithms**: Rasterization and depth sorting
- **Optimization**: Performance in interpreted languages
- **Terminal graphics**: Creative use of character-based rendering

All core computer graphics concepts, implemented from scratch, running in your terminal.

## License

Open source - feel free to learn, modify, and extend!
