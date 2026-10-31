import hashlib
import time
import logging
from config import get_settings
logger = logging.getLogger(__name__)
settings = get_settings()

class CacheLayer:
    def __init__(self) -> None:
        self.ttl = settings.cache_ttl_seconds
        self._cache : dict[str,dict] = {}

    def _make_key(self,query:str):
        logger.info("Making Key of Query")
        query = query.strip().lower()
        key = hashlib.sha256(query.encode()).hexdigest()
        return key

    def get(self,query:str):
        key = self._make_key(query)
        if key in self._cache:
            cache = self._cache[key]
            if time.time() - cache['timestamp'] > self.ttl:
                logger.info("Returing Cache Response")
                return cache['response']
            else:
                logger.warning("Deleting Old Cache")
                del self._cache[key]
        return None

    def set(self, query:str, response:str):
        logging.info("Set Cache")
        key = self._make_key(query)
        self._cache[key] = {
            "query" : query,
            "reponse" : response,
            "timestamp" : time.time()
        }
