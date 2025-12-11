import timeit

# Test 1: Python print
def python_print():
    output = "█" * 1000
    print('\033[H' + output, flush=True)

# Test 2: Cython wrapper around print (hypothetical)
# Would still call the same system calls!

time1 = timeit.timeit(python_print, number=100)
print(f"Python: {time1:.3f}s")

# Cython would be: ~same time (maybe 1-2% faster)