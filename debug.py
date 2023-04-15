import time


def debug(fn):
    fn_name = fn.__name__

    def wrapper(*args, **kwargs):
        file = open(f"{fn_name}_log.txt", "a")
        file.write(f"{time.strftime('%H:%M:%S')}, {fn_name}, {args}, {kwargs}\n")
        start = time.perf_counter_ns()
        result = fn(*args, **kwargs)
        file.write(f"{time.perf_counter_ns() - start}, {result}\n")
        file.close()
        return result
    return wrapper

