import numpy as np
from typing import Dict, Tuple, List, Optional, Any
from core.scenario_manager import ScenarioConfig


class MonteCarloEngine:
    """Calculates risk uncertainty and sensitivity metrics for a given site score profile."""

    @staticmethod
    def calculate_iss_geometric(scores: Dict[str, float], weights: Dict[str, float], penalise_threshold: Optional[float] = None, penalise_cap: float = 55.0) -> float:
        """Helper to calculate composite ISS using weighted geometric mean, with optional threshold cap."""
        prod = 1.0
        for vec, score in scores.items():
            w = weights.get(vec, 1.0 / 7.0)
            # Clip score to [0.1, 100] to prevent mathematical zeros in geometric products
            s_clipped = max(min(score, 100.0), 0.1)
            prod *= (s_clipped ** w)
        
        iss = prod
        
        # Apply hard threshold cap if any vector is below penalise_threshold
        if penalise_threshold is not None:
            for score in scores.values():
                if score < penalise_threshold:
                    iss = min(iss, penalise_cap)
                    break
        return iss

    def run_simulation(
        self,
        baseline_scores: Dict[str, float],
        scenario: ScenarioConfig,
        n_simulations: int = 500,
        noise_std: float = 5.0
    ) -> Tuple[Tuple[float, float], List[float]]:
        """
        Runs Monte Carlo trials with gaussian noise (default std=5.0) on scores.
        Returns:
            - Tuple[lower_90_ci, upper_90_ci]
            - List of all simulated ISS values (for histogram visualization)
        """
        np.random.seed(42)  # Maintain deterministic results across runs
        sim_results = []
        vectors = list(baseline_scores.keys())

        for _ in range(n_simulations):
            trial_scores = {}
            for vec in vectors:
                base = baseline_scores[vec]
                # Gaussian noise around the baseline
                perturbed = np.random.normal(loc=base, scale=noise_std)
                trial_scores[vec] = max(min(perturbed, 100.0), 0.1)

            trial_iss = self.calculate_iss_geometric(
                trial_scores,
                scenario.weights,
                scenario.penalise_threshold,
                scenario.penalise_cap or 55.0
            )
            sim_results.append(trial_iss)

        # Retrieve 90% confidence interval (5th to 95th percentiles)
        lower_ci = float(np.percentile(sim_results, 5))
        upper_ci = float(np.percentile(sim_results, 95))

        return (lower_ci, upper_ci), sim_results

    def generate_tornado_data(
        self,
        baseline_scores: Dict[str, float],
        scenario: ScenarioConfig,
        delta: float = 20.0
    ) -> List[Dict[str, Any]]:
        """
        Computes marginal impacts of each vector by varying it by +/- delta.
        Returns a sorted list of dictionaries with low/high swings.
        """
        tornado_results = []
        baseline_iss = self.calculate_iss_geometric(
            baseline_scores,
            scenario.weights,
            scenario.penalise_threshold,
            scenario.penalise_cap or 55.0
        )

        for vec, score in baseline_scores.items():
            # Scenario weight for this vector
            weight = scenario.weights.get(vec, 0.0)
            if weight == 0.0:
                continue

            # Calculate ISS at baseline - delta
            low_scores = baseline_scores.copy()
            low_scores[vec] = max(score - delta, 0.1)
            iss_low = self.calculate_iss_geometric(
                low_scores,
                scenario.weights,
                scenario.penalise_threshold,
                scenario.penalise_cap or 55.0
            )

            # Calculate ISS at baseline + delta
            high_scores = baseline_scores.copy()
            high_scores[vec] = min(score + delta, 100.0)
            iss_high = self.calculate_iss_geometric(
                high_scores,
                scenario.weights,
                scenario.penalise_threshold,
                scenario.penalise_cap or 55.0
            )

            swing = abs(iss_high - iss_low)

            tornado_results.append({
                "vector": vec,
                "base_score": score,
                "iss_low": iss_low,
                "iss_high": iss_high,
                "swing": swing,
                "baseline_iss": baseline_iss
            })

        # Sort by total swing descending for tornado layout
        tornado_results.sort(key=lambda x: x["swing"], reverse=True)
        return tornado_results
