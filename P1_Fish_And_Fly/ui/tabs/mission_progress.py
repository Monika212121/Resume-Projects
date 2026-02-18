import os
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from ui.grid.coverage_grid import CellState
from src.common.logging import logger

'''
COLOR_MAP = {
    CellState.POLLUTED: "#D35400",             # dark orange
    CellState.SURFACE_TRAVERSED: "#F5B041",    # light orange
    CellState.UNDERWATER_TRAVERSED: "#85C1E9", # light blue
    CellState.CLEANED: "#154360",               # dark blue
}
'''

COLOR_MAP = {
    CellState.POLLUTED: "#F5B041",             # light orange
    CellState.SURFACE_TRAVERSED: "#85C1E9",    # light blue
    CellState.CLEANED: "#154360",               # dark blue
}


def render_mission_progress(stats):
    st.markdown("## 🗺️ Mission Progress")

    #grid_obj = stats.coverage_grid_obj
    #stats_dict = grid_obj.coverage_stats()

    coverage_grid = st.session_state.coverage_grid
    stats_dict = coverage_grid.coverage_stats()

    col1, col2, col3 = st.columns(3)
    col1.metric("Area Visited (%)", stats_dict["progress_pct"])
    col2.metric("Area Cleaned (%)", stats_dict["cleaned_pct"])
    col3.metric("Highly Polluted (%)", stats_dict["remaining_polluted_pct"])

    fig, ax = plt.subplots(figsize=(3, 3))

    #grid = grid_obj.grid
    grid = coverage_grid.grid
    logger.info(f"render_mission_progress(): grid value: {grid}")

    color_idx = np.vectorize(lambda x: list(CellState).index(CellState(x)))(grid)
    cmap = plt.matplotlib.colors.ListedColormap(COLOR_MAP.values())

    ax.imshow(color_idx, cmap=cmap)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Top-down Area Coverage Map")

    st.pyplot(fig)


def render_mission_progress2():
    st.markdown("## 🗺️ Mission Progress")

    path = "artifacts/logs/coverage_grid.npy"
    if not os.path.exists(path):
        st.info("Mission not started yet")
        return
    
    grid = np.load(path)
    st.write(grid.shape)
    logger.info(f"render_mission_progress(): grid value: {grid}")

    '''
    col1, col2, col3 = st.columns(3)
    col1.metric("Area Visited (%)", stats_dict["progress_pct"])
    col2.metric("Area Cleaned (%)", stats_dict["cleaned_pct"])
    col3.metric("Highly Polluted (%)", stats_dict["remaining_polluted_pct"])
    '''

    fig, ax = plt.subplots(figsize=(3, 3))

    color_idx = np.vectorize(lambda x: list(CellState).index(CellState(x)))(grid)
    cmap = plt.matplotlib.colors.ListedColormap(COLOR_MAP.values())

    ax.imshow(color_idx, cmap=cmap)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Top-down Area Coverage Map")

    st.pyplot(fig)

