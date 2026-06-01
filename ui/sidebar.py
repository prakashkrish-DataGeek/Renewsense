import streamlit as st
from visualisation.themes import PRIMARY_BLUE, TEXT_SECONDARY

def render_sidebar() -> str:
    """Renders the custom styled sidebar panel with branding and navigation options."""
    st.sidebar.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 25px; margin-top: 10px;">
            <h1 style="color: {PRIMARY_BLUE}; font-family: 'DM Serif Display', Georgia, serif; font-size: 2.2rem; margin-bottom: 0px; padding-bottom: 0px;">RenewSense</h1>
            <p style="color: {TEXT_SECONDARY}; font-size: 0.85rem; font-style: italic; margin-top: 0px; padding-top: 0px;">"Where geospatial intelligence meets capital allocation"</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.sidebar.markdown("### 🗺️ NAVIGATION")
    
    page = st.sidebar.radio(
        label="Select Workspace View:",
        options=[
            "🌍 Site Analysis",
            "📊 Portfolio Comparison",
            "🎛️ Scenario Builder",
            "🗺️ Regional Heat Map",
            "📄 Reports & Export",
            "📚 Methodology"
        ],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    
    # Render Application info
    st.sidebar.markdown("### ⚙️ APP STATUS")
    demo_mode = st.session_state.get("demo_mode", True)
    if demo_mode:
        st.sidebar.warning("⚡ DEMO MODE ACTIVE (Synthetic Data)")
    else:
        st.sidebar.success("🟢 LIVE API MODE ACTIVE")
        
    st.sidebar.markdown(
        """
        <div style="font-size: 0.75rem; color: #8FA3B1; margin-top: 30px; border-top: 1px solid #2C3E50; padding-top: 10px;">
            Author Context: <b>Senior Digital Leader</b><br>
            Repo: <b>renewsense-geospatial-engine</b><br>
            Version: <b>1.0.0 (Production)</b>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    return page
