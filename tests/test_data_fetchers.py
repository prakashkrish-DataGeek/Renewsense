import pytest
from data.fetchers.era5_ghi import SolarFetcher
from data.fetchers.wind_atlas import WindFetcher
from data.fetchers.aqueduct import AqueductFetcher

def test_fetcher_base_fallback():
    fetcher = SolarFetcher()
    # If credentials are not present, live fetch resolves to synthetic
    res_data, quality = fetcher.fetch_with_fallback(27.0, 74.0, 25)
    assert quality == "SYNTHETIC"
    assert "value" in res_data
    assert "sub_indicators" in res_data

def test_wind_fetcher_heuristics():
    fetcher = WindFetcher()
    # Test high wind speed region Northern Germany
    res_data, _ = fetcher.fetch_with_fallback(54.0, 10.0, 25)
    assert res_data["value"] >= 450.0  # Favourable wind power density simulated

def test_aqueduct_fetcher_desert_heuristics():
    fetcher = AqueductFetcher()
    # Atacama Desert coordinate -> Extremely high water risk stress score (above 4.0 out of 5)
    res_data, _ = fetcher.fetch_with_fallback(-24.0, -69.0, 25)
    assert res_data["value"] >= 4.0
