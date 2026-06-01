import os
import logging
import diskcache
from typing import Optional, Any

logger = logging.getLogger(__name__)

class CacheManager:
    """Uses diskcache to store and retrieve computationally expensive calculation results."""

    def __init__(self, cache_dir: str = "data/cache", expire_seconds: int = 86400):
        self.cache_dir = cache_dir
        self.expire_seconds = expire_seconds
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        try:
            self.cache = diskcache.Cache(self.cache_dir)
            logger.info(f"Diskcache successfully initialized at: {self.cache_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize diskcache: {e}. Running in non-cached mode.")
            self.cache = None

    def get(self, key: str) -> Optional[Any]:
        if not self.cache:
            return None
        try:
            return self.cache.get(key)
        except Exception as e:
            logger.error(f"Error retrieving from cache: {e}")
            return None

    def set(self, key: str, value: Any):
        if not self.cache:
            return
        try:
            self.cache.set(key, value, expire=self.expire_seconds)
            logger.debug(f"Cache key set: {key}")
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")

    def clear(self):
        if not self.cache:
            return
        try:
            self.cache.clear()
            logger.info("Cache successfully cleared.")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
