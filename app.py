import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    sys.stderr.write(
        "\nModuleNotFoundError: No module named 'dotenv'\n\n"
        "This Python environment is missing project dependencies.\n"
        "Fix (recommended):\n\n"
        "  cd \"{}\"\n"
        "  ./run.sh\n\n"
        "Or manually:\n\n"
        "  python3 -m venv .venv\n"
        "  source .venv/bin/activate\n"
        "  pip install -r requirements.txt\n"
        "  streamlit run app.py\n\n"
        "Current interpreter: {}\n".format(
            Path(__file__).resolve().parent,
            sys.executable,
        )
    )
    sys.exit(1)

import streamlit as st
import os

# Set page configurations first (must be the first Streamlit command)
st.set_page_config(
    page_title="RenewSense — Renewable Investment Sensitivity Engine",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import custom panels and modules
from core.iss_engine import ISSEngine
from core.scenario_manager import ScenarioManager
from core.portfolio import PortfolioManager, PortfolioLocation
from core.monte_carlo import MonteCarloEngine

from ui.sidebar import render_sidebar
from ui.location_panel import render_location_panel
from ui.vector_panel import render_vector_panel
from ui.portfolio_panel import render_portfolio_panel
from ui.scenario_panel import render_scenario_panel
from ui.regional_heatmap import render_regional_heatmap
from ui.methodology_panel import render_methodology_panel
from ui.export_panel import render_export_panel

from visualisation.themes import CUSTOM_CSS
from visualisation.map_renderer import MapRenderer
from visualisation.chart_builder import ChartBuilder
from streamlit_folium import st_folium

# Inject Custom Branding Styles
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ── SESSION STATE INITIALIZATION ─────────────────────────────────────────────
if "portfolio_manager" not in st.session_state:
    st.session_state.portfolio_manager = PortfolioManager()
if "scenario_manager" not in st.session_state:
    st.session_state.scenario_manager = ScenarioManager()
if "iss_engine" not in st.session_state:
    st.session_state.iss_engine = ISSEngine()
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "demo_mode" not in st.session_state:
    # Read default from env, fallback to True (safe for offline run)
    env_demo = os.getenv("DEMO_MODE", "true").lower() == "true"
    st.session_state.demo_mode = env_demo

portfolio_manager = st.session_state.portfolio_manager
scenario_manager = st.session_state.scenario_manager
iss_engine = st.session_state.iss_engine

# ── SIDEBAR RENDER (Branding + Nav Selection) ────────────────────────────────
selected_page = render_sidebar()

# ── PAGE ROUTER ──────────────────────────────────────────────────────────────

if selected_page == "🌍 Site Analysis":
    st.title("🌍 Renewable Site Feasibility Screening")
    st.markdown("Assess physical resource qualities, hydrological stress, environmental vulnerabilities, and grid proximity for any global coordinate.")
    
    # Checkbox in UI header to toggle live mode
    st.session_state.demo_mode = st.checkbox(
        "Run in offline Demo Mode (No API keys required, sub-second loads)",
        value=st.session_state.demo_mode,
        key="demo_mode_checkbox"
    )
    
    # Define Layout Columns
    col_input, col_map, col_score = st.columns([0.30, 0.45, 0.25])
    
    with col_input:
        # Render left-hand inputs
        lat, lon, radius, scenario, loc_name, run_triggered = render_location_panel(scenario_manager)
        
    with col_map:
        st.markdown("### 🗺️ Geospatial Layer Overlay")
        
        # Overlay options checklist
        show_layers = st.multiselect(
            "Layer Overlays Active:",
            options=["Solar GHI", "Wind Resource", "Grid Lines", "Water Stress", "Protected Areas"],
            default=["Solar GHI", "Wind Resource", "Grid Lines", "Water Stress", "Protected Areas"]
        )
        
        basemap = st.selectbox(
            "Select Basemap Layer:",
            options=["CartoDB Dark Matter", "Satellite (Esri)", "Terrain (Stamen)"]
        )
        
        # Build initial map or map using active scores
        active_scores = {}
        active_subs = {}
        if st.session_state.current_result:
            res = st.session_state.current_result
            active_scores = {v: res.vector_scores[v].score for v in res.vector_scores}
            active_subs = {v: res.vector_scores[v].sub_indicators for v in res.vector_scores}
            
        map_object = MapRenderer.render_site_map(
            lat, lon, radius, active_scores, active_subs, basemap, show_layers
        )
        
        # Render map and catch click coordinate updates!
        map_data = st_folium(map_object, width=650, height=450, returned_objects=["last_clicked"])
        
        # Interactive click coordinates syncing
        if map_data and map_data.get("last_clicked"):
            clicked = map_data["last_clicked"]
            clicked_lat = round(clicked["lat"], 5)
            clicked_lon = round(clicked["lng"], 5)
            
            if clicked_lat != st.session_state.resolved_lat or clicked_lon != st.session_state.resolved_lon:
                st.session_state.resolved_lat = clicked_lat
                st.session_state.resolved_lon = clicked_lon
                st.session_state.resolved_name = f"Map Pin ({clicked_lat:.2f}, {clicked_lon:.2f})"
                st.info(f"📍 Coordinates synced from map click: {clicked_lat}, {clicked_lon}")
                st.rerun()

    # Trigger calculation pipeline
    if run_triggered:
        with st.spinner("Executing parallel data fetching and simulation engines..."):
            try:
                result = iss_engine.calculate(
                    latitude=lat,
                    longitude=lon,
                    radius_km=radius,
                    scenario=scenario,
                    use_cache=True,
                    demo_mode=st.session_state.demo_mode
                )
                st.session_state.current_result = result
            except Exception as e:
                st.error(f"ISS pipeline run failed: {e}. Check network credentials or run in offline Demo Mode.")
                logger.error(f"ISS calculation run failed: {e}")

    with col_score:
        if st.session_state.current_result:
            render_vector_panel(
                st.session_state.current_result,
                loc_name,
                lat,
                lon,
                radius,
                portfolio_manager
            )
        else:
            # Welcome box if no calculations run yet
            st.markdown("### 🏆 ISS scorecard")
            st.info("👈 Enter coordinate details or click on address resolvers, and click **RUN INVESTMENT ANALYSIS** to execute the sensitivity engine.")

elif selected_page == "📊 Portfolio Comparison":
    render_portfolio_panel(portfolio_manager, scenario_manager)

elif selected_page == "🎛️ Scenario Builder":
    render_scenario_panel(scenario_manager, portfolio_manager)

elif selected_page == "🗺️ Regional Heat Map":
    render_regional_heatmap(scenario_manager)

elif selected_page == "📄 Reports & Export":
    render_export_panel(portfolio_manager, scenario_manager)

elif selected_page == "📚 Methodology":
    render_methodology_panel()
