# RenewSense — Renewable Investment Sensitivity Engine

```
 ____                           ____
|  _ \  ___ _ __   _____      _/ ___|  ___ _ __  ___  ___
| |_) |/ _ \ '_ \ / _ \ \ /\ / \___ \ / _ \ '_ \/ __|/ _ \
|  _ <|  __/ | | |  __/\ V  V / ___) |  __/ | | \__ \  __/
|_| \_\\___|_| |_|\___| \_/\_/ |____/ \___|_| |_|___/\___|
  "Where geospatial intelligence meets capital allocation"
```

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Streamlit 1.35](https://img.shields.io/badge/Streamlit-1.35-FF4B4B.svg)](https://streamlit.io/)
[![License MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Production Ready](https://img.shields.io/badge/deployment-Docker-0db7ed.svg)](https://www.docker.com/)

---

## What Is RenewSense?

RenewSense is a multi-vector geospatial intelligence platform designed to synthesize physical terrain data, climate risk signals, grid infrastructure proximity, and resource potentials into a unified **Investment Sensitivity Score (ISS)**. 

Designed for investment committees, infrastructure developers, transition analysts, and researchers, the application carries the weight of a professional due-diligence instrument. It provides transparent scoring profiles, sensitivity checks, dynamic scenario pivots, and automated due-diligence investment memo generation.

The application leverages high-fidelity visualization mapping (Folium) alongside robust risk simulation modules (Monte Carlo) and portfolio matrices to ensure capital allocation models successfully account for critical localized constraints.

---

## The ISS Framework

The composite Investment Sensitivity Score is aggregated from seven independent vector metrics:

| Vector | Analytical Dimension | Source Attribution | Normalized Weight (Balanced) |
| :--- | :--- | :--- | :--- |
| **SRI** | Solar Resource Intensity | Copernicus ERA5 GHI Climatology | 0.143 |
| **WRP** | Wind Resource Potential | DTU Global Wind Atlas (100m) | 0.143 |
| **HSI** | Hydrological Stress Index | WRI Aqueduct 4.0 Water Basin Risk | 0.143 |
| **GIR** | Grid Infrastructure Readiness | OpenStreetMap HV Power Networks | 0.143 |
| **EVI** | Environmental Volatility | NOAA NCEI Extreme Events History | 0.143 |
| **RPE** | Regulatory & Policy | World Bank / IEA IRENA Policies | 0.143 |
| **LSA** | Land & Social Acceptance | ESA WorldCover 10m Classifications | 0.143 |

---

## Quick Start (5 minutes)

### Prerequisites
- Python 3.9+ (3.11+ recommended; used by Docker)
- Pip package manager
- Optional: Docker & Docker-Compose

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/prakashkrish-DataGeek/renewsense-geospatial-engine.git
   cd renewsense-geospatial-engine
   ```

2. **Recommended — use the launcher script** (creates `.venv`, installs dependencies, and runs Streamlit with the correct Python):
   ```bash
   ./run.sh
   ```

3. **Or set up manually:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements.txt
   streamlit run app.py
   ```

4. Open your browser at `http://localhost:8501`.

> **Important:** Always run the app from the project virtual environment (via `./run.sh` or an activated `.venv`). Running `streamlit run app.py` with system Python will fail with missing modules such as `dotenv`, `pydantic`, or `streamlit`.

### Demo Mode (No API Keys Required)

By default, the application runs in a sub-second offline **Demo Mode** leveraging latitude/longitude geo-heuristics. Demo mode is enabled via the checkbox on the **Site Analysis** page (or `DEMO_MODE=true` in `.env`).

For live API mode, create a `.env` file in the project root (see [API Keys Setup Guide](#api-keys-setup-guide) below).

---

## Using the App

### Site Analysis workflow

1. Go to **Site Analysis** in the sidebar.
2. Enter a city or region (e.g. `Berlin, Germany`, `Atacama, Chile`) and click **Resolve Address**.
3. Confirm the **Latitude** and **Longitude** fields update to the geocoded coordinates.
4. Click **RUN INVESTMENT ANALYSIS** to compute the ISS scorecard and map overlays.
5. Change city and repeat steps 2–4 — the ISS score updates with the new coordinates.

Coordinates can also be edited manually or set by clicking the map. Each new location requires clicking **RUN INVESTMENT ANALYSIS** to refresh the score.

### Other views

| Page | Purpose |
| :--- | :--- |
| **Portfolio Comparison** | Compare ISS scores across pinned sites |
| **Scenario Builder** | Adjust vector weights and penalty thresholds |
| **Regional Heat Map** | Country-level ISS choropleth |
| **Reports & Export** | Generate PDF/CSV exports and investment memos |
| **Methodology** | Full ISS framework documentation |

---

## Troubleshooting

| Symptom | Cause | Fix |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'dotenv'` | Streamlit started with system Python instead of `.venv` | Run `./run.sh`, or `source .venv/bin/activate` before `streamlit run app.py` |
| `NameError: name 'List' is not defined` on startup | Outdated code or partial checkout | Pull latest changes; ensure `ui/regional_heatmap.py` imports `List` and `Dict` from `typing` |
| Plotly gauge error (`Invalid property ... 'width'`) | Incompatible Plotly gauge config | Pull latest changes; gauge bar uses `thickness`, not `width` |
| ISS score unchanged after geocoding a new city | Analysis run with stale coordinates | After **Resolve Address**, verify lat/lon fields updated, then click **RUN INVESTMENT ANALYSIS** again |
| Geocoding fails or times out | Nominatim rate limits or network | Enter coordinates manually or click the map |

### IDE setup (Cursor / VS Code)

The repo includes `.vscode/settings.json` pointing at `.venv/bin/python`. Reload the window after creating the virtual environment so the IDE uses the project interpreter when running or debugging.

---

## API Keys Setup Guide

To run in Live Mode, update the `.env` file with credentials for external providers:

1. **Copernicus CDS (ERA5 Solar/Wind)**: Register at the [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/) and configure `CDS_API_KEY`.
2. **WRI Aqueduct**: No explicit key required for public layers, but rate-limited; update `AQUEDUCT_API_KEY` for dedicated enterprise queries.
3. **Global Wind Atlas**: DTU point endpoints are publicly queryable.
4. **Anthropic Claude API**: Register at the [Anthropic Console](https://console.anthropic.com/) to acquire an `ANTHROPIC_API_KEY` for streaming investment memo generation.

---

## Architecture Overview

```
                        +---------------------------------------+
                        |           Streamlit Frontend          |
                        +---------------------------------------+
                                            |
                                            v
                        +---------------------------------------+
                        |               ISS Engine              |
                        +---------------------------------------+
                          /                 |                 \
                         v                  v                  v
                 +---------------+  +---------------+  +---------------+
                 |  Live Fetchers |  |  Normaliser   |  |  Monte Carlo  |
                 +---------------+  +---------------+  +---------------+
```

---

## Configuration Reference

| Environment Variable | Allowed Values | Default | Description |
| :--- | :--- | :--- | :--- |
| `APP_ENV` | `development`, `production` | `development` | Run state configuration |
| `CACHE_BACKEND` | `disk`, `none` | `disk` | Local diskcache database |
| `DEMO_MODE` | `true`, `false` | `true` | Offline simulation mode toggle |
| `CLAUDE_MODEL` | Claude model versions | `claude-3-5-sonnet-20241022` | Active LLM model |

---

## Deployment

### Docker

To spin up the containerized application alongside a Redis caching store:

```bash
docker-compose up --build -d
```

The app will expose port `8501`. Dependencies (including `python-dotenv`) are installed inside the container image at build time.

### Streamlit Cloud
1. Fork this repository.
2. Connect your repository to the [Streamlit Cloud Dashboard](https://share.streamlit.io/).
3. Populate dashboard settings with secrets matching `secrets.toml` variables.
4. Click **Deploy**!

---

## Extending RenewSense

### Adding a Custom Vector
1. Create a fetcher class in `data/fetchers/` inheriting from `BaseFetcher`.
2. Register the piecewise normalisation breakpoints in `config/normalisation.yaml`.
3. Register the fetcher inside `core/iss_engine.py`.
4. Update UI labels to present the new statistics.

---

## Licence
This project is licensed under the MIT License - see the LICENSE file for details.

## Author
**Prakash Krishnamurthy** | [GitHub](https://github.com/prakashkrish-DataGeek)
*Senior Digital & Data Transformation Leader | Fractional Chief AI Officer*
