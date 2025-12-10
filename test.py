import timeit

# Test with typical values
def old_style():
    minx, x = 35.7, 44.2
    if minx < x:
        return minx, x
    else:
        return x, minx

def new_style():
    minx, x = 35.7, 44.2
    return min(minx, x), max(minx, x)

print("Old:", timeit.timeit(old_style, number=1_000_000))
print("New:", timeit.timeit(new_style, number=1_000_000))