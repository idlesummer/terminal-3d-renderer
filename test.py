#!/usr/bin/env python3
"""
Night sky simulation with randomly spawning stars
"""
import random
import time
from blessed import Terminal

def main():
    term = Terminal()
    
    # Dimensions
    width = 1200
    height = 600
    
    # Star characters (various unicode stars and sparkles)
    star_chars = ['*', '✦', '✧', '✨', '⋆', '★', '☆', '✪', '✯', '✰', '•', '∙', '·', '⭐', '🌟']
    
    # Star colors (whites, yellows, blues for realistic stars)
    star_colors = [
        term.white,
        term.bright_white, 
        term.yellow,
        term.bright_yellow,
        term.cyan,
        term.bright_cyan,
        term.blue,
    ]
    
    with term.cbreak(), term.hidden_cursor():
        # Clear screen and fill with black/dark background
        print(term.home + term.clear + term.on_black)
        
        # Draw border
        print(term.move_xy(0, 0) + term.white('╔' + '═' * (width - 2) + '╗'))
        for y in range(1, height - 1):
            print(term.move_xy(0, y) + term.white('║'))
            print(term.move_xy(width - 1, y) + term.white('║'))
        print(term.move_xy(0, height - 1) + term.white('╚' + '═' * (width - 2) + '╝'))
        
        # Randomly spawn stars
        try:
            while True:
                # Spawn multiple stars per iteration for a fuller sky
                for _ in range(random.randint(1, 5)):
                    x = random.randint(1, width - 2)
                    y = random.randint(1, height - 2)
                    
                    star = random.choice(star_chars)
                    color = random.choice(star_colors)
                    
                    print(term.move_xy(x, y) + color(star), end='', flush=True)
                
                time.sleep(0.05)  # Small delay for twinkling effect
                
        except KeyboardInterrupt:
            print(term.normal)

if __name__ == '__main__':
    main()