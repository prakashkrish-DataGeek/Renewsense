from data.fetchers.era5_ghi import SolarFetcher
from data.fetchers.wind_atlas import WindFetcher
from data.fetchers.aqueduct import AqueductFetcher
from data.fetchers.osm_grid import OsmGridFetcher
from data.fetchers.extreme_events import ExtremeEventsFetcher
from data.fetchers.policy_db import PolicyDbFetcher
from data.fetchers.land_cover import LandCoverFetcher

__all__ = [
    "SolarFetcher",
    "WindFetcher",
    "AqueductFetcher",
    "OsmGridFetcher",
    "ExtremeEventsFetcher",
    "PolicyDbFetcher",
    "LandCoverFetcher"
]
