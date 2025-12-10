from math import cos, sin, pi
from graphics import Point, Screen


def main():
    try:
        size = 500
        screen = Screen(width=size*2, height=size)

        # ===== DEFINITIONS =====
        side = 350
        half_side = side / 2
        angle = 0.0
        z_dist = side
        focal_length = 100

        # ===== CUBE CENTER =====
        c = Point(0, 0, z_dist + half_side)

        # ===== FACES =====
        f1 = [Point(-half_side, -half_side, z_dist),
              Point( half_side, -half_side, z_dist),
              Point( half_side,  half_side, z_dist),
              Point(-half_side,  half_side, z_dist)]
        
        f2 = [Point( half_side, -half_side, z_dist),
              Point( half_side,  half_side, z_dist),
              Point( half_side,  half_side, z_dist + side),
              Point( half_side, -half_side, z_dist + side)]

        f3 = [Point(-half_side, -half_side, z_dist + side),
              Point( half_side, -half_side, z_dist + side),
              Point( half_side,  half_side, z_dist + side),
              Point(-half_side,  half_side, z_dist + side)]

        f4 = [Point(-half_side, -half_side, z_dist),
              Point(-half_side,  half_side, z_dist),
              Point(-half_side,  half_side, z_dist + side),
              Point(-half_side, -half_side, z_dist + side)]

        f5 = [Point(-half_side,  half_side, z_dist),
              Point( half_side,  half_side, z_dist),
              Point( half_side,  half_side, z_dist + side),
              Point(-half_side,  half_side, z_dist + side)]

        f6 = [Point(-half_side, -half_side, z_dist),
              Point( half_side, -half_side, z_dist),
              Point( half_side, -half_side, z_dist + side),
              Point(-half_side, -half_side, z_dist + side)]

        faces = [
            (f1, '█'),  # Solid
            (f2, '▓'),  # Dark
            (f3, '▒'),  # Medium
            (f4, '░'),  # Light
            (f5, '•'),  # Small square
            (f6, '')   # Bullet point
        ]

        # ===== ROTATIONS =====
        def rotate_x(point: Point, angle: float):
            x, y, z = point.coords()
            cost, sint = cos(angle), sin(angle)
            return Point(x, y*cost - z*sint, y*sint + z*cost)
            
        def rotate_y(point: Point, angle: float):
            x, y, z = point.coords()
            cost, sint = cos(angle), sin(angle)
            return Point(x*cost + z*sint, y, z*cost - x*sint)
            
        def rotate_z(point: Point, angle: float):
            x, y, z = point.coords()
            cost, sint = cos(angle), sin(angle)
            return Point(x*cost - y*sint, x*sint + y*cost, z)

        def rotate(point: Point, angle_x: float, angle_y: float, angle_z: float):
            point = rotate_z(point, angle_z)
            point = rotate_y(point, angle_y)
            point = rotate_x(point, angle_x)
            return point

        # ===== PROJECTION =====
        def project(point: Point, focal_length: float):
            if point.z <= 0:
                return Point(0, 0, 0)
            scale = focal_length / point.z
            return Point(point.x * scale, point.y * scale, point.z)
        
        # ===== TRANSFORMATION =====
        def transform(point: Point, angle_x: float, angle_y: float, 
                     angle_z: float, center: Point, focal_length: float):
            rotated = rotate(point - center, angle_x, angle_y, angle_z)
            translated = rotated + center
            return project(translated, focal_length)

        # Clear screen and hide cursor
        print('\033[2J\033[?25l', end='', flush=True)

        while True:
            screen.clear()

            # Transform all faces and calculate their average z
            face_data = []
            for face_verts, fill in faces:
                # Transform vertices
                transformed = [transform(p, angle, angle, angle, c, focal_length) for p in face_verts]
                
                # Calculate average z (depth)
                avg_z = sum(p.z for p in transformed) / len(transformed)
                
                # Store for sorting
                projected = [p.coords2() for p in transformed]
                face_data.append((avg_z, projected, fill))
            
            # Sort by depth (furthest first = largest z)
            face_data.sort(key=lambda x: x[0], reverse=True)
            
            # Draw faces back-to-front
            for avg_z, projected, fill in face_data:
                screen.polygon(projected, fill=fill)

            print('\033[H', end='', flush=True)
            print(screen.render(), flush=True)

            angle += pi / 96
            if angle >= pi * 2:
                angle = 0

    except KeyboardInterrupt:
        print('\033[?25h\n\nStopped.')

    finally:
        print('\033[?25h', end='', flush=True)


if __name__ == '__main__':
    main()
