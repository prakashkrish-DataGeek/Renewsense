import math
import random
from typing import Dict, Any

class SyntheticDataGenerator:
    """Generates highly realistic geospatial data using lat/lon heuristics for demo and fallback states."""

    def __init__(self):
        pass

    def generate_all(self, lat: float, lon: float, radius_km: int = 25) -> Dict[str, Dict[str, Any]]:
        """Generates raw dictionary values for all 7 vectors based on coordinates."""
        return {
            "SRI": self.generate_vector("SRI", lat, lon, radius_km),
            "WRP": self.generate_vector("WRP", lat, lon, radius_km),
            "HSI": self.generate_vector("HSI", lat, lon, radius_km),
            "GIR": self.generate_vector("GIR", lat, lon, radius_km),
            "EVI": self.generate_vector("EVI", lat, lon, radius_km),
            "RPE": self.generate_vector("RPE", lat, lon, radius_km),
            "LSA": self.generate_vector("LSA", lat, lon, radius_km)
        }

    def generate_vector(self, vector_key: str, lat: float, lon: float, radius_km: int = 25) -> Dict[str, Any]:
        """Runs the custom heuristic mapping for a specific vector."""
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        
        # We use a pseudo-random seed tied to coordinates to keep returns deterministic for a specific spot
        coord_seed = int((abs(lat) * 1000) + (abs(lon) * 10000) + radius_km)
        rng = random.Random(coord_seed)
        
        if vector_key == "SRI":
            # GHI: Latitude model. Cosine squared peaks at equator, tapers towards poles.
            ghi = 7.2 * (math.cos(lat_rad) ** 2) + 1.0
            
            # Regional Adjustments
            # Atacama Desert (Chile) gets a massive solar boost
            if -26.0 <= lat <= -18.0 and -71.0 <= lon <= -67.0:
                ghi = 7.8 + rng.uniform(-0.1, 0.1)
            # Rajasthan (India) desert solar boost
            elif 24.0 <= lat <= 30.0 and 69.0 <= lon <= 76.0:
                ghi = 6.4 + rng.uniform(-0.1, 0.1)
            # Northern Germany solar taper
            elif 50.0 <= lat <= 56.0 and 5.0 <= lon <= 16.0:
                ghi = 3.0 + rng.uniform(-0.15, 0.15)
                
            ghi = max(min(ghi, 8.0), 0.5)
            
            # Sub-indicators
            cloud_persistence = max(min((8.0 - ghi) * 12.0 + rng.uniform(-5, 5), 100.0), 0.0)
            dust_optical_depth = rng.uniform(0.02, 0.25) if "Desert" in self._get_region_name(lat, lon) else rng.uniform(0.01, 0.08)
            albedo_proxy = 0.35 if ghi > 6.0 else 0.18
            
            return {
                "value": round(ghi, 2),
                "sub_indicators": {
                    "annual_mean_ghi": round(ghi, 2),
                    "p90_exceedance_ghi": round(ghi * 0.92, 2),
                    "cloud_persistence_pct": round(cloud_persistence, 1),
                    "dust_optical_depth": round(dust_optical_depth, 3),
                    "albedo_proxy": round(albedo_proxy, 2)
                }
            }
            
        elif vector_key == "WRP":
            # Power Density model. Stronger at coastlines, high latitudes, or elevated terrains.
            pd = 180.0 + 350.0 * (math.sin(3.0 * lat_rad) ** 2)
            
            # Specific calibration regions
            # Northern Germany coast (high wind)
            if 53.0 <= lat <= 56.0 and 5.0 <= lon <= 12.0:
                pd = 550.0 + rng.uniform(-50, 50)
            # Atacama altitude wind
            elif -26.0 <= lat <= -18.0 and -71.0 <= lon <= -67.0:
                pd = 310.0 + rng.uniform(-30, 30)
            # Rajasthan (moderate wind)
            elif 24.0 <= lat <= 30.0 and 69.0 <= lon <= 76.0:
                pd = 180.0 + rng.uniform(-20, 20)
                
            pd = max(min(pd, 1200.0), 30.0)
            ws = math.sqrt(pd / 0.6) / 2.0  # Simple conversion helper to m/s
            
            return {
                "value": round(pd, 1),
                "sub_indicators": {
                    "mean_wind_speed_100m_ms": round(ws, 1),
                    "weibull_k_parameter": round(rng.uniform(1.8, 2.3), 2),
                    "wind_power_density_wm2": round(pd, 1),
                    "turbulence_intensity_pct": round(rng.uniform(8.0, 15.0), 1),
                    "wind_anisotropy_index": round(rng.uniform(0.65, 0.88), 2)
                }
            }
            
        elif vector_key == "HSI":
            # baseline water stress risk score [0 - 5.0]
            # Deserts and hot regions have extremely high stress (4.0 - 5.0)
            stress = 2.0 + 2.0 * math.sin(abs(lat_rad)) + rng.uniform(-0.5, 0.5)
            
            if -26.0 <= lat <= -18.0 and -71.0 <= lon <= -67.0: # Atacama
                stress = 4.8 + rng.uniform(-0.1, 0.1)
            elif 24.0 <= lat <= 30.0 and 69.0 <= lon <= 76.0: # Rajasthan
                stress = 4.4 + rng.uniform(-0.2, 0.2)
            elif 50.0 <= lat <= 56.0 and 5.0 <= lon <= 16.0: # Northern Germany
                stress = 0.8 + rng.uniform(-0.2, 0.2)
                
            stress = max(min(stress, 5.0), 0.0)
            
            return {
                "value": round(stress, 2),
                "sub_indicators": {
                    "baseline_water_stress_ratio": round(stress, 2),
                    "drought_frequency_spei12": round(rng.uniform(1.0, 4.0) if stress > 3.0 else rng.uniform(0.1, 1.2), 2),
                    "aquifer_depletion_rate_m_yr": round(stress * 0.15 if stress > 3.0 else 0.01, 3),
                    "flood_recurrence_interval_yrs": round(rng.uniform(5, 20) if stress < 1.5 else rng.uniform(50, 100), 1)
                }
            }
            
        elif vector_key == "GIR":
            # Grid distance in km
            dist = 35.0 + 40.0 * rng.uniform(-0.5, 0.5)
            
            if -26.0 <= lat <= -18.0 and -71.0 <= lon <= -67.0: # Remote Atacama Desert
                dist = 85.0 + rng.uniform(-10, 15)
            elif 24.0 <= lat <= 30.0 and 69.0 <= lon <= 76.0: # Rajasthan
                dist = 18.0 + rng.uniform(-5, 5)
            elif 50.0 <= lat <= 56.0 and 5.0 <= lon <= 16.0: # Developed Germany
                dist = 4.5 + rng.uniform(-2, 3)
                
            dist = max(min(dist, 200.0), 0.5)
            congestion = 65.0 if dist < 10.0 else 25.0
            
            return {
                "value": round(dist, 1),
                "sub_indicators": {
                    "distance_to_nearest_220kv_transmission_km": round(dist, 1),
                    "substation_capacity_mva_proxy": round(rng.choice([100.0, 250.0, 500.0]), 1),
                    "grid_stability_index": round(rng.uniform(0.75, 0.96) if dist < 30.0 else rng.uniform(0.40, 0.70), 2),
                    "transmission_queue_congestion_pct": round(congestion + rng.uniform(-5, 5), 1)
                }
            }
            
        elif vector_key == "EVI":
            # Extreme natural hazard frequencies
            events = int(rng.uniform(0, 3))
            
            # Coastal / active regions higher
            if -26.0 <= lat <= -18.0 and -71.0 <= lon <= -67.0: # Seismic active Chile
                events = int(rng.uniform(2, 4))
            elif 50.0 <= lat <= 56.0 and 5.0 <= lon <= 16.0: # Stable Germany
                events = 0
                
            return {
                "value": float(events),
                "sub_indicators": {
                    "cat3_extreme_events_last_20yr": float(events),
                    "seismic_hazard_pga_g": round(0.45 if -26.0 <= lat <= -18.0 else 0.02, 3),
                    "soil_liquefaction_probability_pct": round(rng.uniform(1.0, 8.0), 1),
                    "land_subsidence_rate_mm_yr": round(rng.uniform(0.5, 4.5), 1)
                }
            }
            
        elif vector_key == "RPE":
            # Policy index (1-5)
            tier = 3.0
            
            if 50.0 <= lat <= 56.0 and 5.0 <= lon <= 16.0: # Germany (Binding Targets, strong PPA)
                tier = 5.0
            elif -26.0 <= lat <= -18.0 and -71.0 <= lon <= -67.0: # Chile
                tier = 4.0
            elif 24.0 <= lat <= 30.0 and 69.0 <= lon <= 76.0: # India
                tier = 3.5
                
            return {
                "value": tier,
                "sub_indicators": {
                    "iea_policy_strength_tier": tier,
                    "permitting_duration_months": round(36.0 - tier * 4.5, 1),
                    "political_stability_index": round(rng.uniform(0.40, 0.95), 2),
                    "currency_stability_5yr_volatility_pct": round(15.0 - tier * 2.0, 1)
                }
            }
            
        elif vector_key == "LSA":
            # Developable land ratio (0 - 100%)
            dev = 45.0 + rng.uniform(-10, 10)
            
            if -26.0 <= lat <= -18.0 and -71.0 <= lon <= -67.0: # Sparsely populated desert
                dev = 88.0 + rng.uniform(-3, 5)
            elif 24.0 <= lat <= 30.0 and 69.0 <= lon <= 76.0: # Rajasthan desert
                dev = 78.0 + rng.uniform(-5, 5)
            elif 50.0 <= lat <= 56.0 and 5.0 <= lon <= 16.0: # Heavily populated Germany
                dev = 32.0 + rng.uniform(-4, 4)
                
            dev = max(min(dev, 100.0), 0.0)
            pop = 100.0 - dev
            
            return {
                "value": round(dev, 1),
                "sub_indicators": {
                    "developable_land_radius_pct": round(dev, 1),
                    "competing_agricultural_use_pct": round((100.0 - dev) * 0.7, 1),
                    "protected_areas_overlap_pct": round(rng.uniform(0.0, 5.0) if dev > 50.0 else rng.uniform(8.0, 20.0), 1),
                    "indigenous_rights_risk_score": round(rng.uniform(1.0, 4.0) if -26.0 <= lat <= -18.0 else 0.2, 1),
                    "population_density_km2": round(pop * 3.5, 1)
                }
            }

    def _get_region_name(self, lat: float, lon: float) -> str:
        """Returns a generic descriptive string based on coordinates."""
        if -26.0 <= lat <= -18.0 and -71.0 <= lon <= -67.0:
            return "Atacama Desert (Chile)"
        elif 24.0 <= lat <= 30.0 and 69.0 <= lon <= 76.0:
            return "Rajasthan Desert (India)"
        elif 50.0 <= lat <= 56.0 and 5.0 <= lon <= 16.0:
            return "Northern Germany"
        return "Generic Global Site"
