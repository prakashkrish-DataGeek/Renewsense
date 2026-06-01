import streamlit as st
import pandas as pd
from typing import Any, Dict
from visualisation.chart_builder import ChartBuilder
from core.portfolio import PortfolioLocation

def render_vector_panel(result: Any, location_name: str, lat: float, lon: float, radius_km: int, portfolio_manager: Any) -> None:
    """
    Renders the Right Column score panel and detailed vector expanders below.
    """
    st.markdown("### 🏆 Investment Sensitive Score (ISS)")
    
    # 1. Gauge and giant score metrics
    fig_gauge = ChartBuilder.build_iss_gauge(result.iss_score, result.iss_classification)
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
    
    # 2. Confidence interval summary
    ci_lower, ci_upper = result.iss_confidence_interval
    ci_delta = round((ci_upper - ci_lower) / 2.0, 1)
    
    st.markdown(
        f"""
        <div style="background-color: #1A2332; border: 1px solid #2C3E50; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 20px;">
            <span style="font-size: 0.9rem; color: #8FA3B1; font-weight: bold;">90% CONFIDENCE BAND</span><br>
            <span style="font-size: 1.8rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #E8EDF2;">
                ISS {result.iss_score:.1f} &plusmn; {ci_delta}
            </span><br>
            <span style="font-size: 0.85rem; color: #8FA3B1;">
                Range (5th - 95th %tile): <b>{ci_lower:.1f} to {ci_upper:.1f}</b>
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 3. Add to Portfolio Pinning mechanism
    if st.button("📌 PIN LOCATION TO PORTFOLIO", use_container_width=True):
        scores_dict = {v: result.vector_scores[v].score for v in result.vector_scores}
        loc_id = f"{round(lat,2)}_{round(lon,2)}"
        
        # Build portfolio location structure
        p_loc = PortfolioLocation(
            id=loc_id,
            name=location_name,
            latitude=lat,
            longitude=lon,
            radius_km=radius_km,
            vector_scores=scores_dict,
            iss_score=result.iss_score,
            iss_classification=result.iss_classification,
            raw_data=result.raw_data
        )
        
        added = portfolio_manager.add_location(p_loc)
        if added:
            st.success(f"Successfully pinned '{location_name}' to portfolio!")
        else:
            st.warning("Portfolio is full! Max capacity is 12 locations.")

    st.markdown("---")
    
    # 4. Detailed Horizontal Vector Scores Chart
    st.markdown("#### 📊 Vector Scoring Profiles")
    scores_only = {v: result.vector_scores[v].score for v in result.vector_scores}
    fig_scores = ChartBuilder.build_vector_scores_chart(scores_only)
    st.plotly_chart(fig_scores, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("---")

    # 5. Expandable Vector Sub-indicators Detail
    st.markdown("#### 📂 Analytical Vector Breakdowns")
    
    vector_info = {
        "SRI": {
            "title": "☀️ SRI — Solar Resource Intensity",
            "desc": "Analyzes GHI (Global Horizontal Irradiance) raser statistics, seasonal skewing factors, and albedo constraints."
        },
        "WRP": {
            "title": "💨 WRP — Wind Resource Potential",
            "desc": "Evaluates 100m height wind speeds, power densities, Weibull distribution k variables, and seasonal wind anisotropy."
        },
        "HSI": {
            "title": "💧 HSI — Hydrological Stress Index",
            "desc": "Inverted baseline water stress scale representing physical operational water risks for panels, machinery, and utilities."
        },
        "GIR": {
            "title": "🔌 GIR — Grid Infrastructure Readiness",
            "desc": "Assesses distance constraints to high-voltage transmission lines (220kV+), substation capacities, and congestion risks."
        },
        "EVI": {
            "title": "🌋 EVI — Environmental Volatility Index",
            "desc": "Synthesizes regional histories of Category 3+ disasters, active volcanic/seismic vectors, and soil deformation risks."
        },
        "RPE": {
            "title": "⚖️ RPE — Regulatory & Policy Environment",
            "desc": "Quantifies country-level feed-in mechanisms, legal permitting duration averages, and political currency stability metrics."
        },
        "LSA": {
            "title": "🌳 LSA — Land Availability & Social Acceptance",
            "desc": "Measures developable land percentages (excluding protected reserves, high-density residential grids, forests) and social dynamics."
        }
    }
    
    for v_key, info in vector_info.items():
        v_score = result.vector_scores[v_key]
        
        with st.expander(f"{info['title']} (Score: {v_score.score:.1f}/100)"):
            st.markdown(f"**Methodology**: {info['desc']}")
            
            col1, col2 = st.columns(2)
            quality_color = "red" if v_score.data_quality == "SYNTHETIC" else ("orange" if v_score.data_quality == "CACHED" else "green")
            col1.markdown(f"**Raw Value**: `{v_score.raw_value:.2f} {v_score.unit}`")
            col2.markdown(f"**Data Quality**: :font[{v_score.data_quality}]", help="LIVE API = actual queried stats, SYNTHETIC = offline geographic model, CACHED = local saved values.")
            
            # Sub-indicators table
            st.markdown("**Sub-Indicator Matrix**")
            sub_records = []
            for sub_k, sub_v in v_score.sub_indicators.items():
                # Formulate readable labels
                sub_records.append({
                    "Sub-Indicator": sub_k.replace("_", " ").title(),
                    "Value": round(sub_v, 3)
                })
            df_sub = pd.DataFrame(sub_records)
            st.dataframe(df_sub, use_container_width=True, hide_index=True)
            
            # Quartile comparison
            st.markdown("**Global Quartile Standings**")
            if v_score.score >= 75.0:
                st.info("⭐️ **Top Quartile (Excellent)**: Resource quality or infrastructure readiness is globally superior.")
            elif v_score.score >= 50.0:
                st.success("📈 **Above Average**: Site performs within baseline developer standards.")
            else:
                st.warning("⚠️ **Underperforming / Constrained**: Low score indicates serious localized hurdles. Mitigation required.")
