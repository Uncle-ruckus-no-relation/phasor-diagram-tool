import math
import uuid

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib.ticker import AutoMinorLocator


st.set_page_config(page_title="Phasor diagram", page_icon="↗", layout="wide")

ARROWSTYLES = ["->", "-|>"]
ARROWSTYLE_LABELS = {
    "->": "Open V (voltage / impedance)",
    "-|>": "Filled triangle (current / admittance)",
}


def new_phasor(index):
    return {
        "id": uuid.uuid4().hex,
        "name": f"P{index}",
        "vector_mode": "Polar",
        "magnitude": 1.0,
        "angle": 0.0,
        "re": 1.0,
        "im": 0.0,
        "start_mode": "Center",
        "start_magnitude": 1.0,
        "start_angle": 0.0,
        "start_re": 0.0,
        "start_im": 0.0,
        "reference": "",
        "reference_point": "End",
        "color": "#1565c0",
        "width": 1.0,
        "arrowstyle": "->",
    }


def vector_from_phasor(phasor):
    if phasor["vector_mode"] == "Polar":
        angle = math.radians(phasor["angle"])
        return (
            phasor["magnitude"] * math.cos(angle),
            phasor["magnitude"] * math.sin(angle),
        )
    return phasor["re"], phasor["im"]


def resolve_points(phasors):
    resolved = {}
    for phasor in phasors:
        start_mode = phasor["start_mode"]
        if start_mode == "Center":
            start = (0.0, 0.0)
        elif start_mode == "Cartesian (Re, Im)":
            start = (phasor["start_re"], phasor["start_im"])
        elif start_mode == "Polar":
            angle = math.radians(phasor["start_angle"])
            start = (
                phasor["start_magnitude"] * math.cos(angle),
                phasor["start_magnitude"] * math.sin(angle),
            )
        else:
            reference = resolved[phasor["reference"]]
            start = reference[0 if phasor["reference_point"] == "Start" else 1]

        dx, dy = vector_from_phasor(phasor)
        end = (start[0] + dx, start[1] + dy)
        resolved[phasor["id"]] = (start, end)
    return resolved


def axis_limits(coordinates, axis):
    values = coordinates[:, axis]
    lower = min(0.0, float(np.min(values)))
    upper = max(0.0, float(np.max(values)))
    span = upper - lower

    if span == 0:
        return -0.5, 0.5

    padding = span * 0.08
    if lower < 0:
        lower -= padding
    if upper > 0:
        upper += padding
    return lower, upper


def phasor_by_id(phasor_id):
    return next(
        phasor for phasor in st.session_state.phasors if phasor["id"] == phasor_id
    )


def sync_vector_coordinates(phasor_id):
    phasor = phasor_by_id(phasor_id)
    target_mode = st.session_state[f"vector_mode_{phasor_id}"]
    if target_mode == "Cartesian (Re, Im)" and phasor["vector_mode"] == "Polar":
        magnitude = float(st.session_state[f"mag_{phasor_id}"])
        angle = math.radians(float(st.session_state[f"angle_{phasor_id}"]))
        re = magnitude * math.cos(angle)
        im = magnitude * math.sin(angle)
        st.session_state[f"re_{phasor_id}"] = re
        st.session_state[f"im_{phasor_id}"] = im
        phasor["re"] = re
        phasor["im"] = im
    elif target_mode == "Polar" and phasor["vector_mode"] == "Cartesian (Re, Im)":
        re = float(st.session_state[f"re_{phasor_id}"])
        im = float(st.session_state[f"im_{phasor_id}"])
        magnitude = math.hypot(re, im)
        angle = math.degrees(math.atan2(im, re))
        st.session_state[f"mag_{phasor_id}"] = magnitude
        st.session_state[f"angle_{phasor_id}"] = angle
        phasor["magnitude"] = magnitude
        phasor["angle"] = angle


def sync_start_coordinates(phasor_id):
    phasor = phasor_by_id(phasor_id)
    target_mode = st.session_state[f"start_mode_{phasor_id}"]
    if target_mode == "Cartesian (Re, Im)" and phasor["start_mode"] == "Polar":
        magnitude = float(st.session_state[f"start_mag_{phasor_id}"])
        angle = math.radians(float(st.session_state[f"start_angle_{phasor_id}"]))
        re = magnitude * math.cos(angle)
        im = magnitude * math.sin(angle)
        st.session_state[f"start_re_{phasor_id}"] = re
        st.session_state[f"start_im_{phasor_id}"] = im
        phasor["start_re"] = re
        phasor["start_im"] = im
    elif target_mode == "Polar" and phasor["start_mode"] == "Cartesian (Re, Im)":
        re = float(st.session_state[f"start_re_{phasor_id}"])
        im = float(st.session_state[f"start_im_{phasor_id}"])
        magnitude = math.hypot(re, im)
        angle = math.degrees(math.atan2(im, re))
        st.session_state[f"start_mag_{phasor_id}"] = magnitude
        st.session_state[f"start_angle_{phasor_id}"] = angle
        phasor["start_magnitude"] = magnitude
        phasor["start_angle"] = angle


if "phasors" not in st.session_state:
    st.session_state.phasors = [new_phasor(1)]

# Migrate the original defaults and discard arrow styles no longer offered.
if "phasor_style_version" not in st.session_state:
    for phasor in st.session_state.phasors:
        if phasor.get("width") == 2.5:
            phasor["width"] = 1.0
        if phasor.get("arrowstyle") not in ARROWSTYLES:
            phasor["arrowstyle"] = "->"
    st.session_state.phasor_style_version = 1

st.title("Phasor diagram")
st.caption("Define vectors in polar or Cartesian coordinates. Plot limits adjust automatically.")

if st.button("＋ Add phasor", type="primary"):
    st.session_state.phasors.append(new_phasor(len(st.session_state.phasors) + 1))
    st.rerun()

phasors = st.session_state.phasors
for index, phasor in enumerate(phasors):
    earlier = [item["id"] for item in phasors[:index]]
    start_options = ["Center", "Cartesian (Re, Im)", "Polar"]
    if earlier:
        start_options.extend(
            ["Start of another phasor", "End of another phasor"]
        )
    if phasor["start_mode"] not in start_options:
        phasor["start_mode"] = "Center"
    key = phasor["id"]
    numeric_widget_keys = {
        "magnitude": f"mag_{key}",
        "angle": f"angle_{key}",
        "re": f"re_{key}",
        "im": f"im_{key}",
        "start_magnitude": f"start_mag_{key}",
        "start_angle": f"start_angle_{key}",
        "start_re": f"start_re_{key}",
        "start_im": f"start_im_{key}",
        "width": f"width_{key}",
    }
    for field, widget_key in numeric_widget_keys.items():
        st.session_state.setdefault(widget_key, float(phasor[field]))
    with st.expander(f"{phasor['name']} — edit phasor", expanded=index == 0):
        controls = st.columns([1.2, 1, 1])
        phasor["name"] = controls[0].text_input(
            "Name", value=phasor["name"], key=f"name_{key}"
        )
        phasor["vector_mode"] = controls[1].selectbox(
            "Vector defined as",
            ["Polar", "Cartesian (Re, Im)"],
            index=["Polar", "Cartesian (Re, Im)"].index(phasor["vector_mode"]),
            key=f"vector_mode_{key}",
            on_change=sync_vector_coordinates,
            args=(key,),
        )
        phasor["start_mode"] = controls[2].selectbox(
            "Starting point",
            start_options,
            index=start_options.index(phasor["start_mode"]),
            key=f"start_mode_{key}",
            on_change=sync_start_coordinates,
            args=(key,),
        )

        if phasor["vector_mode"] == "Polar":
            values = st.columns(2)
            phasor["magnitude"] = values[0].number_input(
                "Magnitude", key=f"mag_{key}"
            )
            phasor["angle"] = values[1].number_input(
                "Angle (degrees)",
                key=f"angle_{key}",
            )
        else:
            values = st.columns(2)
            phasor["re"] = values[0].number_input(
                "Re component", key=f"re_{key}"
            )
            phasor["im"] = values[1].number_input(
                "Im component", key=f"im_{key}"
            )

        if phasor["start_mode"] == "Cartesian (Re, Im)":
            values = st.columns(2)
            phasor["start_re"] = values[0].number_input(
                "Start Re", key=f"start_re_{key}"
            )
            phasor["start_im"] = values[1].number_input(
                "Start Im", key=f"start_im_{key}"
            )
        elif phasor["start_mode"] == "Polar":
            values = st.columns(2)
            phasor["start_magnitude"] = values[0].number_input(
                "Start radius",
                key=f"start_mag_{key}",
            )
            phasor["start_angle"] = values[1].number_input(
                "Start angle (degrees)",
                key=f"start_angle_{key}",
            )
        elif phasor["start_mode"] in (
            "Start of another phasor",
            "End of another phasor",
        ):
            phasor["reference"] = st.selectbox(
                "Reference phasor",
                earlier,
                format_func=lambda item_id: next(
                    item["name"] for item in phasors if item["id"] == item_id
                ),
                index=earlier.index(phasor["reference"])
                if phasor["reference"] in earlier
                else 0,
                key=f"reference_{key}",
            )
            phasor["reference_point"] = (
                "Start"
                if phasor["start_mode"] == "Start of another phasor"
                else "End"
            )

        style = st.columns([1.2, 1, 1, 1])
        phasor["color"] = style[0].color_picker(
            "Color", value=phasor["color"], key=f"color_{key}"
        )
        phasor["width"] = style[1].number_input(
            "Thickness", min_value=0.1, step=0.5,
            key=f"width_{key}"
        )
        arrow_key = f"arrow_{key}"
        if st.session_state.get(arrow_key) not in (None, *ARROWSTYLES):
            st.session_state[arrow_key] = phasor["arrowstyle"]
        phasor["arrowstyle"] = style[2].selectbox(
            "Arrow style",
            ARROWSTYLES,
            index=ARROWSTYLES.index(phasor["arrowstyle"]),
            format_func=lambda arrowstyle: ARROWSTYLE_LABELS[arrowstyle],
            key=arrow_key,
        )
        if style[3].button("Delete", key=f"delete_{key}", disabled=len(phasors) == 1):
            phasors.pop(index)
            st.rerun()

names = [phasor["name"].strip() for phasor in phasors]
for phasor in phasors:
    phasor["name"] = phasor["name"].strip()
if any(not name for name in names):
    st.error("Every phasor needs a name.")
elif len(set(names)) != len(names):
    st.error("Phasor names must be unique so endpoint references are unambiguous.")
else:
    points = resolve_points(phasors)
    fig, ax = plt.subplots(figsize=(8, 8))
    for phasor in phasors:
        start, end = points[phasor["id"]]
        ax.annotate(
            "",
            xy=end,
            xytext=start,
            arrowprops={
                "arrowstyle": phasor["arrowstyle"],
                "color": phasor["color"],
                "linewidth": phasor["width"],
                "mutation_scale": 15,
                "shrinkA": 0,
                "shrinkB": 0,
            },
        )
        ax.annotate(
            phasor["name"],
            xy=end,
            xytext=(5, 5),
            textcoords="offset points",
            color=phasor["color"],
        )

    coordinates = np.asarray([point for pair in points.values() for point in pair])
    if st.checkbox(
        "Shorten plane to fit phasors",
        value=True,
        help="When off, show a symmetric square plane based on the largest coordinate.",
    ):
        ax.set_xlim(*axis_limits(coordinates, 0))
        ax.set_ylim(*axis_limits(coordinates, 1))
    else:
        limit = max(0.5, float(np.max(np.abs(coordinates))) * 1.08)
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
    ax.set_aspect("equal", adjustable="box")
    ax.xaxis.set_minor_locator(AutoMinorLocator(5))
    ax.yaxis.set_minor_locator(AutoMinorLocator(5))
    ax.set_axisbelow(True)
    ax.axhline(0, color="black", linewidth=0.9)
    ax.axvline(0, color="black", linewidth=0.9)
    ax.set_xlabel("1 (Reálna os)")
    ax.set_ylabel("j (Imaginárna os)")
    ax.grid(True, which="major", linestyle="--", linewidth=0.8, alpha=0.65)
    ax.grid(True, which="minor", linestyle=":", linewidth=0.5, alpha=0.5)
    ax.set_title("")
    st.pyplot(fig, width="stretch")
    plt.close(fig)
