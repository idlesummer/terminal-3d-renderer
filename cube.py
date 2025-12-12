from math import cos, sin, pi
from graphics import Point, Screen


def main():
    try:
        size = 600
        screen = Screen(width=size*2, height=size)

        # ===== DEFINITIONS =====
        side = 350
        half_side = side / 2
        angle_x = 0.0
        angle_y = 0.0
        angle_z = 0.0
        z_dist = 300
        focal_length = 100

        # ===== CUBE CENTER =====
        c = Point(0, 0, z_dist + half_side)

        # ===== FACES =====
        f1 = [Point(-half_side, -half_side, z_dist),        # front
              Point( half_side, -half_side, z_dist),
              Point( half_side,  half_side, z_dist),
              Point(-half_side,  half_side, z_dist)]

        f2 = [Point( half_side, -half_side, z_dist),        # right
              Point( half_side,  half_side, z_dist),
              Point( half_side,  half_side, z_dist + side),
              Point( half_side, -half_side, z_dist + side)]

        f3 = [Point(-half_side, -half_side, z_dist + side), # back
              Point( half_side, -half_side, z_dist + side),
              Point( half_side,  half_side, z_dist + side),
              Point(-half_side,  half_side, z_dist + side)]

        f4 = [Point(-half_side, -half_side, z_dist),        # left
              Point(-half_side,  half_side, z_dist),
              Point(-half_side,  half_side, z_dist + side),
              Point(-half_side, -half_side, z_dist + side)]

        f5 = [Point(-half_side,  half_side, z_dist),        # top
              Point( half_side,  half_side, z_dist),
              Point( half_side,  half_side, z_dist + side),
              Point(-half_side,  half_side, z_dist + side)]

        f6 = [Point(-half_side, -half_side, z_dist),        # bottom
              Point( half_side, -half_side, z_dist),
              Point( half_side, -half_side, z_dist + side),
              Point(-half_side, -half_side, z_dist + side)]

        faces = [
            (f1, ''),   # Front - Solid
            (f2, '▓'),  # Right - Dark
            (f3, '▒'),  # Back - Medium
            (f4, '░'),  # Left - Light
            (f5, '▪'),  # Top - Small square
            (f6, '█')   # Bottom - Dot
        ]

        # ===== ROTATIONS =====
        def rotate_x(point: Point, cos_ax: float, sin_ax: float):
            """Rotate around X-axis using direct attribute access"""
            return Point(
                point.x,
                point.y*cos_ax - point.z*sin_ax,
                point.y*sin_ax + point.z*cos_ax)

        def rotate_y(point: Point, cos_ay: float, sin_ay: float):
            """Rotate around Y-axis using direct attribute access"""
            return Point(
                point.x*cos_ay + point.z*sin_ay,
                point.y,
                point.z*cos_ay - point.x*sin_ay)

        def rotate_z(point: Point, cos_az: float, sin_az: float):
            """Rotate around Z-axis using direct attribute access"""
            return Point(
                point.x*cos_az - point.y*sin_az,
                point.x*sin_az + point.y*cos_az,
                point.z)

        def rotate(
            point: Point, 
            cos_ax: float, sin_ax: float, 
            cos_ay: float, sin_ay: float, 
            cos_az: float, sin_az: float
        ):
            """Apply all three rotations"""
            point = rotate_z(point, cos_az, sin_az)
            point = rotate_y(point, cos_ay, sin_ay)
            return rotate_x(point, cos_ax, sin_ax)

        # ===== PROJECTION =====
        def project(point: Point, focal_length: float):
            """Perspective projection with direct attribute access"""
            if point.z <= 0:
                return Point(0, 0, 0)
            scale = focal_length / point.z
            return Point(point.x * scale, point.y * scale, point.z)

        # ===== TRANSFORMATION =====
        def transform(
            point: Point, 
            cos_ax: float, sin_ax: float, 
            cos_ay: float, sin_ay: float, 
            cos_az: float, sin_az: float,
            center: Point, focal_length: float
        ):
            """Transform: translate, rotate, translate back, project"""
            rotated = rotate(point-center, cos_ax, sin_ax, cos_ay, sin_ay, cos_az, sin_az)
            translated = rotated + center
            return project(translated, focal_length)

        # ===== CENTROID Z-DEPTH =====
        def get_centroid_depth(transformed_verts):
            """Optimized for quad faces - manual loop with direct access"""
            total = 0.0
            for p in transformed_verts: total += p.z
            return total * 0.25

        # Clear screen and hide cursor
        print('\033[2J\033[?25l', flush=True)

        # ===== ANGLE STEPS =====
        angle_step_x = pi / (48*2)
        angle_step_y = pi / (48*4)
        angle_step_z = pi / (48*8)
        target_angle = pi * 2

        while True:
            screen.clear()
            
            # Precompute trig values for each axis
            cos_ax, sin_ax = cos(angle_x), sin(angle_x)
            cos_ay, sin_ay = cos(angle_y), sin(angle_y)
            cos_az, sin_az = cos(angle_z), sin(angle_z)

            # Transform all faces and calculate centroid depth
            face_data = []
            for face_verts, fill in faces:
                # Transform vertices
                transformed = [
                    transform(p, cos_ax, sin_ax, cos_ay, sin_ay, cos_az, sin_az, c, focal_length) 
                    for p in face_verts
                ]
                
                # Calculate depth
                depth = get_centroid_depth(transformed)
                
                # Project to 2D
                projected = [(p.x, p.y) for p in transformed]
                face_data.append((depth, projected, fill))
            
            # Sort by depth (furthest first = largest z)
            face_data.sort(key=lambda x: x[0], reverse=True)
            
            # Draw faces back-to-front (painter's algorithm)
            for depth, projected, fill in face_data:
                screen.polygon(projected, fill=fill)

            # Display rendered output
            print('\033[H' + screen.render(), flush=True)
            
            # Update angles independently
            angle_x += angle_step_x
            angle_y += angle_step_y
            angle_z += angle_step_z

            # Wrap angles
            if angle_x >= target_angle: angle_x = 0
            if angle_y >= target_angle: angle_y = 0
            if angle_z >= target_angle: angle_z = 0

    except KeyboardInterrupt:
        print('\033[?25h\n\nStopped.\n', flush=True)

    finally:
        print('\033[?25h', flush=True)


if __name__ == '__main__':
    main()
