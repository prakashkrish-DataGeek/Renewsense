import folium
from typing import Dict, Any, List
from visualisation.themes import PRIMARY_BLUE, ACCENT_TEAL, WARNING_AMBER, RISK_RED, SUCCESS_GREEN, OPTIMAL_YELLOW

class MapRenderer:
    """Renders highly interactive, layered Folium maps overlays representing the 7 analytical vectors."""

    @staticmethod
    def render_site_map(
        lat: float,
        lon: float,
        radius_km: int,
        scores: Dict[str, float],
        sub_indicators: Dict[str, Dict[str, float]],
        basemap_style: str = "CartoDB Dark Matter",
        show_layers: List[str] = None
    ) -> folium.Map:
        """
        Creates a custom layered Folium map centered on target coordinates, with circular overlays representing GHI,
        wind contours, HV power networks, water stress, protected zones, and developable land buffers.
        """
        if show_layers is None:
            show_layers = ["Solar GHI", "Wind Resource", "Grid Lines", "Water Stress", "Protected Areas"]
            
        # Determine basemap
        tiles = "cartodb dark matter"
        attr = "CartoDB"
        if basemap_style == "Satellite (Esri)":
            tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            attr = "Esri Satellite"
        elif basemap_style == "Terrain (Stamen)":
            tiles = "https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{y}/{x}.png"
            attr = "Stamen Terrain"
            
        # Initialize map
        m = folium.Map(location=[lat, lon], zoom_start=11, tiles=tiles, attr=attr)
        
        # 1. Main Coordinate Marker
        popup_html = f"""
        <div style="font-family: 'Source Sans Pro', sans-serif; background-color: #1A2332; color: #E8EDF2; padding: 10px; border-radius: 5px; min-width: 150px;">
            <b style="color: #1B6CA8; font-size: 1.1rem;">Analysis Center</b><br>
            Coordinate: <b>{lat:.4f}, {lon:.4f}</b><br>
            Radius Buffer: <b>{radius_km} km</b><br>
        </div>
        """
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)
        
        # 2. Draw Analysis Radius Circle Buffer
        folium.Circle(
            location=[lat, lon],
            radius=radius_km * 1000,
            color=PRIMARY_BLUE,
            weight=1.5,
            fill=True,
            fill_color=f"{PRIMARY_BLUE}1A",  # Very light blue fill
            tooltip=f"Analysis Radius: {radius_km}km"
        ).add_to(m)
        
        # 3. Add Layers based on selections
        # We simulate high-fidelity spatial overlays relative to coordinate to keep renders light and lightning fast.
        
        # Layer A: Solar GHI Heat Bubble
        if "Solar GHI" in show_layers and "SRI" in scores:
            score_sri = scores["SRI"]
            color_sri = RISK_RED if score_sri < 50 else (WARNING_AMBER if score_sri < 70 else SUCCESS_GREEN)
            folium.Circle(
                location=[lat + 0.02, lon - 0.02],
                radius=max(radius_km * 400, 3000),
                color=color_sri,
                weight=1,
                fill=True,
                fill_color=color_sri,
                fill_opacity=0.25,
                tooltip=f"Solar Irradiance Zone: SRI Score {score_sri:.0f}"
            ).add_to(m)
            
        # Layer B: Wind Contours (Dashed Rings at incremental radius)
        if "Wind Resource" in show_layers and "WRP" in scores:
            score_wrp = scores["WRP"]
            color_wrp = RISK_RED if score_wrp < 50 else (OPTIMAL_YELLOW if score_wrp < 75 else ACCENT_TEAL)
            folium.Circle(
                location=[lat - 0.03, lon + 0.03],
                radius=max(radius_km * 600, 5000),
                color=color_wrp,
                weight=1.5,
                dash_array="5, 5",
                fill=False,
                tooltip=f"Wind Resource Zone: WRP Score {score_wrp:.0f}"
            ).add_to(m)
            
        # Layer C: Grid lines (Simulated HV Connection Corridor)
        if "Grid Lines" in show_layers and "GIR" in scores:
            dist_gir = sub_indicators.get("GIR", {}).get("distance_to_nearest_220kv_transmission_km", 25.0)
            # Create a transmission line path heading north-east
            path = [
                [lat, lon],
                [lat + (dist_gir * 0.005), lon + (dist_gir * 0.007)],
                [lat + (dist_gir * 0.006), lon + (dist_gir * 0.012)]
            ]
            folium.PolyLine(
                locations=path,
                color="#E74C3C",  # Red represents high-voltage
                weight=3,
                opacity=0.8,
                tooltip=f"Simulated HV Connection (Nearest: {dist_gir:.1f}km)"
            ).add_to(m)
            
            # Substation Marker
            sub_popup = f"""
            <div style="font-family: sans-serif; background-color: #1A2332; color: #E8EDF2; padding: 5px;">
                <b>220kV Substation Node</b><br>
                Distance: <b>{dist_gir:.1f} km</b><br>
                Grid Stability: <b>High</b>
            </div>
            """
            folium.Marker(
                location=path[-1],
                popup=folium.Popup(sub_popup, max_width=250),
                icon=folium.Icon(color="red", icon="flash")
            ).add_to(m)

        # Layer D: Water Stress grid boundary
        if "Water Stress" in show_layers and "HSI" in scores:
            score_hsi = scores["HSI"]
            color_hsi = RISK_RED if score_hsi < 35 else (WARNING_AMBER if score_hsi < 65 else SUCCESS_GREEN)
            # Overlay a grid box showing water basin boundaries
            box = [
                [lat - 0.08, lon - 0.08],
                [lat - 0.08, lon + 0.08],
                [lat + 0.08, lon + 0.08],
                [lat + 0.08, lon - 0.08],
                [lat - 0.08, lon - 0.08]
            ]
            folium.PolyLine(
                locations=box,
                color=color_hsi,
                weight=2,
                opacity=0.6,
                fill=True,
                fill_color=color_hsi,
                fill_opacity=0.1,
                tooltip=f"Hydrological Basin: HSI Score {score_hsi:.0f}"
            ).add_to(m)
            
        # Layer E: Protected areas green hatch overlay
        if "Protected Areas" in show_layers:
            # Drawing a small nature reserve polygon to the south-west of coordinate
            reserve = [
                [lat - 0.04, lon - 0.05],
                [lat - 0.07, lon - 0.02],
                [lat - 0.09, lon - 0.06],
                [lat - 0.04, lon - 0.05]
            ]
            folium.Polygon(
                locations=reserve,
                color=SUCCESS_GREEN,
                weight=1,
                fill=True,
                fill_color=SUCCESS_GREEN,
                fill_opacity=0.25,
                tooltip="Protected Reserve (Exclusion Corridor)"
            ).add_to(m)

        return m
