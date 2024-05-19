#!/usr/bin/env python3
"""
Module for caching and counting URL accesses.
"""

import redis
import requests
from functools import wraps
from typing import Callable

# Initialize Redis store
redis_store = redis.Redis()


def data_cacher(method: Callable) -> Callable:
    """
    Caches URL fetch results and counts accesses.
    """
    @wraps(method)
    def invoker(url) -> str:
        """
        Caches result and counts URL accesses.
        """
        redis_store.incr(f'count:{url}')
        result = redis_store.get(f'result:{url}')
        if result:
            return result.decode('utf-8')
        result = method(url)
        redis_store.setex(f'result:{url}', 10, result)
        return result
    return invoker


@data_cacher
def get_page(url: str) -> str:
    """
    Fetches HTML content of a URL.
    """
    return requests.get(url).text
