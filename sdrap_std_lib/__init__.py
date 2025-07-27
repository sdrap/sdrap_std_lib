# Core library imports
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objs as go
import plotly.io as pio
from plotly.subplots import make_subplots
from tqdm import tqdm

import rich
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.console import Console
from rich.live import Live
from rich import print

# --- Pandas Configuration ---
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option("display.max_rows", 100)

if not hasattr(pd.DataFrame, "_tqdm_pandas_applied"):
    tqdm.pandas(desc="my bar!")
    pd.DataFrame._tqdm_pandas_applied = True

pd.options.plotting.backend = "plotly"

# --- Terminal Renderers for Plotly ---
import sys
import os
import subprocess
from base64 import b64encode
from plotly.io._base_renderers import ExternalRenderer

CHUNK_SIZE = 4096
PLOT_FILE = "live_plot.json"  # Shared file for the Streamlit app


class KittyRenderer(ExternalRenderer):
    def __init__(self, scale=2.0):
        self.scale = scale

    def render(self, fig_dict, **kwargs):
        from plotly.graph_objs._figure import Figure

        fig = Figure(fig_dict)
        try:
            png_bytes = fig.to_image(format="png", scale=self.scale)
        except Exception as e:
            print(
                f"Error generating PNG for KittyRenderer (is Kaleido installed?): {e}",
                file=sys.stderr,
            )
            return

        data = b64encode(png_bytes).decode("ascii")
        idx = 0
        while idx < len(data):
            chunk = data[idx : idx + CHUNK_SIZE]
            idx += CHUNK_SIZE
            more_data = 1 if idx < len(data) else 0
            sys.stdout.write(f"\033_Gf=100,a=T,m={more_data};{chunk}\033\\")
        sys.stdout.write("\n")
        sys.stdout.flush()

    def show(self, fig, **kwargs):
        return self.render(fig.to_dict(), **kwargs)


class WeztermRenderer(ExternalRenderer):
    def __init__(self, scale=2.0):
        self.scale = scale

    def render(self, fig_dict, **kwargs):
        from plotly.graph_objs._figure import Figure

        fig = Figure(fig_dict)
        try:
            png_bytes = fig.to_image(format="png", scale=self.scale)
        except Exception as e:
            print(
                f"Error generating PNG for WeztermRenderer (is Kaleido installed?): {e}",
                file=sys.stderr,
            )
            return
        data = b64encode(png_bytes).decode("ascii")
        sys.stdout.write("\033]1337;File=inline=1;preserveAspectRatio=1:")
        idx = 0
        while idx < len(data):
            chunk = data[idx : idx + CHUNK_SIZE]
            idx += CHUNK_SIZE
            sys.stdout.write(chunk)
        sys.stdout.write("\a")
        sys.stdout.write("\n")
        sys.stdout.flush()

    def show(self, fig, **kwargs):
        return self.render(fig.to_dict(), **kwargs)


class StreamlitRenderer(ExternalRenderer):
    def __init__(self):
        pass

    def render(self, fig_dict, **kwargs):
        import json

        with open(PLOT_FILE, "w") as f:
            json.dump(fig_dict, f)
        print(f"Plotly figure saved to '{PLOT_FILE}' for Streamlit viewer.")

    def show(self, fig, **kwargs):
        return self.render(fig.to_dict(), **kwargs)


# Register the renderers
pio.renderers["wezterm"] = WeztermRenderer()
pio.renderers["kitty"] = KittyRenderer()
pio.renderers["streamlit"] = StreamlitRenderer()


# --- Conditionally set default renderer ---
try:
    from IPython import get_ipython

    shell = get_ipython()
    if shell is not None and shell.__class__.__name__ == "TerminalInteractiveShell":
        if os.environ.get("KITTY_WINDOW_ID"):
            pio.renderers.default = "kitty"
        elif os.environ.get("WEZTERM_PANE"):
            pio.renderers.default = "wezterm"
except (ImportError, NameError, AttributeError):
    pass
except Exception:
    pass

# --- Plotly Default Template Configuration ---
pio.templates["draft"] = go.layout.Template()
pio.templates["draft"].layout.legend = {"orientation": "h"}
pio.templates["draft"].layout.autosize = False
pio.templates["draft"].layout.width = 700
pio.templates["draft"].layout.height = 500
pio.templates["draft"].layout.margin = dict(l=50, r=50, b=50, t=50, pad=4)
pio.templates["draft"].layout.title.xanchor = "center"
pio.templates["draft"].layout.title.x = 0.5
plt_colors = px.colors.qualitative.G10
plt_dark_color = "rgb(102, 102, 102)"
pio.templates["draft"].layout.colorway = plt_colors
pio.templates["print"] = pio.templates["draft"]
pio.templates["print"].layout.paper_bgcolor = "rgba(0,0,0,0)"
pio.templates["print"].layout.plot_bgcolor = "rgba(0,0,0,0)"
pio.templates.default = "plotly_white+draft"


# --- Public API of the library ---
__all__ = [
    "np",
    "pd",
    "px",
    "ff",
    "go",
    "pio",
    "make_subplots",
    "tqdm",
    "KittyRenderer",
    "WeztermRenderer",
    "StreamlitRenderer",
    "plt_colors",
    "plt_dark_color",
    "rich",
    "Panel",
    "Markdown",
    "Table",
    "Live",
    "Console",
    "print",
]


def serve_streamlit_app():
    """
    Launch the Streamlit app to view live plots.
    This function should be run from the command line, not in an IPython session.
    """
    app_path = os.path.join(os.path.dirname(__file__), "_streamlit_viewer.py")
    if not os.path.exists(app_path):
        print(f"Error: Streamlit app file not found at {app_path}", file=sys.stderr)
        sys.exit(1)

    try:
        subprocess.run(["streamlit", "run", app_path], check=True)
    except FileNotFoundError:
        print(
            "Error: 'streamlit' command not found. Please install Streamlit.",
            file=sys.stderr,
        )
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error starting Streamlit app: {e}", file=sys.stderr)
        sys.exit(1)
