import threading
from queue import Queue
import time
from math import cos, sin, pi
from graphics import Screen


def render_thread(screen, state, output_queue, running):
    """Producer: Render frames"""
    while running['value']:
        screen.clear()
        
        angle = state['angle']
        cosa, sina = cos(angle), sin(angle)
        square = state['square']
        rotated = [(x*cosa - y*sina, x*sina + y*cosa) for x, y in square]
        
        screen.polygon(rotated, '█')
        screen.point(0, 0, fill='@')
        
        output = screen.render()
        
        # Drop old frames if queue is full
        if output_queue.qsize() > 1:
            try:
                output_queue.get_nowait()
            except:
                pass
        
        output_queue.put(output)


def print_thread(output_queue, running):
    """Consumer: Print frames"""
    while running['value']:
        try:
            output = output_queue.get(timeout=0.1)
            print('\033[H' + output, flush=True)
        except:
            pass


def run(screen_size=500, square_size=350):
    screen = Screen(width=screen_size*2, height=screen_size)
    
    half_side = square_size / 2
    state = {
        'square': [
            (-half_side, -half_side), 
            (half_side,  -half_side), 
            (half_side,  half_side), 
            (-half_side, half_side),
        ],
        'angle': 0.0,
        'angle_step': pi / (96*8),
    }
    
    running = {'value': True}
    output_queue = Queue(maxsize=2)
    
    # Start threads
    renderer = threading.Thread(target=render_thread, args=(screen, state, output_queue, running))
    printer = threading.Thread(target=print_thread, args=(output_queue, running))
    
    renderer.start()
    printer.start()
    
    # Main thread: Update game state
    TICK = 1.0 / 60.0
    try:
        while running['value']:
            state['angle'] += state['angle_step']
            time.sleep(TICK)
    except KeyboardInterrupt:
        running['value'] = False
    
    renderer.join()
    printer.join()
    print('\033[?25h')


def main():
    run(screen_size=500, square_size=350)


if __name__ == '__main__':
    main()