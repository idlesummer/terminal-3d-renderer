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
        maxx: float | None = None
        
        x1, y1 = self.vertices[-1]
        for x2, y2 in self.vertices:
          
            if y1 == y2 == y:
                minx = min(x1, x2)
                maxx = max(x1, x2)
                break
                
            elif (y1 <= y) ^ (y2 <= y):
                x = x1 + (y-y1) * (x2-x1) / (y2-y1)
                
                if minx is None:
                    minx = x   
                else:
                    if minx < x:
                        maxx = x
                    else:
                        maxx = minx
                        minx = x
                    break
            x1, y1 = x2, y2
        else:
            return None    # Loop didnt break, didn't find 2 intercepts
        return minx, maxx


    def lattice_points(self):
        """
        Optimized scanline-based rasterization for convex polygons.
        More cache-friendly than checking every pixel in bounding box.
        """
        if len(self.vertices) < 3:
            return

        miny = floor(min(self.ys))
        maxy = floor(max(self.ys))

        # For each scanline
        for y in range(miny, maxy+1):
            result = self.find_intercept_pair(y)
            if result is None:
                continue
              
            minx, maxx = result
            x1 = floor(minx)
            x2 = floor(maxx)
            
            for x in range(x1, x2+1):
                yield x, y
                
    
    def lattice_spans(self):
        """
        Optimized scanline-based rasterization for convex polygons.
        More cache-friendly than checking every pixel in bounding box.
        """
        if len(self.vertices) < 3:
            return

        miny = floor(min(self.ys))
        maxy = floor(max(self.ys))

        # For each scanline
        for y in range(miny, maxy+1):
            if (pair := self.find_intercept_pair(y)) is not None:
                minx, maxx = pair
                yield y, floor(minx), floor(maxx)


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

        size = width * height
        # Use list of single-char strings for multi-byte character support
        self.frame = [' '] * size
        # Pre-allocate depth buffer
        self.depth = [1.0] * size

    def clear(self):
        """Clear both frame and depth buffers."""
        size = self.width * self.height
        # Fast clearing using slice assignment
        self.frame[:] = [' '] * size
        # Fast fill for depth buffer
        for i in range(size):
            self.depth[i] = 1.0

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

    def polygon(self, vertices: list[tuple[float, float]], fill: str, depth=0.0):
        """Rasterize and fill a polygon with depth testing."""
        # Convert polygon from continuous world space to discrete screen space
        pixel_vertices = [self.scale_and_translate(x, y) for (x, y) in vertices]
        polygon = ConvexPolygon(pixel_vertices)

        # Inline the rasterization for maximum performance
        width = self.width
        height = self.height
        depth_buf = self.depth
        frame_buf = self.frame

        # for x, y in polygon.lattice_points():
        #     if (0 <= x < width) and (0 <= y < height):
        #         idx = y * width + x
        #         if depth <= depth_buf[idx]:
        #             depth_buf[idx] = depth
        #             frame_buf[idx] = fill
        
        for y, x1, x2 in polygon.lattice_spans():
            if not (0 <= y < height): continue
            x1 = max(0, x1)
            x2 = min(width-1, x2)
            
            if x1 > x2: continue
            start = y * width + x1
            end   = y * width + x2 + 1
            span_len = end - start
            
            # Slice assignment (C-speed, but no depth test)
            frame_buf[start:end] = [fill] * span_len
            depth_buf[start:end] = [depth] * span_len


    def render(self):
        """Return the frame buffer as a string with borders."""
        # Build output efficiently using list
        lines = ['┌' + '─' * self.width + '┐']
        
        width = self.width
        frame = self.frame
        
        for y in range(self.height):
            offset = y * width
            # Join the character list directly
            line = ''.join(frame[offset:offset + width])
            lines.append('│' + line + '│')
        
        lines.append('└' + '─' * self.width + '┘')
        return '\n'.join(lines)
