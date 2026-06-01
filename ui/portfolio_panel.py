import streamlit as st
import pandas as pd
from typing import Any
from visualisation.chart_builder import ChartBuilder

def render_portfolio_panel(portfolio_manager: Any, scenario_manager: Any) -> None:
    """
    Renders the Portfolio Comparison tab (Page 2).
    """
    st.markdown("## 📊 Portfolio Comparative Analytics")
    st.markdown("Compare pinned project locations, analyze multi-vector correlations, and benchmark against world-class operating sites.")
    
    locations = portfolio_manager.get_locations()
    
    if not locations:
        st.info("📌 **No locations pinned yet!** Use the 'Site Analysis' page to explore a coordinate and pin it to compare portfolio matrices.")
        return
        
    st.markdown(f"**Currently holding {len(locations)}/12 locations pinned in workspace.**")
    
    # 1. Pinned Locations Table
    st.markdown("### 📂 Pinned Location Inventory")
    
    # Add scenario override inside portfolio page for rankings
    scenarios_list = list(scenario_manager.scenarios.keys())
    selected_scen_name = st.selectbox(
        "Apply Portfolio Scenario Weightings:",
        options=scenarios_list,
        index=0,
        key="portfolio_scenario_override"
    )
    selected_scenario = scenario_manager.get_scenario(selected_scen_name)
    
    # Generate Ranked Inventory
    df_ranked = portfolio_manager.get_ranking_table(selected_scenario)
    st.dataframe(df_ranked, use_container_width=True, hide_index=True)
    
    # Enable location removal
    col_del_select, col_del_btn = st.columns([3, 1])
    loc_to_delete = col_del_select.selectbox("Select site to unpin:", options=[loc.name for loc in locations])
    if col_del_btn.button("🗑️ Unpin Location", use_container_width=True):
        loc_id = next(loc.id for loc in locations if loc.name == loc_to_delete)
        portfolio_manager.remove_location(loc_id)
        st.success(f"Removed '{loc_to_delete}' from workspace.")
        st.rerun()

    st.markdown("---")

    # 2. Charts Layout (Radar Spider overlay + ranked ISS bars)
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("#### 🕸️ Multi-Vector Spider Overlay")
        fig_radar = ChartBuilder.build_portfolio_radar(locations, selected_scenario.name)
        st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
        
    with col_chart2:
        st.markdown("#### 🏆 Composite ISS Comparison")
        fig_bars = ChartBuilder.build_iss_comparison_bars(df_ranked)
        st.plotly_chart(fig_bars, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")

    # 3. Advanced Heatmaps (Scores + Correlation Matrix)
    st.markdown("### 📐 Statistical Correlation & Matrices")
    
    col_heat1, col_heat2 = st.columns(2)
    
    with col_heat1:
        st.markdown("#### 🗺️ Vector Performance Heatmap")
        # Generate custom heatmap from portfolio
        heatmap_records = []
        for loc in locations:
            rec = {"Site Name": loc.name}
            for vec, score in loc.vector_scores.items():
                rec[vec] = score
            heatmap_records.append(rec)
        df_heat = pd.DataFrame(heatmap_records).set_index("Site Name")
        
        fig_heat = px.imshow(
            df_heat,
            labels=dict(x="Analytical Vector", y="Pinned Site", color="Score"),
            x=df_heat.columns,
            y=df_heat.index,
            colorscale="Viridis",
            zmin=0,
            zmax=100
        )
        fig_heat.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            height=280
        )
        st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})
        
    with col_heat2:
        st.markdown("#### 🧬 Pearson Correlation Matrix")
        df_corr = portfolio_manager.get_correlation_matrix()
        fig_corr = ChartBuilder.build_correlation_heatmap(df_corr)
        st.plotly_chart(fig_corr, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")

    # 4. Project Matchmaking / Benchmark delta
    st.markdown("### 🤝 Curated Benchmark Matchmaker")
    st.markdown("Finds the closest operating world-class project based on multi-vector spatial Euclidean distance.")
    
    match_site_name = st.selectbox("Select site to match:", options=[loc.name for loc in locations])
    target_loc = next(loc for loc in locations if loc.name == match_site_name)
    
    with st.spinner("Finding closest comparable..."):
        match_result = portfolio_manager.match_best_comparable(target_loc)
        
    st.markdown(
        f"""
        <div style="background-color: #1A2332; border: 1px solid #2C3E50; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
            <h4 style="color: #17A589; margin-bottom: 10px;">🏆 Best Operating Benchmark Match</h4>
            Project Name: <b>{match_result['project_name']}</b> ({match_result['country']})<br>
            Technology: <b>{match_result['technology']}</b> | Capacity: <b>{match_result['capacity_mw']} MW</b><br>
            Multi-Vector Score distance (Euclidean): <b>{match_result['distance']:.2f}</b> (closer is more similar)<br>
            Benchmark Composite ISS: <b>{match_result['iss_score']:.1f}/100</b>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Display comparative score differences
    st.markdown("**Vector Score Deltas (Target Site minus Operating Benchmark)**")
    delta_cols = st.columns(7)
    categories = ["SRI", "WRP", "HSI", "GIR", "EVI", "RPE", "LSA"]
    for idx, cat in enumerate(categories):
        d_val = match_result["deltas"].get(cat, 0.0)
        delta_color = "green" if d_val >= 0 else "red"
        sign = "+" if d_val >= 0 else ""
        delta_cols[idx].metric(
            label=f"{cat}",
            value=f"{sign}{d_val:.1f}",
            delta=None
        )
        # Apply CSS styling for colors
        delta_cols[idx].markdown(f"<p style='text-align: center; color: {delta_color}; font-weight: bold;'>{sign}{d_val:.1f}</p>", unsafe_allow_html=True)
