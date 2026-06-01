import pytest
from data.processors.normaliser import VectorNormaliser

def test_sri_normalisation():
    normaliser = VectorNormaliser()
    # SRI raw data GHI = 5.5 should return between 73.0 and 82.0
    res_score, unit, _ = normaliser.normalise("SRI", {"value": 5.5})
    assert 73.0 <= res_score <= 82.0
    assert unit == "kWh/m²/day"

def test_hsi_inversion():
    normaliser = VectorNormaliser()
    # High water risk stress raw value (5.0) -> Low score (0.0)
    score_high_risk, _, _ = normaliser.normalise("HSI", {"value": 5.0})
    assert score_high_risk <= 5.0
    
    # Low water risk stress raw value (0.0) -> High score (100.0)
    score_low_risk, _, _ = normaliser.normalise("HSI", {"value": 0.0})
    assert score_low_risk >= 95.0

def test_boundary_clamping():
    normaliser = VectorNormaliser()
    # Test extreme high out of bounds
    score_high, _, _ = normaliser.normalise("SRI", {"value": 999.0})
    assert score_high == 100.0
    
    # Test extreme low out of bounds
    score_low, _, _ = normaliser.normalise("WRP", {"value": -999.0})
    assert score_low == 0.0

def test_unknown_vector():
    normaliser = VectorNormaliser()
    score, unit, _ = normaliser.normalise("UNKNOWN_VECTOR_XYZ", {"value": 50.0})
    assert score == 50.0
    assert unit == "unknown"
