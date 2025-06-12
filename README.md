# My Standard Library (standard_lib)

A personal collection of standard Python imports, configurations, and utilities for data science and plotting.

## Installation

Install the package from GitHub using pip:

```bash
pip install git+ssh://git@github.com/sdrap/sdrap_std_lib.git
```

## What it has
my minimal configuration to get working with my coauthors while allowing me to stay in the terminal ("Kitty" for showing plotly graphs).

It imports and sets some options for 

* numpy
* pandas
* plotly
* rich print

I use the following shortnames

* `np`: for numpy
* `pd`: for pandas
* `px`, `pio`, `go`, `ff`: for plotly express, plotly io (seldom use), plotly figures (classical with `fig = go.Figure()`), and figure factory (for subplots)
* `plt_colors` is my standard color palette.


## Usage

```
from sdrap_std_lib import *

# Now you can use the re-exported modules and variables:
df = pd.DataFrame(...)
fig = px.scatter(...)
print(plt_colors)

# The Kitty renderer should be set as default by Plotly.
fig.show()
```
