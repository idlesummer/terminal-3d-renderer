import math
import sys
import time

# Rotation angles
A = 0.0
B = 0.0
C = 0.0

# Screen
width, height = 160, 44
background_ascii = ord('.')

# Camera / projection
distance_from_cam = 100.0
horizontal_offset = 0.0
K1 = 40.0

# Step
increment_speed = 0.6

# Buffers
zbuffer = [0.0] * (width * height)
buffer = [background_ascii] * (width * height)

def calculate_x(i, j, k, A, B, C):
    return (j * math.sin(A) * math.sin(B) * math.cos(C)
            - k * math.cos(A) * math.sin(B) * math.cos(C)
            + j * math.cos(A) * math.sin(C)
            + k * math.sin(A) * math.sin(C)
            + i * math.cos(B) * math.cos(C))

def calculate_y(i, j, k, A, B, C):
    return (j * math.cos(A) * math.cos(C)
            + k * math.sin(A) * math.cos(C)
            - j * math.sin(A) * math.sin(B) * math.sin(C)
            + k * math.cos(A) * math.sin(B) * math.sin(C)
            - i * math.cos(B) * math.sin(C))

def calculate_z(i, j, k, A, B, C):
    return (k * math.cos(A) * math.cos(B)
            - j * math.sin(A) * math.cos(B)
            + i * math.sin(B))

def plot_surface(cubeX, cubeY, cubeZ, ch, A, B, C, horizontal_offset):
    x = calculate_x(cubeX, cubeY, cubeZ, A, B, C)
    y = calculate_y(cubeX, cubeY, cubeZ, A, B, C)
    z = calculate_z(cubeX, cubeY, cubeZ, A, B, C) + distance_from_cam

    if z <= 0:
        return

    ooz = 1.0 / z
    xp = int(width / 2 + horizontal_offset + K1 * ooz * x * 2)
    yp = int(height / 2 + K1 * ooz * y)

    if 0 <= xp < width and 0 <= yp < height:
        idx = xp + yp * width
        if ooz > zbuffer[idx]:
            zbuffer[idx] = ooz
            buffer[idx] = ch

def clear_buffers():
    for i in range(width * height):
        buffer[i] = background_ascii
        zbuffer[i] = 0.0

def draw_frame():
    sys.stdout.write("\x1b[H")
    # Convert bytes to chars efficiently
    line = []
    for k in range(width * height):
        if k % width:
            line.append(chr(buffer[k]))
        else:
            line.append("\n")
    sys.stdout.write("".join(line))
    sys.stdout.flush()

def frange(start, stop, step):
    x = start
    # Guard against floating rounding preventing termination
    while x < stop - 1e-9:
        yield x
        x += step

def render_cube(cube_width, offset, A, B, C):
    for cubeX in frange(-cube_width, cube_width, increment_speed):
        for cubeY in frange(-cube_width, cube_width, increment_speed):
            plot_surface(cubeX,        cubeY, -cube_width, ord('@'), A, B, C, offset)
            plot_surface(cube_width,   cubeY,  cubeX,      ord('$'), A, B, C, offset)
            plot_surface(-cube_width,  cubeY, -cubeX,      ord('~'), A, B, C, offset)
            plot_surface(-cubeX,       cubeY,  cube_width, ord('#'), A, B, C, offset)
            plot_surface(cubeX,       -cube_width, -cubeY, ord(';'), A, B, C, offset)
            plot_surface(cubeX,        cube_width,  cubeY, ord('+'), A, B, C, offset)

def main():
    global A, B, C
    sys.stdout.write("\x1b[2J")  # clear screen
    sys.stdout.flush()

    try:
        while True:
            clear_buffers()

            # first cube
            render_cube(20.0, -2 * 20.0, A, B, C)
            # second cube
            render_cube(10.0,  1 * 10.0, A, B, C)
            # third cube
            render_cube(5.0,   8 * 5.0,  A, B, C)

            draw_frame()

            A += 0.05
            B += 0.05
            C += 0.01
            time.sleep(0.016)  # ~16ms (similar to usleep(16000))
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
