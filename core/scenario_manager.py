import json
from typing import Dict, Optional
from pydantic import BaseModel, Field, model_validator


class ScenarioConfig(BaseModel):
    name: str
    description: str
    weights: Dict[str, float] = Field(
        ...,
        description="Dictionary mapping vector key to float weight (should sum to 1.0)"
    )
    penalise_threshold: Optional[float] = Field(
        None,
        description="If any vector score falls below this threshold, a hard cap is placed on the ISS score."
    )
    penalise_cap: Optional[float] = Field(
        55.0,
        description="The maximum score the ISS can have if the penalise threshold is triggered."
    )

    @model_validator(mode="after")
    def validate_and_normalise_weights(self) -> "ScenarioConfig":
        expected_keys = {"SRI", "WRP", "HSI", "GIR", "EVI", "RPE", "LSA"}
        missing = expected_keys - set(self.weights.keys())
        if missing:
            raise ValueError(f"Scenario is missing weights for vectors: {missing}")
        
        # Ensure all weights are positive
        for k, v in self.weights.items():
            if v < 0:
                self.weights[k] = 0.0

        # Normalise to sum to 1.0
        total = sum(self.weights.values())
        if total == 0:
            # Fallback to balanced if all are zero
            self.weights = {k: 1.0 / 7.0 for k in expected_keys}
        else:
            self.weights = {k: v / total for k, v in self.weights.items()}

        return self


# Pre-built standard scenarios
BALANCED_DEVELOPER = ScenarioConfig(
    name="Balanced Developer",
    description="Equal weight allocation across all 7 vectors. Suitable for general feasibility screening.",
    weights={
        "SRI": 0.142857,
        "WRP": 0.142857,
        "HSI": 0.142857,
        "GIR": 0.142857,
        "EVI": 0.142857,
        "RPE": 0.142857,
        "LSA": 0.142857
    }
)

CONSERVATIVE_INFRASTRUCTURE = ScenarioConfig(
    name="Conservative Infrastructure",
    description="Heavy emphasis on grid readiness and regulatory/policy environment, prioritizing execution feasibility.",
    weights={
        "GIR": 0.25,
        "RPE": 0.25,
        "SRI": 0.10,
        "WRP": 0.10,
        "HSI": 0.10,
        "EVI": 0.10,
        "LSA": 0.10
    }
)

CLIMATE_FIRST = ScenarioConfig(
    name="Climate-First",
    description="Heavy emphasis on resource quality (solar, wind) and low hydrological risk, optimizing for long-term climate yield.",
    weights={
        "SRI": 0.20,
        "WRP": 0.20,
        "HSI": 0.20,
        "GIR": 0.10,
        "EVI": 0.10,
        "RPE": 0.10,
        "LSA": 0.10
    }
)


class ScenarioManager:
    """Manages the registration, retrieval, and custom creation of weighting scenarios."""

    def __init__(self):
        self.scenarios: Dict[str, ScenarioConfig] = {
            "Balanced Developer": BALANCED_DEVELOPER,
            "Conservative Infrastructure": CONSERVATIVE_INFRASTRUCTURE,
            "Climate-First": CLIMATE_FIRST
        }

    def get_scenario(self, name: str) -> ScenarioConfig:
        if name in self.scenarios:
            return self.scenarios[name]
        return BALANCED_DEVELOPER

    def register_custom_scenario(self, name: str, description: str, weights: Dict[str, float], penalise_threshold: Optional[float] = None) -> ScenarioConfig:
        config = ScenarioConfig(
            name=name,
            description=description,
            weights=weights,
            penalise_threshold=penalise_threshold
        )
        self.scenarios[name] = config
        return config

    def to_json(self, name: str) -> str:
        scenario = self.get_scenario(name)
        return scenario.model_dump_json(indent=2)

    def load_from_json(self, json_str: str) -> ScenarioConfig:
        data = json.loads(json_str)
        config = ScenarioConfig(**data)
        self.scenarios[config.name] = config
        return config
