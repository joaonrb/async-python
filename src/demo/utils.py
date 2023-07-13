"""
utils

João Baptista <joao.baptista@devoteam.com> 2023-07-09
"""
import functools
import inspect
import json
from datetime import datetime

TRIES = 10


def print_duration(func):
    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def decorated(*args, **kwargs):
            start = datetime.now()
            result = await func(*args, **kwargs)
            func_name = f"{func.__name__}({print_args(*args, **kwargs)})"
            print(f"{func_name} executed in {datetime.now() - start}")
            dump(func_name, result)
            return result
    else:
        @functools.wraps(func)
        def decorated(*args, **kwargs):
            start = datetime.now()
            result = func(*args, **kwargs)
            func_name = f"{func.__name__}({print_args(*args, **kwargs)})"
            print(f"{func_name} executed in {datetime.now() - start}")
            dump(func_name, result)
            return result
    return decorated


def dump(name, data):
    with open(f"{name}.json", "w") as f:
        json.dump(data, f, indent=4)


def print_args(*args, **kwargs) -> str:
    args_string = ', '.join((str(arg) for arg in args))
    kwargs_string = ', '.join((f'{key}={value}' for key, value in kwargs.items()))
    if args_string and kwargs_string:
        return f"{args_string}, {kwargs_string}"
    elif args_string:
        return args_string
    elif kwargs_string:
        return kwargs_string
    else:
        return ""
