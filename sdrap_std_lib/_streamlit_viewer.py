# _streamlit_viewer.py

import streamlit as st
import plotly.graph_objects as go
import json
import os
import time

PLOT_FILE = "live_plot.json"
REFRESH_INTERVAL_MS = 1000

st.set_page_config(page_title="Live Plotly Viewer", layout="wide")
st.title("Live Plotly Graph Viewer")
st.markdown(
    "Use `pio.renderers.default = 'streamlit'` in your Python session to send plots here."
)

plot_placeholder = st.empty()
last_mod_time = None

while True:
    try:
        if not os.path.exists(PLOT_FILE):
            with plot_placeholder.container():
                st.warning("Waiting for plot data from your Python session...")
            last_mod_time = None
        else:
            current_mod_time = os.path.getmtime(PLOT_FILE)

            if current_mod_time != last_mod_time:
                with open(PLOT_FILE, "r") as f:
                    fig_json = f.read()

                if fig_json.strip():
                    fig_dict = json.loads(fig_json)
                    fig = go.Figure(fig_dict)

                    with plot_placeholder.container():
                        st.plotly_chart(fig, use_container_width=True)

                    last_mod_time = current_mod_time
                else:
                    with plot_placeholder.container():
                        st.warning("Plot file is empty. Waiting for valid data...")
                    last_mod_time = None
    except json.JSONDecodeError:
        with plot_placeholder.container():
            st.error(
                "Error: Plot file contains invalid JSON. Fix the file or clear it to continue."
            )
        last_mod_time = current_mod_time  # Prevents continuous errors
    except Exception as e:
        with plot_placeholder.container():
            st.error(f"An unexpected error occurred: {e}")
        last_mod_time = current_mod_time

    time.sleep(1)
