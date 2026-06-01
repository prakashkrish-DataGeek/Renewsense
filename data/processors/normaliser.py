import os
import yaml
import logging
import numpy as np
from typing import Dict, Tuple, List, Any

logger = logging.getLogger(__name__)

DEFAULT_NORMALISATION_PARAMS = {
    "SRI": {
        "unit": "kWh/m²/day",
        "breakpoints": [[1.0, 0.0], [2.0, 10.0], [3.0, 30.0], [4.0, 50.0], [5.0, 70.0], [5.5, 80.0], [6.0, 88.0], [7.0, 95.0], [8.0, 100.0]]
    },
    "WRP": {
        "unit": "W/m²",
        "breakpoints": [[50.0, 0.0], [100.0, 15.0], [150.0, 25.0], [250.0, 45.0], [350.0, 65.0], [400.0, 75.0], [550.0, 85.0], [750.0, 95.0], [1000.0, 100.0]]
    },
    "HSI": {
        "unit": "Risk Score (0-5)",
        "breakpoints": [[0.0, 100.0], [1.0, 85.0], [2.0, 65.0], [3.0, 45.0], [4.0, 20.0], [5.0, 0.0]]
    },
    "GIR": {
        "unit": "km",
        "breakpoints": [[0.0, 100.0], [5.0, 95.0], [10.0, 90.0], [25.0, 70.0], [50.0, 45.0], [75.0, 25.0], [100.0, 15.0], [150.0, 0.0]]
    },
    "EVI": {
        "unit": "Events / 20 yrs",
        "breakpoints": [[0.0, 100.0], [1.0, 85.0], [2.0, 70.0], [3.0, 50.0], [4.0, 35.0], [5.0, 20.0], [6.0, 0.0]]
    },
    "RPE": {
        "unit": "Policy Tier (1-5)",
        "breakpoints": [[1.0, 20.0], [2.0, 40.0], [3.0, 60.0], [4.0, 80.0], [5.0, 100.0]]
    },
    "LSA": {
        "unit": "%",
        "breakpoints": [[0.0, 0.0], [10.0, 20.0], [20.0, 40.0], [30.0, 60.0], [50.0, 80.0], [75.0, 100.0]]
    }
}

class VectorNormaliser:
    """Normalises raw vector statistics into [0-100] scores using piecewise linear configurations."""

    def __init__(self, config_path: str = "config/normalisation.yaml"):
        self.config_path = config_path
        self.params = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    config = yaml.safe_load(f)
                    if config:
                        logger.info(f"Loaded normalisation parameters from: {self.config_path}")
                        return config
            except Exception as e:
                logger.error(f"Error reading normalisation config file: {e}. Reverting to defaults.")
        else:
            logger.warning(f"Config path {self.config_path} does not exist. Using defaults.")
        return DEFAULT_NORMALISATION_PARAMS

    def normalise(self, vector_key: str, raw_data: Dict[str, Any]) -> Tuple[float, str, Dict[str, float]]:
        """
        Normalises raw_value for the given vector key.
        Returns:
            - normalised_score (float, 0-100)
            - unit (str)
            - sub_indicators (Dict[str, float])
        """
        if vector_key not in self.params:
            logger.warning(f"Vector {vector_key} not in config. Returning score 50.0.")
            return 50.0, "unknown", {}

        config = self.params[vector_key]
        unit = config.get("unit", "")
        
        # Raw value extracted
        raw_val = raw_data.get("value", 0.0)
        
        # Pull sub-indicators if they exist (or use raw value as only indicator)
        sub_indicators = raw_data.get("sub_indicators", {})
        if not sub_indicators:
            sub_indicators = {"baseline_value": float(raw_val)}

        # Perform piecewise linear interpolation
        breakpoints = config.get("breakpoints", [])
        if not breakpoints:
            return 50.0, unit, sub_indicators

        # Split into x and y arrays
        # Ensure they are sorted by x
        breakpoints = sorted(breakpoints, key=lambda x: x[0])
        x_vals = [float(bp[0]) for bp in breakpoints]
        y_vals = [float(bp[1]) for bp in breakpoints]
        
        # Perform interpolation
        score = float(np.interp(raw_val, x_vals, y_vals))
        
        # Clamp to [0, 100] just in case
        score = max(min(score, 100.0), 0.0)
        
        return round(score, 2), unit, sub_indicators
