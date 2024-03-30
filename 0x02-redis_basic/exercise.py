#!/usr/bin/env python3
import redis
import uuid
from functools import wraps
from typing import Union, Callable, Optional
AllTypes = Union[int, str, bytes, float]
red: str = "\033[91m"
reset: str = "\033[0m"

"""
module doc
"""


def count_calls(method: Callable) -> Callable:
    """
    decorator method
    """
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kargs):
        """
        wrapper
        """
        self._redis.incr(key)
        return method(self, *args, **kargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    deccorator doc
    """
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kargs):
        """
        wrapper
        """
        self._redis.rpush(f"{key}:inputs", str(args))
        data = method(self, *args, **kargs)
        self._redis.rpush(f"{key}:outputs", data)
        return data
    return wrapper


def replay(obj):
    """
    func doc
    """
    key = obj.__qualname__
    self = obj.__self__
    inputs = self._redis.lrange(f"{key}:inputs", 0, -1)
    outputs = self._redis.lrange(f"{key}:outputs", 0, -1)
    combine = zip(inputs, outputs)
    combine = list(combine)
    print(f"{key} was called {len(combine)} times:")
    for i, o in combine:
        print(f"{key}(*{i.decode()}) -> {o.decode()}")


class Cache:
    """
    class doc
    """

    def __init__(self) -> None:
        """
        method doc
        """
        self._redis: redis.Redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        method doc
        """
        random: str = str(uuid.uuid4())
        try:
            self._redis.set(random, data)
        except ConnectionRefusedError as error:
            print(f"{red}The redis server is mostlikely not on{reset}{error}")
            exit()
        return random

    def get_int(self, key: str) -> int:
        """
        method doc
        """
        return self.get(key, str)

    def get_str(self, key: str) -> str:
        """
        method doc
        """
        return self.get(key, str)

    def get(self, key: str, fn: Optional[Callable] = None) -> AllTypes:
        """
        method doc
        """
        data = self._redis.get(key)
        return data if not fn else fn(data)


if __name__ == "__main__":
    cache = Cache()

    TEST_CASES = {
        b"foo": None,
        123: int,
        "bar": lambda d: d.decode("utf-8")
    }

    for value, fn in TEST_CASES.items():
        key = cache.store(value)
        assert cache.get(key, fn=fn) == value
        print(cache.get(key, fn=fn))
