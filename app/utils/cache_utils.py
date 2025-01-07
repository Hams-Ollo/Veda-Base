"""Cache utilities for performance optimization."""

from typing import Dict, Any, Optional, Callable, TypeVar, ParamSpec
import logging
from datetime import datetime, timedelta
from functools import wraps
import asyncio
import json
from pathlib import Path
import pickle
from collections import OrderedDict

logger = logging.getLogger(__name__)

T = TypeVar('T')
P = ParamSpec('P')

class AsyncLRUCache:
    """Async-compatible LRU cache implementation."""
    
    def __init__(self, max_size: int = 1000, ttl: Optional[int] = None):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: OrderedDict[str, tuple[Any, Optional[float]]] = OrderedDict()
        self.lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        async with self.lock:
            if key not in self.cache:
                return None
            
            value, expiry = self.cache[key]
            if expiry and datetime.now().timestamp() > expiry:
                del self.cache[key]
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return value
    
    async def set(self, key: str, value: Any):
        """Set item in cache."""
        async with self.lock:
            expiry = (datetime.now() + timedelta(seconds=self.ttl)).timestamp() if self.ttl else None
            
            if key in self.cache:
                self.cache.move_to_end(key)
            else:
                if len(self.cache) >= self.max_size:
                    self.cache.popitem(last=False)  # Remove least recently used
            
            self.cache[key] = (value, expiry)
    
    async def delete(self, key: str):
        """Remove item from cache."""
        async with self.lock:
            if key in self.cache:
                del self.cache[key]
    
    async def clear(self):
        """Clear all items from cache."""
        async with self.lock:
            self.cache.clear()

class DiskCache:
    """Persistent disk-based cache."""
    
    def __init__(self, cache_dir: Path, max_size_mb: int = 1000):
        self.cache_dir = cache_dir
        self.max_size_mb = max_size_mb
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.lock = asyncio.Lock()
        self.metadata: Dict[str, Dict[str, Any]] = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Load cache metadata from disk."""
        metadata_path = self.cache_dir / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path) as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self):
        """Save cache metadata to disk."""
        with open(self.cache_dir / "metadata.json", 'w') as f:
            json.dump(self.metadata, f)
    
    def _get_cache_path(self, key: str) -> Path:
        """Get file path for cached item."""
        return self.cache_dir / f"{key}.cache"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get item from disk cache."""
        async with self.lock:
            if key not in self.metadata:
                return None
            
            meta = self.metadata[key]
            if meta.get("expiry") and datetime.now().timestamp() > meta["expiry"]:
                await self.delete(key)
                return None
            
            try:
                with open(self._get_cache_path(key), 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.error(f"Error reading cache file: {str(e)}")
                await self.delete(key)
                return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set item in disk cache."""
        async with self.lock:
            cache_path = self._get_cache_path(key)
            
            try:
                with open(cache_path, 'wb') as f:
                    pickle.dump(value, f)
                
                self.metadata[key] = {
                    "created_at": datetime.now().timestamp(),
                    "expiry": datetime.now().timestamp() + ttl if ttl else None,
                    "size": cache_path.stat().st_size
                }
                self._save_metadata()
                
                # Check and enforce size limit
                await self._enforce_size_limit()
                
            except Exception as e:
                logger.error(f"Error writing to cache: {str(e)}")
                if cache_path.exists():
                    cache_path.unlink()
    
    async def delete(self, key: str):
        """Remove item from disk cache."""
        async with self.lock:
            if key in self.metadata:
                cache_path = self._get_cache_path(key)
                if cache_path.exists():
                    cache_path.unlink()
                del self.metadata[key]
                self._save_metadata()
    
    async def _enforce_size_limit(self):
        """Enforce cache size limit by removing old entries."""
        total_size = sum(meta["size"] for meta in self.metadata.values())
        max_size_bytes = self.max_size_mb * 1024 * 1024
        
        if total_size > max_size_bytes:
            # Sort by creation time and remove oldest entries
            sorted_entries = sorted(
                self.metadata.items(),
                key=lambda x: x[1]["created_at"]
            )
            
            while total_size > max_size_bytes and sorted_entries:
                key, meta = sorted_entries.pop(0)
                await self.delete(key)
                total_size -= meta["size"]

class CacheManager:
    """Manages both memory and disk caches with statistics tracking."""
    
    def __init__(self):
        self.memory_cache = AsyncLRUCache()
        self.disk_cache = DiskCache(Path("cache"))
        self.stats = {
            "hits": 0,
            "misses": 0,
            "size": 0,
            "count": 0
        }
    
    async def get(self, key: str, use_disk: bool = False) -> Optional[Any]:
        """Get item from cache."""
        cache = self.disk_cache if use_disk else self.memory_cache
        result = await cache.get(key)
        
        if result is not None:
            self.stats["hits"] += 1
        else:
            self.stats["misses"] += 1
        
        return result
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, use_disk: bool = False):
        """Set item in cache."""
        cache = self.disk_cache if use_disk else self.memory_cache
        await cache.set(key, value, ttl)
        self.stats["count"] += 1
    
    async def delete(self, key: str, use_disk: bool = False):
        """Remove item from cache."""
        cache = self.disk_cache if use_disk else self.memory_cache
        await cache.delete(key)
        self.stats["count"] = max(0, self.stats["count"] - 1)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0
        
        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": hit_rate,
            "count": self.stats["count"],
            "size": self.stats["size"]
        }

# Global cache manager instance
cache_manager = CacheManager()

def cache_result(
    ttl: Optional[int] = None,
    use_disk: bool = False
):
    """Decorator for caching function results."""
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{hash(str(args))}{hash(str(kwargs))}"
            
            # Try to get from cache
            result = await cache_manager.get(key, use_disk)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(key, result, ttl, use_disk)
            return result
        
        return wrapper
    return decorator 