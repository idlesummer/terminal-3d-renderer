import time
from math import cos, sin, pi
from graphics import Point, Screen


def main():
    try:
        screen = Screen(width=80, height=40)

        # ===== DEFINITIONS =====
        side = 20                     # side length
        half_side = side / 2          # half the side length
        t = 0.0                       # angle
        z = 2                         # distance from origin

        # ===== FACES =====
        c = Point(0, 0, z + half_side)       # cube center as a Point object
        
        f1 = [Point(-half_side, -half_side, half_side),    # bottom-left
              Point( half_side, -half_side, half_side),    # bottom-right
              Point( half_side,  half_side, half_side),    # top-right
              Point(-half_side,  half_side, half_side)]    # top-left

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
        # def project(point, dist):
        #     return Point(dist)


        # project = lambda p, z: (z*p.x/p.z, z*p.y/p.z)

        

        # Clear screen and hide cursor
        print('\033[2J\033[?25l', end='')

        while True:
            screen.clear()

            # Rotate cube face in 3D (around Y-axis for horizontal spin)
            rotated_3d = []
            for p in f1:
                # Rotate around Y-axis
                nx = p.x * cos(t) + p.z * sin(t)
                ny = p.y
                nz = -p.x * sin(t) + p.z * cos(t)
                rotated_3d.append(Point(nx, ny, nz))

            # Project 3D points to 2D using perspective projection
            distance = 50  # Camera distance from origin
            projected = []
            for p in rotated_3d:
                # Perspective divide
                scale = distance / (distance + p.z)
                px = p.x * scale
                py = p.y * scale
                projected.append((px, py))

            # Draw the projected face
            screen.polygon(projected, fill='·')

            print('\033[H', end='')
            print(screen.render())

            t = (t + pi/96) if (t < pi*2) else 0
            time.sleep(0.05)

    except KeyboardInterrupt:
        print('\033[?25h\n\nStopped.')


if __name__ == '__main__':

    main()
