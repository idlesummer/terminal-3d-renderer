from math import cos, floor, sin
import time 


class Polygon:
    """A polygon defined by N vertices in continuous space."""

    def __init__(self, vertices):
        """Create polygon from vertices."""
        self.vertices = vertices
        self.xs, self.ys = zip(*vertices)

    @staticmethod    
    def segment_contains(x, y, x1, y1, x2, y2):
        """Return True if point (x, y) lies exactly on the segment from (x1, y1) to (x2, y2) inclusive."""

        # Collinearity check (cross product)
        if (x-x1)*(y2-y1) - (y-y1)*(x2-x1) != 0:
            return False

        # Between check (inclusive)
        return (x-x1) * (x-x2) <= 0 and (y-y1) * (y-y2) <= 0

    def contains(self, x, y):
        """Point-in-polygon (edge/vertex inclusive) using ray casting with a half-open rule."""
        inside = False

        # Start with last vertex to close the loop
        x1, y1 = self.vertices[-1]
        for x2, y2 in self.vertices:
            if self.segment_contains(x, y, x1, y1, x2, y2):
                return True

            # Ray casting (half-open)
            if (y1 > y) != (y2 > y):                            # Does the scanline y cross the vertical span of this edge?
                x_intercept = x1 + (y-y1) * (x2-x1) / (y2-y1)   # Compute x intersection

                if x < x_intercept:                             # Count only intersections to the RIGHT of the point
                    inside = not inside
            x1, y1 = x2, y2                                     # Advance to next vertex

        return inside


class BoundingBox:
    """
    Discrete bounding box for polygon rasterization.
    
    Handles the conversion from continuous geometry to discrete
    screen pixels. Responsible for all discrete/pixel operations.
    """

    def __init__(self, polygon: Polygon, width, height):
        self.polygon = polygon

        # Discretize continuous bounds to integer pixels
        self.minx = floor(min(polygon.xs))
        self.maxx = floor(max(polygon.xs))
        self.miny = floor(min(polygon.ys))
        self.maxy = floor(max(polygon.ys))
        
        # Clamp to screen bounds
        self.minx = max(0, self.minx)
        self.maxx = min(width - 1, self.maxx)
        self.miny = max(0, self.miny)
        self.maxy = min(height - 1, self.maxy)

    def interior_cells(self):
        """Iterate over all (x, y) integer points in the bounding box."""
        for y in range(self.miny, self.maxy + 1):
            for x in range(self.minx, self.maxx + 1):
                if self.polygon.contains(x, y):
                    yield x, y

 
class Screen:
    """Software renderer; assumes world coordinates, centers origin, fixed 2:1 scaling."""

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.ox = width // 2      # origin at center (x)
        self.oy = height // 2     # origin at center (y)

        # Inline 2D buffers
        self.frame = [' '] * (width * height)
        self.depth = [1.0] * (width * height)   # 0.0 = near, 1.0 = far

    def clear(self):
        """Clear both frame and depth buffers."""
        self.frame[:] = [' '] * (self.width * self.height)
        self.depth[:] = [1.0] * (self.width * self.height)

    def set_pixel(self, x, y, char, depth):
        """Draw a single pixel with depth testing (unsafe)."""
        idx = y * self.width + x
        if depth <= self.depth[idx]:
            self.depth[idx] = depth
            self.frame[idx] = char

    def world_to_screen(self, x, y):
        """Convert world coordinates to screen coordinates."""
        sx = self.ox + x * 2    # horizontal units are 2:1 to compensate terminal aspect ratio
        sy = self.oy - y
        return sx, sy
    
    def point(self, pos, char, depth=0.0):
        """Draw a single world-space point."""
        x, y = pos
        sx, sy = self.world_to_screen(x, y)

        # Only draw if inside screen
        if 0 <= sx < self.width and 0 <= sy < self.height:
            self.set_pixel(sx, sy, char, depth)

    def polygon(self, vertices, fill='#', depth=0.0):
        """Rasterize and fill a polygon with depth testing."""
        # Convert world coordinates to screen coordinates
        screen_vertices = [self.world_to_screen(x, y) for (x, y) in vertices]
        polygon = Polygon(screen_vertices)
        bbox = BoundingBox(polygon, self.width, self.height)

        for x, y in bbox.interior_cells():
            self.set_pixel(x, y, char=fill, depth=depth)

    def display(self):
        """Display the frame buffer to terminal."""
        
        print('\033[H', end='')
        print('┌' + '─' * self.width + '┐') # Header
        
        for y in range(self.height):        # Content
            start = y * self.width
            end = start + self.width
            print('│' + ''.join(self.frame[start:end]) + '│')

        print('└' + '─' * self.width + '┘') # Footer


def main():
    screen = Screen(width=80, height=40)

    # Clear screen and hide cursor
    print('\033[2J\033[?25l', end='')

    # Define square in Cartesian (world) space
    s = 25
    square = [(-s/2, -s/2), (s/2, -s/2), (s/2, s/2), (-s/2, s/2)]
    angle = 0.0

    try:
        while True:
            screen.clear()

            # Rotate square in world space
            rotated = []
            for x, y in square:
                newx = x * cos(angle) - y * sin(angle)
                newy = x * sin(angle) + y * cos(angle)
                rotated.append((newx, newy))

            # Draw (screen handles coordinate transformation)
            screen.polygon(rotated, fill='.')
            screen.display()

            angle += 0.05
            time.sleep(0.05)

    except KeyboardInterrupt:
        print('\033[?25h\n\nStopped.')


if __name__ == '__main__':
    main()
