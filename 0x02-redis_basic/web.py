#!/usr/bin/env python3
import redis
import requests
from typing import Callable, Dict
"""
doc
"""
count: Dict = {}


def count(func: Callable):
    """
    decorator
    """
    cache: redis.Redis = redis.Redis(db=10)

    @wrapper(func)
    def wrapper(url: str):
        cache.incr(f"count:{url}")
        count[f"count:{url}"] = cache.get(f"count:{url}").decode()
        res: str = cache.get(f"count:{url}:cache").decode()
        if res:
            return res
        res: str = func(url)
        cache.expire(f"count:{url}:cache", 10, res)
        return res
    return wrapper


@count
def get_page(url: str) -> str:
    """
    doc
    """
    res = requests.get(url).text
    return res


if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk"
    print(get_page(url))
    print(count[f"count:{url}"])
