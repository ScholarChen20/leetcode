"""线程安全 LRU Cache 实现。"""

from __future__ import annotations

from collections import OrderedDict
import threading
from typing import Generic, TypeVar


K = TypeVar("K")
V = TypeVar("V")


class LRUCache(Generic[K, V]):
    """基于 OrderedDict 的固定容量最近最少使用缓存。"""

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity 必须为正数。")
        self.capacity = capacity
        self._data: OrderedDict[K, V] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: K) -> V | None:
        """读取缓存；命中后将键移动到最新位置。"""
        with self._lock:
            if key not in self._data:
                return None
            self._data.move_to_end(key)
            return self._data[key]

    def put(self, key: K, value: V) -> None:
        """写入缓存；超过容量时淘汰最久未使用项。"""
        with self._lock:
            if key in self._data:
                self._data.move_to_end(key)
            self._data[key] = value
            if len(self._data) > self.capacity:
                self._data.popitem(last=False)

    def keys(self) -> list[K]:
        """返回从最久未使用到最近使用的键列表。"""
        with self._lock:
            return list(self._data.keys())


if __name__ == "__main__":
    cache = LRUCache[str, int](capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a")
    cache.put("c", 3)
    print("a:", cache.get("a"), "b:", cache.get("b"), "keys:", cache.keys())
