import math
import time

# ============================================================================
# ROTATION
# ============================================================================

def rotation_matrix_x(angle):
    """Rotation matrix around X-axis"""
    c, s = math.cos(angle), math.sin(angle)
    return [
        [1, 0, 0],
        [0, c, -s],
        [0, s, c]
    ]

def rotation_matrix_y(angle):
    """Rotation matrix around Y-axis"""
    c, s = math.cos(angle), math.sin(angle)
    return [
        [c, 0, s],
        [0, 1, 0],
        [-s, 0, c]
    ]

def rotation_matrix_z(angle):
    """Rotation matrix around Z-axis"""
    c, s = math.cos(angle), math.sin(angle)
    return [
        [c, -s, 0],
        [s, c, 0],
        [0, 0, 1]
    ]

def multiply_matrix_vector(matrix, vector):
    """Multiply 3x3 matrix by 3D vector"""
    return [
        sum(matrix[i][j] * vector[j] for j in range(3))
        for i in range(3)
    ]

def rotate_point(point, angle_x, angle_y, angle_z):
    """
    Rotate a 3D point by given angles.
    
    Args:
        point: (x, y, z) tuple
        angle_x, angle_y, angle_z: rotation angles in radians
    
    Returns:
        (x, y, z) rotated point
    """
    rotated = list(point)
    
    # Apply rotations in order: X, Y, Z
    for matrix in [rotation_matrix_x(angle_x), 
                   rotation_matrix_y(angle_y), 
                   rotation_matrix_z(angle_z)]:
        rotated = multiply_matrix_vector(matrix, rotated)
    
    return tuple(rotated)

def rotate_points(points, angle_x, angle_y, angle_z):
    """Rotate multiple points"""
    return [rotate_point(p, angle_x, angle_y, angle_z) for p in points]


# ============================================================================
# PROJECTION
# ============================================================================

def project_point(point_3d, distance_from_cam=60, K1=40):
    """
    Project a 3D point to 2D screen coordinates.
    
    Args:
        point_3d: (x, y, z) tuple
        distance_from_cam: distance of camera from origin
        K1: perspective scaling factor
    
    Returns:
        (screen_x, screen_y, depth) or None if behind camera
    """
    x, y, z = point_3d
    
    # Move to camera space
    z = z + distance_from_cam
    
    if z <= 0.1:
        return None  # Behind camera
    
    # Perspective projection
    ooz = 1.0 / z
    screen_x = K1 * ooz * x * 2  # *2 for terminal aspect ratio
    screen_y = K1 * ooz * y
    
    return (screen_x, screen_y, ooz)  # Return depth for z-buffer


def project_points(points_3d, distance_from_cam=60, K1=40):
    """
    Project multiple 3D points to 2D.
    
    Args:
        points_3d: list of (x, y, z) tuples
    
    Returns:
        list of (screen_x, screen_y, depth) tuples or None for invalid points
    """
    return [project_point(p, distance_from_cam, K1) for p in points_3d]


# ============================================================================
# POLYGON FILLING
# ============================================================================

def point_in_quad(px, py, v0, v1, v2, v3):
    """
    Check if point (px, py) is inside the quad defined by v0, v1, v2, v3.
    Uses the cross product sign test.
    
    Args:
        px, py: point coordinates
        v0, v1, v2, v3: quad vertices as (x, y, depth) tuples
    
    Returns:
        True if point is inside quad
    """
    def sign(px, py, ax, ay, bx, by):
        """Calculate which side of line ab the point p is on"""
        return (px - bx) * (ay - by) - (ax - bx) * (py - by)
    
    # Extract just x, y from vertices
    v0x, v0y = v0[0], v0[1]
    v1x, v1y = v1[0], v1[1]
    v2x, v2y = v2[0], v2[1]
    v3x, v3y = v3[0], v3[1]
    
    # Check all four edges
    d1 = sign(px, py, v0x, v0y, v1x, v1y)
    d2 = sign(px, py, v1x, v1y, v2x, v2y)
    d3 = sign(px, py, v2x, v2y, v3x, v3y)
    d4 = sign(px, py, v3x, v3y, v0x, v0y)
    
    # Point is inside if all signs are same (all positive or all negative)
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0) or (d4 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0) or (d4 > 0)
    
    return not (has_neg and has_pos)


def interpolate_depth(px, py, v0, v1, v2, v3):
    """
    Interpolate the depth value at point (px, py) inside the quad.
    Uses inverse distance weighting.
    
    Args:
        px, py: point coordinates
        v0, v1, v2, v3: vertices as (x, y, depth) tuples
    
    Returns:
        interpolated depth value
    """
    total_weight = 0.0
    weighted_depth = 0.0
    
    for vx, vy, vz in [v0, v1, v2, v3]:
        dist = math.sqrt((px - vx)**2 + (py - vy)**2)
        
        if dist < 0.001:  # Point is very close to a vertex
            return vz
        
        weight = 1.0 / (dist + 0.1)
        weighted_depth += weight * vz
        total_weight += weight
    
    return weighted_depth / total_weight if total_weight > 0 else v0[2]


def fill_quad(vertices_2d, buffer, z_buffer, width, height, char='#'):
    """
    Fill a quad (4-sided polygon) in the buffer with depth testing.
    
    Args:
        vertices_2d: list of 4 (screen_x, screen_y, depth) tuples (already projected!)
        buffer: 1D character buffer (width * height)
        z_buffer: 1D depth buffer (width * height)
        width: screen width
        height: screen height
        char: character to fill with
    
    Returns:
        None (modifies buffer and z_buffer in place)
    """
    if len(vertices_2d) != 4:
        raise ValueError("fill_quad requires exactly 4 vertices")
    
    # Check if any vertices are invalid
    if any(v is None for v in vertices_2d):
        return  # Skip if any vertex is behind camera
    
    v0, v1, v2, v3 = vertices_2d
    
    # Find bounding box
    xs = [v[0] for v in vertices_2d]
    ys = [v[1] for v in vertices_2d]
    
    min_x = int(min(xs))
    max_x = int(max(xs))
    min_y = int(min(ys))
    max_y = int(max(ys))
    
    # Clip to screen bounds
    min_x = max(0, min_x)
    max_x = min(width - 1, max_x)
    min_y = max(0, min_y)
    max_y = min(height - 1, max_y)
    
    # Scan all pixels in bounding box
    for py in range(min_y, max_y + 1):
        for px in range(min_x, max_x + 1):
            if point_in_quad(px, py, v0, v1, v2, v3):
                # Interpolate depth at this pixel
                depth = interpolate_depth(px, py, v0, v1, v2, v3)
                
                # Depth test
                idx = px + py * width
                if depth > z_buffer[idx]:
                    z_buffer[idx] = depth
                    buffer[idx] = char


# ============================================================================
# DISPLAY
# ============================================================================

def display(buffer, width, height):
    """
    Display the buffer to the terminal.
    
    Args:
        buffer: 1D character buffer (width * height)
        width: screen width
        height: screen height
    """
    print("\033[H", end="")  # Move cursor to home
    
    for y in range(height):
        line = ""
        for x in range(width):
            line += buffer[x + y * width]
        print(line)


# ============================================================================
# ANIMATED EXAMPLE
# ============================================================================

def main():
    WIDTH = 80
    HEIGHT = 40
    
    # Clear screen and hide cursor
    print("\033[2J\033[?25l", end="")
    
    # Define a quad in 3D space (front face of a cube)
    quad_3d = [
        (-10, -10, 0),   # bottom-left
        (10, -10, 0),    # bottom-right
        (10, 10, 0),     # top-right
        (-10, 10, 0),    # top-left
    ]
    
    # Animation variables
    angle_x = 0.0
    angle_y = 0.0
    angle_z = 0.0
    
    try:
        while True:
            # Initialize buffers
            buffer = [' '] * (WIDTH * HEIGHT)
            z_buffer = [0.0] * (WIDTH * HEIGHT)
            
            # PIPELINE:
            # Step 1: Rotate the 3D points
            rotated_quad = rotate_points(quad_3d, angle_x, angle_y, angle_z)
            
            # Step 2: Project 3D points to 2D
            projected_quad = project_points(rotated_quad, distance_from_cam=60, K1=40)
            
            # Step 3: Convert to screen coordinates (center on screen)
            quad_screen = []
            for proj in projected_quad:
                if proj:
                    sx, sy, depth = proj
                    screen_x = WIDTH // 2 + sx
                    screen_y = HEIGHT // 2 - sy  # Flip Y (screen goes down)
                    quad_screen.append((screen_x, screen_y, depth))
                else:
                    quad_screen.append(None)
            
            # Step 4: Fill the quad with '#' character
            fill_quad(quad_screen, buffer, z_buffer, WIDTH, HEIGHT, '#')
            
            # Step 5: Display
            display(buffer, WIDTH, HEIGHT)
            
            # Update rotation angles
            angle_x += 0.05
            angle_y += 0.07
            angle_z += 0.03
            
            # Control frame rate
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        # Show cursor and clean exit
        print("\033[?25h\n\nAnimation stopped.")


if __name__ == "__main__":
    main()
