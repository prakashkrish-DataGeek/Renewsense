import streamlit as st
import os

def render_methodology_panel() -> None:
    """
    Renders the Methodology documentation page (Page 6).
    """
    st.markdown("## 📚 Framework Methodology & Technical Guide")
    st.markdown("Detailed documentation of index formulations, geometric mean aggregations, and risk simulation equations.")
    
    methodology_path = "METHODOLOGY.md"
    
    if os.path.exists(methodology_path):
        try:
            with open(methodology_path, "r") as f:
                md_content = f.read()
            st.markdown(md_content, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Could not load METHODOLOGY.md: {e}")
    else:
        st.warning("METHODOLOGY.md file was not found in the workspace.")
