# ── RenewSense Theme Constants ──────────────────────────────────────────────
# Establishes primary palettes, score ranges, and custom CSS injections for Streamlit

# HEX Color Codes
PRIMARY_BLUE = "#1B6CA8"      # Deep institutional blue
ACCENT_TEAL = "#17A589"       # Positive signals, high scores
WARNING_AMBER = "#E67E22"     # Moderate risk, medium scores
RISK_RED = "#C0392B"          # High risk, low scores
BACKGROUND_DARK = "#0E1117"   # Primary background
CARD_BACKGROUND = "#1A2332"   # Panel background
BORDER_SUBTLE = "#2C3E50"     # Card borders, dividers
TEXT_PRIMARY = "#E8EDF2"      # Primary text
TEXT_SECONDARY = "#8FA3B1"    # Metadata, labels, captions
SUCCESS_GREEN = "#27AE60"
OPTIMAL_YELLOW = "#F1C40F"

# ISS Score Band Colors
SCORE_BANDS = [
    {"range": (0.0, 30.0), "color": RISK_RED, "label": "High Sensitivity / Elevated Risk"},
    {"range": (30.1, 50.0), "color": WARNING_AMBER, "label": "Moderate-High Sensitivity"},
    {"range": (50.1, 70.0), "color": OPTIMAL_YELLOW, "label": "Moderate Sensitivity"},
    {"range": (70.1, 85.0), "color": SUCCESS_GREEN, "label": "Low-Moderate Sensitivity / Favourable"},
    {"range": (85.1, 100.0), "color": PRIMARY_BLUE, "label": "Low Sensitivity / Prime Investment Grade"}
]

def get_color_for_score(score: float) -> str:
    """Helper to retrieve the correct hex code for a score."""
    for band in SCORE_BANDS:
        r = band["range"]
        if r[0] <= score <= r[1]:
            return band["color"]
    return PRIMARY_BLUE  # Default fallback

# Custom CSS injection for beautiful Streamlit typography and containers
CUSTOM_CSS = """
<style>
    /* Main Background & Card Styling */
    .stApp {
        background-color: #0E1117;
        color: #E8EDF2;
    }
    
    div[data-testid="stSidebar"] {
        background-color: #101520 !important;
        border-right: 1px solid #2C3E50;
    }
    
    /* Custom Card container */
    .renewsense-card {
        background-color: #1A2332;
        border: 1px solid #2C3E50;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
    }
    
    .renewsense-header {
        font-family: 'Playfair Display', 'DM Serif Display', Georgia, serif;
        color: #1B6CA8;
        font-weight: 700;
        margin-bottom: 5px;
    }
    
    /* Horizontal score bar styles */
    .score-bar-label {
        font-size: 0.9rem;
        font-weight: 600;
        color: #8FA3B1;
        margin-bottom: 2px;
    }
    
    .score-bar-container {
        background-color: #2C3E50;
        border-radius: 4px;
        height: 12px;
        width: 100%;
        margin-bottom: 10px;
        overflow: hidden;
    }
    
    .score-bar-fill {
        height: 100%;
        border-radius: 4px;
    }
    
    /* Giant Score display */
    .giant-score-display {
        font-size: 3.2rem;
        font-weight: 900;
        font-family: 'JetBrains Mono', monospace;
        margin-top: 5px;
        margin-bottom: 0px;
    }
</style>
"""
