from math import floor
from typing import Self


class Point:
    x: float
    y: float
    z: float
    
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
        
    def coords(self):
        return self.x, self.y, self.z
    
    def __sub__(self, other: Self):
        return Point(self.x-other.x, self.y-other.y, self.z-other.z)


class ConvexPolygon:
    """A convex polygon defined by N vertices in continuous space."""
    vertices: list[tuple[float, float]]
    xs: tuple[float, ...]
    ys: tuple[float, ...]

    def __init__(self, vertices: list[tuple[float, float]]):
        """Create polygon from vertices."""
        self.vertices = vertices
        self.xs, self.ys = zip(*vertices)
      
    def find_intercept_pair(self, y: int) -> tuple[float, float] | None:
        minx: float | None = None
        x1, y1 = self.vertices[-1]

        for x2, y2 in self.vertices:
            if y1 == y2 == y:       # if y lies in a horizontal edge
                return min(x1, x2), max(x1, x2)

            if (y1 <= y) ^ (y2 <= y): # if y ∈ [min(y1,y2), max(y1,y2))
                x = x1 + (y-y1) * (x2-x1) / (y2-y1)
                if minx is None:    # first hit
                    minx = x   
                else:               # second hit
                    return min(minx, x), max(minx, x)
            x1, y1 = x2, y2
        return None

    def lattice_spans(self):
        """
        Optimized scanline-based rasterization for convex polygons.
        More cache-friendly than checking every pixel in bounding box.
        """
        if len(self.vertices) < 3: return
        miny = floor(min(self.ys))
        maxy = floor(max(self.ys))

        for y in range(miny, maxy+1):
            if (pair := self.find_intercept_pair(y)) is not None:
                minx, maxx = pair
                yield y, floor(minx), floor(maxx)


class Screen:
    """
    Draws shapes on a screen using world coordinates with the origin in the center.
    Horizontally stretched 2:1 to look correct on a terminal.
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

        # Use list of single-char strings for multi-byte character support
        self.frame_buf = [' '] * (size := width*height)
        self.depth_buf = [1.0] * size

    def clear(self):
        """Clear both frame and depth buffers."""
        size = self.width * self.height
        # Fast clearing using slice assignment
        self.frame_buf = [' '] * size
        self.depth_buf = [1.0] * size

    def scale_and_translate(self, x: float, y: float):
        """Scale and translate world coordinates to screen-aligned continuous coordinates."""
        sx = self.ox + x*2  # horizontal units are 2:1 to compensate terminal aspect ratio
        sy = self.oy - y
        return sx, sy

    def point(self, x: float, y: float, fill: str, depth=0.0):
        """Draw a single world-space point."""
        sx, sy = self.scale_and_translate(x, y)
        sx, sy = int(sx), int(sy)

        if (0 <= sx < self.width) and (0 <= sy < self.height):
            idx = sy * self.width + sx
            if depth <= self.depth_buf[idx]:
                self.depth_buf[idx] = depth
                self.frame_buf[idx] = fill

    def polygon(self, vertices: list[tuple[float, float]], fill: str, depth=0.0):
        """Rasterize and fill a polygon with depth testing."""
        # Convert polygon from continuous world space to discrete screen space
        pixel_vertices = [self.scale_and_translate(x, y) for (x, y) in vertices]
        polygon = ConvexPolygon(pixel_vertices)

        # Cache attributes for maximum performance
        width, height = self.width, self.height
        depth_buf = self.depth_buf
        frame_buf = self.frame_buf
        
        for y, x1, x2 in polygon.lattice_spans():
            if not (0 <= y < height): continue
            x1, x2 = max(0, x1), min(width-1, x2)

            if x1 > x2: continue
            idx = y*width + x1

            for _ in range(x1, x2+1):
                if depth <= depth_buf[idx]:
                    depth_buf[idx] = depth
                    frame_buf[idx] = fill
                idx += 1 

    def render(self):
        """Return the frame buffer as a string with borders."""
        # Build output efficiently using list
        lines = ['┌' + '─' * self.width + '┐']
        width = self.width
        frame = self.frame_buf

        for y in range(self.height):
            row = y * width
            # Join the character list directly
            line = ''.join(frame[row:row + width])
            lines.append('│' + line + '│')

        lines.append('└' + '─' * self.width + '┘')
        return '\n'.join(lines)
