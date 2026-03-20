import time
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from ui.repo.object_repo import load_objects
from ui.repo.telemetry_repo import load_telemetry

from ui.tabs.home import render_home
from ui.tabs.mission_intelligence import render_mission_intelligence
from ui.tabs.waste_analytics import render_waste
from ui.tabs.ai_decisions import render_ai
from ui.tabs.fish_health import render_health

from src.common.config.configuration import ConfigurationManager


# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(layout="wide")
st_autorefresh(interval=2000, key="auto_refresh")

# -------------------------
# UI COMPACT STYLE (NO SCROLL)
# -------------------------
st.markdown("""
<style>

/* Remove top padding */
.block-container {
    padding-top: 0.2rem !important;
    padding-bottom: 0rem !important;
}

/* Force everything inside screen */
html, body, [data-testid="stAppViewContainer"] {
    height: 100vh;
    overflow: hidden;
}

/* Prevent scroll */
section.main > div {
    height: 100vh;
    overflow: hidden;
}

/* Compact charts */
canvas {
    max-height: 240px !important;
}

/* Smaller fonts for smaller screens */
@media (max-width: 1200px) {
    h1, h2, h3 {
        font-size: 15px !important;
    }
    p, div {
        font-size: 12px !important;
    }
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# TIMER
# -------------------------
if "mission_start_time" not in st.session_state:
    st.session_state.mission_start_time = time.time()


# -------------------------
# LOAD DATA
# -------------------------
try:
    fly_cfg_manager = ConfigurationManager("fly")
    log_file_paths = fly_cfg_manager.get_log_file_paths()

    objects_df = load_objects(log_file_paths.mission_object_log)
    telemetry_df = load_telemetry(log_file_paths.mission_telemetry_log)
    if objects_df is None or telemetry_df is None:
        st.stop()

except Exception as e:
    st.error(f"Data loading failed: {e}")
    st.stop()

# -------------------------
# HEADER METRICS
# -------------------------
try:
    latest = telemetry_df.iloc[-1]

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

    col1.metric("Elapsed Time", int(time.time() - st.session_state.mission_start_time))
    col4.metric("Mission Phase", latest.get("mission_phase", "NA"))
    col7.metric("Fish Machine State", latest.get("fish_state", "NA"))

except Exception as e:
    st.error(f"Header render failed: {e}")


# -------------------------
# TABS
# -------------------------
tabs = st.tabs([
    "Home",
    "Mission Intelligence",
    "Waste Analytics",
    "AI Decision Analysis",
    "Fish System Health"
])

with tabs[0]:
    render_home()

with tabs[1]:
    render_mission_intelligence(telemetry_df)

with tabs[2]:
    render_waste(objects_df)

with tabs[3]:
    render_ai(objects_df)

with tabs[4]:
    render_health(telemetry_df)
