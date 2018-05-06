MAE 259B Course Project (Group 2)
====

Environment requirement
----
- Python 3 and the following Python libraries (which could be installed via `pip`):
    - NumPy
    - SymPy (only for `diff/`)
    - AIOHTTP (only for `server.py`)
- A modern web browser (e.g. latest Google Chrome) for visualization.

Files
----
- `runBeam.py`: implementation of discrete elastic rods, for 2D straight beams. Results saved to `data/` directory.
- `runCircle.py`: 2D elastic rods in a circular shape. Results saved to `data/` directory.
- `server.py`: read existing solutions in `data/` for visualization in web browsers.
- Other `.py` files in root directory are included modules. See the comments in the beginning of each file.
- `index.html` and `list` in root directory is solely for *GitHub Pages* use.

Directories
----
- `data/`: generated data files (in JSON format).
- `diff/`: carry out differentiation with SymPy to get gradients and hessians.
- `mid-presentation/`: progress presentation.
- `screenshots/`: directory for holding screenshots.
- `visualize/`: resources for visualizing data in web browser.