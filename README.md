# terminal-3d-renderer

A terminal-based 3D graphics renderer built from scratch to show my understanding of basic computer graphics concepts and discrete mathematics.

---

## Setup

This project renders a spinning 3D cube in your terminal using basic math and Python.

**Performance note:** The code is highly optimized in native Python - every major performance bottleneck has been addressed.

**Run the demos:**

```bash
# 2D rotating square
python src/square.py

# 3D spinning cube
python src/cube.py
```

**Important:** Zoom out your terminal to maximum for the best viewing experience.

---

## Theory

### Points as Data

A point is a tuple of values representing a position:
- 2D point: `(x, y)`
- 3D point: `(x, y, z)`

Example: `(3, 5)` means 3 units right, 5 units up from origin `(0, 0)`.

### Functions Transform Points

We can pass a point to a function and get a new point back:

```python
def transform(point):
    x, y = point
    new_x = x + 10
    new_y = y + 10
    return (new_x, new_y)

p1 = (3, 5)
p2 = transform(p1)  # (13, 15)
```

### Rotation Concept

Rotation takes a point and an angle `θ` (theta), then outputs a new point rotated around the origin.

```python
new_point = rotate(point, theta)
```

Think of it like a slider: adjust `θ` and the point moves in a circle around `(0, 0)`.

**Example:** Rotate `(3, 4)` by 180 degrees (π radians):

```python
from math import pi

point = (3, 4)           # Positive quadrant
rotated = rotate(point, pi)  # 180 degrees
# Result: (-3, -4)       # Negative quadrant
```

The point flips to the opposite side of the origin.

---

## Rotation

### The Rotation Formula

To rotate a point `(x, y)` by angle `θ`:

$$x' = x\cos(\theta) - y\sin(\theta)$$

$$y' = x\sin(\theta) + y\cos(\theta)$$

```python
from math import cos, sin

def rotate(point, theta):
    x, y = point
    new_x = x * cos(theta) - y * sin(theta)
    new_y = x * sin(theta) + y * cos(theta)
    return (new_x, new_y)
```

### Derivation

<details>
<summary>How we derive this formula from polar coordinates</summary>

**Polar Representation**

Any point `(x, y)` can be written as:

$$(x, y) = (r\cos(\theta), r\sin(\theta))$$

where:
- `r` = distance from origin
- `θ` = angle from x-axis

**Rotating by Angle h**

To rotate by `h` degrees, add `h` to the angle:

$$(x', y') = (r\cos(\theta + h), r\sin(\theta + h))$$

**Problem:** We don't know `r` or `θ` directly from `(x, y)`.

**Solution:** Use the sum of angles identity.

$$\cos(\theta + h) = \cos(\theta)\cos(h) - \sin(\theta)\sin(h)$$

$$\sin(\theta + h) = \sin(\theta)\cos(h) + \cos(\theta)\sin(h)$$

Substitute into our rotation formula:

$$x' = r\cos(\theta + h) = r[\cos(\theta)\cos(h) - \sin(\theta)\sin(h)]$$

$$y' = r\sin(\theta + h) = r[\sin(\theta)\cos(h) + \cos(\theta)\sin(h)]$$

Distribute `r`:

$$x' = r\cos(\theta)\cos(h) - r\sin(\theta)\sin(h)$$

$$y' = r\sin(\theta)\cos(h) + r\cos(\theta)\sin(h)$$

But `x = r cos(θ)` and `y = r sin(θ)`, so:

$$x' = x\cos(h) - y\sin(h)$$

$$y' = x\sin(h) + y\cos(h)$$

</details>

---

## Rotating Multiple Points

If we can rotate one point, we can rotate many.

```python
def rotate_points(points, theta):
    return [rotate(p, theta) for p in points]
```

### Creating Shapes

A shape is just a list of points connected in order.

```python
def polygon(points):
    """Connect points sequentially to form a polygon"""
    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i + 1) % len(points)]  # Wrap to first point
        draw_line(p1, p2)
```

### Rotating Shapes

**Pipeline:** points → rotate → connect → display

```python
# Define a square
square = [(1, 1), (1, -1), (-1, -1), (-1, 1)]

# Rotate it
rotated = rotate_points(square, theta)

# Draw it
polygon(rotated)
```

Think in terms of input/output functions:
- `rotate(points, theta)` → rotated points
- `polygon(points)` → draws connected lines

### Rotating Shapes Not Centered at Origin

If your shape isn't centered at `(0, 0)`, rotation won't work correctly.

**Solution:** Translate to origin, rotate, translate back.

```python
def center(polygon):
    """Move polygon to origin"""
    # Calculate centroid
    cx = sum(p[0] for p in polygon) / len(polygon)
    cy = sum(p[1] for p in polygon) / len(polygon)
    # Translate all points
    return [(x - cx, y - cy) for x, y in polygon]

def revert(polygon, original):
    """Move polygon back to original position"""
    # Calculate offset from original
    cx_orig = sum(p[0] for p in original) / len(original)
    cy_orig = sum(p[1] for p in original) / len(original)
    # Translate back
    return [(x + cx_orig, y + cy_orig) for x, y in polygon]

# Complete pipeline
new_polygon = revert(rotate_points(center(polygon), theta), polygon)
```

---

## Rasterization: Drawing Polygons on the Terminal (The Hardest Part)

Now we can rotate shapes, but how do we actually draw them on the screen?

### Terminal Cell Coordinates

The terminal grid IS our coordinate system. Each character cell is 1 unit.

**Key insight:** We work directly in terminal cell coordinates (where 1.0 = one cell), but use floating-point precision.

Example: A point at `(5.7, 10.3)` means 5.7 cells right, 10.3 cells down. This fractional position is preserved through all transformations.

### Aspect Ratio Correction

Terminal characters are roughly twice as tall as they are wide. To compensate:

```python
# Map world coordinates to terminal cell coordinates
terminal_x = origin_x + world_x * 2  # Scale x by 2
terminal_y = origin_y - world_y       # Flip y (terminal coords go down)
```

The `* 2` on x-coordinates makes circles look round instead of squashed.

**Important:** The results are still floats (like `43.6` cells). We maintain sub-cell precision through the entire pipeline - rotation, projection, scaling - all in terminal cell coordinates.

### When Do We Snap to Integer Cells?

Only at the final rasterization step, when determining which actual cells to fill:

```python
# Polygon vertices are in continuous terminal cell coordinates
vertices = [(5.7, 10.3), (15.2, 10.8), (15.4, 20.1), (5.3, 20.4)]

# Rasterizer uses these fractional coordinates to find edge intersections
# Only floors when deciding which cells to fill
for y in range(floor(min_y), floor(max_y) + 1):
    left_x, right_x = find_intersections(y)  # Returns floats like 5.7, 15.2
    fill_cells(floor(left_x), floor(right_x))  # Fill cells 5 through 15
```

This keeps animations smooth - even tiny rotations update the fractional coordinates, and different cells get filled as shapes glide smoothly across the grid.

### Polygon Fill (Convex Polygons Only)

The polygon fill algorithm only works for **convex polygons** - shapes where all interior angles are less than 180°. A square or triangle is convex. A star or C-shape is not.

### Scanline Algorithm

The current implementation uses a scanline approach. After trying different rasterization variants, this is the most optimized solution.

**How it works:**

1. For each horizontal row `y` in the polygon's bounding box:
   - Find where the row intersects the polygon edges
   - This gives us a leftmost point and rightmost point
   - Fill all pixels between left and right

**Visual example:**

```
       Bounding Box
    ┌──────●──────┐  ← Top vertex
    │   .-' '-.   │
    │ .-'     '-. │
    ●─────────────●  ← Scanline finds left (●) and right (●) intersections
    │'-▓▓▓▓▓▓▓  .-'  ← Fill pixels between intersections (▓)
    │  '-▓▓▓  .-' │
    └────'-●-'────┘  ← Bottom vertex
```

For each horizontal row, we find exactly 2 intersection points (left and right), then fill everything between them.

```python
def rasterize_polygon(vertices):
    for y in range(min_y, max_y + 1):
        # Find left and right intersection points
        left_x, right_x = find_edge_intersections(vertices, y)

        # Fill the span
        for x in range(left_x, right_x + 1):
            draw_pixel(x, y)
```

**Finding intersections:**

For a given scanline at height `y`, check each edge of the polygon:
- If the edge crosses the scanline, calculate where using linear interpolation
- The first intersection is the left boundary, the second is the right boundary

```python
# Linear interpolation to find x where edge crosses y
x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
```

**Why this is fast:**
- Only visits pixels inside the polygon (no wasted checks)
- Simple arithmetic (addition and comparison in the inner loop)
- Cache-friendly memory access (fills pixels left-to-right)

---

## 3D Graphics

### Projection: Mapping 3D  → 2D

**Problem:** How do we display a 3D object on a 2D screen?

**Answer:** Map 3D points to 2D by simulating a camera.

**Concept:** Draw lines from the 3D object through a 2D plane (screen) to the camera. Where each line intersects the plane is where we draw.

```
Side view (looking along X-axis):

         Y-axis
           ↑
           |                                 (x, y, z)
           |               Screen Plane        .-●
           |                     |          .-'  |
           |                     |       .-'     |
           |                     |    .-'        |
           |          (x',y',z') | .-'           |
           |                    .●'              |
           |                 .-' |               | y
           |              .-'    |               |
           |           .-'       |               |
           |        .-'          | y'            |
           |     .-'             |               |
   Camera  |  .-'                |               |
  (origin) ●─────────────────────┼───────────────┼─→ Z-axis (depth)
           0             z'=focal_length         z
```

- Object point in 3D: `(x, y, z)`
- Projected point on screen plane: `(x', y', z')` where `z' = focal_length`
- For 2D rendering, we only use `(x', y')`

**Projection formula:**

$$x' = \frac{x \cdot z'}{z}, \quad y' = \frac{y \cdot z'}{z}, \quad z' = \text{focal length}$$

```python
def project(point_3d, focal_length=256):
    x, y, z = point_3d
    if z == 0:
        z = 0.1  # Avoid division by zero

    scale = focal_length / z
    x_2d = x * scale
    y_2d = y * scale
    return (x_2d, y_2d)
```

Objects farther away (larger `z`) appear smaller (smaller scale).

<details>
<summary>Derivation using similar triangles</summary>

**Setup:**
- Camera at origin `(0, 0, 0)`
- Screen plane at `z = focal_length` (parallel to xy-plane)
- Object at `z > focal_length` (farther away)

From the diagram, we have two similar triangles:
- Small triangle: camera to projected point (height `y'`, depth `focal_length`)
- Large triangle: camera to object point (height `y`, depth `z`)

Using similar triangles:

$$\frac{y'}{z'} = \frac{y}{z}$$

Solving for `y'`:

$$y' = \frac{y z'}{z}$$

The same applies for the x-coordinate:

$$x' = \frac{x z'}{z}$$

</details>

---

## Building a 3D Cube

A cube is just 6 squares arranged in 3D space.

**Define vertices:**

```python
vertices = [
    (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),  # Back face
    (-1, -1,  1), (1, -1,  1), (1, 1,  1), (-1, 1,  1)   # Front face
]
```

**Define faces** (each face is 4 vertex indices):

```python
faces = [
    [0, 1, 2, 3],  # Back
    [4, 5, 6, 7],  # Front
    [0, 1, 5, 4],  # Bottom
    [2, 3, 7, 6],  # Top
    [0, 3, 7, 4],  # Left
    [1, 2, 6, 5]   # Right
]
```

Each face is a polygon. Draw all 6 faces and you have a cube.

---

## 3D Rotation

In 3D, we have three rotation axes: X, Y, Z.

### Rotation Around X-axis

Y and Z change, X stays constant:

$$x' = x$$
$$y' = y\cos(\theta) - z\sin(\theta)$$
$$z' = y\sin(\theta) + z\cos(\theta)$$

### Rotation Around Y-axis

X and Z change, Y stays constant:

$$x' = x\cos(\theta) + z\sin(\theta)$$
$$y' = y$$
$$z' = z\cos(\theta) - x\sin(\theta)$$

### Rotation Around Z-axis

X and Y change, Z stays constant (same as 2D rotation):

$$x' = x\cos(\theta) - y\sin(\theta)$$
$$y' = x\sin(\theta) + y\cos(\theta)$$
$$z' = z$$

**Pattern:** The axis you rotate around doesn't change.

### Applying Rotations

Apply all three rotations sequentially:

```python
def rotate_3d(point, angle_x, angle_y, angle_z):
    x, y, z = point

    # Rotate around X
    y, z = y * cos(angle_x) - z * sin(angle_x), y * sin(angle_x) + z * cos(angle_x)

    # Rotate around Y
    x, z = x * cos(angle_y) + z * sin(angle_y), z * cos(angle_y) - x * sin(angle_y)

    # Rotate around Z
    x, y = x * cos(angle_z) - y * sin(angle_z), x * sin(angle_z) + y * cos(angle_z)

    return (x, y, z)
```

---

## Complete Pipeline

For each frame:

1. **Rotate** all vertices in 3D
2. **Project** 3D vertices to 2D screen coordinates
3. **Draw** each face by connecting projected points
4. **Display** the frame

```python
# Rotate all vertices
rotated = [rotate_3d(v, angle_x, angle_y, angle_z) for v in vertices]

# Project to 2D
projected = [project(v) for v in rotated]

# Draw each face
for face in faces:
    points = [projected[i] for i in face]
    polygon(points)
```

---

## Summary

**2D Rotation:**
- Points as tuples
- Rotation formula derived from polar coordinates
- Rotate multiple points to rotate shapes

**Rasterization:**
- Scanline algorithm fills convex polygons
- Find left/right intersections per row
- Fill pixels between boundaries

**3D Extension:**
- Add Z axis
- Three rotation axes (X, Y, Z)
- Projection maps 3D to 2D using perspective

**Complete Pipeline:**
- Define geometry (vertices, faces)
- Apply 3D transformations (rotation)
- Project to 2D screen (perspective)
- Rasterize polygons (scanline fill)
- Display on terminal

---

*BTW I spent more time trying to map all this into the terminal than the actual math*
