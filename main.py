from math import cos, sin, floor, pi
import time 


class Polygon:
    """A polygon defined by N vertices in continuous space."""
    vertices: list[tuple[float, float]]
    xs: tuple[float, ...]
    ys: tuple[float, ...]

    def __init__(self, vertices: list[tuple[float, float]]):
        """Create polygon from vertices."""
        self.vertices = vertices
        self.xs, self.ys = zip(*vertices)

    @staticmethod    
    def segment_contains(
        x:  float, y:  float, 
        x1: float, y1: float, 
        x2: float, y2: float,
    ):
        """Return True if point (x, y) lies exactly on the segment from (x1, y1) to (x2, y2) inclusive."""
        if (x-x1)*(y2-y1) - (y-y1)*(x2-x1) != 0:                # Collinearity check (cross product)
            return False
        return (x-x1) * (x-x2) <= 0 and (y-y1) * (y-y2) <= 0    # Between check (inclusive)

    def contains(self, x: float, y: float):
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

    def lattice_points(self):
        """Iterate over all (x, y) integer points inside the polygon."""
        minx, maxx = floor(min(self.xs)), floor(max(self.xs))
        miny, maxy = floor(min(self.ys)), floor(max(self.ys))

        for y in range(miny, maxy + 1):
            for x in range(minx, maxx + 1):
                if self.contains(x, y):
                    yield x, y


class Screen:
    """
    Draws shapes on a screen using world coordinates with the origin in the center.
    Horizontally stretched 2:1 to look right on a terminal.
    """
    width: int
    height: int
    ox: int
    oy: int
    frame: list[str]
    depth: list[float]

    def __init__(self, width: int, height: int):
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

    def set_pixel(self, x: int, y: int, char: str, depth: float):
        """Draw a single pixel with depth testing."""
        if (0 <= x < self.width) and (0 <= y < self.height):
            idx = y * self.width + x
            if depth <= self.depth[idx]:
                self.depth[idx] = depth
                self.frame[idx] = char

    def scale_and_translate(self, x: float, y: float):
        """Scale and translate world coordinates to screen-aligned continuous coordinates."""
        sx = self.ox + x * 2    # horizontal units are 2:1 to compensate terminal aspect ratio
        sy = self.oy - y
        return sx, sy

    def point(self, x: float, y: float, fill: str, depth=0.0):
        """Draw a single world-space point."""
        sx, sy = self.scale_and_translate(x, y)
        self.set_pixel(floor(sx), floor(sy), fill, depth)

    def polygon(self, vertices: list[tuple[float, float]], fill, depth=0.0):
        """Rasterize and fill a polygon with depth testing."""
        # Convert polygon from continuous world space to discrete screen space
        # before generating lattice points; accounts for 2:1 horizontal scaling
        pixel_vertices = [self.scale_and_translate(x, y) for (x, y) in vertices]
        polygon = Polygon(pixel_vertices)

        for x, y in polygon.lattice_points():
            self.set_pixel(x, y, char=fill, depth=depth)

    def render(self):
        """Return the frame buffer as a string with borders."""
        buffer = ['┌' + '─' * self.width + '┐\n']

        for y in range(self.height):
            offset = y * self.width
            buffer.append('│')
            buffer.extend(''.join(self.frame[offset:offset+self.width]))
            buffer.append('│\n')

        buffer.append('└' + '─' * self.width + '┘')
        return ''.join(buffer)


def main():
    screen = Screen(width=80, height=40)

    # Define square in Cartesian (world) space
    s = 25
    square = [(-s/2, -s/2), (s/2, -s/2), (s/2, s/2), (-s/2, s/2)]
    angle = 0.0

    # Clear screen and hide cursor
    print('\033[2J\033[?25l', end='')

    try:
        while True:
            screen.clear()

            # Rotate square in world space
            rotated = []
            for x, y in square:
                nx = x * cos(angle) - y * sin(angle)
                ny = x * sin(angle) + y * cos(angle)
                rotated.append((nx, ny))

            # Draw (screen handles coordinate transformation)
            screen.polygon(rotated, fill='·')

            print('\033[H', end='')
            print(screen.render())

            angle += pi / 96
            time.sleep(0.05)

    except KeyboardInterrupt:
        print('\033[?25h\n\nStopped.')


if __name__ == '__main__':
    main()
