import time
from numba import jit

@jit
def calculo(n):
    for i in range(n):
        10 * 2

start = time.time()
calculo(1000000000)
end = time.time()

print(end-start)
