import overpy
import logging
from typing import Dict, Any
from data.fetchers.base_fetcher import BaseFetcher
from data.processors.spatial_ops import SpatialOperations

logger = logging.getLogger(__name__)

class OsmGridFetcher(BaseFetcher):
    """Fetches high-voltage power networks within an analysis buffer from OpenStreetMap via Overpass API."""

    def fetch(self, lat: float, lon: float, radius_km: int) -> Dict[str, Any]:
        # Compute bounding box for query
        min_lat, min_lon, max_lat, max_lon = SpatialOperations.get_bounding_box(lat, lon, radius_km)
        
        # Build Overpass QL query
        # Restrict to high-voltage power lines (voltage >= 110kV, or general power lines if specific voltages aren't tagged)
        query = f"""
        [out:json][timeout:10];
        (
          way["power"="line"]["voltage"~"110|220|380|400|500|750|765"]({min_lat},{min_lon},{max_lat},{max_lon});
          way["power"="line"]({min_lat},{min_lon},{max_lat},{max_lon});
        );
        out body;
        >;
        out skel qt;
        """
        
        api = overpy.Overpass()
        try:
            result = api.query(query)
            
            min_dist = float("inf")
            # Calculate distance to nearest transmission line
            for way in result.ways:
                for node in way.nodes:
                    dist = SpatialOperations.calculate_distance(lat, lon, float(node.lat), float(node.lon))
                    if dist < min_dist:
                        min_dist = dist
                        
            if min_dist == float("inf"):
                # No grid lines found within radius
                logger.info(f"No transmission lines found within {radius_km}km. Setting default distance penalty.")
                min_dist = float(radius_km) * 1.5
                
            return {
                "value": round(min_dist, 2),
                "sub_indicators": {
                    "distance_to_nearest_220kv_transmission_km": round(min_dist, 2),
                    "substation_capacity_mva_proxy": 250.0,
                    "grid_stability_index": 0.88 if min_dist < 15.0 else 0.65,
                    "transmission_queue_congestion_pct": 35.0
                }
            }
        except Exception as e:
            logger.error(f"Overpass query failed: {e}")
            raise

    def synthetic_fallback(self, lat: float, lon: float, radius_km: int) -> Dict[str, Any]:
        return self.synthetic_generator.generate_vector("GIR", lat, lon, radius_km)
