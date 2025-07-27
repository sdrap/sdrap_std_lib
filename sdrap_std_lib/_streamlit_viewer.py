# streamlit_plot_viewer.py

import streamlit as st
import plotly.graph_objects as go
import json
import os
import time

# --- Configuration (must match sdrap_std_lib/__init__.py) ---
PLOT_FILE = "live_plot.json"

st.set_page_config(page_title="Live Plotly Viewer", layout="wide")
st.title("Live Plotly Graph Viewer")
st.markdown(
    "Use `pio.renderers.default = 'streamlit'` in your Python session to send plots here."
)

# Use st.empty to create a container for the plot that can be updated in place
plot_container = st.empty()


# --- Main app logic ---
def update_plot():
    """
    Reads the Plotly figure from a JSON file and updates the session state.
    """
    if not os.path.exists(PLOT_FILE):
        return

    try:
        # Check for file modification time to know when to update
        current_mod_time = os.path.getmtime(PLOT_FILE)
        if (
            "last_mod_time" not in st.session_state
            or st.session_state.last_mod_time != current_mod_time
        ):
            with open(PLOT_FILE, "r") as f:
                fig_json = f.read()

            if fig_json.strip():
                fig_dict = json.loads(fig_json)
                st.session_state.figure = go.Figure(fig_dict)
            else:
                st.session_state.figure = go.Figure()

            st.session_state.last_mod_time = current_mod_time

    except (json.JSONDecodeError, FileNotFoundError):
        st.session_state.figure = go.Figure()


# Initialize session state for the plot if it doesn't exist
if "figure" not in st.session_state:
    st.session_state.figure = go.Figure()
    st.session_state.last_mod_time = None

# Update the plot state if the file has changed
update_plot()

# Display the chart with a unique key
# The key is essential to prevent the "duplicate ID" error on reruns
with plot_container:
    st.plotly_chart(
        st.session_state.figure, use_container_width=True, key="live_plot_key"
    )

# Optional: Add an "Rerun" button to manually check for updates
st.button("Manual Refresh", on_click=update_plot)
