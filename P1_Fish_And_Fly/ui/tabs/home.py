import time
import streamlit as st


def render_home(stats, mission_start_time: float):

    # =====================================================
    # GLOBAL STYLES
    # =====================================================
    st.markdown(
        """
        <style>

        .hero-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 10px 20px 70px 20px;
        }

        .title {
            font-size: 42px;
            font-weight: 700;
            color: #1E6091;
            margin-bottom: 10px;
        }

        .subtitle {
            max-width: 760px;
            font-size: 16px;
            line-height: 1.65;
            color: #333;
            margin-left: auto;
            margin-right: auto;
        }

        .card {
            padding: 28px;
            border-radius: 20px;
            transition: all 0.25s ease;
            height: 100%;
        }

        .fish-card {
            background: rgba(233, 246, 251, 0.95);
            border: 1px solid #A9D6E5;
        }

        .fly-card {
            background: rgba(255, 243, 230, 0.95);
            border: 1px solid #FFD6A5;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 14px 26px rgba(0,0,0,0.08);
        }

        .metric-box {
            background: white;
            border-radius: 18px;
            padding: 22px;
            box-shadow: 0 10px 22px rgba(0,0,0,0.07);
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 2, 2, 2, 2, 2, 1])
    with col4:
        st.image("ui/assets/ff_logo2.png", width=260)

    # =====================================================
    # HERO SECTION (FIXED CENTERING)
    #<div style="font-size:56px; margin-bottom:12px;">🐟 + 🪰</div>                             # can be added if desired
    # =====================================================
    st.markdown(
        """
        <div class="hero-wrapper">
            <div class="title">
                Fish–Fly Autonomous Cleaning System
            </div>
            <p class="subtitle">
                A cooperative autonomous system where an underwater <b> Fish </b> robot performs
                navigation-driven area cleaning, while a lightweight <b> Fly </b> agent continuously
                monitors mission health, progress, and safety using heartbeat signals.
            </p>
            <br>
            <a href="#" target="_blank">View Documentation</a>
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # FISH & FLY CARDS
    # =====================================================
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="card fish-card">
                <h3>🐟 Fish Machine</h3>
                <p>
                The Fish executes underwater traversal and cleaning using
                spatial coverage logic. Progress is measured by area covered,
                not object detection density.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="card fly-card">
                <h3>🪰 Fly Machine</h3>
                <p>
                The Fly monitors heartbeat timing, communication silence,
                and mission deltas to ensure operational safety without
                interfering with Fish autonomy.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # =====================================================
    # KEY MISSION METRICS
    # =====================================================
    elapsed_time = int(time.time() - mission_start_time)

    m1, m2, m3 = st.columns(3)

    with m1:
        st.markdown(
            f"""
            <div class="metric-box">
                <div style="color:#666;">Mission Phase</div>
                <h2>{stats.mission_phase}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m2:
        st.markdown(
            f"""
            <div class="metric-box">
                <div style="color:#666;">Area Cleaned</div>
                <h2>{stats.coverage_stats["cleaned_pct"]}%</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m3:
        st.markdown(
            f"""
            <div class="metric-box">
                <div style="color:#666;">Elapsed Time</div>
                <h2>{elapsed_time}s</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
