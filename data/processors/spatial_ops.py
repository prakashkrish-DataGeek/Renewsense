import math
from typing import Tuple, Dict, Any, List

class SpatialOperations:
    """Provides high-performance spatial utility functions for buffers, distances, and bounding boxes."""

    @staticmethod
    def get_bounding_box(lat: float, lon: float, radius_km: float) -> Tuple[float, float, float, float]:
        """
        Calculates a bounding box around a point given a radius in kilometers.
        Returns: Tuple[min_lat, min_lon, max_lat, max_lon]
        """
        # Coordinate offsets in radians
        lat_rad = math.radians(lat)
        
        # Earth radius
        R = 6371.0
        
        # Offsets
        delta_lat = radius_km / R
        delta_lon = radius_km / (R * math.cos(lat_rad))
        
        min_lat = lat - math.degrees(delta_lat)
        max_lat = lat + math.degrees(delta_lat)
        min_lon = lon - math.degrees(delta_lon)
        max_lon = lon + math.degrees(delta_lon)
        
        return min_lat, min_lon, max_lat, max_lon

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Haversine formula to compute great-circle distance between two coordinates in kilometers.
        """
        R = 6371.0  # Earth radius
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(d_lat / 2) ** 2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(d_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
        
    @staticmethod
    def create_geojson_point(lat: float, lon: float, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a GeoJSON Point representation."""
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": properties
        }
