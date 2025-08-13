OpenClime (CC0) — Simple, Decomposable Regional Climate Model
License: CC0 1.0 (Public Domain). Everything here is dedicated to the public domain.

OpenClime is a mesoscale decomposable prototype climate model with:

Local energy balance (EBM) for each grid cell

Water balance (rainfall/irrigation/evapotranspiration/runoff/infiltration)

Vegetation dynamics (LAI, coarse plant carbon)

Horizontal advection of humidity (q) — simple upwind scheme

Hooks for connecting to ERA5/MERRA-2 datasets (future implementation)

The model was built as a basis for testing interventions at the regional scale: afforestation/irrigation using desalinated water powered by solar energy, albedo changes, and more.

Quick Installation
bash
Copy
Edit
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
Quick Run (Demo)
bash
Copy
Edit
python examples/run_demo.py
The script creates a 10×20 grid with constant westerly winds, injects a "humidity patch" in the west, and runs for 5 days.
The demo’s purpose: to showcase the advection engine and cell-to-cell coupling.

Project Structure
pgsql
Copy
Edit
openclime-cc0/
├─ LICENSE
├─ README.md
├─ requirements.txt
├─ src/climodel/
│  ├─ __init__.py
│  ├─ gridcell.py         # Single grid cell: energy/water/vegetation
│  ├─ model.py            # ClimateModel: grid, winds, advection, simulation loop
│  └─ drivers.py          # Data hooks (ERA5 etc.) — future implementation
├─ tools/
│  └─ adkonachi.py        # “Adkonachi” — experimental CLI wrapper for defining simulations in plain natural language
└─ examples/
   ├─ run_demo.py         # Basic run example
   └─ config.yaml         # Example configuration
“Adkonachi” — Plain Language Execution
The tools/adkonachi.py script allows writing requests like:

arduino
Copy
Edit
"Experiment: Afforest 30% of cells [3:7,2:6] for 10 days, irrigate 3 mm/day"
It then generates a configuration file and runs the model with those settings.

This is a POA (Proof of Approach) rather than full NLP; the goal is to document the format and operational flow.

Next Steps
Actual ERA5 connection via cdsapi/xarray

Basic cloud parameterization (RH-based + shallow convection)

Heat advection (not just q) and improved flow scheme (CFL/flux limiters)

Calibration against regional hindcast (Eastern Mediterranean)

Micro layer (1–100 m) for areas of interest — deterministic downscaling