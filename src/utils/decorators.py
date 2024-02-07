"""Module contains decorators that can be used to decorate functions."""

import time


def timer(func):
    """
    Decorator function to measure the execution time of a function.

    :param func: The function to be timed.
    :return: The wrapped function.
    """

    def wrapper(*args, **kwargs):
        """
        Wrapper function that measures the execution time of the decorated function.

        :param args: Variable length argument list.
        :param kwargs: Arbitrary keyword arguments.
        :return: The result of the decorated function.
        """
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time for {func.__name__}: {execution_time} seconds")
        return result

    return wrapper
