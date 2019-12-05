import statistics
from time import time


def timeit(fn: callable, number: int = 1,
           status_fn: callable = lambda n, t: print("\rRun #", n + 1, "took", t, "ms.", end="", flush=True),
           cleanup_fn: callable = lambda r: print("", flush=True)):
    runs = []
    result = None
    for i in range(number):
        start_time = time()
        result = fn()
        end_time = time()
        runs.append(round((end_time - start_time) * 1000, 5))
        if status_fn:
            status_fn(i, runs[i])
    result = {'return': result, 'avg': statistics.mean(runs), 'fastest': min(runs), 'slowest': max(runs)}
    if cleanup_fn:
        cleanup_fn(result)
    return result