import re
import math
import json
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="GCM Level Road Calculator", layout="wide")

# ─── DEFAULT VEHICLE PROFILES ─────────────────────────────────────────────────
# These are factory defaults. Session edits are stored in
# st.session_state["vehicle_profiles"] and reset on browser refresh.

DEFAULT_VEHICLE_PROFILES = {
    "Test Vehicle 1": {
        "vehicle_mass": 3350.0,
        "rated_GCM": 6850.0,
        "peak_torque_Nm": 400.0,
        "peak_torque_rpm": 2000,
        "peak_power_kW": 200.0,
        "peak_power_rpm": 4000,
        "idle_rpm": 800,
        "redline_rpm": 4500,
        "torque_curve": [
            (800,  220), (1000, 250), (1500, 350), (2000, 400),
            (2500, 400), (3000, 380), (3500, 350), (4000, 320), (4500, 280),
        ],
        "final_drive_ratio": 3.70,
        "driveline_efficiency": 0.88,
        "tyre_size": "265/65R17",
        "tyre_radius": 0.380,
        "num_vehicle_tyres": 4,
        "tyre_pressure_kPa": 280.0,
        "front_tyre_pressure_kPa": 280.0,
        "rear_tyre_pressure_kPa": 280.0,
        "front_left_base_tyre_load_kg": 880.5,
        "front_right_base_tyre_load_kg": 880.5,
        "rear_left_base_tyre_load_kg": 794.5,
        "rear_right_base_tyre_load_kg": 794.5,
        "wheelbase_mm": 3125.0,
        "rear_axle_to_towball_mm": 1450.0,
        "front_axle_limit_kg": 1650.0,
        "rear_axle_limit_kg": 2050.0,
        "gvm_limit_kg": 3700.0,
        "tyre_type": "Highway",
        "Cd": 0.40,
        "frontal_area": 3.50,
        "gear_ratios": [4.71, 3.14, 2.11, 1.67, 1.29, 1.00, 0.84, 0.67, 0.60, 0.52],
    },
    "Medium Dual Cab 4WD": {
        "vehicle_mass": 2200.0,
        "rated_GCM": 6000.0,
        "peak_torque_Nm": 500.0,
        "peak_torque_rpm": 1600,
        "peak_power_kW": 150.0,
        "peak_power_rpm": 3200,
        "idle_rpm": 750,
        "redline_rpm": 3800,
        "torque_curve": [
            (750,  250), (1200, 420), (1600, 500), (2000, 500),
            (2400, 480), (2800, 440), (3200, 380), (3800, 300),
        ],
        "final_drive_ratio": 3.31,
        "driveline_efficiency": 0.88,
        "tyre_size": "265/65R17",
        "tyre_radius": 0.375,
        "num_vehicle_tyres": 4,
        "tyre_pressure_kPa": 280.0,
        "tyre_type": "All-Terrain",
        "Cd": 0.42,
        "frontal_area": 3.10,
        "gear_ratios": [3.99, 2.37, 1.55, 1.16, 0.85, 0.67],
    },
    "Large Dual Cab 4WD": {
        "vehicle_mass": 2700.0,
        "rated_GCM": 7500.0,
        "peak_torque_Nm": 650.0,
        "peak_torque_rpm": 1600,
        "peak_power_kW": 170.0,
        "peak_power_rpm": 3200,
        "idle_rpm": 750,
        "redline_rpm": 3800,
        "torque_curve": [
            (750,  320), (1200, 550), (1600, 650), (2000, 650),
            (2400, 620), (2800, 580), (3200, 480), (3800, 370),
        ],
        "final_drive_ratio": 3.70,
        "driveline_efficiency": 0.87,
        "tyre_size": "285/75R16",
        "tyre_radius": 0.400,
        "num_vehicle_tyres": 4,
        "tyre_pressure_kPa": 300.0,
        "tyre_type": "All-Terrain",
        "Cd": 0.45,
        "frontal_area": 3.40,
        "gear_ratios": [4.17, 2.34, 1.52, 1.14, 0.87, 0.69],
    },
    "Full-Size Pickup / 1500 Class": {
        "vehicle_mass": 2500.0,
        "rated_GCM": 7700.0,
        "peak_torque_Nm": 600.0,
        "peak_torque_rpm": 2400,
        "peak_power_kW": 250.0,
        "peak_power_rpm": 4200,
        "idle_rpm": 600,
        "redline_rpm": 5500,
        "torque_curve": [
            (600,  280), (1200, 430), (1800, 570), (2400, 600),
            (3000, 590), (3600, 560), (4200, 500), (5000, 400), (5500, 340),
        ],
        "final_drive_ratio": 3.92,
        "driveline_efficiency": 0.88,
        "tyre_size": "275/65R18",
        "tyre_radius": 0.400,
        "num_vehicle_tyres": 4,
        "tyre_pressure_kPa": 280.0,
        "tyre_type": "Highway",
        "Cd": 0.50,
        "frontal_area": 3.80,
        "gear_ratios": [4.71, 2.99, 2.14, 1.77, 1.52, 1.27, 1.00, 0.85, 0.69, 0.64],
    },
    "Boxy Wagon 4WD": {
        "vehicle_mass": 2700.0,
        "rated_GCM": 7000.0,
        "peak_torque_Nm": 650.0,
        "peak_torque_rpm": 1600,
        "peak_power_kW": 200.0,
        "peak_power_rpm": 3200,
        "idle_rpm": 750,
        "redline_rpm": 4000,
        "torque_curve": [
            (750,  300), (1200, 500), (1600, 650), (2000, 650),
            (2400, 630), (2800, 580), (3200, 480), (4000, 360),
        ],
        "final_drive_ratio": 3.31,
        "driveline_efficiency": 0.88,
        "tyre_size": "285/60R18",
        "tyre_radius": 0.385,
        "num_vehicle_tyres": 4,
        "tyre_pressure_kPa": 280.0,
        "tyre_type": "Highway",
        "Cd": 0.48,
        "frontal_area": 3.30,
        "gear_ratios": [4.17, 2.34, 1.52, 1.14, 0.87, 0.69, 0.58],
    },
    "Custom": {
        "vehicle_mass": 3500.0,
        "rated_GCM": 8000.0,
        "peak_torque_Nm": 400.0,
        "peak_torque_rpm": 2000,
        "peak_power_kW": 200.0,
        "peak_power_rpm": 4000,
        "idle_rpm": 800,
        "redline_rpm": 4500,
        "torque_curve": [
            (800,  200), (1500, 350), (2000, 400), (2500, 400),
            (3000, 380), (3500, 350), (4000, 300), (4500, 250),
        ],
        "final_drive_ratio": 3.70,
        "driveline_efficiency": 0.88,
        "tyre_size": "265/65R17",
        "tyre_radius": 0.380,
        "num_vehicle_tyres": 4,
        "tyre_pressure_kPa": 280.0,
        "tyre_type": "Highway",
        "Cd": 0.40,
        "frontal_area": 3.20,
        "gear_ratios": [1.00],
    },
}

# ─── TRAILER PROFILES ────────────────────────────────────────────────────────────
# Trailer values are held in profiles. The normal calculator view only asks for
# trailer mass, then interpolates towball mass and individual wheel loads from the
# selected profile's calibrated loading points.

DEFAULT_TRAILER_PROFILES = {
    "AIC Dual-Axle Flat Front Trailer": {
        "profile_name": "AIC Dual-Axle Flat Front Trailer",
        "number_of_axles": 2,
        "number_of_tyres": 4,
        "tyre_size": "235/75R15",
        "tyre_pressure_kPa": 350.0,
        "tyre_radius_m": 0.365,
        "tyre_type": "Highway",
        "trailer_Cd": 0.55,
        "frontal_width_m": 2.40,
        "frontal_height_m": 1.80,
        "frontal_area_m2": 4.32,
        "weight_profiles": [
            {
                "profile_name": "Light load",
                "trailer_mass_kg": 1500.0,
                "tow_ball_mass_kg": 150.0,
                "front_left_tyre_load_kg": 337.5,
                "front_right_tyre_load_kg": 337.5,
                "rear_left_tyre_load_kg": 337.5,
                "rear_right_tyre_load_kg": 337.5,
            },
            {
                "profile_name": "Balanced load",
                "trailer_mass_kg": 2500.0,
                "tow_ball_mass_kg": 250.0,
                "front_left_tyre_load_kg": 562.5,
                "front_right_tyre_load_kg": 562.5,
                "rear_left_tyre_load_kg": 562.5,
                "rear_right_tyre_load_kg": 562.5,
            },
            {
                "profile_name": "GCM test load",
                "trailer_mass_kg": 3500.0,
                "tow_ball_mass_kg": 350.0,
                "front_left_tyre_load_kg": 787.5,
                "front_right_tyre_load_kg": 787.5,
                "rear_left_tyre_load_kg": 787.5,
                "rear_right_tyre_load_kg": 787.5,
            },
        ],
    },
    "Custom": {
        "profile_name": "Custom",
        "number_of_axles": 2,
        "number_of_tyres": 4,
        "tyre_size": "235/75R15",
        "tyre_pressure_kPa": 350.0,
        "tyre_radius_m": 0.365,
        "tyre_type": "Highway",
        "trailer_Cd": 0.55,
        "frontal_width_m": 2.40,
        "frontal_height_m": 1.80,
        "frontal_area_m2": 4.32,
        "weight_profiles": [
            {
                "profile_name": "Light load",
                "trailer_mass_kg": 1500.0,
                "tow_ball_mass_kg": 150.0,
                "front_left_tyre_load_kg": 337.5,
                "front_right_tyre_load_kg": 337.5,
                "rear_left_tyre_load_kg": 337.5,
                "rear_right_tyre_load_kg": 337.5,
            },
            {
                "profile_name": "Balanced load",
                "trailer_mass_kg": 2500.0,
                "tow_ball_mass_kg": 250.0,
                "front_left_tyre_load_kg": 562.5,
                "front_right_tyre_load_kg": 562.5,
                "rear_left_tyre_load_kg": 562.5,
                "rear_right_tyre_load_kg": 562.5,
            },
            {
                "profile_name": "GCM test load",
                "trailer_mass_kg": 3500.0,
                "tow_ball_mass_kg": 350.0,
                "front_left_tyre_load_kg": 787.5,
                "front_right_tyre_load_kg": 787.5,
                "rear_left_tyre_load_kg": 787.5,
                "rear_right_tyre_load_kg": 787.5,
            },
        ],
    },
}


def enrich_trailer_profile(name, prof):
    """Normalise older trailer profile dictionaries into the current named weight-profile schema."""
    t = dict(prof)

    # Convert older keys if present.
    t.setdefault("profile_name", name)
    t.setdefault("number_of_axles", t.get("num_axles", 2))
    t.setdefault("number_of_tyres", t.get("num_tyres", 4))
    t.setdefault("tyre_size", t.get("tyre_size", "235/75R15"))
    t.setdefault("tyre_pressure_kPa", t.get("tyre_pressure_kPa", 350.0))
    t.setdefault("tyre_radius_m", t.get("tyre_radius", t.get("tyre_radius_m", 0.365)))
    t.setdefault("tyre_type", t.get("tyre_type", "Highway"))
    t.setdefault("trailer_Cd", t.get("Cd", t.get("trailer_Cd", 0.55)))
    t.setdefault("frontal_width_m", t.get("frontal_width", t.get("frontal_width_m", 2.40)))
    t.setdefault("frontal_height_m", t.get("frontal_height", t.get("frontal_height_m", 1.80)))
    t.setdefault("frontal_area_m2", t.get("frontal_area_m2", t["frontal_width_m"] * t["frontal_height_m"]))

    # Backwards compatibility: convert old interpolation_points to named weight_profiles.
    if "weight_profiles" not in t:
        if "interpolation_points" in t and t["interpolation_points"]:
            t["weight_profiles"] = []
            for i, pt in enumerate(t["interpolation_points"]):
                t["weight_profiles"].append({
                    "profile_name": pt.get("profile_name", pt.get("label", f"Weight profile {i + 1}")),
                    "trailer_mass_kg": float(pt.get("trailer_mass_kg", 0.0)),
                    "tow_ball_mass_kg": float(pt.get("tow_ball_mass_kg", 0.0)),
                    "front_left_tyre_load_kg": float(pt.get("front_left_tyre_load_kg", 0.0)),
                    "front_right_tyre_load_kg": float(pt.get("front_right_tyre_load_kg", 0.0)),
                    "rear_left_tyre_load_kg": float(pt.get("rear_left_tyre_load_kg", 0.0)),
                    "rear_right_tyre_load_kg": float(pt.get("rear_right_tyre_load_kg", 0.0)),
                })
        else:
            m = float(t.get("trailer_mass", 3500.0))
            ball = float(t.get("tow_ball_mass", 0.10 * m))
            each = max(0.0, (m - ball) / 4.0)
            t["weight_profiles"] = [{
                "profile_name": "Profile load",
                "trailer_mass_kg": m,
                "tow_ball_mass_kg": ball,
                "front_left_tyre_load_kg": each,
                "front_right_tyre_load_kg": each,
                "rear_left_tyre_load_kg": each,
                "rear_right_tyre_load_kg": each,
            }]

    # Clean, sort and normalise weight profiles.
    clean_profiles = []
    for i, wp in enumerate(t.get("weight_profiles", [])):
        try:
            clean_profiles.append({
                "profile_name": str(wp.get("profile_name", f"Weight profile {i + 1}")),
                "trailer_mass_kg": float(wp.get("trailer_mass_kg", 0.0)),
                "tow_ball_mass_kg": float(wp.get("tow_ball_mass_kg", 0.0)),
                "front_left_tyre_load_kg": float(wp.get("front_left_tyre_load_kg", 0.0)),
                "front_right_tyre_load_kg": float(wp.get("front_right_tyre_load_kg", 0.0)),
                "rear_left_tyre_load_kg": float(wp.get("rear_left_tyre_load_kg", 0.0)),
                "rear_right_tyre_load_kg": float(wp.get("rear_right_tyre_load_kg", 0.0)),
            })
        except (TypeError, ValueError):
            continue

    if len(clean_profiles) < 2:
        base_mass = clean_profiles[0]["trailer_mass_kg"] if clean_profiles else 1500.0
        base_ball = clean_profiles[0]["tow_ball_mass_kg"] if clean_profiles else 0.10 * base_mass
        base_each = max(0.0, (base_mass - base_ball) / 4.0)
        clean_profiles = [
            {
                "profile_name": "Light load",
                "trailer_mass_kg": base_mass,
                "tow_ball_mass_kg": base_ball,
                "front_left_tyre_load_kg": base_each,
                "front_right_tyre_load_kg": base_each,
                "rear_left_tyre_load_kg": base_each,
                "rear_right_tyre_load_kg": base_each,
            },
            {
                "profile_name": "GCM test load",
                "trailer_mass_kg": base_mass + 1000.0,
                "tow_ball_mass_kg": 0.10 * (base_mass + 1000.0),
                "front_left_tyre_load_kg": max(0.0, ((base_mass + 1000.0) - 0.10 * (base_mass + 1000.0)) / 4.0),
                "front_right_tyre_load_kg": max(0.0, ((base_mass + 1000.0) - 0.10 * (base_mass + 1000.0)) / 4.0),
                "rear_left_tyre_load_kg": max(0.0, ((base_mass + 1000.0) - 0.10 * (base_mass + 1000.0)) / 4.0),
                "rear_right_tyre_load_kg": max(0.0, ((base_mass + 1000.0) - 0.10 * (base_mass + 1000.0)) / 4.0),
            },
        ]

    t["weight_profiles"] = sorted(clean_profiles, key=lambda p: p["trailer_mass_kg"])

    # Keep a legacy interpolation_points alias for older downloaded JSON compatibility.
    t["interpolation_points"] = [dict(wp) for wp in t["weight_profiles"]]

    # Keep legacy keys for older sections or downloaded JSON compatibility.
    t["num_axles"] = int(t["number_of_axles"])
    t["num_tyres"] = int(t["number_of_tyres"])
    t["tyre_radius"] = float(t["tyre_radius_m"])
    t["Cd"] = float(t["trailer_Cd"])
    t["frontal_width"] = float(t["frontal_width_m"])
    t["frontal_height"] = float(t["frontal_height_m"])
    return t

DEFAULT_TRAILER_PROFILES = {
    name: enrich_trailer_profile(name, prof)
    for name, prof in DEFAULT_TRAILER_PROFILES.items()
}

# ─── AUTOMATIC TORQUE CURVE GENERATION ─────────────────────────────────────────

def generate_torque_curve_from_profile(
    peak_torque_Nm, peak_torque_rpm, peak_power_kW,
    peak_power_rpm, idle_rpm, redline_rpm,
):
    """
    Generate a simple estimated torque curve from ordinary vehicle profile values.

    The user enters peak torque, peak power, the RPM where each occurs, idle RPM,
    and redline RPM. The app then builds an approximate torque curve internally so
    the normal profile editor does not require manual RPM/torque point entry.
    """
    peak_torque_Nm = max(float(peak_torque_Nm), 0.0)
    peak_torque_rpm = max(float(peak_torque_rpm), 1.0)
    peak_power_kW = max(float(peak_power_kW), 0.0)
    peak_power_rpm = max(float(peak_power_rpm), 1.0)
    idle_rpm = max(float(idle_rpm), 1.0)
    redline_rpm = max(float(redline_rpm), idle_rpm)

    peak_power_W = peak_power_kW * 1000.0
    torque_at_peak_power = peak_power_W / max(peak_power_rpm * 2.0 * math.pi / 60.0, 1.0)
    torque_at_peak_power = max(torque_at_peak_power, 0.0)

    rpm_points = [
        idle_rpm,
        (idle_rpm + peak_torque_rpm) / 2.0,
        peak_torque_rpm,
        (peak_torque_rpm + peak_power_rpm) / 2.0,
        peak_power_rpm,
        (peak_power_rpm + redline_rpm) / 2.0,
        redline_rpm,
    ]
    torque_points = [
        0.60 * peak_torque_Nm,
        0.85 * peak_torque_Nm,
        peak_torque_Nm,
        (peak_torque_Nm + torque_at_peak_power) / 2.0,
        torque_at_peak_power,
        0.90 * torque_at_peak_power,
        0.75 * torque_at_peak_power,
    ]

    # Remove duplicate RPMs by keeping the highest torque at that RPM.
    curve_by_rpm = {}
    for rpm, tq in zip(rpm_points, torque_points):
        rpm_key = int(round(rpm))
        tq_val = max(float(tq), 0.0)
        if rpm_key not in curve_by_rpm:
            curve_by_rpm[rpm_key] = tq_val
        else:
            curve_by_rpm[rpm_key] = max(curve_by_rpm[rpm_key], tq_val)

    return [(float(rpm), float(tq)) for rpm, tq in sorted(curve_by_rpm.items())]


def get_active_torque_curve(profile):
    """Prefer the generated torque curve, with legacy torque_curve fallback."""
    curve = profile.get("generated_torque_curve")
    if curve and len(curve) >= 2:
        return [tuple(pt) for pt in curve]
    curve = profile.get("torque_curve")
    if curve and len(curve) >= 2:
        return [tuple(pt) for pt in curve]
    return generate_torque_curve_from_profile(
        profile.get("peak_torque_Nm", 0.0),
        profile.get("peak_torque_rpm", 1.0),
        profile.get("peak_power_kW", 0.0),
        profile.get("peak_power_rpm", 1.0),
        profile.get("idle_rpm", 1.0),
        profile.get("redline_rpm", 1.0),
    )

# ─── PROFILE DEFAULT ENRICHMENT ────────────────────────────────────────────────

def enrich_vehicle_profile(name, prof):
    """Add newer tyre-load / friction fields to older profile dictionaries."""
    p = dict(prof)
    vehicle_mass = float(p.get("vehicle_mass", 0.0))

    # Default base axle split before trailer tow ball load is applied.
    front_each = vehicle_mass * 0.55 / 2.0
    rear_each = vehicle_mass * 0.45 / 2.0

    p.setdefault("front_tyre_pressure_kPa", p.get("tyre_pressure_kPa", 280.0))
    p.setdefault("rear_tyre_pressure_kPa", p.get("tyre_pressure_kPa", 280.0))
    p.setdefault("front_left_base_tyre_load_kg", front_each)
    p.setdefault("front_right_base_tyre_load_kg", front_each)
    p.setdefault("rear_left_base_tyre_load_kg", rear_each)
    p.setdefault("rear_right_base_tyre_load_kg", rear_each)
    p.setdefault("driven_axle_type", "AWD")

    # Normalise legacy driven-axle labels from older saved profiles.
    _drive_map = {
        "RWD": "RWD",
        "FWD": "FWD",
        "AWD": "AWD",
    }
    p["driven_axle_type"] = _drive_map.get(p.get("driven_axle_type"), p.get("driven_axle_type", "AWD"))
    p.setdefault("tyre_road_friction_coefficient", 0.80)
    p.setdefault("wheelbase_mm", 3125.0)
    p.setdefault("rear_axle_to_towball_mm", 1450.0)
    p.setdefault("front_axle_limit_kg", vehicle_mass * 0.55 if vehicle_mass > 0 else 1650.0)
    p.setdefault("rear_axle_limit_kg", vehicle_mass * 0.45 + 500.0 if vehicle_mass > 0 else 2050.0)
    p.setdefault("gvm_limit_kg", vehicle_mass + 350.0 if vehicle_mass > 0 else 3700.0)

    # Generate the working torque curve from profile engine specs.
    # Legacy torque_curve values are retained only for backwards compatibility.
    if not p.get("generated_torque_curve"):
        p["generated_torque_curve"] = generate_torque_curve_from_profile(
            p.get("peak_torque_Nm", 0.0),
            p.get("peak_torque_rpm", 1.0),
            p.get("peak_power_kW", 0.0),
            p.get("peak_power_rpm", 1.0),
            p.get("idle_rpm", 1.0),
            p.get("redline_rpm", 1.0),
        )
    else:
        p["generated_torque_curve"] = [tuple(pt) for pt in p["generated_torque_curve"]]

    # Keep legacy fields for compatibility with older saved profiles.
    p.setdefault("num_vehicle_tyres", 4)
    p.setdefault("tyre_pressure_kPa", p.get("front_tyre_pressure_kPa", 280.0))
    return p

DEFAULT_VEHICLE_PROFILES = {
    name: enrich_vehicle_profile(name, prof)
    for name, prof in DEFAULT_VEHICLE_PROFILES.items()
}

# ─── SESSION STATE INIT ───────────────────────────────────────────────────────────
# Deep-copy profiles into session state on first load so edits persist per session.

if "vehicle_profiles" not in st.session_state:
    st.session_state["vehicle_profiles"] = {
        name: enrich_vehicle_profile(name, prof)
        for name, prof in DEFAULT_VEHICLE_PROFILES.items()
    }
else:
    # Backwards compatibility: add any new fields to profiles already in session state.
    st.session_state["vehicle_profiles"] = {
        name: enrich_vehicle_profile(name, prof)
        for name, prof in st.session_state["vehicle_profiles"].items()
    }


# ─── TRAILER SESSION STATE INIT ─────────────────────────────────────────────────

if "trailer_profiles" not in st.session_state:
    st.session_state["trailer_profiles"] = {
        name: enrich_trailer_profile(name, prof)
        for name, prof in DEFAULT_TRAILER_PROFILES.items()
    }
else:
    st.session_state["trailer_profiles"] = {
        name: enrich_trailer_profile(name, prof)
        for name, prof in st.session_state["trailer_profiles"].items()
    }

# ─── CONSTANTS & TYRE TYPES ──────────────────────────────────────────────────────

g = 9.81
TYRE_TYPES = ["Highway", "All-Terrain", "Mud-Terrain"]
DRIVEN_AXLE_TYPES = ["AWD", "FWD", "RWD"]
LOW_SPEED_MPS = 1.0   # m/s — below this speed, engine is at idle for launch

# ─── HELPER FUNCTIONS ────────────────────────────────────────────────────────────

BASE_CRR_P1 = {"Highway": 0.0075, "All-Terrain": 0.011, "Mud-Terrain": 0.015}
REF_PRESSURE_KPA = 280.0

def estimate_crr(tyre_type, tyre_pressure_kpa):
    base = BASE_CRR_P1.get(tyre_type, 0.010)
    return round(base * (REF_PRESSURE_KPA / max(tyre_pressure_kpa, 50.0)) ** 0.5, 5)

BASE_CRR_P2 = {"Highway": 0.010, "All-Terrain": 0.013, "Mud-Terrain": 0.017}

def calc_crr_p2(tyre_type, loaded_radius_m, unloaded_radius_m):
    base = BASE_CRR_P2.get(tyre_type, 0.012)
    if unloaded_radius_m <= 0:
        return base
    ratio = loaded_radius_m / unloaded_radius_m
    return base * (1.0 + 2.5 * max(0.0, 1.0 - ratio))

def parse_tyre_size(tyre_str):
    m = re.match(r"(\d+)/(\d+)[Rr](\d+(?:\.\d+)?)", tyre_str.strip())
    if not m:
        return None
    sw = float(m.group(1)) / 1000.0
    sh = sw * (float(m.group(2)) / 100.0)
    rd = float(m.group(3)) * 0.0254
    ud = rd + 2.0 * sh
    return {"section_width_m": sw, "rim_diameter_m": rd,
            "sidewall_height_m": sh, "unloaded_diameter_m": ud,
            "unloaded_radius_m": ud / 2.0}

def calc_contact_patch(load_N, pressure_kPa, section_width_m):
    p_Pa = max(pressure_kPa * 1000.0, 1.0)
    area = load_N / p_Pa
    return area, area / max(section_width_m, 0.001)

def interp_torque(torque_curve, rpm):
    """Linear interpolation from torque curve; clamped to endpoints."""
    if not torque_curve:
        return None
    rpms    = [p[0] for p in torque_curve]
    torques = [p[1] for p in torque_curve]
    if rpm <= rpms[0]:
        return torques[0]
    if rpm >= rpms[-1]:
        return torques[-1]
    for i in range(1, len(rpms)):
        if rpms[i - 1] <= rpm <= rpms[i]:
            frac = (rpm - rpms[i - 1]) / (rpms[i] - rpms[i - 1])
            return torques[i - 1] + frac * (torques[i] - torques[i - 1])
    return torques[-1]

def select_best_gear(
    gear_ratios, final_drive_ratio, driveline_efficiency,
    tyre_radius_m, idle_rpm, redline_rpm, torque_curve,
    peak_power_W, V_mps, fallback_torque_Nm=400.0,
):
    """
    Evaluate every gear at the given vehicle speed and select the valid gear
    that gives the highest available engine-based tractive force.

    Low-speed launch correction:
    At low road speeds the calculated engine RPM can fall below idle. In reality,
    clutch or torque converter slip allows the engine to remain at or above idle.
    Therefore, effective RPM is floored at idle RPM for calculation purposes.

    A gear is invalid only if the effective RPM exceeds redline.

    This remains an idealised best-force shift strategy and does not yet include
    shift delay, torque converter multiplication, traction control intervention,
    or manufacturer shift scheduling.
    """
    TWO_PI = 2.0 * math.pi
    wheel_rad_s = V_mps / max(tyre_radius_m, 0.001)

    rows = []
    best_idx = None
    best_F = -1.0

    for gi, gr in enumerate(gear_ratios):
        rpm_calc = wheel_rad_s * gr * final_drive_ratio * 60.0 / TWO_PI

        # Floor RPM at idle to allow launch/low-speed slip modelling.
        effective_rpm = max(rpm_calc, float(idle_rpm))

        # Gear is invalid only above redline.
        valid = effective_rpm <= redline_rpm

        if valid:
            tq = interp_torque(torque_curve, effective_rpm) if torque_curve else fallback_torque_Nm

            # Engine power from torque and RPM, capped by profile peak power.
            P_eng = tq * effective_rpm * TWO_PI / 60.0
            P_cap = min(P_eng, peak_power_W)

            # Wheel torque and torque-limited tractive force.
            T_whl = tq * gr * final_drive_ratio * driveline_efficiency
            F_tq = T_whl / max(tyre_radius_m, 0.001)

            # Power-limited tractive force.
            F_pw = P_cap / max(V_mps, 1.0)

            # Final engine-based available force.
            F_avail = min(F_tq, F_pw)
        else:
            tq = P_eng = P_cap = T_whl = F_tq = F_pw = F_avail = None

        rows.append({
            "Gear": gi + 1,
            "Gear Ratio": round(gr, 3),
            "Calc RPM": round(rpm_calc, 0),
            "Effective RPM": round(effective_rpm, 0),
            "Torque (Nm)": round(tq, 1) if tq is not None else None,
            "Eng Power (W)": round(P_eng, 0) if P_eng is not None else None,
            "Cap Power (W)": round(P_cap, 0) if P_cap is not None else None,
            "F_torque (N)": round(F_tq, 1) if F_tq is not None else None,
            "F_power (N)": round(F_pw, 1) if F_pw is not None else None,
            "F_available (N)": round(F_avail, 1) if F_avail is not None else None,
            "Valid": valid,
            "Selected": False,
        })

        if valid and F_avail is not None and F_avail > best_F:
            best_F = F_avail
            best_idx = gi

    if best_idx is not None:
        rows[best_idx]["Selected"] = True

    return rows, best_idx

def interp_time_at_speed(speeds_kmh, times_s, target_kmh):
    if not speeds_kmh:
        return None
    if speeds_kmh[0] >= target_kmh:
        return times_s[0] if abs(speeds_kmh[0] - target_kmh) < 1e-6 else None
    for i in range(1, len(speeds_kmh)):
        if speeds_kmh[i - 1] < target_kmh <= speeds_kmh[i]:
            frac = (target_kmh - speeds_kmh[i - 1]) / (speeds_kmh[i] - speeds_kmh[i - 1])
            return times_s[i - 1] + frac * (times_s[i] - times_s[i - 1])
    return None


def _linear_interp_extrap(x, xs, ys):
    """Linear interpolation with end-segment extrapolation."""
    pts = sorted(zip(xs, ys), key=lambda p: p[0])
    if not pts:
        return 0.0
    if len(pts) == 1:
        return float(pts[0][1])

    if x <= pts[0][0]:
        x0, y0 = pts[0]
        x1, y1 = pts[1]
    elif x >= pts[-1][0]:
        x0, y0 = pts[-2]
        x1, y1 = pts[-1]
    else:
        x0 = y0 = x1 = y1 = None
        for i in range(1, len(pts)):
            if pts[i - 1][0] <= x <= pts[i][0]:
                x0, y0 = pts[i - 1]
                x1, y1 = pts[i]
                break

    if x1 == x0:
        return float(y0)
    return float(y0 + (x - x0) * (y1 - y0) / (x1 - x0))


def interpolate_trailer_profile(tp, trailer_mass_kg):
    """Interpolate towball and wheel loads from named trailer weight profiles."""
    points = sorted(tp.get("weight_profiles", tp.get("interpolation_points", [])), key=lambda p: p["trailer_mass_kg"])
    if not points:
        ball = 0.10 * trailer_mass_kg
        each = max(0.0, (trailer_mass_kg - ball) / 4.0)
        return {
            "tow_ball_mass_kg": ball,
            "front_left_tyre_load_kg": each,
            "front_right_tyre_load_kg": each,
            "rear_left_tyre_load_kg": each,
            "rear_right_tyre_load_kg": each,
        }, False, []

    xs = [float(p["trailer_mass_kg"]) for p in points]
    out = {}
    for key in [
        "tow_ball_mass_kg",
        "front_left_tyre_load_kg",
        "front_right_tyre_load_kg",
        "rear_left_tyre_load_kg",
        "rear_right_tyre_load_kg",
    ]:
        ys = [float(p[key]) for p in points]
        out[key] = _linear_interp_extrap(float(trailer_mass_kg), xs, ys)

    extrapolated = trailer_mass_kg < min(xs) or trailer_mass_kg > max(xs)
    return out, extrapolated, points


def build_new_weight_profile(existing_profiles):
    """Create a sensible new trailer weight profile based on the current highest mass."""
    profiles = sorted(existing_profiles, key=lambda p: float(p.get("trailer_mass_kg", 0.0)))
    if profiles:
        new_mass = float(profiles[-1].get("trailer_mass_kg", 0.0)) + 500.0
    else:
        new_mass = 0.0
    new_ball = 0.10 * new_mass
    new_each = max(0.0, (new_mass - new_ball) / 4.0)
    return {
        "profile_name": "New weight profile",
        "trailer_mass_kg": new_mass,
        "tow_ball_mass_kg": new_ball,
        "front_left_tyre_load_kg": new_each,
        "front_right_tyre_load_kg": new_each,
        "rear_left_tyre_load_kg": new_each,
        "rear_right_tyre_load_kg": new_each,
    }

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────────

st.sidebar.header("Inputs")

# ── Vehicle Profile ──────────────────────────────────────────────────────────────

st.sidebar.subheader("Vehicle Profile")

selected_vehicle = st.sidebar.selectbox(
    "Select Vehicle Profile",
    list(st.session_state["vehicle_profiles"].keys()),
)
vp  = st.session_state["vehicle_profiles"][selected_vehicle]
vk  = selected_vehicle   # widget key prefix
_ver = st.session_state.get(f"ev_ver_{vk}", 0)
_vkv = f"{vk}_v{_ver}"   # versioned key — refreshes widgets after apply/reset

reference_vehicle_mass = float(vp.get("vehicle_mass", 0.0))
st.sidebar.caption(
    f"Reference vehicle mass only: {reference_vehicle_mass:,.0f} kg. "
    "Calculations use the sum of individual base tyre loads."
)
GCM = st.sidebar.number_input(
    "Rated GCM (kg)", value=float(vp["rated_GCM"]),
    min_value=1.0, step=100.0, key=f"gcm_{vk}",
)

# ── Edit Vehicle Profile ──────────────────────────────────────────────────────────

with st.sidebar.expander("✏️ Edit Vehicle Profile", expanded=False):
    st.caption(
        "Changes apply to this browser session only. "
        "Download JSON to save your profiles for future reference."
    )

    # ── Engine ──
    st.markdown("**Engine**")
    e_ptq     = st.number_input("Peak torque (Nm)",    value=float(vp["peak_torque_Nm"]),  min_value=0.0, step=10.0,  key=f"e_ptq_{_vkv}")
    e_ptq_rpm = st.number_input("Peak torque RPM",     value=int(vp["peak_torque_rpm"]),    min_value=0, step=100,     key=f"e_ptq_rpm_{_vkv}")
    e_ppw     = st.number_input("Peak power (kW)",     value=float(vp["peak_power_kW"]),   min_value=0.0, step=5.0,   key=f"e_ppw_{_vkv}")
    e_ppw_rpm = st.number_input("Peak power RPM",      value=int(vp["peak_power_rpm"]),     min_value=0, step=100,     key=f"e_ppw_rpm_{_vkv}")
    e_idle    = st.number_input("Idle RPM",            value=int(vp["idle_rpm"]),           min_value=0, step=50,      key=f"e_idle_{_vkv}")
    e_redline = st.number_input("Redline RPM",         value=int(vp["redline_rpm"]),        min_value=100, step=100,   key=f"e_redline_{_vkv}")

    # ── Driveline ──
    st.markdown("**Driveline**")
    e_fdr = st.number_input("Final drive ratio",        value=float(vp["final_drive_ratio"]),      min_value=0.01, step=0.01,  format="%.3f", key=f"e_fdr_{_vkv}")
    e_de  = st.number_input("Driveline efficiency (0-1)", value=float(vp["driveline_efficiency"]), min_value=0.0, max_value=1.0, step=0.01, format="%.2f", key=f"e_de_{_vkv}")

    # ── Tyres / Loads / Traction ──
    st.markdown("**Tyres**")
    e_ts   = st.text_input("Tyre size",                 value=vp["tyre_size"],                   key=f"e_ts_{_vkv}")
    e_tr   = st.number_input("Loaded tyre radius (m)",  value=float(vp["tyre_radius"]),          min_value=0.01, step=0.005, format="%.3f", key=f"e_tr_{_vkv}")
    e_tt   = st.selectbox("Tyre type", TYRE_TYPES,
                           index=TYRE_TYPES.index(vp["tyre_type"]),                              key=f"e_tt_{_vkv}")

    st.markdown("**Vehicle Tyre Loads and Pressures**")
    e_ftp = st.number_input("Front tyre pressure (kPa)", value=float(vp["front_tyre_pressure_kPa"]), min_value=50.0, step=10.0, key=f"e_ftp_{_vkv}")
    e_rtp = st.number_input("Rear tyre pressure (kPa)",  value=float(vp["rear_tyre_pressure_kPa"]),  min_value=50.0, step=10.0, key=f"e_rtp_{_vkv}")
    e_fl_load = st.number_input("Front left base tyre load (kg)",  value=float(vp["front_left_base_tyre_load_kg"]),  min_value=0.0, step=10.0, key=f"e_fl_load_{_vkv}")
    e_fr_load = st.number_input("Front right base tyre load (kg)", value=float(vp["front_right_base_tyre_load_kg"]), min_value=0.0, step=10.0, key=f"e_fr_load_{_vkv}")
    e_rl_load = st.number_input("Rear left base tyre load (kg)",   value=float(vp["rear_left_base_tyre_load_kg"]),   min_value=0.0, step=10.0, key=f"e_rl_load_{_vkv}")
    e_rr_load = st.number_input("Rear right base tyre load (kg)",  value=float(vp["rear_right_base_tyre_load_kg"]),  min_value=0.0, step=10.0, key=f"e_rr_load_{_vkv}")

    st.markdown("**Axle Geometry and Limits**")
    e_wb = st.number_input("Wheelbase (mm)", value=float(vp["wheelbase_mm"]), min_value=0.0, step=25.0, key=f"e_wb_{_vkv}")
    e_tb_overhang = st.number_input("Rear axle to towball (mm)", value=float(vp["rear_axle_to_towball_mm"]), min_value=0.0, step=25.0, key=f"e_tb_overhang_{_vkv}")
    e_front_limit = st.number_input("Front axle limit (kg)", value=float(vp["front_axle_limit_kg"]), min_value=0.0, step=25.0, key=f"e_front_limit_{_vkv}")
    e_rear_limit = st.number_input("Rear axle limit (kg)", value=float(vp["rear_axle_limit_kg"]), min_value=0.0, step=25.0, key=f"e_rear_limit_{_vkv}")
    e_gvm_limit = st.number_input("GVM limit (kg)", value=float(vp["gvm_limit_kg"]), min_value=0.0, step=25.0, key=f"e_gvm_limit_{_vkv}")

    st.markdown("**Traction Limit**")
    e_drive = st.selectbox(
        "Driven axle type", DRIVEN_AXLE_TYPES,
        index=DRIVEN_AXLE_TYPES.index(vp.get("driven_axle_type", "AWD")),
        key=f"e_drive_{_vkv}"
    )
    e_mu = st.number_input("Tyre-road friction coefficient", value=float(vp["tyre_road_friction_coefficient"]), min_value=0.0, max_value=2.0, step=0.05, format="%.2f", key=f"e_mu_{_vkv}")

    # ── Aerodynamics ──
    st.markdown("**Aerodynamics**")
    e_cd = st.number_input("Vehicle Cd",             value=float(vp["Cd"]),           min_value=0.0, step=0.01, format="%.2f", key=f"e_cd_{_vkv}")
    e_fa = st.number_input("Frontal area (m²)",      value=float(vp["frontal_area"]), min_value=0.1, step=0.1,  format="%.2f", key=f"e_fa_{_vkv}")

    # ── Transmission ──
    st.markdown("**Transmission**")
    _gr_default = ", ".join(f"{r:.4g}" for r in vp["gear_ratios"])
    e_gr = st.text_input("Gear ratios (comma-separated)", value=_gr_default, key=f"e_gr_{_vkv}")

    # ── Generated Torque Curve Notice ──
    st.markdown("**Generated Torque Curve**")
    st.caption(
        "Torque curve points are generated automatically from peak torque, peak power, "
        "their RPM values, idle RPM and redline RPM. They are not directly editable."
    )

    # ── Buttons ──
    _ca, _cb = st.columns(2)
    _apply = _ca.button("Apply Changes",     key=f"apply_{vk}")
    _reset = _cb.button("Reset to Defaults", key=f"reset_{vk}")

    if _apply:
        _errors = []
        try:
            _new_gr  = [float(x.strip()) for x in e_gr.split(",") if x.strip()]
            if not _new_gr:
                _errors.append("At least one gear ratio is required.")
        except ValueError as _exc:
            _errors.append(f"Parse error: {_exc}")

        if _errors:
            for _e in _errors:
                st.error(_e)
        else:
            st.session_state["vehicle_profiles"][selected_vehicle] = {
                "vehicle_mass":        e_fl_load + e_fr_load + e_rl_load + e_rr_load,
                "rated_GCM":           GCM,
                "peak_torque_Nm":      e_ptq,
                "peak_torque_rpm":     int(e_ptq_rpm),
                "peak_power_kW":       e_ppw,
                "peak_power_rpm":      int(e_ppw_rpm),
                "idle_rpm":            int(e_idle),
                "redline_rpm":         int(e_redline),
                "generated_torque_curve": generate_torque_curve_from_profile(
                    e_ptq, e_ptq_rpm, e_ppw, e_ppw_rpm, e_idle, e_redline
                ),
                "torque_curve": generate_torque_curve_from_profile(
                    e_ptq, e_ptq_rpm, e_ppw, e_ppw_rpm, e_idle, e_redline
                ),  # legacy/reference field
                "final_drive_ratio":   e_fdr,
                "driveline_efficiency": e_de,
                "tyre_size":           e_ts,
                "tyre_radius":         e_tr,
                "tyre_type":           e_tt,
                "front_tyre_pressure_kPa": e_ftp,
                "rear_tyre_pressure_kPa":  e_rtp,
                "tyre_pressure_kPa":   e_ftp,  # legacy/reference field
                "num_vehicle_tyres":   4,
                "front_left_base_tyre_load_kg":  e_fl_load,
                "front_right_base_tyre_load_kg": e_fr_load,
                "rear_left_base_tyre_load_kg":   e_rl_load,
                "rear_right_base_tyre_load_kg":  e_rr_load,
                "wheelbase_mm":        e_wb,
                "rear_axle_to_towball_mm": e_tb_overhang,
                "front_axle_limit_kg": e_front_limit,
                "rear_axle_limit_kg":  e_rear_limit,
                "gvm_limit_kg":        e_gvm_limit,
                "driven_axle_type":    e_drive,
                "tyre_road_friction_coefficient": e_mu,
                "Cd":                  e_cd,
                "frontal_area":        e_fa,
                "gear_ratios":         _new_gr,
            }
            st.session_state[f"ev_ver_{vk}"] = _ver + 1
            st.success("✅ Profile updated for this session.")
            st.rerun()

    if _reset:
        _def = DEFAULT_VEHICLE_PROFILES[selected_vehicle]
        st.session_state["vehicle_profiles"][selected_vehicle] = enrich_vehicle_profile(selected_vehicle, _def)
        st.session_state[f"ev_ver_{vk}"] = _ver + 1
        st.success("✅ Reset to defaults.")
        st.rerun()

    # ── Download JSON ──
    def _profiles_json():
        out = {}
        for _n, _p in st.session_state["vehicle_profiles"].items():
            _pc = dict(_p)
            if "torque_curve" in _pc:
                _pc["torque_curve"] = [list(pt) for pt in _pc["torque_curve"]]
            if "generated_torque_curve" in _pc:
                _pc["generated_torque_curve"] = [list(pt) for pt in _pc["generated_torque_curve"]]
            out[_n] = _pc
        return json.dumps(out, indent=2)

    st.download_button(
        "📥 Download Profiles JSON",
        _profiles_json(),
        file_name="vehicle_profiles.json",
        mime="application/json",
        key=f"dl_{vk}",
    )

st.sidebar.divider()

# ── Trailer Profile ───────────────────────────────────────────────────────────────

st.sidebar.subheader("Fixed Dual-Axle Trailer Profile")
selected_trailer = st.sidebar.selectbox(
    "Select Trailer Profile", list(st.session_state["trailer_profiles"].keys())
)
tp = st.session_state["trailer_profiles"][selected_trailer]
tk = selected_trailer
_tver = st.session_state.get(f"et_ver_{tk}", 0)
_tkv = f"{tk}_v{_tver}"

# Normal trailer input: only trailer mass is entered by the user.
_weight_profiles_default = sorted(tp.get("weight_profiles", tp.get("interpolation_points", [])), key=lambda p: p["trailer_mass_kg"])
_trailer_mass_default = float(_weight_profiles_default[-1]["trailer_mass_kg"]) if _weight_profiles_default else 3500.0
m_trailer = st.sidebar.number_input(
    "Trailer mass / trailer weight (kg)",
    value=_trailer_mass_default,
    min_value=0.0,
    step=50.0,
    key=f"tm_{tk}",
)

# Interpolate trailer ball load and wheel loads from profile points.
trailer_interp, trailer_extrapolated, trailer_points = interpolate_trailer_profile(tp, m_trailer)
tow_ball_mass = trailer_interp["tow_ball_mass_kg"]
trailer_fl_load_kg = trailer_interp["front_left_tyre_load_kg"]
trailer_fr_load_kg = trailer_interp["front_right_tyre_load_kg"]
trailer_rl_load_kg = trailer_interp["rear_left_tyre_load_kg"]
trailer_rr_load_kg = trailer_interp["rear_right_tyre_load_kg"]

num_trailer_tyres = int(tp["number_of_tyres"])
trailer_tyre_pressure = float(tp["tyre_pressure_kPa"])
trailer_tyre_type = tp["tyre_type"]
trailer_tyre_radius = float(tp["tyre_radius_m"])
Cd_trailer = float(tp["trailer_Cd"])
frontal_width = float(tp["frontal_width_m"])
frontal_height = float(tp["frontal_height_m"])
A_trailer = float(tp.get("frontal_area_m2", frontal_width * frontal_height))

if trailer_extrapolated:
    st.sidebar.warning(
        "The entered trailer mass is outside the calibrated trailer profile range. "
        "Trailer ball load and wheel loads are extrapolated."
    )

with st.sidebar.expander("Trailer Plot", expanded=False):
    if trailer_points:
        df_tp_plot = pd.DataFrame(trailer_points).sort_values("trailer_mass_kg")
        fig_t, ax_t = plt.subplots(figsize=(7, 4))
        x = df_tp_plot["trailer_mass_kg"]
        ax_t.plot(x, df_tp_plot["tow_ball_mass_kg"], marker="o", label="Towball mass")
        ax_t.plot(x, df_tp_plot["front_left_tyre_load_kg"], marker="o", label="Front left tyre load")
        ax_t.plot(x, df_tp_plot["front_right_tyre_load_kg"], marker="o", label="Front right tyre load")
        ax_t.plot(x, df_tp_plot["rear_left_tyre_load_kg"], marker="o", label="Rear left tyre load")
        ax_t.plot(x, df_tp_plot["rear_right_tyre_load_kg"], marker="o", label="Rear right tyre load")
        ax_t.axvline(m_trailer, linestyle="--", linewidth=1.2, label="Current trailer mass")
        ax_t.set_xlabel("Trailer mass (kg)")
        ax_t.set_ylabel("Mass/load (kg)")
        ax_t.set_title("Trailer profile interpolation curves")
        ax_t.legend(fontsize=7)
        ax_t.spines["top"].set_visible(False)
        ax_t.spines["right"].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig_t)
        plt.close(fig_t)
        st.dataframe(df_tp_plot, use_container_width=True, hide_index=True)
    else:
        st.info("No trailer interpolation points are available for this profile.")

with st.sidebar.expander("✏️ Edit Trailer Profiles", expanded=False):
    st.caption("Changes apply to this browser session only. Download JSON to save trailer profiles for future reference.")

    st.markdown("**Trailer Geometry and Tyres**")
    et_axles = st.number_input("Number of axles", value=int(tp["number_of_axles"]), min_value=1, step=1, key=f"et_axles_{_tkv}")
    et_tyres = st.number_input("Number of tyres", value=int(tp["number_of_tyres"]), min_value=1, step=1, key=f"et_tyres_{_tkv}")
    et_ts = st.text_input("Tyre size", value=tp["tyre_size"], key=f"et_ts_{_tkv}")
    et_tp = st.number_input("Tyre pressure (kPa)", value=float(tp["tyre_pressure_kPa"]), min_value=50.0, step=10.0, key=f"et_tp_{_tkv}")
    et_tr = st.number_input("Loaded tyre radius (m)", value=float(tp["tyre_radius_m"]), min_value=0.01, step=0.005, format="%.3f", key=f"et_tr_{_tkv}")
    et_tt = st.selectbox("Tyre type", TYRE_TYPES, index=TYRE_TYPES.index(tp["tyre_type"]), key=f"et_tt_{_tkv}")

    st.markdown("**Aerodynamics**")
    et_cd = st.number_input("Trailer Cd", value=float(tp["trailer_Cd"]), min_value=0.0, step=0.01, format="%.2f", key=f"et_cd_{_tkv}")
    et_fw = st.number_input("Frontal width (m)", value=float(tp["frontal_width_m"]), min_value=0.1, step=0.05, format="%.2f", key=f"et_fw_{_tkv}")
    et_fh = st.number_input("Frontal height (m)", value=float(tp["frontal_height_m"]), min_value=0.1, step=0.05, format="%.2f", key=f"et_fh_{_tkv}")
    et_fa = st.number_input("Frontal area (m²)", value=float(tp.get("frontal_area_m2", et_fw * et_fh)), min_value=0.1, step=0.05, format="%.2f", key=f"et_fa_{_tkv}")

    st.markdown("**Trailer Weight Profiles**")
    st.caption(
        "Each row is one measured or estimated trailer loading condition. "
        "The app interpolates towball mass and wheel loads from these rows based on the entered trailer mass."
    )

    _wp_state_key = f"trailer_weight_profiles_editor_{_tkv}"
    if _wp_state_key not in st.session_state:
        st.session_state[_wp_state_key] = [
            dict(wp) for wp in sorted(tp.get("weight_profiles", tp.get("interpolation_points", [])), key=lambda p: p["trailer_mass_kg"])
        ]

    if st.button("Add Weight Profile", key=f"add_wp_{_tkv}"):
        st.session_state[_wp_state_key].append(build_new_weight_profile(st.session_state[_wp_state_key]))
        st.rerun()

    _wp_df_source = pd.DataFrame(st.session_state[_wp_state_key])
    if _wp_df_source.empty:
        _wp_df_source = pd.DataFrame([build_new_weight_profile([]), build_new_weight_profile([build_new_weight_profile([])])])

    _wp_df_source = _wp_df_source[[
        "profile_name",
        "trailer_mass_kg",
        "tow_ball_mass_kg",
        "front_left_tyre_load_kg",
        "front_right_tyre_load_kg",
        "rear_left_tyre_load_kg",
        "rear_right_tyre_load_kg",
    ]]

    edited_weight_profiles_df = st.data_editor(
        _wp_df_source,
        key=f"wp_editor_{_tkv}",
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "profile_name": st.column_config.TextColumn("Profile name"),
            "trailer_mass_kg": st.column_config.NumberColumn("Trailer mass (kg)", min_value=0.0, step=50.0, format="%.1f"),
            "tow_ball_mass_kg": st.column_config.NumberColumn("Towball mass (kg)", min_value=0.0, step=10.0, format="%.1f"),
            "front_left_tyre_load_kg": st.column_config.NumberColumn("Front left tyre load (kg)", min_value=0.0, step=10.0, format="%.1f"),
            "front_right_tyre_load_kg": st.column_config.NumberColumn("Front right tyre load (kg)", min_value=0.0, step=10.0, format="%.1f"),
            "rear_left_tyre_load_kg": st.column_config.NumberColumn("Rear left tyre load (kg)", min_value=0.0, step=10.0, format="%.1f"),
            "rear_right_tyre_load_kg": st.column_config.NumberColumn("Rear right tyre load (kg)", min_value=0.0, step=10.0, format="%.1f"),
        },
    )
    st.caption("Use Add Weight Profile to append a row. Rows can also be edited directly in the table. Keep at least two rows for interpolation.")

    _ta, _tb = st.columns(2)
    _t_apply = _ta.button("Apply Trailer Profile Changes", key=f"t_apply_{tk}")
    _t_reset = _tb.button("Reset Trailer Profile to Defaults", key=f"t_reset_{tk}")

    if _t_apply:
        _errors = []
        _new_weight_profiles = []
        try:
            _wp_df = edited_weight_profiles_df.copy()
            _wp_df = _wp_df.dropna(how="all")
            for i, row in _wp_df.iterrows():
                profile_name = str(row.get("profile_name", "")).strip() or f"Weight profile {len(_new_weight_profiles) + 1}"
                wp = {
                    "profile_name": profile_name,
                    "trailer_mass_kg": float(row.get("trailer_mass_kg", 0.0)),
                    "tow_ball_mass_kg": float(row.get("tow_ball_mass_kg", 0.0)),
                    "front_left_tyre_load_kg": float(row.get("front_left_tyre_load_kg", 0.0)),
                    "front_right_tyre_load_kg": float(row.get("front_right_tyre_load_kg", 0.0)),
                    "rear_left_tyre_load_kg": float(row.get("rear_left_tyre_load_kg", 0.0)),
                    "rear_right_tyre_load_kg": float(row.get("rear_right_tyre_load_kg", 0.0)),
                }
                _new_weight_profiles.append(wp)

            if len(_new_weight_profiles) < 2:
                _errors.append("At least two trailer weight profiles are required for interpolation.")

            _masses_check = [wp["trailer_mass_kg"] for wp in _new_weight_profiles]
            if len(_masses_check) != len(set(_masses_check)):
                _errors.append("Trailer mass values must be unique across weight profiles.")

            for wp in _new_weight_profiles:
                for _key in [
                    "trailer_mass_kg",
                    "tow_ball_mass_kg",
                    "front_left_tyre_load_kg",
                    "front_right_tyre_load_kg",
                    "rear_left_tyre_load_kg",
                    "rear_right_tyre_load_kg",
                ]:
                    if wp[_key] < 0:
                        _errors.append(f"{wp['profile_name']}: {_key} cannot be negative.")
        except (TypeError, ValueError) as _exc:
            _errors.append(f"Parse error: {_exc}")

        if _errors:
            for _e in _errors:
                st.error(_e)
        else:
            _new_weight_profiles = sorted(_new_weight_profiles, key=lambda p: p["trailer_mass_kg"])
            st.session_state["trailer_profiles"][selected_trailer] = enrich_trailer_profile(selected_trailer, {
                "profile_name": selected_trailer,
                "number_of_axles": int(et_axles),
                "number_of_tyres": int(et_tyres),
                "tyre_size": et_ts,
                "tyre_pressure_kPa": et_tp,
                "tyre_radius_m": et_tr,
                "tyre_type": et_tt,
                "trailer_Cd": et_cd,
                "frontal_width_m": et_fw,
                "frontal_height_m": et_fh,
                "frontal_area_m2": et_fa,
                "weight_profiles": _new_weight_profiles,
            })
            if _wp_state_key in st.session_state:
                del st.session_state[_wp_state_key]
            st.session_state[f"et_ver_{tk}"] = _tver + 1
            st.success("✅ Trailer profile updated for this session.")
            st.rerun()

    if _t_reset:
        _def_t = DEFAULT_TRAILER_PROFILES[selected_trailer]
        st.session_state["trailer_profiles"][selected_trailer] = enrich_trailer_profile(selected_trailer, _def_t)
        st.session_state[f"et_ver_{tk}"] = _tver + 1
        st.success("✅ Trailer profile reset to defaults.")
        st.rerun()

    def _trailer_profiles_json():
        return json.dumps(st.session_state["trailer_profiles"], indent=2)

    st.download_button(
        "📥 Download Trailer Profiles JSON",
        _trailer_profiles_json(),
        file_name="trailer_profiles.json",
        mime="application/json",
        key=f"t_dl_{tk}",
    )

st.sidebar.divider()

# ── Environmental & Operating Conditions ─────────────────────────────────────────

st.sidebar.subheader("Environmental Conditions")
ambient_temperature_C = st.sidebar.number_input(
    "Ambient temperature (°C)", value=20.0, step=1.0, format="%.1f"
)
average_wind_kmh = st.sidebar.number_input(
    "Average wind speed (km/h)", value=0.0, min_value=0.0, step=1.0, format="%.1f"
)
maximum_wind_kmh = st.sidebar.number_input(
    "Maximum wind speed (km/h)", value=0.0, min_value=0.0, step=1.0, format="%.1f"
)
st.sidebar.caption(
    "Average wind is used for the expected acceleration result. Maximum wind is used "
    "for the worst-case acceleration result. Both are currently treated as direct headwinds."
)

standard_pressure_Pa = 101325.0
temperature_K = ambient_temperature_C + 273.15
if temperature_K <= 0:
    st.sidebar.error("Ambient temperature must be above absolute zero (-273.15 °C).")
    air_density = 1.225
else:
    air_density = standard_pressure_Pa / (287.05 * temperature_K)

average_wind_mps = average_wind_kmh / 3.6
maximum_wind_mps = maximum_wind_kmh / 3.6

environmental_conditions = {
    "source": "Manual",
    "location": "Manual input",
    "date": "",
    "ambient_temperature_C": ambient_temperature_C,
    "average_wind_kmh": average_wind_kmh,
    "maximum_wind_kmh": maximum_wind_kmh,
}

st.sidebar.caption(f"Calculated air density: {air_density:.3f} kg/m³")
st.sidebar.divider()

st.sidebar.subheader("Phase 1 — Operating Condition")
speed_kmh = st.sidebar.number_input(
    "Vehicle speed (km/h)", value=100.0, min_value=0.0, step=5.0
)

# ─── READ PROFILE VALUES ─────────────────────────────────────────────────────────
# Re-read vp after any edits (session state may have changed via Apply button).
vp = st.session_state["vehicle_profiles"][selected_vehicle]

final_drive_ratio    = vp["final_drive_ratio"]
driveline_efficiency = vp["driveline_efficiency"]
tyre_radius          = vp["tyre_radius"]
vehicle_tyre_type    = vp["tyre_type"]
front_tyre_pressure  = vp["front_tyre_pressure_kPa"]
rear_tyre_pressure   = vp["rear_tyre_pressure_kPa"]
Cd_vehicle           = vp["Cd"]
A_vehicle            = vp["frontal_area"]
peak_power_kW        = vp["peak_power_kW"]
active_torque_curve  = get_active_torque_curve(vp)
driven_axle_type     = vp["driven_axle_type"]
tyre_road_mu         = vp["tyre_road_friction_coefficient"]
wheelbase_mm         = float(vp["wheelbase_mm"])
rear_axle_to_towball_mm = float(vp["rear_axle_to_towball_mm"])
front_axle_limit_kg  = float(vp["front_axle_limit_kg"])
rear_axle_limit_kg   = float(vp["rear_axle_limit_kg"])
gvm_limit_kg         = float(vp["gvm_limit_kg"])

# ─── PHASE 1 CALCULATIONS ────────────────────────────────────────────────────────

V = speed_kmh / 3.6   # m/s

# Vehicle test mass and combination mass are calculated from individual tyre loads below.
Crr_vehicle_front = estimate_crr(vehicle_tyre_type, front_tyre_pressure)
Crr_vehicle_rear  = estimate_crr(vehicle_tyre_type, rear_tyre_pressure)
Crr_vehicle = (Crr_vehicle_front + Crr_vehicle_rear) / 2.0
Crr_trailer = estimate_crr(trailer_tyre_type, trailer_tyre_pressure)

# Vehicle individual tyre loads. Base loads are stored in the vehicle profile.
# The trailer towball download creates axle load transfer using the TD method:
# front change = -ball_mass × rear_axle_to_towball / wheelbase
# rear change  =  ball_mass × (1 + rear_axle_to_towball / wheelbase)
fl_base_kg = float(vp["front_left_base_tyre_load_kg"])
fr_base_kg = float(vp["front_right_base_tyre_load_kg"])
rl_base_kg = float(vp["rear_left_base_tyre_load_kg"])
rr_base_kg = float(vp["rear_right_base_tyre_load_kg"])

front_axle_unhitched_kg = fl_base_kg + fr_base_kg
rear_axle_unhitched_kg = rl_base_kg + rr_base_kg
vehicle_test_mass_unhitched_kg = front_axle_unhitched_kg + rear_axle_unhitched_kg

# Use wheel-load-derived vehicle mass as the source of truth for all mass calculations.
m_total = vehicle_test_mass_unhitched_kg + m_trailer
GCM_utilisation = (m_total / GCM) * 100.0 if GCM > 0 else 0.0

if wheelbase_mm > 0:
    towball_lever_ratio = rear_axle_to_towball_mm / wheelbase_mm
    front_axle_change_kg = -tow_ball_mass * towball_lever_ratio
    rear_axle_change_kg = tow_ball_mass * (1.0 + towball_lever_ratio)
else:
    towball_lever_ratio = 0.0
    front_axle_change_kg = 0.0
    rear_axle_change_kg = tow_ball_mass

front_axle_connected_kg = front_axle_unhitched_kg + front_axle_change_kg
rear_axle_connected_kg = rear_axle_unhitched_kg + rear_axle_change_kg
vehicle_test_mass_connected_kg = front_axle_connected_kg + rear_axle_connected_kg
expected_vehicle_connected_kg = vehicle_test_mass_unhitched_kg + tow_ball_mass

# Split connected axle loads equally left/right for this first-order model.
fl_loaded_kg = front_axle_connected_kg / 2.0
fr_loaded_kg = front_axle_connected_kg / 2.0
rl_loaded_kg = rear_axle_connected_kg / 2.0
rr_loaded_kg = rear_axle_connected_kg / 2.0

fl_added_ball_kg = fl_loaded_kg - fl_base_kg
fr_added_ball_kg = fr_loaded_kg - fr_base_kg
rl_added_ball_kg = rl_loaded_kg - rl_base_kg
rr_added_ball_kg = rr_loaded_kg - rr_base_kg

fl_load_N = fl_loaded_kg * g
fr_load_N = fr_loaded_kg * g
rl_load_N = rl_loaded_kg * g
rr_load_N = rr_loaded_kg * g

front_loaded_N = fl_load_N + fr_load_N
rear_loaded_N  = rl_load_N + rr_load_N
loaded_vehicle_tyre_total_N = front_loaded_N + rear_loaded_N
base_vehicle_tyre_mass_kg = vehicle_test_mass_unhitched_kg
loaded_vehicle_tyre_mass_kg = vehicle_test_mass_connected_kg

trailer_fl_load_N = trailer_fl_load_kg * g
trailer_fr_load_N = trailer_fr_load_kg * g
trailer_rl_load_N = trailer_rl_load_kg * g
trailer_rr_load_N = trailer_rr_load_kg * g
trailer_tyre_supported_mass = max(0.0, trailer_fl_load_kg + trailer_fr_load_kg + trailer_rl_load_kg + trailer_rr_load_kg)
expected_trailer_tyre_supported_mass = max(0.0, m_trailer - tow_ball_mass)
trailer_supported_mass_diff = trailer_tyre_supported_mass - expected_trailer_tyre_supported_mass
avg_trailer_load_per_tyre_N = (trailer_tyre_supported_mass * g) / max(num_trailer_tyres, 1)

# Rolling resistance from tyre vertical loads.
F_rr_vehicle = (Crr_vehicle_front * front_loaded_N) + (Crr_vehicle_rear * rear_loaded_N)
F_rr_trailer = Crr_trailer * trailer_tyre_supported_mass * g

relative_air_speed_p1_mps = V + average_wind_mps
F_aero_vehicle = 0.5 * air_density * Cd_vehicle * A_vehicle * relative_air_speed_p1_mps ** 2
F_aero_trailer = 0.5 * air_density * Cd_trailer * A_trailer * relative_air_speed_p1_mps ** 2

F_resistance_total = F_rr_vehicle + F_rr_trailer + F_aero_vehicle + F_aero_trailer

# Automatic gear selection
gear_rows_p1, best_idx_p1 = select_best_gear(
    gear_ratios          = vp["gear_ratios"],
    final_drive_ratio    = final_drive_ratio,
    driveline_efficiency = driveline_efficiency,
    tyre_radius_m        = tyre_radius,
    idle_rpm             = vp["idle_rpm"],
    redline_rpm          = vp["redline_rpm"],
    torque_curve         = active_torque_curve,
    peak_power_W         = peak_power_kW * 1000.0,
    V_mps                = V,
    fallback_torque_Nm   = vp["peak_torque_Nm"],
)

if best_idx_p1 is not None:
    _bp1       = gear_rows_p1[best_idx_p1]
    p1_gear    = _bp1["Gear"]
    p1_ratio   = _bp1["Gear Ratio"]
    p1_rpm     = _bp1["Effective RPM"]
    p1_torque  = _bp1["Torque (Nm)"]
    p1_power_W = _bp1["Cap Power (W)"]
    p1_F_tq    = _bp1["F_torque (N)"]
    p1_F_pw    = _bp1["F_power (N)"]
    F_engine_available = _bp1["F_available (N)"]
    T_wheel    = (p1_torque * p1_ratio * final_drive_ratio * driveline_efficiency
                  if p1_torque else 0.0)
else:
    p1_gear = p1_ratio = p1_rpm = p1_torque = p1_power_W = p1_F_tq = p1_F_pw = None
    F_engine_available = 0.0
    T_wheel = 0.0

# Basic tyre-road friction limit based on driven axle normal load.
if driven_axle_type == "RWD":
    driven_axle_normal_N = rear_loaded_N
elif driven_axle_type == "FWD":
    driven_axle_normal_N = front_loaded_N
else:  # AWD
    driven_axle_normal_N = loaded_vehicle_tyre_total_N

F_traction_limit = tyre_road_mu * driven_axle_normal_N
F_available = min(F_engine_available, F_traction_limit)
traction_limited = F_available < F_engine_available

F_net   = F_available - F_resistance_total
a       = F_net / m_total if m_total > 0 else 0.0
F_hitch = m_trailer * a + F_rr_trailer + F_aero_trailer

# ─── PHASE 2A — TYRE GEOMETRY & ADJUSTED CRR ─────────────────────────────────────

veh_tyre_geom = parse_tyre_size(vp["tyre_size"])
trl_tyre_geom = parse_tyre_size(tp["tyre_size"])

veh_unloaded_r = veh_tyre_geom["unloaded_radius_m"] if veh_tyre_geom else tyre_radius
trl_unloaded_r = trl_tyre_geom["unloaded_radius_m"] if trl_tyre_geom else trailer_tyre_radius

veh_deflection = max(0.0, veh_unloaded_r - tyre_radius)
trl_deflection = max(0.0, trl_unloaded_r - trailer_tyre_radius)

veh_sw = veh_tyre_geom["section_width_m"] if veh_tyre_geom else 0.265
trl_sw = trl_tyre_geom["section_width_m"] if trl_tyre_geom else 0.235

# Individual vehicle contact patches use loaded tyre loads and front/rear pressures.
fl_cp_area, fl_cp_len = calc_contact_patch(fl_load_N, front_tyre_pressure, veh_sw)
fr_cp_area, fr_cp_len = calc_contact_patch(fr_load_N, front_tyre_pressure, veh_sw)
rl_cp_area, rl_cp_len = calc_contact_patch(rl_load_N, rear_tyre_pressure, veh_sw)
rr_cp_area, rr_cp_len = calc_contact_patch(rr_load_N, rear_tyre_pressure, veh_sw)

veh_cp_area = (fl_cp_area + fr_cp_area + rl_cp_area + rr_cp_area) / 4.0
veh_cp_len  = (fl_cp_len + fr_cp_len + rl_cp_len + rr_cp_len) / 4.0
trl_fl_cp_area, trl_fl_cp_len = calc_contact_patch(trailer_fl_load_N, trailer_tyre_pressure, trl_sw)
trl_fr_cp_area, trl_fr_cp_len = calc_contact_patch(trailer_fr_load_N, trailer_tyre_pressure, trl_sw)
trl_rl_cp_area, trl_rl_cp_len = calc_contact_patch(trailer_rl_load_N, trailer_tyre_pressure, trl_sw)
trl_rr_cp_area, trl_rr_cp_len = calc_contact_patch(trailer_rr_load_N, trailer_tyre_pressure, trl_sw)
trl_cp_area = (trl_fl_cp_area + trl_fr_cp_area + trl_rl_cp_area + trl_rr_cp_area) / 4.0
trl_cp_len = (trl_fl_cp_len + trl_fr_cp_len + trl_rl_cp_len + trl_rr_cp_len) / 4.0

Crr_veh_p2 = calc_crr_p2(vehicle_tyre_type, tyre_radius, veh_unloaded_r)
Crr_trl_p2 = calc_crr_p2(trailer_tyre_type, trailer_tyre_radius, trl_unloaded_r)

# ─── MAIN AREA ───────────────────────────────────────────────────────────────────

st.title("GCM Level Road Calculator")
st.markdown(
    """
    **Phase 1 — Level Road Steady-State Calculator.**
    Estimates towing performance for a vehicle and trailer on a flat, level road at a
    single selected speed. Gear is selected automatically from the vehicle profile using
    engine RPM and the torque curve. All inputs and outputs use SI units.
    """
)

gcm_exceeded  = m_total > GCM
net_negative  = F_net < 0
no_valid_gear = best_idx_p1 is None

if gcm_exceeded:
    st.error(
        f"GCM EXCEEDED: Combination mass {m_total:,.0f} kg > "
        f"rated GCM {GCM:,.0f} kg  (over by {m_total - GCM:,.0f} kg)."
    )
if no_valid_gear:
    st.error(
        f"NO VALID GEAR at {speed_kmh:.0f} km/h — all gears exceed the "
        f"redline ({vp['redline_rpm']:,} RPM)."
    )
elif net_negative:
    st.warning(
        f"Net force is {F_net:,.0f} N. "
        "The vehicle cannot maintain speed or accelerate at this condition."
    )

# Warn if the stored/reference vehicle mass does not match the wheel-load-derived vehicle test mass.
if reference_vehicle_mass > 0 and abs(reference_vehicle_mass - vehicle_test_mass_unhitched_kg) > 0.02 * reference_vehicle_mass:
    st.warning(
        "The reference vehicle mass does not match the sum of individual base tyre loads. "
        "Calculations are using the individual tyre loads."
    )

# ─── ENVIRONMENTAL SUMMARY ──────────────────────────────────────────────────────

with st.expander("Environmental Summary", expanded=False):
    _ec1, _ec2, _ec3 = st.columns(3)
    _ec1.metric("Ambient Temperature", f"{ambient_temperature_C:.1f} °C")
    _ec2.metric("Calculated Air Density", f"{air_density:.3f} kg/m³")
    _ec3.metric("Standard Pressure", "101.325 kPa")
    _ew1, _ew2, _ew3 = st.columns(3)
    _ew1.metric("Average Wind", f"{average_wind_kmh:.1f} km/h")
    _ew2.metric("Maximum Wind", f"{maximum_wind_kmh:.1f} km/h")
    _ew3.metric("Phase 1 Relative Airspeed", f"{relative_air_speed_p1_mps * 3.6:.1f} km/h")
    st.caption(
        "Temperature affects aerodynamic resistance through air density. Average wind "
        "represents expected conditions, while maximum wind represents a worst-case steady "
        "headwind. Wind direction, crosswind, yaw and gust duration are not yet modelled."
    )

# ─── PROFILE SUMMARY ─────────────────────────────────────────────────────────────

with st.expander("Profile Summary", expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Vehicle**")
        st.write(f"Profile: {selected_vehicle}")
        st.write(f"Vehicle test mass from wheel loads: {vehicle_test_mass_unhitched_kg:,.0f} kg  |  Rated GCM: {GCM:,.0f} kg")
        st.write(f"Peak torque: {vp['peak_torque_Nm']:.0f} Nm @ {vp['peak_torque_rpm']:,} RPM")
        st.write(f"Peak power:  {vp['peak_power_kW']:.0f} kW @ {vp['peak_power_rpm']:,} RPM")
        st.write(f"Idle RPM: {vp['idle_rpm']:,}  |  Redline RPM: {vp['redline_rpm']:,}")
        st.write(f"Final drive: {final_drive_ratio:.3f}  |  Driveline eff: {driveline_efficiency:.2f}")
        st.write(f"Tyre: {vp['tyre_size']}  ({vehicle_tyre_type})")
        st.write(f"Front pressure: {front_tyre_pressure:.0f} kPa  |  Rear pressure: {rear_tyre_pressure:.0f} kPa")
        st.write(f"Unloaded r: {veh_unloaded_r:.3f} m  |  Loaded r: {tyre_radius:.3f} m  |  Deflection: {veh_deflection*1000:.1f} mm")
        st.write(f"Front axle loaded: {front_loaded_N/g:,.1f} kg  |  Rear axle loaded: {rear_loaded_N/g:,.1f} kg")
        st.write(f"Loaded tyre mass total: {loaded_vehicle_tyre_mass_kg:,.1f} kg")
        st.write(f"Average contact patch: {veh_cp_area*10000:.1f} cm²  ×  {veh_cp_len*100:.1f} cm")
        st.write(f"Driven axle: {driven_axle_type}  |  μ: {tyre_road_mu:.2f}")
        st.write(f"Wheelbase: {wheelbase_mm:.0f} mm  |  Rear axle to towball: {rear_axle_to_towball_mm:.0f} mm")
        st.write(f"Axle limits F/R: {front_axle_limit_kg:.0f} / {rear_axle_limit_kg:.0f} kg  |  GVM: {gvm_limit_kg:.0f} kg")
        st.write(f"Vehicle Cd: {Cd_vehicle:.2f}  |  Frontal area: {A_vehicle:.2f} m²")
        st.write(f"Phase 1 Crr: {Crr_vehicle:.5f}  |  Phase 2A Crr: {Crr_veh_p2:.5f}")
        st.write(f"Gear ratios: {vp['gear_ratios']}")
    with c2:
        st.markdown("**Trailer**")
        st.write(f"Profile: {selected_trailer}")
        st.write(f"Trailer mass: {m_trailer:,.0f} kg  |  Tow ball: {tow_ball_mass:,.0f} kg")
        st.write(f"Tyre-supported mass: {trailer_tyre_supported_mass:,.0f} kg")
        st.write(f"Tyre: {tp['tyre_size']}  ({trailer_tyre_type}, {trailer_tyre_pressure:.0f} kPa)")
        st.write(f"Unloaded r: {trl_unloaded_r:.3f} m  |  Loaded r: {trailer_tyre_radius:.3f} m  |  Deflection: {trl_deflection*1000:.1f} mm")
        st.write(f"Interpolated tyre-supported mass: {trailer_tyre_supported_mass:,.1f} kg")
        st.write(f"Average contact patch: {trl_cp_area*10000:.1f} cm²  ×  {trl_cp_len*100:.1f} cm")
        st.write(f"Trailer Cd: {Cd_trailer:.2f}  |  Frontal area: {A_trailer:.2f} m²  ({frontal_width:.2f} × {frontal_height:.2f} m)")
        st.write(f"Phase 1 Crr: {Crr_trailer:.5f}  |  Phase 2A Crr: {Crr_trl_p2:.5f}")
    st.markdown("---")
    st.markdown("**Combination**")
    _cc1, _cc2, _cc3 = st.columns(3)
    _cc1.write(f"Total mass: {m_total:,.0f} kg")
    _cc1.write(f"Vehicle test mass source: wheel loads ({vehicle_test_mass_unhitched_kg:,.0f} kg)")
    _cc2.write(f"Rated GCM: {GCM:,.0f} kg")
    _cc3.write(f"GCM utilisation: {GCM_utilisation:.1f}%")
    st.caption(
        "Rolling resistance is estimated from tyre type, tyre loading, pressure and "
        "loaded-radius correction. Contact patch values are engineering approximations."
    )


# ─── GENERATED TORQUE CURVE ───────────────────────────────────────────────────

with st.expander("Generated Torque Curve", expanded=False):
    torque_curve_rows = []
    for rpm, tq in active_torque_curve:
        power_kW = tq * rpm * 2.0 * math.pi / 60.0 / 1000.0
        torque_curve_rows.append({
            "RPM": round(rpm, 0),
            "Torque (Nm)": round(tq, 1),
            "Power (kW)": round(power_kW, 1),
        })
    df_torque_curve = pd.DataFrame(torque_curve_rows)
    st.caption(
        "This estimated torque curve is generated automatically from peak torque, peak power, "
        "their RPM values, idle RPM and redline RPM. It is used for gear selection and acceleration calculations."
    )
    st.dataframe(df_torque_curve, use_container_width=True, hide_index=True)

    if len(df_torque_curve) >= 2:
        fig_tc, ax_tc = plt.subplots(figsize=(8, 4))
        ax_tc.plot(df_torque_curve["RPM"], df_torque_curve["Torque (Nm)"], marker="o", linewidth=2, label="Torque")
        ax_tc.set_xlabel("Engine speed (RPM)")
        ax_tc.set_ylabel("Torque (Nm)")
        ax_tc.set_title("Generated Torque and Power Curve", fontweight="bold")
        ax_tc.spines["top"].set_visible(False)
        ax_tc.spines["right"].set_visible(False)

        ax_pw = ax_tc.twinx()
        ax_pw.plot(df_torque_curve["RPM"], df_torque_curve["Power (kW)"], marker="s", linestyle="--", linewidth=2, label="Power")
        ax_pw.set_ylabel("Power (kW)")

        lines_1, labels_1 = ax_tc.get_legend_handles_labels()
        lines_2, labels_2 = ax_pw.get_legend_handles_labels()
        ax_tc.legend(lines_1 + lines_2, labels_1 + labels_2, loc="best")
        plt.tight_layout()
        st.pyplot(fig_tc)
        plt.close(fig_tc)

# ─── VEHICLE AXLE LOAD TRANSFER ────────────────────────────────────────────────

with st.expander("Vehicle Axle Load Transfer", expanded=False):
    axle_rows = [
        {"Item": "Front axle unhitched load", "Value": front_axle_unhitched_kg, "Units": "kg", "Check": ""},
        {"Item": "Rear axle unhitched load", "Value": rear_axle_unhitched_kg, "Units": "kg", "Check": ""},
        {"Item": "Vehicle test mass unhitched", "Value": vehicle_test_mass_unhitched_kg, "Units": "kg", "Check": ""},
        {"Item": "Towball download", "Value": tow_ball_mass, "Units": "kg", "Check": ""},
        {"Item": "Wheelbase", "Value": wheelbase_mm, "Units": "mm", "Check": ""},
        {"Item": "Rear axle to towball", "Value": rear_axle_to_towball_mm, "Units": "mm", "Check": ""},
        {"Item": "Front axle load change", "Value": front_axle_change_kg, "Units": "kg", "Check": ""},
        {"Item": "Rear axle load change", "Value": rear_axle_change_kg, "Units": "kg", "Check": ""},
        {"Item": "Front axle connected load", "Value": front_axle_connected_kg, "Units": "kg", "Check": "PASS" if front_axle_connected_kg <= front_axle_limit_kg else "FAIL"},
        {"Item": "Rear axle connected load", "Value": rear_axle_connected_kg, "Units": "kg", "Check": "PASS" if rear_axle_connected_kg <= rear_axle_limit_kg else "FAIL"},
        {"Item": "Vehicle test mass connected", "Value": vehicle_test_mass_connected_kg, "Units": "kg", "Check": "PASS" if vehicle_test_mass_connected_kg <= gvm_limit_kg else "FAIL"},
        {"Item": "Expected connected total", "Value": expected_vehicle_connected_kg, "Units": "kg", "Check": ""},
        {"Item": "Front axle limit", "Value": front_axle_limit_kg, "Units": "kg", "Check": ""},
        {"Item": "Rear axle limit", "Value": rear_axle_limit_kg, "Units": "kg", "Check": ""},
        {"Item": "GVM limit", "Value": gvm_limit_kg, "Units": "kg", "Check": ""},
    ]
    st.dataframe(pd.DataFrame(axle_rows).round({"Value": 1}), use_container_width=True, hide_index=True)

    _ax1, _ax2, _ax3 = st.columns(3)
    _ax1.metric("Front axle connected", f"{front_axle_connected_kg:,.1f} kg", delta=f"Limit {front_axle_limit_kg:,.0f} kg", delta_color="off")
    _ax2.metric("Rear axle connected", f"{rear_axle_connected_kg:,.1f} kg", delta=f"Limit {rear_axle_limit_kg:,.0f} kg", delta_color="off")
    _ax3.metric("Connected vehicle mass", f"{vehicle_test_mass_connected_kg:,.1f} kg", delta=f"GVM {gvm_limit_kg:,.0f} kg", delta_color="off")

    if wheelbase_mm <= 0:
        st.warning("Wheelbase must be greater than zero for axle load transfer calculation.")
    if rear_axle_to_towball_mm < 0:
        st.warning("Rear axle to towball distance cannot be negative.")
    if abs(vehicle_test_mass_connected_kg - expected_vehicle_connected_kg) > 1.0:
        st.warning("Connected vehicle test mass does not match unhitched mass plus towball download within 1 kg.")
    if front_axle_connected_kg < 0:
        st.warning("Front axle connected load has become negative. Check input values.")
    if front_axle_connected_kg > front_axle_limit_kg:
        st.warning("Front axle connected load exceeds the front axle limit.")
    if rear_axle_connected_kg > rear_axle_limit_kg:
        st.warning("Rear axle connected load exceeds the rear axle limit.")
    if vehicle_test_mass_connected_kg > gvm_limit_kg:
        st.warning("Connected vehicle test mass exceeds the GVM limit.")

    st.caption(
        "This calculation follows the TD-style axle load transfer method. Because the towball load acts behind the rear axle, "
        "the front axle unloads and the rear axle gains more than the towball download. The towball mass is not added again "
        "to GCM because the trailer mass already includes it."
    )

# ─── VEHICLE INDIVIDUAL TYRE LOADS ──────────────────────────────────────────────

with st.expander("Vehicle Individual Tyre Loads", expanded=False):
    tyre_rows = [
        {"Tyre Position": "Front Left",  "Base Load (kg)": fl_base_kg, "Axle Transfer Change (kg)": fl_added_ball_kg, "Loaded Load (kg)": fl_loaded_kg, "Loaded Load (N)": fl_load_N, "Pressure (kPa)": front_tyre_pressure, "Contact Patch Area (cm²)": fl_cp_area * 10000.0, "Contact Patch Length (cm)": fl_cp_len * 100.0},
        {"Tyre Position": "Front Right", "Base Load (kg)": fr_base_kg, "Axle Transfer Change (kg)": fr_added_ball_kg, "Loaded Load (kg)": fr_loaded_kg, "Loaded Load (N)": fr_load_N, "Pressure (kPa)": front_tyre_pressure, "Contact Patch Area (cm²)": fr_cp_area * 10000.0, "Contact Patch Length (cm)": fr_cp_len * 100.0},
        {"Tyre Position": "Rear Left",   "Base Load (kg)": rl_base_kg, "Axle Transfer Change (kg)": rl_added_ball_kg, "Loaded Load (kg)": rl_loaded_kg, "Loaded Load (N)": rl_load_N, "Pressure (kPa)": rear_tyre_pressure,  "Contact Patch Area (cm²)": rl_cp_area * 10000.0, "Contact Patch Length (cm)": rl_cp_len * 100.0},
        {"Tyre Position": "Rear Right",  "Base Load (kg)": rr_base_kg, "Axle Transfer Change (kg)": rr_added_ball_kg, "Loaded Load (kg)": rr_loaded_kg, "Loaded Load (N)": rr_load_N, "Pressure (kPa)": rear_tyre_pressure,  "Contact Patch Area (cm²)": rr_cp_area * 10000.0, "Contact Patch Length (cm)": rr_cp_len * 100.0},
    ]
    df_tyres = pd.DataFrame(tyre_rows)
    st.dataframe(df_tyres.round({
        "Base Load (kg)": 1,
        "Axle Transfer Change (kg)": 1,
        "Loaded Load (kg)": 1,
        "Loaded Load (N)": 0,
        "Contact Patch Area (cm²)": 1,
        "Contact Patch Length (cm)": 1,
    }), use_container_width=True, hide_index=True)

    base_diff = base_vehicle_tyre_mass_kg - reference_vehicle_mass
    loaded_diff = loaded_vehicle_tyre_mass_kg - expected_vehicle_connected_kg
    c1, c2, c3 = st.columns(3)
    c1.metric("Vehicle test mass from wheel loads", f"{base_vehicle_tyre_mass_kg:,.1f} kg", delta=f"{base_diff:+.1f} kg vs reference", delta_color="off")
    c2.metric("Connected vehicle tyre load total", f"{loaded_vehicle_tyre_mass_kg:,.1f} kg", delta=f"{loaded_diff:+.1f} kg vs unhitched + ball", delta_color="off")
    c3.metric("Towball download", f"{tow_ball_mass:,.1f} kg")

    if reference_vehicle_mass > 0 and abs(base_diff) > 0.02 * reference_vehicle_mass:
        st.warning("The reference vehicle mass does not match the sum of individual base tyre loads. Calculations are using the individual tyre loads.")
    if expected_vehicle_connected_kg > 0 and abs(loaded_diff) > 0.02 * expected_vehicle_connected_kg:
        st.warning("The connected tyre loads do not closely match unhitched wheel-load mass plus towball mass.")

    st.caption(
        "Connected tyre loads are derived from the TD-style axle load transfer calculation using wheelbase and rear axle to towball distance. "
        "Each connected axle load is split equally left/right for this first-order model."
    )


# ─── TRAILER WHEEL LOAD SUMMARY ────────────────────────────────────────────────

with st.expander("Trailer Wheel Load Summary", expanded=False):
    trl_rows = [
        {"Tyre Position": "Front Left", "Interpolated Tyre Load (kg)": trailer_fl_load_kg, "Tyre Load (N)": trailer_fl_load_N, "Pressure (kPa)": trailer_tyre_pressure, "Contact Patch Area (cm²)": trl_fl_cp_area * 10000.0, "Contact Patch Length (cm)": trl_fl_cp_len * 100.0},
        {"Tyre Position": "Front Right", "Interpolated Tyre Load (kg)": trailer_fr_load_kg, "Tyre Load (N)": trailer_fr_load_N, "Pressure (kPa)": trailer_tyre_pressure, "Contact Patch Area (cm²)": trl_fr_cp_area * 10000.0, "Contact Patch Length (cm)": trl_fr_cp_len * 100.0},
        {"Tyre Position": "Rear Left", "Interpolated Tyre Load (kg)": trailer_rl_load_kg, "Tyre Load (N)": trailer_rl_load_N, "Pressure (kPa)": trailer_tyre_pressure, "Contact Patch Area (cm²)": trl_rl_cp_area * 10000.0, "Contact Patch Length (cm)": trl_rl_cp_len * 100.0},
        {"Tyre Position": "Rear Right", "Interpolated Tyre Load (kg)": trailer_rr_load_kg, "Tyre Load (N)": trailer_rr_load_N, "Pressure (kPa)": trailer_tyre_pressure, "Contact Patch Area (cm²)": trl_rr_cp_area * 10000.0, "Contact Patch Length (cm)": trl_rr_cp_len * 100.0},
    ]
    st.dataframe(pd.DataFrame(trl_rows).round({
        "Interpolated Tyre Load (kg)": 1,
        "Tyre Load (N)": 0,
        "Contact Patch Area (cm²)": 1,
        "Contact Patch Length (cm)": 1,
    }), use_container_width=True, hide_index=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Trailer mass", f"{m_trailer:,.1f} kg")
    c2.metric("Interpolated towball mass", f"{tow_ball_mass:,.1f} kg")
    c3.metric("Interpolated tyre-supported mass", f"{trailer_tyre_supported_mass:,.1f} kg")
    c4.metric("Support mass difference", f"{trailer_supported_mass_diff:+.1f} kg")

    st.write(f"Expected tyre-supported mass = trailer mass - towball mass = {expected_trailer_tyre_supported_mass:,.1f} kg")
    if expected_trailer_tyre_supported_mass > 0 and abs(trailer_supported_mass_diff) > 0.02 * expected_trailer_tyre_supported_mass:
        st.warning("The interpolated trailer tyre-supported mass differs from trailer mass minus towball mass by more than 2%.")
    if trailer_extrapolated:
        st.warning("The entered trailer mass is outside the calibrated trailer profile range. Trailer ball load and wheel loads are extrapolated.")

# ─── MASS CALCULATIONS ───────────────────────────────────────────────────────────

st.subheader("Mass Calculations")
_mc1, _mc2, _mc3 = st.columns(3)
_mc1.metric("Front Axle Unhitched Load", f"{front_axle_unhitched_kg:,.0f} kg")
_mc2.metric("Rear Axle Unhitched Load", f"{rear_axle_unhitched_kg:,.0f} kg")
_mc3.metric("Vehicle Test Mass from Wheel Loads", f"{vehicle_test_mass_unhitched_kg:,.0f} kg")
_mc4, _mc5, _mc6 = st.columns(3)
_mc4.metric("Trailer Mass", f"{m_trailer:,.0f} kg")
_mc5.metric("Total Combination Mass", f"{m_total:,.0f} kg")
_mc6.metric(
    "GCM Utilisation", f"{GCM_utilisation:.1f}%",
    delta=f"{GCM_utilisation - 100:.1f}% over limit" if gcm_exceeded else None,
    delta_color="inverse",
)
st.caption(f"Rated GCM: {GCM:,.0f} kg. Vehicle mass is derived from individual base tyre loads, not the reference vehicle mass field.")

# ─── DRIVELINE / TRACTIVE FORCE ──────────────────────────────────────────────────

st.subheader("Driveline / Tractive Force")

_dc1, _dc2, _dc3 = st.columns(3)
_dc1.metric(
    "Auto-Selected Gear",
    f"Gear {p1_gear}  (ratio {p1_ratio:.3f})" if p1_gear else "N/A",
)
_dc2.metric("Engine RPM", f"{int(p1_rpm):,}" if p1_rpm is not None else "N/A")
_dc3.metric("Torque at RPM", f"{p1_torque:,.0f} Nm" if p1_torque is not None else "N/A")

_dc4, _dc5, _dc6 = st.columns(3)
_dc4.metric(
    "Engine Power (capped)",
    f"{p1_power_W / 1000:.1f} kW" if p1_power_W is not None else "N/A",
)
_dc5.metric("Engine-Limited Available Force", f"{F_engine_available:,.0f} N")
_dc6.metric("Final Available Force", f"{F_available:,.0f} N")

_dc7, _dc8, _dc9 = st.columns(3)
_dc7.metric("Traction Limit", f"{F_traction_limit:,.0f} N")
_dc8.metric("Driven Axle Normal Load", f"{driven_axle_normal_N:,.0f} N")
_dc9.metric("Limit State", "Traction-limited" if traction_limited else "Engine-limited")

# ─── GEAR SELECTION CHECK ────────────────────────────────────────────────────────

with st.expander("Gear Selection Check", expanded=False):
    st.caption(
        f"All gears evaluated at {speed_kmh:.0f} km/h ({V:.2f} m/s).  "
        f"Idle: {vp['idle_rpm']:,} RPM  |  Redline: {vp['redline_rpm']:,} RPM.  "
        "Calculated engine RPM is floored at idle RPM to allow launch/low-speed "
        "clutch or torque converter slip. Gears are only marked invalid if "
        "effective RPM exceeds redline."
    )
    st.info(
        "**Gear selection note:** The current model selects the valid gear that produces "
        "the highest available tractive force at each speed step. This is an idealised "
        "shift strategy and does not yet include shift delay, torque converter slip, "
        "traction control, or manufacturer shift scheduling.  \n"
        "Torque is interpolated from the vehicle profile torque curve at the calculated "
        "engine RPM. Engine power is calculated from torque and RPM, then capped by the "
        "profile peak power value. Peak torque RPM and peak power RPM are stored for "
        "profile reference and validation. The traction limit is applied after the best engine-based gear is selected."
    )
    _disp = []
    for _r in gear_rows_p1:
        _disp.append({
            "Gear":           _r["Gear"],
            "Ratio":          _r["Gear Ratio"],
            "Calc RPM":       int(_r["Calc RPM"]),
            "Eff. RPM":       int(_r["Effective RPM"]),
            "Torque (Nm)":    f"{_r['Torque (Nm)']:.0f}"      if _r["Torque (Nm)"]    is not None else "—",
            "Eng kW":         f"{_r['Eng Power (W)']/1000:.1f}" if _r["Eng Power (W)"] is not None else "—",
            "Cap kW":         f"{_r['Cap Power (W)']/1000:.1f}" if _r["Cap Power (W)"] is not None else "—",
            "F_torque (N)":   f"{_r['F_torque (N)']:.0f}"     if _r["F_torque (N)"]   is not None else "—",
            "F_power (N)":    f"{_r['F_power (N)']:.0f}"      if _r["F_power (N)"]    is not None else "—",
            "F_avail (N)":    f"{_r['F_available (N)']:.0f}"  if _r["F_available (N)"] is not None else "—",
            "Valid":          "✅" if _r["Valid"] else "❌ Over redline",
            "Selected":       "★" if _r["Selected"] else "",
        })
    st.dataframe(pd.DataFrame(_disp), use_container_width=True, hide_index=True)
    st.caption(
        f"Traction limit after gear selection: {F_traction_limit:,.0f} N "
        f"based on {driven_axle_type}, μ = {tyre_road_mu:.2f}, and driven axle normal load = {driven_axle_normal_N:,.0f} N."
    )

# ─── PERFORMANCE ─────────────────────────────────────────────────────────────────

st.subheader("Performance")
_pc1, _pc2, _pc3, _pc4 = st.columns(4)
_pc1.metric("Net Force",         f"{F_net:,.0f} N")
_pc2.metric("Acceleration",      f"{a:.4f} m/s²")
_pc3.metric("Hitch Force",       f"{F_hitch:,.0f} N")
_pc4.metric("Hitch Force",       f"{F_hitch / 1000:.3f} kN")

# ─── FORCE SUMMARY TABLE ─────────────────────────────────────────────────────────

st.subheader("Force Summary Table")
_fs_data = {
    "Force Component": [
        "Vehicle Rolling Resistance",
        "Trailer Rolling Resistance",
        "Vehicle Aerodynamic Drag",
        "Trailer Aerodynamic Drag",
        "Total Resistance",
        "Engine-Limited Tractive Force",
        "Traction Limit",
        "Final Available Tractive Force",
        "Net Force",
        "Hitch Force",
    ],
    "Value (N)": [
        round(F_rr_vehicle, 1), round(F_rr_trailer, 1),
        round(F_aero_vehicle, 1), round(F_aero_trailer, 1),
        round(F_resistance_total, 1), round(F_engine_available, 1),
        round(F_traction_limit, 1), round(F_available, 1),
        round(F_net, 1), round(F_hitch, 1),
    ],
    "Value (kN)": [
        round(F_rr_vehicle / 1000, 3), round(F_rr_trailer / 1000, 3),
        round(F_aero_vehicle / 1000, 3), round(F_aero_trailer / 1000, 3),
        round(F_resistance_total / 1000, 3), round(F_engine_available / 1000, 3),
        round(F_traction_limit / 1000, 3), round(F_available / 1000, 3),
        round(F_net / 1000, 3), round(F_hitch / 1000, 3),
    ],
}
st.dataframe(pd.DataFrame(_fs_data), use_container_width=True, hide_index=True)

# ─── RESISTANCE FORCE BAR CHART ──────────────────────────────────────────────────

st.subheader("Resistance Force Breakdown")
_cats   = ["Vehicle\nRolling Resistance", "Trailer\nRolling Resistance",
           "Vehicle\nAero Drag", "Trailer\nAero Drag"]
_vals   = [F_rr_vehicle, F_rr_trailer, F_aero_vehicle, F_aero_trailer]
_colors = ["#1976D2", "#64B5F6", "#E64A19", "#FF8A65"]

fig, ax = plt.subplots(figsize=(9, 4))
bars = ax.bar(_cats, _vals, color=_colors, edgecolor="white", linewidth=0.8)
for bar, val in zip(bars, _vals):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + max(_vals) * 0.01,
        f"{val:,.0f} N",
        ha="center", va="bottom", fontsize=9, fontweight="bold",
    )
ax.set_ylabel("Force (N)", fontsize=11)
ax.set_title("Resistance Forces at Selected Speed", fontsize=12, fontweight="bold")
ax.set_ylim(0, max(_vals) * 1.2 if max(_vals) > 0 else 100)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2A — PREDICTED LEVEL ROAD ACCELERATION
# ═══════════════════════════════════════════════════════════════════════════════

st.divider()
st.header("Phase 2A — Predicted Level Road Acceleration")
st.markdown(
    """
    Simulates level-road acceleration using the selected vehicle, trailer and environmental
    conditions. Two runs are calculated: an expected case using average wind and a worst-case
    steady-headwind case using maximum wind.

    **Assumptions:** flat level road · direct longitudinal headwind · no crosswind/yaw ·
    constant wind throughout each run · torque curve evaluated independently at each speed step.
    """
)

_sa, _sb, _sc = st.columns(3)
sim_start_kmh  = _sa.number_input("Start speed (km/h)", value=0.0, min_value=0.0, step=1.0, key="sim_start")
sim_target_kmh = _sb.number_input("Target speed (km/h)", value=96.6, min_value=1.0, step=1.0, key="sim_target")
sim_step_kmh   = _sc.number_input(
    "Speed step (km/h)", value=0.5, min_value=0.01, max_value=5.0,
    step=0.1, format="%.2f", key="sim_step"
)

F_rr_veh_p2 = Crr_veh_p2 * loaded_vehicle_tyre_total_N
F_rr_trl_p2 = Crr_trl_p2 * trailer_tyre_supported_mass * g
P_watts_p2 = peak_power_kW * 1000.0

n_steps = math.ceil((sim_target_kmh - sim_start_kmh) / sim_step_kmh)
sim_speeds = [sim_start_kmh + i * sim_step_kmh for i in range(n_steps + 1)]
sim_speeds = [s for s in sim_speeds if s <= sim_target_kmh + 1e-9]
if not sim_speeds or abs(sim_speeds[-1] - sim_target_kmh) > 1e-6:
    sim_speeds.append(sim_target_kmh)

def run_acceleration_simulation(wind_kmh, case_name):
    """Run one stepped-speed simulation using a constant longitudinal headwind."""
    wind_mps = wind_kmh / 3.6
    rows, speeds_out, times_out = [], [], []
    stopped = False
    cumtime = 0.0

    for idx, v_kmh in enumerate(sim_speeds):
        road_speed_mps = v_kmh / 3.6
        relative_air_speed_mps = road_speed_mps + wind_mps

        F_aero_veh = 0.5 * air_density * Cd_vehicle * A_vehicle * relative_air_speed_mps ** 2
        F_aero_trl = 0.5 * air_density * Cd_trailer * A_trailer * relative_air_speed_mps ** 2
        F_res = F_rr_veh_p2 + F_rr_trl_p2 + F_aero_veh + F_aero_trl

        g_rows, b_idx = select_best_gear(
            gear_ratios=vp["gear_ratios"],
            final_drive_ratio=final_drive_ratio,
            driveline_efficiency=driveline_efficiency,
            tyre_radius_m=tyre_radius,
            idle_rpm=vp["idle_rpm"],
            redline_rpm=vp["redline_rpm"],
            torque_curve=active_torque_curve,
            peak_power_W=P_watts_p2,
            V_mps=road_speed_mps,
            fallback_torque_Nm=vp["peak_torque_Nm"],
        )

        if b_idx is not None:
            best = g_rows[b_idx]
            F_engine = best["F_available (N)"]
            gear = best["Gear"]
        else:
            F_engine = 0.0
            gear = None

        F_final = min(F_engine, F_traction_limit)
        traction_limited_sim = F_final < F_engine
        F_net_sim = F_final - F_res
        a_sim = F_net_sim / m_total if m_total > 0 else 0.0

        speeds_out.append(v_kmh)
        times_out.append(cumtime)
        rows.append({
            "Case": case_name,
            "Road Speed (km/h)": round(v_kmh, 2),
            "Wind Speed (km/h)": round(wind_kmh, 2),
            "Relative Air Speed (km/h)": round(relative_air_speed_mps * 3.6, 2),
            "Air Density (kg/m³)": round(air_density, 4),
            "Gear": gear,
            "F_engine_available (N)": round(F_engine, 1),
            "F_traction_limit (N)": round(F_traction_limit, 1),
            "F_available (N)": round(F_final, 1),
            "Traction Limited": traction_limited_sim,
            "F_rr Vehicle (N)": round(F_rr_veh_p2, 1),
            "F_rr Trailer (N)": round(F_rr_trl_p2, 1),
            "F_aero Vehicle (N)": round(F_aero_veh, 1),
            "F_aero Trailer (N)": round(F_aero_trl, 1),
            "F_resistance (N)": round(F_res, 1),
            "F_net (N)": round(F_net_sim, 1),
            "Acceleration (m/s²)": round(a_sim, 4),
            "Cumulative Time (s)": round(cumtime, 3),
        })

        if a_sim <= 0:
            stopped = True
            break

        if idx < len(sim_speeds) - 1:
            dV = (sim_speeds[idx + 1] - v_kmh) / 3.6
            cumtime += dV / a_sim

    t48 = interp_time_at_speed(speeds_out, times_out, 48.3)
    t64 = interp_time_at_speed(speeds_out, times_out, 64.4)
    t96 = interp_time_at_speed(speeds_out, times_out, 96.6)
    t64_96 = (t96 - t64) if (t64 is not None and t96 is not None) else None
    overall = (
        t48 is not None and t48 <= 12 and
        t96 is not None and t96 <= 30 and
        t64_96 is not None and t64_96 <= 18
    )
    return {
        "rows": rows,
        "speed": speeds_out,
        "time": times_out,
        "stopped": stopped,
        "T_48": t48,
        "T_64": t64,
        "T_96": t96,
        "T_64_96": t64_96,
        "overall_pass": overall,
    }

avg_sim = run_acceleration_simulation(average_wind_kmh, "Average Wind")
max_sim = run_acceleration_simulation(maximum_wind_kmh, "Maximum Wind")
no_wind_sim = run_acceleration_simulation(0.0, "No Wind")

def fmt_t(t):
    return f"{t:.2f} s" if t is not None else "Not reached"

def pf(t, lim):
    return "✅ PASS" if t is not None and t <= lim else "❌ FAIL"

st.subheader("Average Wind Results")
_aw1, _aw2, _aw3, _aw4 = st.columns(4)
_aw1.metric("IVM to 48.3 km/h", fmt_t(avg_sim["T_48"]), delta="Limit: 12 s", delta_color="off")
_aw2.metric("IVM to 96.6 km/h", fmt_t(avg_sim["T_96"]), delta="Limit: 30 s", delta_color="off")
_aw3.metric("64.4 to 96.6 km/h", fmt_t(avg_sim["T_64_96"]), delta="Limit: 18 s", delta_color="off")
_aw4.metric("Overall Result", "✅ PASS" if avg_sim["overall_pass"] else "❌ FAIL")

st.subheader("Maximum Wind Results")
_mw1, _mw2, _mw3, _mw4 = st.columns(4)
_mw1.metric("IVM to 48.3 km/h", fmt_t(max_sim["T_48"]), delta="Limit: 12 s", delta_color="off")
_mw2.metric("IVM to 96.6 km/h", fmt_t(max_sim["T_96"]), delta="Limit: 30 s", delta_color="off")
_mw3.metric("64.4 to 96.6 km/h", fmt_t(max_sim["T_64_96"]), delta="Limit: 18 s", delta_color="off")
_mw4.metric("Overall Result", "✅ PASS" if max_sim["overall_pass"] else "❌ FAIL")

for label, result in [("Average wind", avg_sim), ("Maximum wind", max_sim)]:
    if result["stopped"] and result["T_96"] is None:
        st.warning(
            f"{label} simulation stopped at {result['speed'][-1]:.1f} km/h because net force "
            "reached zero before the target speed."
        )

st.subheader("Acceleration Test Comparison")
comparison_df = pd.DataFrame({
    "Test Target": ["IVM to 48.3 km/h", "IVM to 96.6 km/h", "64.4 to 96.6 km/h"],
    "No-Wind Time": [fmt_t(no_wind_sim["T_48"]), fmt_t(no_wind_sim["T_96"]), fmt_t(no_wind_sim["T_64_96"])],
    "Average-Wind Time": [fmt_t(avg_sim["T_48"]), fmt_t(avg_sim["T_96"]), fmt_t(avg_sim["T_64_96"])],
    "Maximum-Wind Time": [fmt_t(max_sim["T_48"]), fmt_t(max_sim["T_96"]), fmt_t(max_sim["T_64_96"])],
    "Limit (s)": [12, 30, 18],
    "Average-Wind Pass / Fail": [pf(avg_sim["T_48"], 12), pf(avg_sim["T_96"], 30), pf(avg_sim["T_64_96"], 18)],
    "Maximum-Wind Pass / Fail": [pf(max_sim["T_48"], 12), pf(max_sim["T_96"], 30), pf(max_sim["T_64_96"], 18)],
})
st.dataframe(comparison_df, use_container_width=True, hide_index=True)

if len(avg_sim["rows"]) > 1 and len(max_sim["rows"]) > 1:
    df_avg = pd.DataFrame(avg_sim["rows"])
    df_max = pd.DataFrame(max_sim["rows"])
    _pl, _pr = st.columns(2)

    with _pl:
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        ax1.plot(df_avg["Cumulative Time (s)"], df_avg["Road Speed (km/h)"], linewidth=2, label="Average wind")
        ax1.plot(df_max["Cumulative Time (s)"], df_max["Road Speed (km/h)"], linewidth=2, label="Maximum wind")
        ax1.axhline(48.3, linestyle="--", linewidth=0.8, alpha=0.6)
        ax1.axhline(96.6, linestyle="--", linewidth=0.8, alpha=0.6)
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Road speed (km/h)")
        ax1.set_title("Speed vs Time", fontweight="bold")
        ax1.legend(fontsize=8)
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        plt.tight_layout(); st.pyplot(fig1); plt.close(fig1)

    with _pr:
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.plot(df_avg["Road Speed (km/h)"], df_avg["Acceleration (m/s²)"], linewidth=2, label="Average wind")
        ax2.plot(df_max["Road Speed (km/h)"], df_max["Acceleration (m/s²)"], linewidth=2, label="Maximum wind")
        ax2.axhline(0, linestyle="--", linewidth=0.8)
        ax2.set_xlabel("Road speed (km/h)")
        ax2.set_ylabel("Acceleration (m/s²)")
        ax2.set_title("Acceleration vs Speed", fontweight="bold")
        ax2.legend(fontsize=8)
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        plt.tight_layout(); st.pyplot(fig2); plt.close(fig2)

    with _pl:
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        ax3.plot(df_avg["Road Speed (km/h)"], df_avg["F_available (N)"], linewidth=2, label="Final available tractive force")
        ax3.plot(df_avg["Road Speed (km/h)"], df_avg["F_resistance (N)"], linewidth=2, linestyle="--", label="Average-wind total resistance")
        ax3.plot(df_max["Road Speed (km/h)"], df_max["F_resistance (N)"], linewidth=2, linestyle=":", label="Maximum-wind total resistance")
        ax3.set_xlabel("Road speed (km/h)")
        ax3.set_ylabel("Force (N)")
        ax3.set_title("Tractive Force and Wind-Adjusted Resistance", fontweight="bold")
        ax3.legend(fontsize=8)
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)
        plt.tight_layout(); st.pyplot(fig3); plt.close(fig3)

    with _pr:
        gear_num = pd.to_numeric(df_avg["Gear"], errors="coerce").dropna()
        speed_gear = df_avg.loc[gear_num.index, "Road Speed (km/h)"]
        fig4, ax4 = plt.subplots(figsize=(6, 4))
        ax4.step(speed_gear, gear_num, linewidth=2, where="post")
        ax4.set_xlabel("Road speed (km/h)")
        ax4.set_ylabel("Gear")
        ax4.set_yticks(range(1, len(vp["gear_ratios"]) + 1))
        ax4.set_title("Selected Gear vs Speed", fontweight="bold")
        ax4.spines["top"].set_visible(False)
        ax4.spines["right"].set_visible(False)
        plt.tight_layout(); st.pyplot(fig4); plt.close(fig4)

    with st.expander("Average Wind Simulation Data", expanded=False):
        st.dataframe(df_avg, use_container_width=True, hide_index=True)

    with st.expander("Maximum Wind Simulation Data", expanded=False):
        st.dataframe(df_max, use_container_width=True, hide_index=True)
else:
    st.info("Increase the simulation speed range (target > start) to run both wind simulations.")

st.caption(
    "Temperature affects aerodynamic resistance through calculated air density. Average wind "
    "represents expected conditions, while maximum wind represents a worst-case steady headwind. "
    "Wind direction, crosswind, yaw and gust duration are not yet modelled."
)

