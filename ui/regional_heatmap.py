import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Any, Dict, List
from core.monte_carlo import MonteCarloEngine

def render_regional_heatmap(scenario_manager: Any) -> None:
    """
    Renders the Regional Heatmap choropleth page (Page 4).
    """
    st.markdown("## 🗺️ Global Regional Heat Map")
    st.markdown("Assess national and sub-national composite investment sensitivity metrics globally.")
    
    # 1. Filter layout
    col_scen, col_continent = st.columns(2)
    scenarios_list = list(scenario_manager.scenarios.keys())
    selected_scen_name = col_scen.selectbox("Heatmap Scenario Weights:", options=scenarios_list, key="heatmap_scen")
    selected_scenario = scenario_manager.get_scenario(selected_scen_name)
    
    continent_filter = col_continent.selectbox("Filter Continent:", options=["Global", "Asia", "Europe", "South America", "North America", "Africa", "Oceania"])
    
    st.markdown("---")

    # 2. Database of country scores
    # We pre-compute realistic vector scores for 30 focus nations to feed our choropleth
    countries_data = _get_heatmap_countries_db()
    
    # Calculate ISS for all countries under current scenario
    records = []
    for c in countries_data:
        # Check continent filter
        if continent_filter != "Global" and c["continent"] != continent_filter:
            continue
            
        iss = MonteCarloEngine.calculate_iss_geometric(
            c["vector_scores"],
            selected_scenario.weights,
            selected_scenario.penalise_threshold,
            selected_scenario.penalise_cap or 55.0
        )
        
        records.append({
            "ISO": c["iso"],
            "Country": c["name"],
            "Continent": c["continent"],
            "Income Group": c["income_group"],
            "ISS": round(iss, 1),
            "IRENA Member": c["irena_member"]
        })
        
    df_countries = pd.DataFrame(records)
    
    if df_countries.empty:
        st.warning("No countries match the selected continent filter.")
        return
        
    # 3. Interactive Plotly Choropleth Map
    st.markdown("### 🌍 Composite ISS Choropleth View")
    fig_choro = px.choropleth(
        df_countries,
        locations="ISO",
        color="ISS",
        hover_name="Country",
        projection="natural earth",
        color_continuous_scale="Viridis",
        range_color=[30, 95],
        labels={"ISS": "Composite ISS"}
    )
    fig_choro.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        geo=dict(
            bgcolor='rgba(0,0,0,0)',
            showland=True,
            landcolor="#1A2332",
            showocean=True,
            oceancolor="#0E1117",
            showlakes=True,
            lakecolor="#0E1117",
            showrivers=False
        ),
        margin=dict(l=0, r=0, t=10, b=0),
        height=400
    )
    st.plotly_chart(fig_choro, use_container_width=True)
    
    st.markdown("---")

    # 4. Ranked Country Leaderboards
    st.markdown("### 🏆 Country Investment Suitability Standings")
    
    col_table, col_insights = st.columns([3, 2])
    
    with col_table:
        st.markdown(f"**Top Countries ranked by Composite ISS ({selected_scen_name})**")
        df_ranked = df_countries.sort_values(by="ISS", ascending=False).reset_index(drop=True)
        st.dataframe(df_ranked, use_container_width=True, hide_index=True)
        
    with col_insights:
        st.markdown("#### 💡 Emerging Market Insights")
        # Exclude high-income (World Bank definition) and show highest scoring emerging nations
        df_emerging = df_ranked[df_ranked["Income Group"] != "High Income"].head(5)
        
        st.markdown("Top Emerging Transition Suitability Targets:")
        for idx, row in df_emerging.iterrows():
            st.markdown(
                f"""
                <div style="background-color: #1A2332; border: 1px solid #2C3E50; padding: 10px; border-radius: 6px; margin-bottom: 8px;">
                    <b>{row['Country']}</b> ({row['Continent']})<br>
                    Composite ISS: <font color='#17A589'><b>{row['ISS']:.1f}</b></font> | Group: <b>{row['Income Group']}</b>
                </div>
                """,
                unsafe_allow_html=True
            )

def _get_heatmap_countries_db() -> List[Dict]:
    """Returns structured, realistic multi-vector scores for 30 focus nations globally."""
    # Custom baseline vector scores
    return [
        {
            "name": "Chile", "iso": "CHL", "continent": "South America", "income_group": "Upper Middle Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 92.0, "WRP": 70.0, "HSI": 25.0, "GIR": 75.0, "EVI": 70.0, "RPE": 88.0, "LSA": 85.0}
        },
        {
            "name": "Germany", "iso": "DEU", "continent": "Europe", "income_group": "High Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 35.0, "WRP": 85.0, "HSI": 85.0, "GIR": 92.0, "EVI": 95.0, "RPE": 94.0, "LSA": 40.0}
        },
        {
            "name": "India", "iso": "IND", "continent": "Asia", "income_group": "Lower Middle Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 84.0, "WRP": 55.0, "HSI": 20.0, "GIR": 82.0, "EVI": 65.0, "RPE": 78.0, "LSA": 60.0}
        },
        {
            "name": "Egypt", "iso": "EGY", "continent": "Africa", "income_group": "Lower Middle Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 88.0, "WRP": 74.0, "HSI": 15.0, "GIR": 60.0, "EVI": 88.0, "RPE": 65.0, "LSA": 80.0}
        },
        {
            "name": "Morocco", "iso": "MAR", "continent": "Africa", "income_group": "Lower Middle Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 90.0, "WRP": 75.0, "HSI": 30.0, "GIR": 68.0, "EVI": 85.0, "RPE": 82.0, "LSA": 75.0}
        },
        {
            "name": "United States", "iso": "USA", "continent": "North America", "income_group": "High Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 75.0, "WRP": 78.0, "HSI": 50.0, "GIR": 85.0, "EVI": 70.0, "RPE": 85.0, "LSA": 80.0}
        },
        {
            "name": "Australia", "iso": "AUS", "continent": "Oceania", "income_group": "High Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 94.0, "WRP": 72.0, "HSI": 35.0, "GIR": 70.0, "EVI": 80.0, "RPE": 82.0, "LSA": 92.0}
        },
        {
            "name": "United Arab Emirates", "iso": "ARE", "continent": "Asia", "income_group": "High Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 92.0, "WRP": 30.0, "HSI": 10.0, "GIR": 88.0, "EVI": 95.0, "RPE": 84.0, "LSA": 70.0}
        },
        {
            "name": "Kenya", "iso": "KEN", "continent": "Africa", "income_group": "Lower Middle Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 88.0, "WRP": 80.0, "HSI": 55.0, "GIR": 45.0, "EVI": 75.0, "RPE": 72.0, "LSA": 68.0}
        },
        {
            "name": "Spain", "iso": "ESP", "continent": "Europe", "income_group": "High Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 68.0, "WRP": 62.0, "HSI": 40.0, "GIR": 84.0, "EVI": 88.0, "RPE": 86.0, "LSA": 65.0}
        },
        {
            "name": "South Africa", "iso": "ZAF", "continent": "Africa", "income_group": "Upper Middle Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 86.0, "WRP": 68.0, "HSI": 30.0, "GIR": 75.0, "EVI": 85.0, "RPE": 70.0, "LSA": 78.0}
        },
        {
            "name": "China", "iso": "CHN", "continent": "Asia", "income_group": "Upper Middle Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 70.0, "WRP": 80.0, "HSI": 45.0, "GIR": 90.0, "EVI": 72.0, "RPE": 80.0, "LSA": 58.0}
        },
        {
            "name": "Brazil", "iso": "BRA", "continent": "South America", "income_group": "Upper Middle Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 75.0, "WRP": 74.0, "HSI": 80.0, "GIR": 68.0, "EVI": 85.0, "RPE": 75.0, "LSA": 70.0}
        },
        {
            "name": "Mexico", "iso": "MEX", "continent": "North America", "income_group": "Upper Middle Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 84.0, "WRP": 60.0, "HSI": 35.0, "GIR": 72.0, "EVI": 75.0, "RPE": 68.0, "LSA": 74.0}
        },
        {
            "name": "Denmark", "iso": "DNK", "continent": "Europe", "income_group": "High Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 25.0, "WRP": 95.0, "HSI": 90.0, "GIR": 90.0, "EVI": 98.0, "RPE": 96.0, "LSA": 50.0}
        },
        {
            "name": "United Kingdom", "iso": "GBR", "continent": "Europe", "income_group": "High Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 30.0, "WRP": 90.0, "HSI": 85.0, "GIR": 88.0, "EVI": 92.0, "RPE": 90.0, "LSA": 45.0}
        },
        {
            "name": "Saudi Arabia", "iso": "SAU", "continent": "Asia", "income_group": "High Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 90.0, "WRP": 40.0, "HSI": 12.0, "GIR": 80.0, "EVI": 95.0, "RPE": 74.0, "LSA": 75.0}
        },
        {
            "name": "Vietnam", "iso": "VNM", "continent": "Asia", "income_group": "Lower Middle Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 68.0, "WRP": 70.0, "HSI": 70.0, "GIR": 60.0, "EVI": 60.0, "RPE": 70.0, "LSA": 50.0}
        },
        {
            "name": "Turkey", "iso": "TUR", "continent": "Asia", "income_group": "Upper Middle Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 65.0, "WRP": 64.0, "HSI": 40.0, "GIR": 80.0, "EVI": 78.0, "RPE": 72.0, "LSA": 62.0}
        },
        {
            "name": "Japan", "iso": "JPN", "continent": "Asia", "income_group": "High Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 48.0, "WRP": 65.0, "HSI": 80.0, "GIR": 92.0, "EVI": 45.0, "RPE": 88.0, "LSA": 32.0}
        },
        {
            "name": "Jordan", "iso": "JOR", "continent": "Asia", "income_group": "Upper Middle Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 88.0, "WRP": 50.0, "HSI": 15.0, "GIR": 75.0, "EVI": 90.0, "RPE": 78.0, "LSA": 78.0}
        },
        {
            "name": "Morocco", "iso": "MAR", "continent": "Africa", "income_group": "Lower Middle Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 86.0, "WRP": 74.0, "HSI": 32.0, "GIR": 72.0, "EVI": 88.0, "RPE": 80.0, "LSA": 74.0}
        },
        {
            "name": "Oman", "iso": "OMN", "continent": "Asia", "income_group": "High Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 90.0, "WRP": 55.0, "HSI": 18.0, "GIR": 70.0, "EVI": 92.0, "RPE": 76.0, "LSA": 80.0}
        },
        {
            "name": "Kazakhstan", "iso": "KAZ", "continent": "Asia", "income_group": "Upper Middle Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 50.0, "WRP": 82.0, "HSI": 40.0, "GIR": 50.0, "EVI": 85.0, "RPE": 68.0, "LSA": 85.0}
        },
        {
            "name": "Argentina", "iso": "ARG", "continent": "South America", "income_group": "Upper Middle Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 68.0, "WRP": 88.0, "HSI": 45.0, "GIR": 60.0, "EVI": 82.0, "RPE": 65.0, "LSA": 80.0}
        },
        {
            "name": "Colombia", "iso": "COL", "continent": "South America", "income_group": "Upper Middle Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 65.0, "WRP": 76.0, "HSI": 85.0, "GIR": 65.0, "EVI": 80.0, "RPE": 72.0, "LSA": 60.0}
        },
        {
            "name": "Canada", "iso": "CAN", "continent": "North America", "income_group": "High Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 38.0, "WRP": 78.0, "HSI": 90.0, "GIR": 72.0, "EVI": 88.0, "RPE": 84.0, "LSA": 88.0}
        },
        {
            "name": "New Zealand", "iso": "NZL", "continent": "Oceania", "income_group": "High Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 42.0, "WRP": 88.0, "HSI": 92.0, "GIR": 78.0, "EVI": 78.0, "RPE": 88.0, "LSA": 75.0}
        },
        {
            "name": "India", "iso": "IND", "continent": "Asia", "income_group": "Lower Middle Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 84.0, "WRP": 55.0, "HSI": 22.0, "GIR": 80.0, "EVI": 65.0, "RPE": 78.0, "LSA": 62.0}
        },
        {
            "name": "Italy", "iso": "ITA", "continent": "Europe", "income_group": "High Income", "irena_member": "Yes",
            "vector_scores": {"SRI": 56.0, "WRP": 54.0, "HSI": 45.0, "GIR": 86.0, "EVI": 82.0, "RPE": 82.0, "LSA": 58.0}
        }
    ]
