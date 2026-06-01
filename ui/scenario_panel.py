import streamlit as st
import pandas as pd
from typing import Any
from core.monte_carlo import MonteCarloEngine

def render_scenario_panel(scenario_manager: Any, portfolio_manager: Any) -> None:
    """
    Renders the Scenario Builder tab (Page 3).
    """
    st.markdown("## 🎛️ Scenario Weightings Builder")
    st.markdown("Manage standard capital weighting allocations, adjust vector trade-offs, and implement risk thresholds.")
    
    # 1. Show pre-built cards
    st.markdown("### 🏛️ Pre-built Standard Configurations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            """
            <div style="background-color: #1A2332; border: 1px solid #2C3E50; padding: 15px; border-radius: 8px; min-height: 200px;">
                <b style="color: #1B6CA8; font-size: 1.1rem;">Balanced Developer</b><br>
                <p style="font-size: 0.85rem; color: #8FA3B1; margin-top: 5px;">
                    Equal weight allocation (0.143 each) across all 7 vector categories. Best for initial screening and broad pre-feasibility reviews.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col2:
        st.markdown(
            """
            <div style="background-color: #1A2332; border: 1px solid #2C3E50; padding: 15px; border-radius: 8px; min-height: 200px;">
                <b style="color: #17A589; font-size: 1.1rem;">Conservative Infrastructure</b><br>
                <p style="font-size: 0.85rem; color: #8FA3B1; margin-top: 5px;">
                    Heavy weights on Grid Infrastructure (0.25) and Permitting/Regulatory (0.25). Prioritizes projects with low execution risk.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col3:
        st.markdown(
            """
            <div style="background-color: #1A2332; border: 1px solid #2C3E50; padding: 15px; border-radius: 8px; min-height: 200px;">
                <b style="color: #E67E22; font-size: 1.1rem;">Climate-First</b><br>
                <p style="font-size: 0.85rem; color: #8FA3B1; margin-top: 5px;">
                    Heavy weights on Solar (0.20), Wind (0.20), and low Hydrological Water Risk (0.20). Prioritizes long-term resource yield assets.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # 2. Form to Create Custom Weight allocations
    st.markdown("### 🎛️ Create Custom Weight Profile")
    st.markdown("Adjust individual vector sliders. The weights will automatically be normalized to sum to 1.0.")
    
    with st.form("custom_scenario_form"):
        scen_name = st.text_input("Scenario Name:", value="Custom Strategy Beta")
        scen_desc = st.text_area("Scenario Description:", value="Custom weighting focusing on targeted localized dynamics.")
        
        # 7 sliders
        w_sri = st.slider("☀️ Solar SRI Weight:", 0.0, 1.0, 0.15, step=0.05)
        w_wrp = st.slider("💨 Wind WRP Weight:", 0.0, 1.0, 0.15, step=0.05)
        w_hsi = st.slider("💧 Hydrological HSI Weight:", 0.0, 1.0, 0.15, step=0.05)
        w_gir = st.slider("🔌 Grid GIR Weight:", 0.0, 1.0, 0.20, step=0.05)
        w_evi = st.slider("🌋 Environmental EVI Weight:", 0.0, 1.0, 0.10, step=0.05)
        w_rpe = st.slider("⚖️ Regulatory RPE Weight:", 0.0, 1.0, 0.15, step=0.05)
        w_lsa = st.slider("🌳 Land/Acceptance LSA Weight:", 0.0, 1.0, 0.10, step=0.05)
        
        # Penalise Threshold overrides
        st.markdown("**⚠️ Penalisation Safeguards**")
        use_penalty = st.checkbox("Enable Score Floor Penalisation", value=False, help="If any vector score falls below this threshold, composite ISS is capped.")
        penalty_thresh = st.slider("Safeguard Threshold Floor Score:", 0, 100, 30, step=5)
        penalty_cap = st.slider("Maximum ISS Score if Safeguard is triggered:", 0, 100, 55, step=5)
        
        btn_save = st.form_submit_button("💾 REGISTER CUSTOM SCENARIO")
        
        if btn_save:
            weights = {
                "SRI": w_sri,
                "WRP": w_wrp,
                "HSI": w_hsi,
                "GIR": w_gir,
                "EVI": w_evi,
                "RPE": w_rpe,
                "LSA": w_lsa
            }
            thresh = float(penalty_thresh) if use_penalty else None
            
            registered = scenario_manager.register_custom_scenario(
                name=scen_name,
                description=scen_desc,
                weights=weights,
                penalise_threshold=thresh
            )
            # Apply custom cap
            if use_penalty:
                registered.penalise_cap = float(penalty_cap)
                
            st.success(f"Custom Scenario '{scen_name}' registered successfully! (Weights normalized to sum to 1.0)")
            
    st.markdown("---")

    # 3. Live Scenario Comparisons of Pinned Locations
    st.markdown("### 🔀 Multi-Scenario Sensitivity Scoreboard")
    st.markdown("Compare composite ISS scores for currently pinned locations across ALL registered scenarios.")
    
    locations = portfolio_manager.get_locations()
    
    if not locations:
        st.info("📌 **No locations pinned!** Pin locations in 'Site Analysis' first to compare them against scenario overrides here.")
        return
        
    records = []
    for loc in locations:
        rec = {"Site Name": loc.name}
        for name, scen in scenario_manager.scenarios.items():
            iss = MonteCarloEngine.calculate_iss_geometric(
                loc.vector_scores,
                scen.weights,
                scen.penalise_threshold,
                scen.penalise_cap or 55.0
            )
            rec[name] = round(iss, 1)
        records.append(rec)
        
    df_compare = pd.DataFrame(records)
    st.dataframe(df_compare, use_container_width=True, hide_index=True)
