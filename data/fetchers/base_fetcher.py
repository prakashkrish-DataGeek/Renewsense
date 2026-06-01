from abc import ABC, abstractmethod
import logging
from typing import Dict, Tuple, Any
from data.synthetic.data_generator import SyntheticDataGenerator

logger = logging.getLogger(__name__)

class BaseFetcher(ABC):
    """Abstract base class that all RenewSense data fetchers must implement."""

    def __init__(self):
        self.synthetic_generator = SyntheticDataGenerator()

    @abstractmethod
    def fetch(self, lat: float, lon: float, radius_km: int) -> Dict[str, Any]:
        """Performs live API request. Must raise exceptions on network errors, bad status, etc."""
        pass

    def fetch_with_fallback(self, lat: float, lon: float, radius_km: int) -> Tuple[Dict[str, Any], str]:
        """
        Executes fetch with error resilience. Falls back to synthetic heuristics
        on failure or if coordinates are out of bounds.
        """
        try:
            # First, check if API is configured/key exists if required (otherwise fallback immediately)
            if not self._is_api_configured():
                raise ValueError("API credentials not configured. Skipping live fetch.")
                
            logger.info(f"Initiating live request: {self.__class__.__name__} for lat={lat}, lon={lon}")
            result = self.fetch(lat, lon, radius_km)
            logger.info(f"Successful live fetch: {self.__class__.__name__}")
            return result, "LIVE"
        except Exception as e:
            logger.warning(f"Live fetch failed in {self.__class__.__name__}: {e}. Activating synthetic fallback.")
            result = self.synthetic_fallback(lat, lon, radius_km)
            return result, "SYNTHETIC"

    @abstractmethod
    def synthetic_fallback(self, lat: float, lon: float, radius_km: int) -> Dict[str, Any]:
        """Generates realistic synthetic estimations based on geographic location heuristics."""
        pass

    def _is_api_configured(self) -> bool:
        """Helper to check if required keys are in env. Overridden by children if necessary."""
        return True
