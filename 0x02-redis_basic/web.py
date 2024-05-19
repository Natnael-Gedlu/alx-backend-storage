#!/usr/bin/env python3
"""
Module for caching and counting URL accesses.
"""

import requests
import redis
from functools import wraps

store = redis.Redis()


def count_url_access(method):
    """
    Decorator to count and cache URL accesses.
    """

    @wraps(method)
    def wrapper(url):
        """
        Wrapper to handle caching and counting.
        """
        cached_key = f"cached:{url}"
        count_key = f"count:{url}"

        cached_data = store.get(cached_key)
        if cached_data:
            return cached_data.decode("utf-8")

        html = method(url)

        store.incr(count_key)
        store.set(cached_key, html)
        store.expire(cached_key, 10)
        return html

    return wrapper


@count_url_access
def get_page(url: str) -> str:
    """
    Fetches a web page.
    """
    res = requests.get(url)
    return res.text
