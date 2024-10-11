import multiprocessing
import time

def worker_task(n):
    """Function that calculates the square of the given number."""
    print(f"Worker {n} is calculating {n} * {n}")
    time.sleep(1)  # Simulate some work with a delay.
    return n * n

if __name__ == '__main__':
    num_proc = 4  # Number of worker processes to use.

    # Create a pool of worker processes.
    with multiprocessing.Pool(processes=num_proc) as pool:
        results = []

        # Submit tasks to the pool using apply_async().
        for i in range(10):
            result = pool.apply_async(worker_task, args=(i,))
            results.append(result)

        # Wait for all the asynchronous tasks to complete.
        for r in results:
            try:
                # Get the result from each task. This will raise any exceptions that occurred in the worker process.
                print(f"Result: {r.get()}")
            except Exception as e:
                print(f"An error occurred: {e}")

    print("All tasks completed.")
