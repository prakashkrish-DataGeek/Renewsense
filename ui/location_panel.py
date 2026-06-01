import streamlit as st
from geopy.geocoders import Nominatim
import logging
from typing import Tuple, Any

logger = logging.getLogger(__name__)

def render_location_panel(scenario_manager: Any) -> Tuple[float, float, int, Any, str, bool]:
    """
    Renders the Left Column input panel for Site Analysis.
    Returns: Tuple[lat, lon, radius, selected_scenario, location_name, run_triggered]
    """
    st.markdown("### 📍 Location Parameters")
    
    # 1. Address Geocoder Lookup
    address_input = st.text_input(
        "Geocode Address (e.g. Rajasthan, India or Atacama, Chile):",
        value="",
        placeholder="Search globally..."
    )
    
    geocode_triggered = st.button("🔍 Resolve Address")
    
    # Session state variables to store resolved lat/lon
    if "resolved_lat" not in st.session_state:
        st.session_state.resolved_lat = 27.0238  # Default Rajasthan lat
    if "resolved_lon" not in st.session_state:
        st.session_state.resolved_lon = 74.2179  # Default Rajasthan lon
    if "resolved_name" not in st.session_state:
        st.session_state.resolved_name = "Rajasthan, India"

    if geocode_triggered and address_input.strip():
        with st.spinner("Resolving coordinates..."):
            try:
                geolocator = Nominatim(user_agent="renewsense_geospatial_engine")
                location = geolocator.geocode(address_input, timeout=5)
                if location:
                    st.session_state.resolved_lat = location.latitude
                    st.session_state.resolved_lon = location.longitude
                    st.session_state.resolved_name = location.address.split(",")[0] + ", " + location.address.split(",")[-1].strip()
                    st.success(f"Resolved: {st.session_state.resolved_name} ({location.latitude:.4f}, {location.longitude:.4f})")
                else:
                    st.error("Address could not be found. Please enter manually.")
            except Exception as e:
                logger.error(f"Geocoding failed: {e}")
                st.warning("Public geocoding service is unavailable. Please enter coordinates manually.")

    # 2. Manual Coordinates Inputs (key= binds widgets to session state so geocode updates stick)
    col_lat, col_lon = st.columns(2)
    lat_val = col_lat.number_input(
        "Latitude (°)",
        min_value=-90.0,
        max_value=90.0,
        format="%.5f",
        key="resolved_lat"
    )
    lon_val = col_lon.number_input(
        "Longitude (°)",
        min_value=-180.0,
        max_value=180.0,
        format="%.5f",
        key="resolved_lon"
    )

    location_name = st.text_input(
        "Location Label:",
        key="resolved_name"
    )

    st.markdown("---")

    # 3. Buffer Radius Slider
    radius_km = st.slider(
        "Analysis Buffer Radius (km):",
        min_value=10,
        max_value=50,
        value=25,
        step=5,
        help="Affects geofencing buffers for OSM transmission lines, water stress zones, and protect corridors."
    )

    # 4. Scenario weight selector
    scenarios_list = list(scenario_manager.scenarios.keys())
    selected_scen_name = st.selectbox(
        "Weight Configuration Scenario:",
        options=scenarios_list,
        index=0,
        help="Selects the weight vectors to combine individual scores into the composite ISS."
    )
    selected_scenario = scenario_manager.get_scenario(selected_scen_name)

    st.markdown("---")
    
    # 5. Core execution trigger
    run_triggered = st.button(
        "🚀 RUN INVESTMENT ANALYSIS",
        use_container_width=True,
        type="primary"
    )
    
    return lat_val, lon_val, radius_km, selected_scenario, location_name, run_triggered
