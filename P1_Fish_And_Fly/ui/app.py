import time
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from ui.config import LOG_PATH, REFRESH_INTERVAL_SEC
from ui.repo.log_repository import LogRepository
from ui.adapters.stats_adapter import StatsAdapter

from ui.tabs.fly import render_fly
from ui.tabs.home import render_home
from ui.tabs.fish import render_fish
from ui.tabs.mission_progress import render_mission_progress2


st.set_page_config(layout="wide")

# mission_start_time should be stored once (e.g., session_state)
if "mission_start_time" not in st.session_state:
    st.session_state.mission_start_time = time.time()

st_autorefresh(
    interval=REFRESH_INTERVAL_SEC * 1000,
    key="auto_refresh"
)


# Taking data from Backend
repo = LogRepository(LOG_PATH)
df = repo.load()

tab_home, tab_mission, tab_fish, tab_fly = st.tabs(["Home", "Mission Progress", "Fish", "Fly"])

# Weaving all data into a single stats object, which is passed to all the tabs separately
stats = StatsAdapter(df)


with tab_home:
    render_home(stats, mission_start_time= st.session_state.mission_start_time)

with tab_mission:
    render_mission_progress2()

with tab_fish:
    render_fish(stats)

with tab_fly:
    render_fly(stats)

