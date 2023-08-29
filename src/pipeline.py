from joblib import Parallel, delayed, cpu_count
from typing import Callable
from socket import gethostname
from io import StringIO
from contextlib import redirect_stdout
from sys import settrace
from math import floor, log
from timeit import default_timer as timer

production_servers = [...]
development_servers = [...]


def measure(func: Callable):
    def inner(*args, **kwargs):
        print(f"\N{STOPWATCH} | Calling {func.__name__}()")
        start = timer()
        func(*args, **kwargs)
        elapsed_sec = timer() - start
        print(f"\N{STOPWATCH} | Done: {func.__name__}() took {elapsed_sec:.4f} sec")

    return inner


def repeat(n: int = 1):
    def decorator(func: Callable):
        def inner(*args, **kwargs):
            for _ in range(n):
                func(*args, **kwargs)

        return inner

    return decorator


def parallel(func=None, args=(), merge_func=lambda x: x, parallelism=cpu_count()):
    def decorator(func: Callable):
        def inner(*args, **kwargs):
            results = Parallel(n_jobs=parallelism)(delayed(func)(*args, **kwargs) for i in range(parallelism))
            return merge_func(results)

        return inner

    if func is None:
        # decorator was used like @parallel(...)
        return decorator
    else:
        # decorator was used like @parallel, without parens
        return decorator(func)


def production(func: Callable):
    def inner(*args, **kwargs):
        if gethostname() in production_servers:
            return func(*args, **kwargs)
        else:
            print('\N{FACTORY} | This host is not a production server, skipping function decorated with @production...')

    return inner


def development(func: Callable):
    def inner(*args, **kwargs):
        if gethostname() not in production_servers:
            return func(*args, **kwargs)
        else:
            print('\N{HAMMER AND WRENCH} | This host is a production server, skipping function decorated with '
                  '@development...')

    return inner


def inactive(func: Callable):
    def inner(*args, **kwargs):
        print('\N{NO ENTRY}| Skipping function decorated with @inactive...')

    return inner


def deployable(func):
    def inner(*args, **kwargs):
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


def redirect(func=None, line_print: Callable = None):
    def decorator(func: Callable):
        def inner(*args, **kwargs):
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


def stacktrace(func=None, exclude_files=['anaconda']):
    def tracer_func(frame, event, arg):
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

    def decorator(func: Callable):
        def inner(*args, **kwargs):
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


def traceclass(cls: type):
    def make_traced(cls: type, method_name: str, method: Callable):
        def traced_method(*args, **kwargs):
            print(f'--> Executing: {cls.__name__}::{method_name}()')
            return method(*args, **kwargs)

        return traced_method

    for name in cls.__dict__.keys():
        if callable(getattr(cls, name)) and name != '__class__':
            setattr(cls, name, make_traced(cls, name, getattr(cls, name)))
    return cls
