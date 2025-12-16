"""Performance optimizations and caching."""

import asyncio
import time
from functools import lru_cache, wraps
from typing import Any, Dict, Optional, Callable
from collections import OrderedDict
import threading
from dataclasses import dataclass

from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with TTL."""

    value: Any
    timestamp: float
    ttl: float

    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl


class LRUCache:
    """Thread-safe LRU cache with TTL."""

    def __init__(self, max_size: int = 128, default_ttl: float = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self.lock:
            if key not in self.cache:
                return None

            entry = self.cache[key]
            if entry.is_expired():
                del self.cache[key]
                return None

            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return entry.value

    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Put value in cache."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
            elif len(self.cache) >= self.max_size:
                # Remove oldest item
                self.cache.popitem(last=False)

            ttl = ttl or self.default_ttl
            self.cache[key] = CacheEntry(value, time.time(), ttl)

    def clear(self) -> None:
        """Clear cache."""
        with self.lock:
            self.cache.clear()

    def size(self) -> int:
        """Get cache size."""
        with self.lock:
            return len(self.cache)


# Global cache instances
contract_cache = LRUCache(max_size=settings.model_cache_size, default_ttl=600)
model_cache = LRUCache(max_size=50, default_ttl=1800)


def async_lru_cache(maxsize: int = 128, ttl: float = 300):
    """Async LRU cache decorator."""

    def decorator(func: Callable):
        cache = LRUCache(max_size=maxsize, default_ttl=ttl)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"

            # Try cache
            result = cache.get(key)
            if result is not None:
                return result

            # Execute function
            result = await func(*args, **kwargs)
            cache.put(key, result)
            return result

        wrapper.cache_clear = cache.clear
        wrapper.cache_info = lambda: {"size": cache.size()}
        return wrapper

    return decorator


def timed_cache(maxsize: int = 128, ttl: float = 300):
    """Cache decorator with timing."""

    def decorator(func: Callable):
        cache = LRUCache(max_size=maxsize, default_ttl=ttl)

        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            # Create cache key
            key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"

            # Try cache
            result = cache.get(key)
            if result is not None:
                logger.debug("Cache hit", function=func.__name__, key=key)
                return result

            # Execute function
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            cache.put(key, result)
            logger.debug(
                "Cache miss",
                function=func.__name__,
                key=key,
                execution_time=execution_time,
            )
            return result

        wrapper.cache_clear = cache.clear
        wrapper.cache_info = lambda: {"size": cache.size()}
        return wrapper

    return decorator


class PerformanceMonitor:
    """Monitor performance metrics."""

    def __init__(self):
        self.metrics: Dict[str, list] = {}
        self.lock = threading.Lock()

    def record(self, operation: str, duration: float) -> None:
        """Record operation duration."""
        with self.lock:
            if operation not in self.metrics:
                self.metrics[operation] = []
            self.metrics[operation].append(duration)

            # Keep only last 1000 measurements
            if len(self.metrics[operation]) > 1000:
                self.metrics[operation] = self.metrics[operation][-1000:]

    def get_stats(self, operation: str) -> Dict[str, float]:
        """Get statistics for operation."""
        with self.lock:
            if operation not in self.metrics or not self.metrics[operation]:
                return {}

            durations = self.metrics[operation]
            return {
                "count": len(durations),
                "avg": sum(durations) / len(durations),
                "min": min(durations),
                "max": max(durations),
                "p95": sorted(durations)[int(len(durations) * 0.95)],
            }

    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Get all statistics."""
        return {op: self.get_stats(op) for op in self.metrics}


# Global performance monitor
performance_monitor = PerformanceMonitor()


def monitor_performance(operation_name: Optional[str] = None):
    """Decorator to monitor function performance."""

    def decorator(func: Callable):
        name = operation_name or f"{func.__module__}.{func.__name__}"

        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                performance_monitor.record(name, duration)

        return wrapper

    return decorator


async def cleanup_expired_cache():
    """Background task to clean expired cache entries."""
    while True:
        try:
            # This would be implemented in LRUCache
            # For now, just log
            logger.debug("Cache cleanup task")
            await asyncio.sleep(60)  # Run every minute
        except Exception as e:
            logger.error("Cache cleanup error", error=str(e))
            await asyncio.sleep(60)
