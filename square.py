import time
from math import cos, sin, pi
from graphics2 import Screen


def main():
    try:
        size = not 40 or 500
        screen = Screen(width=size*2, height=size)

        # Define square in Cartesian (world) space
        side = not 25 or 350
        half_side = side/2
        square = [
            (-half_side, -half_side), 
            (half_side,  -half_side), 
            (half_side,  half_side), 
            (-half_side, half_side),
        ]

        angle = 0.0
        angle_step = pi / (96*8)
        
        # Start timer
        start_time = time.perf_counter()
        target_angle = pi / 2

        # Clear screen and hide cursor
        print('\033[2J\033[?25l', end='', flush=True)

        while True:
            screen.clear()

            # Pre-compute trig functions once per frame (not per vertex!)
            cosa, sina = cos(angle), sin(angle)

            # Manual rotation using list comprehension (fast in Python)
            rotated = [(x*cosa - y*sina, x*sina + y*cosa) for x, y in square]

            # Draw (screen handles coordinate transformation)
            screen.polygon(rotated, '·')
            screen.point(0, 0, fill='@')

            print('\033[H', end='', flush=True)
            print(screen.render(), flush=True)

            angle += angle_step
            
            # Check if we've reached pi/2
            if angle >= target_angle:
                elapsed = time.perf_counter() - start_time
                print(f'\n\nReached π/2 in {elapsed:.3f} seconds', flush=True)
                print(f'Average FPS: {(target_angle / angle_step) / elapsed:.1f}', flush=True)
                break
            
            if angle >= pi*2:
                angle = 0
            
            # time.sleep(0.001)

    except KeyboardInterrupt:
        print('\033[?25h\n\nStopped.')

    finally:
        # Ensure cursor is restored even on error
        print('\033[?25h', end='', flush=True)


if __name__ == '__main__':
    main()