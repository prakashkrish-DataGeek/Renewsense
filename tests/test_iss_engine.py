import pytest
from core.iss_engine import ISSEngine
from core.scenario_manager import ScenarioConfig, BALANCED_DEVELOPER, CLIMATE_FIRST
from core.monte_carlo import MonteCarloEngine

def test_perfect_location():
    # Synthetic "perfect" location: all 7 vectors are 100
    scores = {v: 100.0 for v in ["SRI", "WRP", "HSI", "GIR", "EVI", "RPE", "LSA"]}
    weights = BALANCED_DEVELOPER.weights
    iss = MonteCarloEngine.calculate_iss_geometric(scores, weights)
    assert round(iss, 1) == 100.0

def test_worst_location():
    # Synthetic "worst" location: all vectors are 0 (clipped to 0.1 for geometric math)
    scores = {v: 0.0 for v in ["SRI", "WRP", "HSI", "GIR", "EVI", "RPE", "LSA"]}
    weights = BALANCED_DEVELOPER.weights
    iss = MonteCarloEngine.calculate_iss_geometric(scores, weights)
    assert round(iss, 1) <= 1.0  # Clipped product near zero

def test_geometric_mean_penalisation():
    # High score on 6 vectors (95.0), complete failure on 1 vector (5.0)
    scores = {v: 95.0 for v in ["SRI", "WRP", "HSI", "EVI", "RPE", "LSA"]}
    scores["GIR"] = 5.0  # No grid connectivity
    
    weights = BALANCED_DEVELOPER.weights
    iss_geo = MonteCarloEngine.calculate_iss_geometric(scores, weights)
    
    # Arithmetic average would be ~82.0
    # ISS must be significantly lower due to geometric mean product properties
    assert iss_geo < 60.0

def test_scenario_weight_shifts():
    # Site has high resources (SRI=90, WRP=90) but poor infrastructure/permitting (GIR=30, RPE=30)
    scores = {
        "SRI": 90.0, "WRP": 90.0, "HSI": 75.0,
        "GIR": 30.0, "EVI": 80.0, "RPE": 30.0, "LSA": 80.0
    }
    
    # Under Climate-First (heavy resource weights), ISS should be higher
    iss_climate = MonteCarloEngine.calculate_iss_geometric(scores, CLIMATE_FIRST.weights)
    
    # Under Conservative Infrastructure (heavy grid/policy weights), ISS should be lower
    from core.scenario_manager import CONSERVATIVE_INFRASTRUCTURE
    iss_infra = MonteCarloEngine.calculate_iss_geometric(scores, CONSERVATIVE_INFRASTRUCTURE.weights)
    
    assert iss_climate > iss_infra

def test_monte_carlo_ci_bounds():
    scores = {
        "SRI": 80.0, "WRP": 65.0, "HSI": 50.0,
        "GIR": 75.0, "EVI": 85.0, "RPE": 70.0, "LSA": 75.0
    }
    
    engine = MonteCarloEngine()
    (lower_ci, upper_ci), _ = engine.run_simulation(
        scores,
        BALANCED_DEVELOPER,
        n_simulations=100
    )
    
    # Check that CI is wider than 0 and narrower than 20 points wide
    assert lower_ci < upper_ci
    ci_width = upper_ci - lower_ci
    assert 0.0 < ci_width <= 20.0
