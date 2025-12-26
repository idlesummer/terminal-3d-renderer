# From Square to Cube

*Understanding 3D Graphics Step by Step*

---

## What We're Building

You're going to learn how computers turn 3D objects into 2D images on your screen. We'll start with something simple—a rotating square—and work our way up to a spinning 3D cube.

> **The Journey:** Think of this like learning to ride a bike. We'll start with training wheels (2D rotation), then gradually remove them until you're doing tricks (3D graphics).

---

## Step 1: Rotating a Square (2D)

### Understanding Coordinates

Imagine a piece of graph paper. Every point on that paper has two numbers: how far right (x) and how far up (y).

```
      Y (up)
      |
      |
      |_ _ _ _ X (right)
     O
```

Point at (3, 2) means: go 3 units right, 2 units up.

### What Is Rotation?

Rotation means spinning something around a point (usually the center). When you rotate a square, each corner moves to a new position.

**The Magic Formula:** To rotate any point around the center, we use a simple trick from trigonometry (don't worry, Python does the math for us).

$$x' = x \cdot \cos(\theta) - y \cdot \sin(\theta)$$

$$y' = x \cdot \sin(\theta) + y \cdot \cos(\theta)$$

**What this means:**
- $x'$ and $y'$ are the new coordinates after rotation
- $\theta$ is how much we're spinning (in radians—think of it as a measure of turn)

### Code Example

Here's how we rotate a point in Python:

```python
from math import cos, sin

def rotate_point(x, y, angle):
    # Calculate new position after rotation
    new_x = x * cos(angle) - y * sin(angle)
    new_y = x * sin(angle) + y * cos(angle)
    return new_x, new_y
```

That's it! This tiny function can rotate any point around the origin (0, 0).

**Try it:** Run `square.py` to see a rotating square in your terminal. Watch how all four corners move in a circle.

---

## Step 2: Thinking in 3D

### Adding the Third Dimension

In 2D, we had X (left/right) and Y (up/down). In 3D, we add Z (forward/backward).

```
        Y (up)
        |
        |
        |_ _ _ _ _ X (right)
       /
      /
     Z (toward you)
```

Now points have three numbers: (x, y, z)

> **Real World Example:** Imagine you're a bird looking down at a city. X is east/west, Y is how tall buildings are, and Z is north/south. Every building corner has three coordinates.

### Three Ways to Rotate

In 2D, we could only spin things around one point. In 3D, we can rotate around three different axes.

**Rotation around X-axis (Pitch)**  
Like nodding your head "yes"

**Rotation around Y-axis (Yaw)**  
Like shaking your head "no"

**Rotation around Z-axis (Roll)**  
Like tilting your head sideways

### The Rotation Formulas

#### Around X-axis (nodding):

$$x' = x$$

$$y' = y \cdot \cos(\theta) - z \cdot \sin(\theta)$$

$$z' = y \cdot \sin(\theta) + z \cdot \cos(\theta)$$

Notice: $x$ stays the same! We're spinning around the X-axis, so X doesn't change.

#### Around Y-axis (shaking head):

$$x' = x \cdot \cos(\theta) + z \cdot \sin(\theta)$$

$$y' = y$$

$$z' = z \cdot \cos(\theta) - x \cdot \sin(\theta)$$

Now $y$ stays constant because we're rotating around it.

#### Around Z-axis (tilting):

$$x' = x \cdot \cos(\theta) - y \cdot \sin(\theta)$$

$$y' = x \cdot \sin(\theta) + y \cdot \cos(\theta)$$

$$z' = z$$

This one is just like our 2D rotation! $z$ doesn't change.

> **Pattern Recognition:** See how these are similar to our 2D formula? We're just applying the same rotation trick to different pairs of coordinates.

---

## Step 3: Squashing 3D into 2D

### The Problem

Your screen is flat (2D), but our cube exists in 3D space. We need to "flatten" it somehow. This is called **projection**.

> **Real Life Example:** Think about taking a photo. You're capturing a 3D scene (the real world) onto a 2D surface (the photo). That's exactly what projection does.

### Perspective Makes It Real

Objects that are farther away should look smaller. This is called **perspective projection**.

Imagine looking down railroad tracks—they appear to get closer together in the distance.

### The Projection Formula

$$\text{scale} = \frac{\text{focal\_length}}{z}$$

$$\text{screen}_x = x \cdot \text{scale}$$

$$\text{screen}_y = y \cdot \text{scale}$$

**Breaking it down:**
- **focal_length:** Like the zoom on a camera. Bigger = more zoomed in
- $z$: How far away the point is from the camera
- **scale:** How much to shrink the point

**Key insight:** Bigger $z$ (farther away) → smaller scale → smaller on screen!

### Putting It Together

```python
def project_to_2d(x, y, z, focal_length=100):
    # Points farther away (bigger z) appear smaller
    scale = focal_length / z
    
    # Apply perspective
    screen_x = x * scale
    screen_y = y * scale
    
    return screen_x, screen_y
```

> **Magic Moment:** This simple division (focal_length ÷ z) is what makes distant objects look small and creates the illusion of depth!

---

## Step 4: The Complete Journey

### From 3D Cube to Screen Pixels

Let's trace what happens to a single point on our cube:

**Start:** Point at (100, 100, 300)

↓

**Step 1 - Rotate (3D):**
- Apply X, Y, Z rotations
- New position: (85, 120, 280)

↓

**Step 2 - Project (3D→2D):**
- scale = 100 ÷ 280 = 0.357
- Screen position: (30, 43)

↓

**Step 3 - Draw:**
- Put a character at row 43, column 30

### One More Thing: Drawing Order

What if one face of the cube is behind another? We need to draw the back faces first, then the front faces on top.

> **Painter's Algorithm:** Just like painting a picture, we paint the background first, then the foreground. We sort faces by their distance (z-value) and draw from farthest to nearest.

```python
# Sort faces by depth (farthest first)
faces.sort(key=lambda face: face.average_z, reverse=True)

# Draw from back to front
for face in faces:
    draw_face(face)
```

---

## You Did It!

### What You Learned

- **2D Rotation:** How to spin points around a center using sin and cos
- **3D Coordinates:** Adding a third dimension (z) to represent depth
- **3D Rotation:** Spinning around three different axes (X, Y, Z)
- **Perspective Projection:** Making far things look small (the magic of depth)
- **Rendering Pipeline:** The complete journey from 3D object to 2D screen

### Ready to See It in Action?

Run `python cube.py` in your terminal and watch all these concepts come together in a beautiful spinning cube! Every frame applies all these transformations dozens of times.

> **Next Steps:** Try changing the rotation speeds in the code, or add more shapes. You now understand the fundamentals of 3D graphics—the same concepts used in video games and movies!

---

*Made with math and patience*