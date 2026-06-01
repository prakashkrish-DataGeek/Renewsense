import time
import logging
from typing import Dict, Tuple, Any, Optional
from pydantic import BaseModel, Field
from concurrent.futures import ThreadPoolExecutor

from core.scenario_manager import ScenarioConfig, BALANCED_DEVELOPER
from core.monte_carlo import MonteCarloEngine
from data.processors.normaliser import VectorNormaliser
from data.processors.cache_manager import CacheManager
from data.synthetic.data_generator import SyntheticDataGenerator

# Configure logging
logger = logging.getLogger(__name__)

class VectorScore(BaseModel):
    score: float = Field(..., ge=0, le=100)
    raw_value: Any
    unit: str
    data_quality: str  # "LIVE" | "SYNTHETIC" | "CACHED"
    sub_indicators: Dict[str, float] = {}

class ISSResult(BaseModel):
    iss_score: float = Field(..., ge=0, le=100)
    iss_classification: str
    iss_confidence_interval: Tuple[float, float]
    vector_scores: Dict[str, VectorScore]
    metadata: Dict[str, Any]
    raw_data: Dict[str, Any]

class ISSEngine:
    """Core RenewSense engine orchestrating parallel data fetching, normalization, ISS calculation, and risk simulation."""

    def __init__(self, cache_dir: str = "data/cache"):
        self.normaliser = VectorNormaliser()
        self.cache_manager = CacheManager(cache_dir)
        self.synthetic_generator = SyntheticDataGenerator()
        self.monte_carlo = MonteCarloEngine()

        # Import fetchers locally or configure them
        self._init_fetchers()

    def _init_fetchers(self):
        # We will dynamically load or instantiate fetchers here to avoid circular imports.
        # Each fetcher will have its class in data.fetchers
        try:
            from data.fetchers.era5_ghi import SolarFetcher
            from data.fetchers.wind_atlas import WindFetcher
            from data.fetchers.aqueduct import AqueductFetcher
            from data.fetchers.osm_grid import OsmGridFetcher
            from data.fetchers.extreme_events import ExtremeEventsFetcher
            from data.fetchers.policy_db import PolicyDbFetcher
            from data.fetchers.land_cover import LandCoverFetcher

            self.fetchers = {
                "SRI": SolarFetcher(),
                "WRP": WindFetcher(),
                "HSI": AqueductFetcher(),
                "GIR": OsmGridFetcher(),
                "EVI": ExtremeEventsFetcher(),
                "RPE": PolicyDbFetcher(),
                "LSA": LandCoverFetcher()
            }
        except Exception as e:
            logger.warning(f"Could not load all live fetchers: {e}. Fallbacks will be used.")
            self.fetchers = {}

    def calculate(
        self,
        latitude: float,
        longitude: float,
        radius_km: int = 25,
        scenario: ScenarioConfig = BALANCED_DEVELOPER,
        use_cache: bool = True,
        demo_mode: bool = False
    ) -> ISSResult:
        """
        Runs the ISS calculation pipeline:
        1. Checks local cache for (lat, lon, radius, scenario)
        2. Fetches raw data for 7 vectors in parallel (thread pool)
        3. Normalises raw data to 0-100 scores
        4. Calculates ISS weighted geometric mean
        5. Computes confidence interval via Monte Carlo
        6. Returns detailed ISSResult Pydantic model
        """
        start_time = time.time()
        
        # 1. Cache lookup
        cache_key = f"{round(latitude, 4)}_{round(longitude, 4)}_{radius_km}_{scenario.name}"
        if use_cache:
            cached_result = self.cache_manager.get(cache_key)
            if cached_result:
                logger.info(f"Cache hit for key: {cache_key}")
                # Mark as cached
                for score in cached_result.vector_scores.values():
                    score.data_quality = "CACHED"
                cached_result.metadata["cache_status"] = "HIT"
                cached_result.metadata["calculation_duration_sec"] = time.time() - start_time
                return cached_result

        logger.info(f"Cache miss or bypassed. Running full calculation for key: {cache_key}")
        
        raw_results = {}
        data_qualities = {}
        
        # 2. Parallel data fetching
        vectors = ["SRI", "WRP", "HSI", "GIR", "EVI", "RPE", "LSA"]
        
        if demo_mode or not self.fetchers:
            # Sub-second synthetic generation
            logger.info("Executing in DEMO_MODE: Generating synthetic location heuristics.")
            raw_results = self.synthetic_generator.generate_all(latitude, longitude, radius_km)
            for v in vectors:
                data_qualities[v] = "SYNTHETIC"
        else:
            # Parallel execution via ThreadPool
            with ThreadPoolExecutor(max_workers=7) as executor:
                future_to_vector = {
                    executor.submit(self.fetchers[v].fetch_with_fallback, latitude, longitude, radius_km): v
                    for v in vectors
                }
                for future in future_to_vector:
                    v = future_to_vector[future]
                    try:
                        raw_data, quality = future.result()
                        raw_results[v] = raw_data
                        data_qualities[v] = quality
                    except Exception as exc:
                        logger.error(f"Vector {v} generated an exception: {exc}")
                        # Fallback to synthetic if fetcher crashed completely
                        syn_data = self.synthetic_generator.generate_vector(v, latitude, longitude, radius_km)
                        raw_results[v] = syn_data
                        data_qualities[v] = "SYNTHETIC"

        # 3. Score normalization
        vector_scores = {}
        scores_dict = {}
        for v in vectors:
            raw_data = raw_results[v]
            score_val, unit, sub_ind = self.normaliser.normalise(v, raw_data)
            
            vector_scores[v] = VectorScore(
                score=score_val,
                raw_value=raw_data.get("value", 0.0),
                unit=unit,
                data_quality=data_qualities[v],
                sub_indicators=sub_ind
            )
            scores_dict[v] = score_val

        # 4. Calculate ISS composite score
        iss_score = MonteCarloEngine.calculate_iss_geometric(
            scores_dict,
            scenario.weights,
            scenario.penalise_threshold,
            scenario.penalise_cap or 55.0
        )
        
        iss_class = self.classify_iss(iss_score)

        # 5. Monte Carlo simulation
        (ci_lower, ci_upper), _ = self.monte_carlo.run_simulation(
            scores_dict,
            scenario,
            n_simulations=500,
            noise_std=5.0
        )

        calculation_time = time.time() - start_time
        
        # Compile metadata
        metadata = {
            "latitude": latitude,
            "longitude": longitude,
            "radius_km": radius_km,
            "scenario_name": scenario.name,
            "calculation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "calculation_duration_sec": round(calculation_time, 3),
            "cache_status": "MISS",
            "demo_mode": demo_mode
        }

        # 6. Assemble result
        result = ISSResult(
            iss_score=round(iss_score, 1),
            iss_classification=iss_class,
            iss_confidence_interval=(round(ci_lower, 1), round(ci_upper, 1)),
            vector_scores=vector_scores,
            metadata=metadata,
            raw_data=raw_results
        )

        # Save to cache
        if use_cache:
            self.cache_manager.set(cache_key, result)

        return result

    @staticmethod
    def classify_iss(score: float) -> str:
        if score <= 30:
            return "High Sensitivity / Elevated Risk"
        elif score <= 50:
            return "Moderate-High Sensitivity"
        elif score <= 70:
            return "Moderate Sensitivity"
        elif score <= 85:
            return "Low-Moderate Sensitivity / Favourable"
        else:
            return "Low Sensitivity / Prime Investment Grade"
