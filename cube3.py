from time import perf_counter
from math import cos, sin, pi
from graphics import Point, Screen


def main():
    try:
        size = 500
        screen = Screen(width=size*2, height=size)

        # ===== CUBE DEFINITIONS =====
        
        # Cube 1 - Center
        side1 = 200
        half_side1 = side1 / 2
        z_dist1 = 400
        c1 = Point(0, 0, z_dist1 + half_side1)
        angle_x1, angle_y1, angle_z1 = 0.0, 0.0, 0.0
        step_x1 = pi / (48*2)
        step_y1 = pi / (48*2)
        step_z1 = pi / (48*2)
        
        # Cube 2 - Left, smaller, faster rotation
        side2 = 120
        half_side2 = side2 / 2
        z_dist2 = 300
        c2 = Point(-250, 0, z_dist2 + half_side2)
        angle_x2, angle_y2, angle_z2 = 0.0, 0.0, 0.0
        step_x2 = pi / (48*1)  # Faster X
        step_y2 = pi / (48*3)  # Slower Y
        step_z2 = pi / (48*5)  # Even slower Z
        
        # Cube 3 - Right, medium, opposite rotation
        side3 = 150
        half_side3 = side3 / 2
        z_dist3 = 350
        c3 = Point(250, 0, z_dist3 + half_side3)
        angle_x3, angle_y3, angle_z3 = 0.0, 0.0, 0.0
        step_x3 = -pi / (48*2)  # Reverse X
        step_y3 = pi / (48*4)   # Slow Y
        step_z3 = -pi / (48*3)  # Reverse Z

        focal_length = 100

        # ===== CREATE CUBE FACES =====
        def create_cube_faces(half_side, z_dist):
            """Generate all 6 faces of a cube"""
            return [
                # Front
                [Point(-half_side, -half_side, z_dist),
                 Point( half_side, -half_side, z_dist),
                 Point( half_side,  half_side, z_dist),
                 Point(-half_side,  half_side, z_dist)],
                
                # Right
                [Point( half_side, -half_side, z_dist),
                 Point( half_side,  half_side, z_dist),
                 Point( half_side,  half_side, z_dist + half_side*2),
                 Point( half_side, -half_side, z_dist + half_side*2)],
                
                # Back
                [Point(-half_side, -half_side, z_dist + half_side*2),
                 Point( half_side, -half_side, z_dist + half_side*2),
                 Point( half_side,  half_side, z_dist + half_side*2),
                 Point(-half_side,  half_side, z_dist + half_side*2)],
                
                # Left
                [Point(-half_side, -half_side, z_dist),
                 Point(-half_side,  half_side, z_dist),
                 Point(-half_side,  half_side, z_dist + half_side*2),
                 Point(-half_side, -half_side, z_dist + half_side*2)],
                
                # Top
                [Point(-half_side,  half_side, z_dist),
                 Point( half_side,  half_side, z_dist),
                 Point( half_side,  half_side, z_dist + half_side*2),
                 Point(-half_side,  half_side, z_dist + half_side*2)],
                
                # Bottom
                [Point(-half_side, -half_side, z_dist),
                 Point( half_side, -half_side, z_dist),
                 Point( half_side, -half_side, z_dist + half_side*2),
                 Point(-half_side, -half_side, z_dist + half_side*2)]
            ]
        
        # Create faces for each cube
        cube1_faces = create_cube_faces(half_side1, z_dist1)
        cube2_faces = create_cube_faces(half_side2, z_dist2)
        cube3_faces = create_cube_faces(half_side3, z_dist3)
        
        # Assign different fills to each cube
        fills1 = ['█', '▓', '▒', '░', '▪', '·']  # Cube 1 - grayscale
        fills2 = ['@', '#', '$', '%', '&', '*']  # Cube 2 - symbols
        fills3 = ['◆', '◇', '○', '●', '□', '■']  # Cube 3 - shapes

        # ===== ROTATIONS =====
        def rotate_x(point: Point, cos_ax: float, sin_ax: float):
            return Point(
                point.x,
                point.y*cos_ax - point.z*sin_ax,
                point.y*sin_ax + point.z*cos_ax)

        def rotate_y(point: Point, cos_ay: float, sin_ay: float):
            return Point(
                point.x*cos_ay + point.z*sin_ay,
                point.y,
                point.z*cos_ay - point.x*sin_ay)

        def rotate_z(point: Point, cos_az: float, sin_az: float):
            return Point(
                point.x*cos_az - point.y*sin_az,
                point.x*sin_az + point.y*cos_az,
                point.z)

        def rotate(point, cos_ax, sin_ax, cos_ay, sin_ay, cos_az, sin_az):
            point = rotate_z(point, cos_az, sin_az)
            point = rotate_y(point, cos_ay, sin_ay)
            return rotate_x(point, cos_ax, sin_ax)

        # ===== PROJECTION =====
        def project(point: Point, focal_length: float):
            if point.z <= 0:
                return Point(0, 0, 0)
            scale = focal_length / point.z
            return Point(point.x * scale, point.y * scale, point.z)

        # ===== TRANSFORMATION =====
        def transform(point, cos_ax, sin_ax, cos_ay, sin_ay, cos_az, sin_az, center, focal_length):
            rotated = rotate(point-center, cos_ax, sin_ax, cos_ay, sin_ay, cos_az, sin_az)
            translated = rotated + center
            return project(translated, focal_length)

        # ===== CENTROID Z-DEPTH =====
        def get_centroid_depth(transformed_verts):
            total = 0.0
            for p in transformed_verts: total += p.z
            return total * 0.25

        # Clear screen and hide cursor
        print('\033[2J\033[?25l', flush=True)

        target_angle = pi * 2

        while True:
            screen.clear()
            
            # ===== PROCESS ALL CUBES =====
            all_face_data = []
            
            # === CUBE 1 ===
            cos_ax1, sin_ax1 = cos(angle_x1), sin(angle_x1)
            cos_ay1, sin_ay1 = cos(angle_y1), sin(angle_y1)
            cos_az1, sin_az1 = cos(angle_z1), sin(angle_z1)
            
            for i, face_verts in enumerate(cube1_faces):
                transformed = [
                    transform(p, cos_ax1, sin_ax1, cos_ay1, sin_ay1, cos_az1, sin_az1, c1, focal_length)
                    for p in face_verts
                ]
                depth = get_centroid_depth(transformed)
                projected = [(p.x, p.y) for p in transformed]
                all_face_data.append((depth, projected, fills1[i]))
            
            # === CUBE 2 ===
            cos_ax2, sin_ax2 = cos(angle_x2), sin(angle_x2)
            cos_ay2, sin_ay2 = cos(angle_y2), sin(angle_y2)
            cos_az2, sin_az2 = cos(angle_z2), sin(angle_z2)
            
            for i, face_verts in enumerate(cube2_faces):
                transformed = [
                    transform(p, cos_ax2, sin_ax2, cos_ay2, sin_ay2, cos_az2, sin_az2, c2, focal_length)
                    for p in face_verts
                ]
                depth = get_centroid_depth(transformed)
                projected = [(p.x, p.y) for p in transformed]
                all_face_data.append((depth, projected, fills2[i]))
            
            # === CUBE 3 ===
            cos_ax3, sin_ax3 = cos(angle_x3), sin(angle_x3)
            cos_ay3, sin_ay3 = cos(angle_y3), sin(angle_y3)
            cos_az3, sin_az3 = cos(angle_z3), sin(angle_z3)
            
            for i, face_verts in enumerate(cube3_faces):
                transformed = [
                    transform(p, cos_ax3, sin_ax3, cos_ay3, sin_ay3, cos_az3, sin_az3, c3, focal_length)
                    for p in face_verts
                ]
                depth = get_centroid_depth(transformed)
                projected = [(p.x, p.y) for p in transformed]
                all_face_data.append((depth, projected, fills3[i]))
            
            # Sort ALL faces by depth (painter's algorithm works across cubes!)
            all_face_data.sort(key=lambda x: x[0], reverse=True)
            
            # Draw all faces back-to-front
            for depth, projected, fill in all_face_data:
                screen.polygon(projected, fill=fill)

            # Display rendered output
            print('\033[H' + screen.render(), flush=True)
            
            # Update angles for each cube independently
            angle_x1 += step_x1
            angle_y1 += step_y1
            angle_z1 += step_z1
            
            angle_x2 += step_x2
            angle_y2 += step_y2
            angle_z2 += step_z2
            
            angle_x3 += step_x3
            angle_y3 += step_y3
            angle_z3 += step_z3
            
            # Wrap angles
            if angle_x1 >= target_angle: angle_x1 = 0
            if angle_y1 >= target_angle: angle_y1 = 0
            if angle_z1 >= target_angle: angle_z1 = 0
            
            if angle_x2 >= target_angle: angle_x2 = 0
            if angle_y2 >= target_angle: angle_y2 = 0
            if angle_z2 >= target_angle: angle_z2 = 0
            
            if angle_x3 >= target_angle: angle_x3 = 0
            if angle_y3 >= target_angle: angle_y3 = 0
            if angle_z3 >= target_angle: angle_z3 = 0

    except KeyboardInterrupt:
        print('\033[?25h\n\nStopped.\n', flush=True)
    finally:
        print('\033[?25h', flush=True)


if __name__ == '__main__':
    main()