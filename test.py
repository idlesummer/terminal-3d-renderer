import timeit
from statistics import mean

# Sample data - 4 vertices (like a cube face)
vertices = [
    type('Point', (), {'z': 100.0}),
    type('Point', (), {'z': 200.0}),
    type('Point', (), {'z': 300.0}),
    type('Point', (), {'z': 400.0}),
]

def method_sum_div():
    """Using sum() / len()"""
    return sum(p.z for p in vertices) / len(vertices)

def method_mean():
    """Using statistics.mean()"""
    return mean(p.z for p in vertices)

def method_sum_div_list():
    """Using sum() / len() with list comprehension"""
    z_values = [p.z for p in vertices]
    return sum(z_values) / len(z_values)

def method_manual():
    """Manual accumulation (fastest possible)"""
    total = 0.0
    count = 0
    for p in vertices:
        total += p.z
        count += 1
    return total / count

def method_manual_fixed():
    """Manual with known count (for quads only)"""
    total = 0.0
    for p in vertices:
        total += p.z
    return total * 0.25  # Divide by 4

# Run benchmarks
iterations = 1_000_000

print("Benchmarking z-depth calculations (1 million iterations):\n")

time1 = timeit.timeit(method_sum_div, number=iterations)
print(f"sum() / len():              {time1:.4f}s")

time2 = timeit.timeit(method_mean, number=iterations)
print(f"statistics.mean():          {time2:.4f}s")

time3 = timeit.timeit(method_sum_div_list, number=iterations)
print(f"sum() / len() (list):       {time3:.4f}s")

time4 = timeit.timeit(method_manual, number=iterations)
print(f"Manual loop:                {time4:.4f}s")

time5 = timeit.timeit(method_manual_fixed, number=iterations)
print(f"Manual (fixed count):       {time5:.4f}s")

print(f"\nSpeedup factor:")
print(f"sum() / len() vs mean():    {time2/time1:.2f}x faster")
print(f"Manual vs sum():            {time1/time4:.2f}x faster")
print(f"Fixed vs sum():             {time1/time5:.2f}x faster")