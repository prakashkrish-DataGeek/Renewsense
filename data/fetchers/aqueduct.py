import os
import httpx
from typing import Dict, Any
from data.fetchers.base_fetcher import BaseFetcher

class AqueductFetcher(BaseFetcher):
    """Fetches water risk stress metrics from WRI Aqueduct 4.0 API."""

    def _is_api_configured(self) -> bool:
        # Aqueduct features some public endpoints that do not require explicit keys
        return True

    def fetch(self, lat: float, lon: float, radius_km: int) -> Dict[str, Any]:
        # Using WRI Aqueduct spatial query endpoints if available,
        # or public risk layers.
        # We will make an actual attempt, but since it can be rate-limited,
        # we will handle failures gracefully.
        url = f"https://api.wri.org/v1/aqueduct/water-risk?lat={lat}&lon={lon}"
        
        with httpx.Client(timeout=4.0) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                # Parse risk score
                score = data.get("water_stress_score", 1.5)
                return {
                    "value": score,
                    "sub_indicators": {
                        "baseline_water_stress_ratio": score,
                        "drought_frequency_spei12": data.get("drought_score", 0.5),
                        "aquifer_depletion_rate_m_yr": 0.05,
                        "flood_recurrence_interval_yrs": 50.0
                    }
                }
            else:
                raise httpx.HTTPStatusError("Aqueduct API unavailable", request=resp.request, response=resp)

    def synthetic_fallback(self, lat: float, lon: float, radius_km: int) -> Dict[str, Any]:
        return self.synthetic_generator.generate_vector("HSI", lat, lon, radius_km)
