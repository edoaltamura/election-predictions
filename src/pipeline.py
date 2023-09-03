#!/usr/bin/env python
# encoding: utf-8

"""
@Author:              Edoardo Altamura
@Year:                2023
@Email:               edoardo.altamura@outlook.com
@Copyright:           Copyright (c) 2023 Edoardo Altamura
@Last Modified by:    Edoardo Altamura
@Latest release:      5 Sep 2023
@Project:             Election predictions (Data Science with The Economist)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
from joblib import Parallel, delayed, cpu_count
from typing import Callable, Any, List, Union, Tuple, Type
from functools import wraps
from socket import gethostname
from io import StringIO
from contextlib import redirect_stdout
from sys import settrace
from math import floor, log
from timeit import default_timer as timer

production_servers = [...]
development_servers = [...]


def measure(func: Callable) -> Callable:
    """
    Measure and display the execution time of a function.

    This decorator function measures the execution time of the wrapped function and displays the elapsed time in
    seconds.

    :param func: The function to be measured.
    :return: Decorated function that measures and displays execution time.

    Example usage:
        ```python
        @measure
        def some_function():
            # Code to be measured
            pass

        some_function()
        ```
    """

    @wraps(func)
    def inner(*args, **kwargs) -> Any:
        print(f"\N{STOPWATCH} | Calling {func.__name__}()")
        start = timer()

        # The function to be executed
        func(*args, **kwargs)

        elapsed_sec = timer() - start
        print(f"\N{STOPWATCH} | Done: {func.__name__}() took {elapsed_sec:.4f} sec")

    return inner


def repeat(n: int = 1) -> Callable:
    """
    Repeat the execution of a function multiple times.

    This decorator function allows you to repeat the execution of a wrapped function a specified number of times.

    :param n: The number of times to repeat the execution (default is 1).
    :return: Decorated function that repeats the execution.

    Example usage:
        ```python
        @repeat(n=3)
        def print_hello():
            print("Hello, World!")

        print_hello()
        ```
    """

    def decorator(func: Callable) -> Callable:
        def inner(*args, **kwargs) -> Any:
            for _ in range(n):
                # The function to be executed
                func(*args, **kwargs)

        return inner

    return decorator


def parallel(func: Union[Callable, None] = None,
             args: Union[Tuple, List] = (),
             merge_func: Callable[[List[Any]], Any] = lambda x: x,
             parallelism: int = cpu_count()) -> Callable:
    """
    Decorator for parallel execution of a function.

    This decorator function allows you to execute a function in parallel multiple times and merge the results using a
    merge function.

    :param func: The function to be decorated (optional if used as a decorator).
    :param args: Arguments to be passed to the decorated function.
    :param merge_func: A function to merge the results of parallel executions (default is identity function).
    :param parallelism: The number of parallel executions (default is the number of CPU cores).

    :return: Decorated function that executes in parallel and merges results.

    Example usage:
        ```python
        @parallel(parallelism=4)
        def square(x):
            return x * x

        result = square(5)  # Calls square(5) in parallel 4 times and merges the results.
        ```
    """
    def decorator(func: Callable) -> Callable:

        def inner(*args, **kwargs) -> Union[None, Any]:

            results = Parallel(n_jobs=parallelism)(delayed(func)(*args, **kwargs) for i in range(parallelism))
            return merge_func(results)

        return inner

    if func is None:
        # decorator was used like @parallel(...)
        return decorator
    else:
        # decorator was used like @parallel, without parens
        return decorator(func)


def production(func: Callable) -> Callable:
    """
    Decorator to mark a function for production use only.

    This decorator function allows you to mark a function for use only on production servers. If the current host is a
    production server, the function is executed; otherwise, a message is printed, indicating that the function has been
    skipped.

    :param func: The function to be decorated.

    :return: Decorated function that executes only on production servers.

    Example usage:
        ```python
        @production
        def expensive_production_task():
            # Code for production use only
            pass

        expensive_production_task()  # Execute on production servers, skip on others.
        ```
    """
    def inner(*args, **kwargs) -> Union[None, Any]:
        if gethostname() in production_servers:
            return func(*args, **kwargs)
        else:
            print('\N{FACTORY} | This host is not a production server, skipping function decorated with @production...')

    return inner


def development(func: Callable) -> Callable:
    """
    Decorator to mark a function for development use only.

    This decorator function allows you to mark a function for use only during development and not on production servers.
    If the current host is not a production server, the function is executed; otherwise, a message is printed,
    indicating that the function has been skipped.

    :param func: The function to be decorated.

    :return: Decorated function that executes only in development environments.

    Example usage:
        ```python
        @development
        def debug_function():
            # Code for debugging and development purposes
            pass

        debug_function()  # Execute in development environments, skip on production servers.
        ```
    """
    def inner(*args, **kwargs) -> Union[None, Any]:
        if gethostname() not in production_servers:
            return func(*args, **kwargs)
        else:
            print('\N{HAMMER AND WRENCH} | This host is a production server, skipping function decorated with '
                  '@development...')

    return inner


def inactive(func: Callable) -> Callable:
    """
    Decorator to mark a function as inactive.

    This decorator function allows you to mark a function as inactive, meaning it will not execute the function but will
    print a message indicating that the function has been skipped.

    :param func: The function to be decorated.

    :return: Decorated function that is inactive and only prints a message.

    Example usage:
        ```python
        @inactive
        def deprecated_function():
            # Old code that should not be used anymore
            pass

        deprecated_function()  # Skip execution, print a message.
        ```
    """
    def inner(*args, **kwargs) -> None:
        print('\N{NO ENTRY}| Skipping function decorated with @inactive...')

    return inner


def deployable(func: Callable) -> Callable:
    """
    Decorator to control the deployability of a function.

    This decorator function allows you to control whether a function can be executed in different deployment environments
    (e.g., production, development, or skipped). It checks the 'deploy' keyword argument and the current host's
    environment to determine whether to execute the function or print a skip message.

    :param func: The function to be decorated.

    :return: Decorated function that can be controlled based on deployment environment.

    Example usage:
        ```python
        @deployable
        def deployable_function():
            # Code that can be controlled based on deployment environment
            pass

        # Deploy in production environment
        deployable_function(deploy='production')

        # Deploy in development environment
        deployable_function(deploy='development')

        # Skip deployment
        deployable_function(deploy='skip')
        ```
    """
    def inner(*args, **kwargs) -> Union[None, Any]:
        if 'deploy' in kwargs:
            if kwargs['deploy'].lower() in ['production', 'prod'] and gethostname() not in production_servers:
                print('\N{FACTORY} | This host is not a production server, skipping...')
                return
            if kwargs['deploy'].lower() in ['development', 'dev'] and gethostname() not in development_servers:
                print('\N{HAMMER AND WRENCH} | This host is not a development server, skipping...')
                return
            if kwargs['deploy'].lower() in ['skip', 'none']:
                print('Skipping...')
                return
            del kwargs['deploy']  # to avoid func() throwing an unexpected keyword exception
        return func(*args, **kwargs)

    return inner


def redirect(func: Union[Callable, None] = None, line_print: Union[Callable, None] = None) -> Callable:
    """
    Decorator to redirect function output and optionally print specific lines.

    This decorator function allows you to redirect the output of a function and optionally print specific lines from the
    output. It can be used for debugging and inspecting the output of a function.

    :param func: The function to be decorated (optional if used as a decorator).
    :param line_print: A custom function to print specific lines from the output (optional).

    :return: Decorated function that redirects and optionally prints output lines.

    Example usage:
        ```python
        @redirect(line_print=print)  # Redirect and print all lines
        def debug_function():
            # Code with output
            pass

        debug_function()  # Redirect and print all lines of output

        @redirect
        def custom_output_function():
            # Code with output
            pass

        custom_output_function()  # Redirect without custom line printing
        ```
    """
    def decorator(func: Callable) -> Callable:

        def inner(*args, **kwargs) -> None:

            with StringIO() as buf, redirect_stdout(buf):
                func(*args, **kwargs)
                output = buf.getvalue()
            lines = output.splitlines()
            if line_print is not None:
                for line in lines:
                    line_print(line)
            else:
                width = floor(log(len(lines), 10)) + 1
                for i, line in enumerate(lines):
                    i += 1
                    print(f'{i:0{width}}: {line}')

        return inner

    if func is None:
        # decorator was used like @redirect(...)
        return decorator
    else:
        # decorator was used like @redirect, without parens
        return decorator(func)


def stacktrace(func: Callable = None, exclude_files: List[str] = ['anaconda']) -> Callable:
    """
    Decorator to trace function calls and returns, optionally excluding specific files.

    This decorator function allows you to trace function calls and returns, printing information about the executed
    functions and their arguments. You can exclude specific files from tracing.

    :param func: The function to be decorated (optional if used as a decorator).
    :param exclude_files: List of filenames to exclude from tracing (default is ['anaconda']).

    :return: Decorated function with tracing.

    Example usage:
        ```python
        @stacktrace(exclude_files=['exclude_this.py'])
        def traced_function():
            # Code to trace
            pass

        traced_function()  # Trace the function's calls and returns, excluding 'exclude_this.py'.

        @stacktrace
        def custom_trace_function():
            # Code to trace without excluding files
            pass

        custom_trace_function()  # Trace the function's calls and returns without excluding files.
        ```
    """
    def tracer_func(frame, event, arg) -> Union[None, Any]:
        co = frame.f_code
        func_name = co.co_name
        caller_filename = frame.f_back.f_code.co_filename
        if func_name == 'write':
            return  # ignore write() calls from print statements
        for file in exclude_files:
            if file in caller_filename:
                return  # ignore in ipython notebooks
        args = str(tuple([frame.f_locals[arg] for arg in frame.f_code.co_varnames]))
        if args.endswith(',)'):
            args = args[:-2] + ')'
        if event == 'call':
            print(f'--> Executing: {func_name}{args}')
            return tracer_func
        elif event == 'return':
            print(f'--> Returning: {func_name}{args} -> {repr(arg)}')
        return

    def decorator(func: Callable) -> Callable:

        def inner(*args, **kwargs) -> None:
            settrace(tracer_func)
            func(*args, **kwargs)
            settrace(None)

        return inner

    if func is None:
        # decorator was used like @stacktrace(...)
        return decorator
    else:
        # decorator was used like @stacktrace, without parens
        return decorator(func)


def traceclass(cls: Type) -> Type:
    """
    Decorator to trace method executions within a class.

    This decorator function allows you to trace the executions of all methods within a class. It prints information about
    the executed methods and their arguments.

    :param cls: The class to be decorated.

    :return: Decorated class with traced methods.

    Example usage:
        ```python
        @traceclass
        class TracedClass:
            def __init__(self):
                pass

            def traced_method(self):
                # Code for the traced method
                pass

        traced_instance = TracedClass()
        traced_instance.traced_method()  # Trace the execution of the 'traced_method'.
        ```
    """
    def make_traced(cls: Type, method_name: str, method: Callable) -> Callable:

        def traced_method(*args, **kwargs) -> Any:

            print(f'--> Executing: {cls.__name__}::{method_name}()')
            return method(*args, **kwargs)

        return traced_method

    for name in cls.__dict__.keys():

        if callable(getattr(cls, name)) and name != '__class__':
            setattr(cls, name, make_traced(cls, name, getattr(cls, name)))

    return cls
