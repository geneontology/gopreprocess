import time


def timer(func):
    """
    Decorator function to measure the execution time of a function.

    Args:
        func: The function to be timed.

    Returns:
        The wrapped function.

    Example:
        @timer
        def my_function():
            # Function code here

        my_function()  # Execution time for my_function: 0.1234 seconds

    :param func: The function to be timed.
    :return: The wrapped function.
    """
    def wrapper(*args, **kwargs):
        """
        Wrapper function that measures the execution time of the decorated function.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The result of the decorated function.

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
