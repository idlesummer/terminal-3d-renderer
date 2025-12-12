import curses
import random
import string


def main(stdscr):
    # Hide cursor
    curses.curs_set(0)
    
    # Set up colors if available
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        for i in range(1, 8):
            curses.init_pair(i, i, -1)
    
    # Create a 1200x600 pad
    pad_height = 600
    pad_width = 1200
    pad = curses.newpad(pad_height, pad_width)
    
    # Fill the pad with random characters
    chars = string.ascii_letters + string.digits + string.punctuation + ' '
    
    for y in range(pad_height):
        for x in range(pad_width):
            # Skip the very last cell to avoid curses error
            if y == pad_height - 1 and x == pad_width - 1:
                continue
            
            char = random.choice(chars)
            color = random.randint(1, 7) if curses.has_colors() else 0
            
            try:
                pad.addch(y, x, char, curses.color_pair(color))
            except curses.error:
                pass
    
    # Add some labels in the pad
    pad.addstr(0, 0, f"PAD SIZE: {pad_width}x{pad_height} | Use arrow keys to scroll, 'q' to quit")
    pad.addstr(299, 600, "*** MIDDLE OF PAD ***")
    pad.addstr(599, 0, "*** BOTTOM OF PAD ***")
    
    # Initial pad position
    pad_y = 0
    pad_x = 0
    
    while True:
        # Get terminal dimensions
        term_h, term_w = stdscr.getmaxyx()
        
        # Refresh only the pad (no stdscr output at all)
        pad.refresh(pad_y, pad_x, 0, 0, term_h - 1, term_w - 1)
        

if __name__ == '__main__':
    curses.wrapper(main)
