import timeit

class PointWithIter:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z
    
    def __iter__(self):
        return iter((self.x, self.y, self.z))

class PointWithCoords:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z
    
    def coords(self):
        return self.x, self.y, self.z

# Benchmark
p_iter = PointWithIter(1.0, 2.0, 3.0)
p_coords = PointWithCoords(1.0, 2.0, 3.0)

def method_iter():
    x, y, z = p_iter  # Uses __iter__
    return x + y + z

def method_coords():
    x, y, z = p_coords.coords()
    return x + y + z

def method_direct():
    x, y, z = p_coords.x, p_coords.y, p_coords.z
    return x + y + z

iterations = 1_000_000

print("Unpacking methods (1M iterations):\n")
time1 = timeit.timeit(method_iter, number=iterations)
print(f"__iter__ unpack:     {time1:.4f}s")

time2 = timeit.timeit(method_coords, number=iterations)
print(f"coords() unpack:     {time2:.4f}s")

time3 = timeit.timeit(method_direct, number=iterations)
print(f"Direct access:       {time3:.4f}s")

print(f"\nSpeedup:")
print(f"Direct vs __iter__:  {time1/time3:.2f}x faster")
print(f"Direct vs coords():  {time2/time3:.2f}x faster")
