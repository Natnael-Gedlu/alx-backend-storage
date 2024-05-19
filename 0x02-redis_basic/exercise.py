#!/usr/bin/env python3
"""
Module for caching with Redis and tracking call history.
"""

import uuid
from functools import wraps
from typing import Callable, Union
import redis


def count_calls(method: Callable) -> Callable:
    """
    Decorator to count calls to a method.
    """
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper to increment call count.
        """
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to store call history.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper to log input and output.
        """
        input_key = method.__qualname__ + ":inputs"
        output_key = method.__qualname__ + ":outputs"

        output = method(self, *args, **kwargs)

        self._redis.rpush(input_key, str(args))
        self._redis.rpush(output_key, str(output))

        return output

    return wrapper


def replay(fn: Callable):
    """
    Display the history of calls to a function.
    """
    r = redis.Redis()
    f_name = fn.__qualname__
    n_calls = r.get(f_name)
    try:
        n_calls = n_calls.decode('utf-8')
    except Exception:
        n_calls = 0
    print(f'{f_name} was called {n_calls} times:')

    ins = r.lrange(f_name + ":inputs", 0, -1)
    outs = r.lrange(f_name + ":outputs", 0, -1)

    for i, o in zip(ins, outs):
        try:
            i = i.decode('utf-8')
        except Exception:
            i = ""
        try:
            o = o.decode('utf-8')
        except Exception:
            o = ""

        print(f'{f_name}(*{i}) -> {o}')


class Cache():
    """
    Cache class using Redis.
    """

    def __init__(self) -> None:
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str,
            fn: Callable = None) -> Union[str, bytes, int, float]:
        """
        Retrieve data from Redis.
        """
        data = self._redis.get(key)
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> str:
        """
        Retrieve and decode a string from Redis.
        """
        variable = self._redis.get(key)
        return variable.decode("UTF-8")

    def get_int(self, key: str) -> int:
        """
        Retrieve and decode an integer from Redis.
        """
        variable = self._redis.get(key)
        try:
            variable = int(variable.decode("UTF-8"))
        except Exception:
            variable = 0
        return variable
