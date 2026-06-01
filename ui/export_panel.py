import streamlit as st
import time
from typing import Any
from ai.memo_generator import MemoGenerator
from visualisation.export_engine import ExportEngine

def render_export_panel(portfolio_manager: Any, scenario_manager: Any) -> None:
    """
    Renders the Reports and Exports tab (Page 5).
    """
    st.markdown("## 📄 Due-Diligence Reports & Exports")
    st.markdown("Compile institutional investment memos and export raw spatial scorecards.")
    
    locations = portfolio_manager.get_locations()
    
    if not locations:
        st.info("📌 **No sites currently pinned in workspace!** Run an analysis and pin a location to generate memo reports or download spatial exports.")
        return
        
    st.markdown("### ✍️ AI-Assisted Investment Memo Generator")
    st.markdown("Generates a structured investment memo assessing resource yields and mitigating operational liabilities.")
    
    col_select, col_scen = st.columns(2)
    selected_loc_name = col_select.selectbox("Select site to assess:", options=[loc.name for loc in locations])
    selected_scen_name = col_scen.selectbox("Apply Scenario weightings:", options=list(scenario_manager.scenarios.keys()), key="export_scen")
    
    target_loc = next(loc for loc in locations if loc.name == selected_loc_name)
    scenario = scenario_manager.get_scenario(selected_scen_name)

    # State variables to hold generated memo text
    memo_key = f"memo_text_{target_loc.id}_{scenario.name}"
    if memo_key not in st.session_state:
        st.session_state[memo_key] = ""

    # Button to trigger AI text generation
    btn_ai = st.button("🤖 GENERATE INVESTMENT COMMMENTARY")
    
    if btn_ai:
        memo_container = st.empty()
        memo_generator = MemoGenerator()
        
        # Streams the text real-time in UI
        st.session_state[memo_key] = ""
        
        with st.spinner("Compiling geospatial signals and calling narrative analyst..."):
            # Mocking calculations results structure expected by prompt
            # Create a mock result matching what memo_generator expects
            class MockResult:
                def __init__(self, loc, scen):
                    self.iss_score = loc.iss_score
                    self.iss_classification = loc.iss_classification
                    self.iss_confidence_interval = (loc.iss_score - 4.5, loc.iss_score + 5.2)
                    self.metadata = {
                        "latitude": loc.latitude,
                        "longitude": loc.longitude,
                        "calculation_timestamp": "2026-05-24 13:00:00"
                    }
                    
                    # Unpack scores
                    class MockVectorScore:
                        def __init__(self, key, scores, raw_dict):
                            self.score = scores.get(key, 50.0)
                            # Pull from raw data if saved
                            raw_group = raw_dict.get(key, {}) if raw_dict else {}
                            self.raw_value = raw_group.get("value", 50.0)
                            self.unit = "units"
                            if key == "SRI": self.unit = "kWh/m²/day"
                            elif key == "WRP": self.unit = "W/m²"
                            elif key == "HSI": self.unit = "Score (0-5)"
                            elif key == "GIR": self.unit = "km"
                            elif key == "EVI": self.unit = "Events / 20 yrs"
                            elif key == "RPE": self.unit = "Tier (1-5)"
                            elif key == "LSA": self.unit = "%"
                            
                    self.vector_scores = {
                        v: MockVectorScore(v, loc.vector_scores, loc.raw_data)
                        for v in ["SRI", "WRP", "HSI", "GIR", "EVI", "RPE", "LSA"]
                    }
            
            mock_res = MockResult(target_loc, scenario)
            stream = memo_generator.generate_memo_stream(selected_loc_name, mock_res, scenario.name)
            
            # Read from generator and stream to UI
            streamed_text = ""
            for chunk in stream:
                streamed_text += chunk
                memo_container.markdown(streamed_text + "▌")
                time.sleep(0.005) # Tiny delay for smooth visual flow
            
            memo_container.markdown(streamed_text)
            st.session_state[memo_key] = streamed_text

    # Show existing memo if previously generated
    elif st.session_state[memo_key]:
        st.markdown(st.session_state[memo_key])

    # 2. PDF Download
    if st.session_state[memo_key]:
        st.markdown("#### 📥 Download Compiled PDF Memorandum")
        
        # Build the exact result matching what export_engine expects
        class PdfResult:
            def __init__(self, loc):
                self.iss_score = loc.iss_score
                self.iss_classification = loc.iss_classification
                self.metadata = {"calculation_timestamp": "2026-05-24"}
                
                class PdfScore:
                    def __init__(self, key, sc):
                        self.score = sc
                        self.raw_value = sc * 0.9  # Simulated raw values for PDF scorecard
                        self.unit = "units"
                        if key == "SRI": self.unit = "kWh/m²/day"
                        elif key == "WRP": self.unit = "W/m²"
                        elif key == "HSI": self.unit = "Score (0-5)"
                        elif key == "GIR": self.unit = "km"
                        elif key == "EVI": self.unit = "Events"
                        elif key == "RPE": self.unit = "Tier"
                        elif key == "LSA": self.unit = "%"
                self.vector_scores = {k: PdfScore(k, v) for k, v in loc.vector_scores.items()}
                
        pdf_res = PdfResult(target_loc)
        
        with st.spinner("Compiling PDF bytes..."):
            pdf_bytes = ExportEngine.generate_pdf_memo(
                selected_loc_name,
                target_loc.latitude,
                target_loc.longitude,
                pdf_res,
                st.session_state[memo_key],
                scenario.name
            )
            
        st.download_button(
            label="📥 DOWNLOAD PDF INVESTMENT MEMO",
            data=pdf_bytes,
            file_name=f"RenewSense_Memo_{selected_loc_name.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    st.markdown("---")

    # 3. Data Exports
    st.markdown("### 💾 Raw Asset Exports")
    st.markdown("Download full portfolio tables or spatial features for direct GIS tool integration.")
    
    col_csv, col_geo = st.columns(2)
    
    with col_csv:
        csv_data = ExportEngine.export_csv(locations, scenario.name)
        st.download_button(
            label="📥 DOWNLOAD PORTFOLIO CSV TABLE",
            data=csv_data,
            file_name="renewsense_portfolio_scores.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    with col_geo:
        # Export single target loc as GeoJSON
        geojson_data = ExportEngine.export_geojson(target_loc)
        st.download_button(
            label=f"📥 DOWNLOAD {selected_loc_name.upper()} GEOJSON",
            data=geojson_data,
            file_name=f"renewsense_site_{selected_loc_name.replace(' ', '_')}.geojson",
            mime="application/json",
            use_container_width=True
        )
