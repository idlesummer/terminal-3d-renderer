import math
import time


# ============================================================================
# POLYGON CLASS
# ============================================================================

class Polygon:
    """A general polygon defined by N vertices."""

    def __init__(self, vertices):
        self.vertices = vertices

        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]

        self.min_x = math.floor(min(xs))
        self.max_x = math.floor(max(xs))
        self.min_y = math.floor(min(ys))
        self.max_y = math.floor(max(ys))

    def points(self):
        """Iterate over all (x, y) points in the bounding box."""
        for y in range(self.min_y, self.max_y + 1):
            for x in range(self.min_x, self.max_x + 1):
                yield x, y

    def __getitem__(self, idx):
        """Allow indexing: poly[i] gives vertex i."""
        return self.vertices[idx]


# ============================================================================
# MATRIX CLASS
# ============================================================================

class Matrix:
    def __init__(self, height, width, fill):
        self.h = height
        self.w = width
        self.buf = [fill] * (width * height)

    def __getitem__(self, pos):
        x, y = pos
        return self.buf[y * self.w + x]

    def __setitem__(self, pos, value):
        x, y = pos
        self.buf[y * self.w + x] = value

    def fill(self, value):
        self.buf = [value] * (self.w * self.h)

    def row(self, y):
        """Get entire row as a list"""
        sta = y * self.w
        end = sta + self.w
        return self.buf[sta:end]


# ============================================================================
# RENDERER
# ============================================================================


class Renderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.frame = Matrix(height, width, ' ')
        self.depth = Matrix(height, width, 0.0)

    def clear(self):
        """Clear both buffers"""
        self.frame.fill(' ')
        self.depth.fill(0.0)

    def set_pixel(self, x, y, char, depth):
        """Draw a single pixel with depth testing"""
        if not (0 <= x < self.width): return
        if not (0 <= y < self.height): return
        if depth <= self.depth[x, y]: return

        self.depth[x, y] = depth
        self.frame[x, y] = char

    def fill_quad(self, vertices_2d, char='#'):
        """Fill a quad with depth testing"""
        quad = Polygon(vertices_2d)

        # Clamp bounding box to screen bounds
        min_x = max(0, quad.min_x)
        max_x = min(self.width - 1, quad.max_x)
        min_y = max(0, quad.min_y)
        max_y = min(self.height - 1, quad.max_y)

        # Fill all pixels inside quad
        for py in range(min_y, max_y + 1):
            for px in range(min_x, max_x + 1):
                if self._point_in_quad(px, py, quad[0], quad[1], quad[2], quad[3]):
                    depth = self._interpolate_depth(px, py, quad[0], quad[1], quad[2], quad[3])

                    if depth > self.depth[px, py]:
                        self.depth[px, py] = depth
                        self.frame[px, py] = char

    def _point_in_quad(self, px, py, v0, v1, v2, v3):
        """Check if point is inside quad"""
        def sign(px, py, ax, ay, bx, by):
            return (px - bx) * (ay - by) - (ax - bx) * (py - by)
        
        d1 = sign(px, py, v0[0], v0[1], v1[0], v1[1])
        d2 = sign(px, py, v1[0], v1[1], v2[0], v2[1])
        d3 = sign(px, py, v2[0], v2[1], v3[0], v3[1])
        d4 = sign(px, py, v3[0], v3[1], v0[0], v0[1])
        
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0) or (d4 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0) or (d4 > 0)
        return not (has_neg and has_pos)
    
    def _interpolate_depth(self, px, py, v0, v1, v2, v3):
        """Interpolate depth at pixel"""
        total_weight = 0.0
        weighted_depth = 0.0
        
        for vx, vy, vz in [v0, v1, v2, v3]:
            dist = math.sqrt((px - vx)**2 + (py - vy)**2)
            if dist < 0.001:
                return vz
            weight = 1.0 / (dist + 0.1)
            weighted_depth += weight * vz
            total_weight += weight
        
        return weighted_depth / total_weight
    
    def display(self):
        """Display to terminal"""
        print("\033[H", end="")
        for y in range(self.height):
            row = self.frame.row(y)
            print(''.join(row))
            

# ============================================================================
# MAIN - ROTATING SQUARE
# ============================================================================

def main():
    renderer = Renderer(width=80, height=40)

    # Clear screen and hide cursor
    print("\033[2J\033[?25l", end="")

    # Define square
    s = 15
    square = [
        (-s/2, -s/2),
        (s/2, -s/2),
        (s/2, s/2),
        (-s/2, s/2),
    ]

    angle = 0.0

    try:
        while True:
            renderer.clear()

            # Rotate square
            rotated = []
            for x, y in square:
                new_x = x * math.cos(angle) - y * math.sin(angle)
                new_y = x * math.sin(angle) + y * math.cos(angle)

                # Convert to screen coordinates
                screen_x = renderer.width // 2 + new_x * 2
                screen_y = renderer.height // 2 - new_y

                rotated.append((screen_x, screen_y, 1.0))

            # Draw
            renderer.fill_quad(rotated, '.')
            renderer.display()

            angle += 0.05
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\033[?25h\n\nStopped.")


if __name__ == "__main__":
    main()
