"""Caching utilities for the Library of Alexandria."""

import os
import json
import pickle
from typing import Any, Optional, Union, Dict, List
from pathlib import Path
import hashlib
import time
from datetime import datetime, timedelta
from diskcache import Cache
from functools import wraps
import logging
from concurrent.futures import ThreadPoolExecutor
import threading
import shutil

logger = logging.getLogger(__name__)

class CacheConfig:
    """Configuration for caching system."""
    CACHE_DIR = os.getenv('CACHE_DIR', 'cache')
    DEFAULT_TTL = int(os.getenv('CACHE_TTL', 3600))  # 1 hour
    MAX_SIZE = int(os.getenv('CACHE_MAX_SIZE', 1e9))  # 1GB
    SHARDS = int(os.getenv('CACHE_SHARDS', 8))  # Number of cache shards

class CacheManager:
    """Disk-based caching system using diskcache."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
            return cls._instance
    
    def _initialize(self):
        """Initialize the cache manager."""
        self.cache = Cache(
            directory=CacheConfig.CACHE_DIR,
            size_limit=CacheConfig.MAX_SIZE,
            shards=CacheConfig.SHARDS,
            timeout=1.0  # 1 second timeout for operations
        )
        self.logger = logging.getLogger('cache_manager')
        self._executor = ThreadPoolExecutor(max_workers=4)
        self.stats = {'hits': 0, 'misses': 0}
    
    def _get_cache_key(self, key: str, namespace: Optional[str] = None) -> str:
        """Generate a cache key with optional namespace."""
        if namespace:
            return f"{namespace}:{key}"
        return key
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        namespace: Optional[str] = None,
        tag: Optional[str] = None
    ) -> bool:
        """Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            namespace: Optional namespace for the key
            tag: Optional tag for grouping related items
            
        Returns:
            bool: Success status
        """
        cache_key = self._get_cache_key(key, namespace)
        
        try:
            # Store metadata along with value
            cache_data = {
                'value': value,
                'timestamp': time.time(),
                'namespace': namespace,
                'tag': tag
            }
            
            self.cache.set(
                cache_key,
                cache_data,
                expire=ttl or CacheConfig.DEFAULT_TTL
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Cache set error: {str(e)}")
            return False
    
    def get(
        self,
        key: str,
        namespace: Optional[str] = None,
        default: Any = None
    ) -> Any:
        """Get a value from the cache.
        
        Args:
            key: Cache key
            namespace: Optional namespace for the key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        cache_key = self._get_cache_key(key, namespace)
        
        try:
            cache_data = self.cache.get(cache_key)
            if cache_data is None:
                self.stats['misses'] += 1
                return default
                
            self.stats['hits'] += 1
            return cache_data['value']
            
        except Exception as e:
            self.logger.error(f"Cache get error: {str(e)}")
            return default
    
    def delete(
        self,
        key: str,
        namespace: Optional[str] = None
    ) -> bool:
        """Delete a value from the cache.
        
        Args:
            key: Cache key
            namespace: Optional namespace for the key
            
        Returns:
            bool: Success status
        """
        cache_key = self._get_cache_key(key, namespace)
        
        try:
            self.cache.delete(cache_key)
            return True
            
        except Exception as e:
            self.logger.error(f"Cache delete error: {str(e)}")
            return False
    
    def clear_namespace(self, namespace: str) -> bool:
        """Clear all keys in a namespace.
        
        Args:
            namespace: Namespace to clear
            
        Returns:
            bool: Success status
        """
        try:
            pattern = f"{namespace}:"
            keys_to_delete = [
                key for key in self.cache.iterkeys()
                if key.startswith(pattern)
            ]
            
            for key in keys_to_delete:
                self.cache.delete(key)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Cache clear namespace error: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary containing cache statistics
        """
        try:
            total_ops = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_ops * 100) if total_ops > 0 else 0
            
            return {
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'hit_rate': hit_rate,
                'size': self.cache.size,
                'volume': self.cache.volume,
                'count': len(self.cache)
            }
            
        except Exception as e:
            self.logger.error(f"Cache stats error: {str(e)}")
            return {}
    
    def cleanup(self) -> bool:
        """Clean up expired cache entries.
        
        Returns:
            bool: Success status
        """
        try:
            # diskcache handles expiration automatically
            self.cache.expire()
            return True
            
        except Exception as e:
            self.logger.error(f"Cache cleanup error: {str(e)}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all cache entries.
        
        Returns:
            bool: Success status
        """
        try:
            self.cache.clear()
            self.stats = {'hits': 0, 'misses': 0}
            return True
            
        except Exception as e:
            self.logger.error(f"Cache clear error: {str(e)}")
            return False

# Global cache manager instance
cache_manager = CacheManager()

def cached(
    ttl: Optional[int] = None,
    namespace: Optional[str] = None,
    tag: Optional[str] = None
):
    """Decorator for caching function results.
    
    Args:
        ttl: Time to live in seconds
        namespace: Cache namespace
        tag: Optional tag for grouping related items
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_value = cache_manager.get(
                cache_key,
                namespace=namespace
            )
            
            if cached_value is not None:
                return cached_value
            
            # Calculate and cache result
            result = func(*args, **kwargs)
            cache_manager.set(
                cache_key,
                result,
                ttl=ttl,
                namespace=namespace,
                tag=tag
            )
            
            return result
        return wrapper
    return decorator 