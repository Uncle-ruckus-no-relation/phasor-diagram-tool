# Phasor diagram tool

A browser-based phasor editor built with Streamlit, NumPy, and Matplotlib.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit opens the tool in your browser. To make it available online to others,
deploy this folder to a Streamlit-compatible host.

Phasors can be specified by magnitude and angle (degrees), or by Re/Im
components. Each starting point can be the plane center, a polar or Cartesian
coordinate, or the start/end point of an earlier phasor. Plot bounds update to
fit all phasor endpoints independently for Re and Im, avoiding unused
quadrants. The axes retain equal units-per-distance scaling.
Phasors default to thickness 1 and offer an open V arrowhead (voltage/impedance)
or a filled triangle arrowhead (current/admittance), enlarged by 1.5x. The
plane can be shortened independently around the phasors or displayed as a
symmetric square. Switching between polar and Cartesian vector or start-point
coordinates converts the current values automatically.
