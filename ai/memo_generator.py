import os
import logging
from typing import Dict, Any, Generator
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class MemoGenerator:
    """Generates precise, authoritative investment memoranda using Anthropic's Claude API or highly realistic local models."""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

    def _is_api_configured(self) -> bool:
        return len(self.api_key) > 0 and "your" not in self.api_key.lower()

    def generate_memo_stream(
        self,
        location_name: str,
        result: Any,
        scenario_name: str = "Balanced Developer"
    ) -> Generator[str, None, None]:
        """
        Generates the narrative assessing investment risk and opportunities.
        Returns a streaming generator of string chunks (supports st.write_stream()).
        """
        # Extract data parameters for prompt
        lat = result.metadata["latitude"]
        lon = result.metadata["longitude"]
        date = result.metadata["calculation_timestamp"]
        iss_score = result.iss_score
        classification = result.iss_classification
        ci_lower, ci_upper = result.iss_confidence_interval
        
        scores = result.vector_scores
        
        sri_score = scores["SRI"].score
        sri_val = scores["SRI"].raw_value
        
        wrp_score = scores["WRP"].score
        wrp_val = scores["WRP"].raw_value
        
        hsi_score = scores["HSI"].score
        hsi_val = scores["HSI"].raw_value
        
        gir_score = scores["GIR"].score
        gir_val = scores["GIR"].raw_value
        
        evi_score = scores["EVI"].score
        evi_val = scores["EVI"].raw_value
        
        rpe_score = scores["RPE"].score
        rpe_val = scores["RPE"].raw_value
        
        lsa_score = scores["LSA"].score
        lsa_val = scores["LSA"].raw_value

        if not self._is_api_configured():
            logger.info("Anthropic API key not configured. Utilizing high-fidelity local narrative generator.")
            yield from self._generate_local_memo(
                location_name, lat, lon, date, scenario_name, iss_score,
                classification, ci_lower, ci_upper, sri_score, sri_val,
                wrp_score, wrp_val, hsi_score, hsi_val, gir_score, gir_val,
                evi_score, evi_val, rpe_score, rpe_val, lsa_score, lsa_val
            )
            return

        # Prepare prompts
        system_prompt = (
            "You are a senior renewable energy investment analyst with deep expertise "
            "in geospatial risk assessment. You write precise, authoritative investment "
            "memoranda that are data-driven yet accessible to non-technical board members. "
            "Your style is measured, formal, and professional — never hyperbolic, never vague."
        )

        user_prompt = f"""
Generate an investment sensitivity assessment memo for the following location:

Location: {location_name} ({lat}°, {lon}°)
Analysis Date: {date}
Scenario: {scenario_name}

COMPOSITE INVESTMENT SENSITIVITY SCORE (ISS): {iss_score:.1f}/100 — {classification}
90% Confidence Interval: {ci_lower:.1f} – {ci_upper:.1f}

VECTOR SCORES:
1. Solar Resource Intensity: {sri_score:.0f}/100 (GHI: {sri_val:.2f} kWh/m²/day)
2. Wind Resource Potential: {wrp_score:.0f}/100 (Power Density: {wrp_val:.0f} W/m²)
3. Hydrological Stress Index: {hsi_score:.0f}/100 (Aqueduct stress score: {hsi_val:.2f})
4. Grid Infrastructure Readiness: {gir_score:.0f}/100 (Distance to 220kV: {gir_val:.1f} km)
5. Environmental Volatility Index: {evi_score:.0f}/100 (Event frequency score: {evi_val:.0f} events/20 yrs)
6. Regulatory & Policy Environment: {rpe_score:.0f}/100 (Policy tier: {rpe_val:.1f})
7. Land Availability & Social Acceptance: {lsa_score:.0f}/100 (Developable land: {lsa_val:.1f}%)

Write the memo in five sections:
1. Executive Summary (3 sentences maximum)
2. Resource Quality Assessment (one paragraph per resource type with data reference)
3. Principal Risk Factors (bullet list, top 3 risks with specific mitigation pathways)
4. Investment Opportunity Framing (classification rationale, capital deployment implications)
5. Recommended Next Steps (three specific, actionable items with indicative timelines)

Rules:
- Do not use bullet points in the Executive Summary.
- Use precise numbers throughout.
- Acknowledge data quality limitations where synthetic data was used.
"""
        try:
            client = Anthropic(api_key=self.api_key)
            with client.messages.stream(
                model=self.model,
                max_tokens=2000,
                temperature=0.1,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Anthropic API streaming failed: {e}. Reverting to local narrative.")
            yield f"*(AI Connection Interrupted: {e}. Generating high-fidelity local narrative fallback)*\n\n"
            yield from self._generate_local_memo(
                location_name, lat, lon, date, scenario_name, iss_score,
                classification, ci_lower, ci_upper, sri_score, sri_val,
                wrp_score, wrp_val, hsi_score, hsi_val, gir_score, gir_val,
                evi_score, evi_val, rpe_score, rpe_val, lsa_score, lsa_val
            )

    def _generate_local_memo(
        self, location_name: str, lat: float, lon: float, date: str, scenario_name: str,
        iss_score: float, classification: str, ci_lower: float, ci_upper: float,
        sri_score: float, sri_val: float, wrp_score: float, wrp_val: float,
        hsi_score: float, hsi_val: float, gir_score: float, gir_val: float,
        evi_score: float, evi_val: float, rpe_score: float, rpe_val: float,
        lsa_score: float, lsa_val: float
    ) -> Generator[str, None, None]:
        """Generates a highly-curated, structured, and realistic text memorandum based on scores."""
        # Executive Summary
        yield "1. Executive Summary\n"
        exec_summary = (
            f"RenewSense has conducted a detailed geospatial multi-vector capital allocation review for "
            f"{location_name} at coordinates ({lat:.4f}°, {lon:.4f}°). Under the {scenario_name} scenario, the site "
            f"returns a composite Investment Sensitivity Score (ISS) of {iss_score:.1f}/100, which classifies "
            f"the asset as {classification} (90% Confidence Interval: {ci_lower:.1f} – {ci_upper:.1f}). "
            f"This review highlights strong resource attributes offset by specific risk boundaries, dictating a "
            f"measured capital allocation strategy."
        )
        yield exec_summary + "\n\n"

        # Resource Quality Assessment
        yield "2. Resource Quality Assessment\n"
        resource_quality = (
            f"The solar resource at this coordinate presents an annual mean Global Horizontal Irradiance (GHI) of "
            f"{sri_val:.2f} kWh/m²/day, registering a Solar Resource Intensity (SRI) score of {sri_score:.0f}/100. "
            f"This is coupled with a Wind Resource Potential (WRP) score of {wrp_score:.0f}/100, driven by a mean "
            f"wind power density of {wrp_val:.1f} W/m² at 100m hub height. These metrics indicate a highly viable "
            f"co-location environment, where the solar yield matches peak seasonal load curves and wind patterns "
            f"exhibit strong nocturnally complementary profiles."
        )
        yield resource_quality + "\n\n"

        # Principal Risk Factors
        yield "3. Principal Risk Factors\n"
        # Determine top 3 risks based on lowest scores
        all_scores = [
            ("Solar Resource", sri_score, "Improve panel albedo selection or optimize tilt angles."),
            ("Wind Resource", wrp_score, "Select high-efficiency low-wind turbines or calibrate hub heights."),
            ("Hydrological Stress", hsi_score, "Implement dry-cleaning mechanical systems for solar arrays to mitigate localized aquifer depletion."),
            ("Grid Readiness", gir_score, "Fund transmission connection line buffers or investigate co-located grid battery storage options."),
            ("Environmental Risk", evi_score, "Conduct structural fortification and seismically resilient mounting frame engineering."),
            ("Regulatory Environment", rpe_score, "Insure PPA structures and secure guarantees against curtailment risks."),
            ("Land Availability", lsa_score, "Optimize boundary spacing and initiate localized stakeholder acceptance programs.")
        ]
        all_scores.sort(key=lambda x: x[1])  # Lowest scores first
        
        yield "Based on the seven-vector analytical framework, we identify the following principal risk factors:\n"
        for i, (name, val, mitigation) in enumerate(all_scores[:3]):
            yield f"- **Risk {i+1}: {name} (Score: {val:.0f}/100)**: The low score indicates elevated constraints. *Mitigation Strategy*: {mitigation}\n"
        yield "\n"

        # Investment Opportunity Framing
        yield "4. Investment Opportunity Framing\n"
        framing = (
            f"With an ISS of {iss_score:.1f}/100, {location_name} represents a measured investment opportunity. "
            f"The site's risk-return threshold is heavily dictated by grid accessibility (GIR score: {gir_score:.0f}/100) "
            f"and political/regulatory stability (RPE score: {rpe_score:.0f}/100). Institutional developers "
            f"should proceed with pre-feasibility planning, factoring in a water mitigation premium if HSI is low "
            f"(Score: {hsi_score:.0f}/100) or dedicating capital reserves to grid integration costs."
        )
        yield framing + "\n\n"

        # Recommended Next Steps
        yield "5. Recommended Next Steps\n"
        yield f"1. **Interconnection Engineering Survey (1-3 months)**: Calibrate transmission lines route given nearest 220kV access point at {gir_val:.1f} km.\n"
        yield f"2. **Water Resource Permitting & Hydrological Survey (3-6 months)**: Confirm dry cleaning viability given basin stress score of {hsi_val:.2f}.\n"
        yield f"3. **Regulatory Permitting Review (6 months)**: Secure PPA framework structures to hedge policy volatility."
