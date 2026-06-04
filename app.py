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

DEFAULT_TRAILER_PROFILES = {
    "AIC Dual-Axle Flat Front Trailer": {
        "trailer_mass": 3500.0, "tow_ball_mass": 350.0,
        "num_axles": 2, "num_tyres": 4,
        "tyre_size": "235/75R15", "tyre_pressure_kPa": 350.0,
        "tyre_radius": 0.365, "tyre_type": "Highway",
        "Cd": 0.55, "frontal_width": 2.40, "frontal_height": 1.80,
    },
    "Light Load Configuration": {
        "trailer_mass": 1500.0, "tow_ball_mass": 100.0,
        "num_axles": 2, "num_tyres": 4,
        "tyre_size": "205/75R15", "tyre_pressure_kPa": 300.0,
        "tyre_radius": 0.340, "tyre_type": "Highway",
        "Cd": 0.55, "frontal_width": 2.20, "frontal_height": 1.60,
    },
    "Balanced Load Configuration": {
        "trailer_mass": 2500.0, "tow_ball_mass": 150.0,
        "num_axles": 2, "num_tyres": 4,
        "tyre_size": "225/75R15", "tyre_pressure_kPa": 340.0,
        "tyre_radius": 0.355, "tyre_type": "Highway",
        "Cd": 0.55, "frontal_width": 2.30, "frontal_height": 1.70,
    },
    "Heavy Front Load Configuration": {
        "trailer_mass": 3500.0, "tow_ball_mass": 350.0,
        "num_axles": 2, "num_tyres": 4,
        "tyre_size": "235/75R15", "tyre_pressure_kPa": 380.0,
        "tyre_radius": 0.365, "tyre_type": "Highway",
        "Cd": 0.55, "frontal_width": 2.40, "frontal_height": 1.90,
    },
    "Custom": {
        "trailer_mass": 2000.0, "tow_ball_mass": 150.0,
        "num_axles": 2, "num_tyres": 4,
        "tyre_size": "225/75R15", "tyre_pressure_kPa": 340.0,
        "tyre_radius": 0.355, "tyre_type": "Highway",
        "Cd": 0.55, "frontal_width": 2.30, "frontal_height": 1.70,
    },
}


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
    p.setdefault("driven_axle_type", "Four Wheel Drive")
    p.setdefault("tyre_road_friction_coefficient", 0.80)
    p.setdefault("wheelbase_mm", 3125.0)
    p.setdefault("rear_axle_to_towball_mm", 1450.0)
    p.setdefault("front_axle_limit_kg", vehicle_mass * 0.55 if vehicle_mass > 0 else 1650.0)
    p.setdefault("rear_axle_limit_kg", vehicle_mass * 0.45 + 500.0 if vehicle_mass > 0 else 2050.0)
    p.setdefault("gvm_limit_kg", vehicle_mass + 350.0 if vehicle_mass > 0 else 3700.0)

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
        name: {**enrich_vehicle_profile(name, prof), "torque_curve": [tuple(pt) for pt in prof["torque_curve"]]}
        for name, prof in DEFAULT_VEHICLE_PROFILES.items()
    }
else:
    # Backwards compatibility: add any new fields to profiles already in session state.
    st.session_state["vehicle_profiles"] = {
        name: enrich_vehicle_profile(name, prof)
        for name, prof in st.session_state["vehicle_profiles"].items()
    }

# ─── CONSTANTS & TYRE TYPES ──────────────────────────────────────────────────────

g = 9.81
TYRE_TYPES = ["Highway", "All-Terrain", "Mud-Terrain"]
DRIVEN_AXLE_TYPES = ["Rear Wheel Drive", "Front Wheel Drive", "Four Wheel Drive"]
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

m_vehicle = st.sidebar.number_input(
    "Vehicle mass (kg)", value=float(vp["vehicle_mass"]),
    min_value=0.0, step=50.0, key=f"m_veh_{vk}",
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
        index=DRIVEN_AXLE_TYPES.index(vp.get("driven_axle_type", "Four Wheel Drive")),
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

    # ── Torque Curve ──
    st.markdown("**Torque Curve**")
    _tc_rpm_def = ", ".join(str(int(pt[0])) for pt in vp["torque_curve"])
    _tc_tq_def  = ", ".join(f"{pt[1]:.4g}" for pt in vp["torque_curve"])
    e_tc_rpm = st.text_input("RPM points",          value=_tc_rpm_def, key=f"e_tc_rpm_{_vkv}")
    e_tc_tq  = st.text_input("Torque values (Nm)",  value=_tc_tq_def,  key=f"e_tc_tq_{_vkv}")

    # ── Validation Warnings ──
    try:
        _check_rpm = [float(x.strip()) for x in e_tc_rpm.split(",") if x.strip()]
        _check_tq  = [float(x.strip()) for x in e_tc_tq.split(",")  if x.strip()]
        if len(_check_rpm) == len(_check_tq) and len(_check_rpm) >= 2:
            _check_curve = list(zip(_check_rpm, _check_tq))
            _max_curve_tq = max(t for _, t in _check_curve)
            if abs(_max_curve_tq - e_ptq) > 10:
                st.warning(
                    f"The entered peak torque ({e_ptq:.0f} Nm) does not match "
                    f"the maximum value in the torque curve ({_max_curve_tq:.0f} Nm)."
                )
            _tq_at_pp = interp_torque(_check_curve, e_ppw_rpm)
            if _tq_at_pp is not None:
                _calc_pw_kW = _tq_at_pp * e_ppw_rpm * 2 * math.pi / 60.0 / 1000.0
                if abs(_calc_pw_kW - e_ppw) > max(10.0, e_ppw * 0.10):
                    st.warning(
                        f"The entered peak power ({e_ppw:.0f} kW) does not closely match "
                        f"the torque curve at the stated peak power RPM "
                        f"({_calc_pw_kW:.1f} kW calculated at {int(e_ppw_rpm)} RPM)."
                    )
    except Exception:
        pass

    # ── Buttons ──
    _ca, _cb = st.columns(2)
    _apply = _ca.button("Apply Changes",     key=f"apply_{vk}")
    _reset = _cb.button("Reset to Defaults", key=f"reset_{vk}")

    if _apply:
        _errors = []
        try:
            _new_gr  = [float(x.strip()) for x in e_gr.split(",")     if x.strip()]
            _new_rpm = [float(x.strip()) for x in e_tc_rpm.split(",") if x.strip()]
            _new_tq  = [float(x.strip()) for x in e_tc_tq.split(",")  if x.strip()]
            if not _new_gr:
                _errors.append("At least one gear ratio is required.")
            if len(_new_rpm) != len(_new_tq):
                _errors.append(
                    f"RPM points ({len(_new_rpm)}) and torque values ({len(_new_tq)}) "
                    "must have the same count."
                )
            elif len(_new_rpm) < 2:
                _errors.append("At least 2 torque curve points are required.")
        except ValueError as _exc:
            _errors.append(f"Parse error: {_exc}")

        if _errors:
            for _e in _errors:
                st.error(_e)
        else:
            st.session_state["vehicle_profiles"][selected_vehicle] = {
                "vehicle_mass":        m_vehicle,
                "rated_GCM":           GCM,
                "peak_torque_Nm":      e_ptq,
                "peak_torque_rpm":     int(e_ptq_rpm),
                "peak_power_kW":       e_ppw,
                "peak_power_rpm":      int(e_ppw_rpm),
                "idle_rpm":            int(e_idle),
                "redline_rpm":         int(e_redline),
                "torque_curve":        [(r, t) for r, t in zip(_new_rpm, _new_tq)],
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
        st.session_state["vehicle_profiles"][selected_vehicle] = {
            **_def,
            "torque_curve": [tuple(pt) for pt in _def["torque_curve"]],
        }
        st.session_state[f"ev_ver_{vk}"] = _ver + 1
        st.success("✅ Reset to defaults.")
        st.rerun()

    # ── Download JSON ──
    def _profiles_json():
        out = {}
        for _n, _p in st.session_state["vehicle_profiles"].items():
            _pc = dict(_p)
            _pc["torque_curve"] = [list(pt) for pt in _pc["torque_curve"]]
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
    "Select Trailer Profile", list(DEFAULT_TRAILER_PROFILES.keys())
)
tp = DEFAULT_TRAILER_PROFILES[selected_trailer]
tk = selected_trailer

m_trailer = st.sidebar.number_input(
    "Trailer mass (kg)", value=float(tp["trailer_mass"]),
    min_value=0.0, step=50.0, key=f"tm_{tk}",
)
tow_ball_mass = st.sidebar.number_input(
    "Tow ball mass (kg)", value=float(tp["tow_ball_mass"]),
    min_value=0.0, step=10.0, key=f"tbm_{tk}",
)
num_trailer_tyres = int(st.sidebar.number_input(
    "Number of trailer tyres", value=int(tp["num_tyres"]),
    min_value=1, step=1, key=f"ntt_{tk}",
))
trailer_tyre_pressure = st.sidebar.number_input(
    "Trailer tyre pressure (kPa)", value=float(tp["tyre_pressure_kPa"]),
    min_value=50.0, step=10.0, key=f"ttp_{tk}",
)
trailer_tyre_type = st.sidebar.selectbox(
    "Trailer tyre type", TYRE_TYPES,
    index=TYRE_TYPES.index(tp["tyre_type"]), key=f"ttt_{tk}",
)
trailer_tyre_radius = st.sidebar.number_input(
    "Trailer loaded tyre radius (m)", value=float(tp["tyre_radius"]),
    min_value=0.01, step=0.005, format="%.3f", key=f"ttr_{tk}",
)
Cd_trailer = st.sidebar.number_input(
    "Trailer Cd", value=float(tp["Cd"]),
    min_value=0.0, step=0.01, format="%.2f", key=f"cdt_{tk}",
)
frontal_width = st.sidebar.number_input(
    "Trailer frontal width (m)", value=float(tp["frontal_width"]),
    min_value=0.1, step=0.05, format="%.2f", key=f"fw_{tk}",
)
frontal_height = st.sidebar.number_input(
    "Trailer frontal height (m)", value=float(tp["frontal_height"]),
    min_value=0.1, step=0.05, format="%.2f", key=f"fh_{tk}",
)
A_trailer_calc = frontal_width * frontal_height
override_area = st.sidebar.checkbox(
    "Override trailer frontal area", value=False, key=f"oa_{tk}"
)
if override_area:
    A_trailer = st.sidebar.number_input(
        "Trailer frontal area override (m²)", value=round(A_trailer_calc, 2),
        min_value=0.1, step=0.05, format="%.2f", key=f"aft_ov_{tk}",
    )
else:
    A_trailer = A_trailer_calc
    st.sidebar.caption(f"Trailer frontal area (w × h): {A_trailer:.2f} m²")

st.sidebar.divider()

# ── Environmental & Operating Conditions ─────────────────────────────────────────

st.sidebar.subheader("Environmental")
air_density = st.sidebar.number_input(
    "Air density (kg/m³)", value=1.225, min_value=0.1, step=0.001, format="%.3f"
)
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
driven_axle_type     = vp["driven_axle_type"]
tyre_road_mu         = vp["tyre_road_friction_coefficient"]
wheelbase_mm         = float(vp["wheelbase_mm"])
rear_axle_to_towball_mm = float(vp["rear_axle_to_towball_mm"])
front_axle_limit_kg  = float(vp["front_axle_limit_kg"])
rear_axle_limit_kg   = float(vp["rear_axle_limit_kg"])
gvm_limit_kg         = float(vp["gvm_limit_kg"])

# ─── PHASE 1 CALCULATIONS ────────────────────────────────────────────────────────

V = speed_kmh / 3.6   # m/s

m_total         = m_vehicle + m_trailer
GCM_utilisation = (m_total / GCM) * 100.0

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

trailer_tyre_supported_mass = max(0.0, m_trailer - tow_ball_mass)
avg_trailer_load_per_tyre_N = (trailer_tyre_supported_mass * g) / max(num_trailer_tyres, 1)

# Rolling resistance from tyre vertical loads.
F_rr_vehicle = (Crr_vehicle_front * front_loaded_N) + (Crr_vehicle_rear * rear_loaded_N)
F_rr_trailer = Crr_trailer * trailer_tyre_supported_mass * g

F_aero_vehicle = 0.5 * air_density * Cd_vehicle * A_vehicle * V ** 2
F_aero_trailer = 0.5 * air_density * Cd_trailer * A_trailer * V ** 2

F_resistance_total = F_rr_vehicle + F_rr_trailer + F_aero_vehicle + F_aero_trailer

# Automatic gear selection
gear_rows_p1, best_idx_p1 = select_best_gear(
    gear_ratios          = vp["gear_ratios"],
    final_drive_ratio    = final_drive_ratio,
    driveline_efficiency = driveline_efficiency,
    tyre_radius_m        = tyre_radius,
    idle_rpm             = vp["idle_rpm"],
    redline_rpm          = vp["redline_rpm"],
    torque_curve         = vp.get("torque_curve"),
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
if driven_axle_type == "Rear Wheel Drive":
    driven_axle_normal_N = rear_loaded_N
elif driven_axle_type == "Front Wheel Drive":
    driven_axle_normal_N = front_loaded_N
else:
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
trl_cp_area, trl_cp_len = calc_contact_patch(avg_trailer_load_per_tyre_N, trailer_tyre_pressure, trl_sw)

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

# ─── PROFILE SUMMARY ─────────────────────────────────────────────────────────────

with st.expander("Profile Summary", expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Vehicle**")
        st.write(f"Profile: {selected_vehicle}")
        st.write(f"Vehicle mass: {m_vehicle:,.0f} kg  |  Rated GCM: {GCM:,.0f} kg")
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
        st.write(f"Avg load/tyre: {avg_trailer_load_per_tyre_N:,.0f} N")
        st.write(f"Contact patch: {trl_cp_area*10000:.1f} cm²  ×  {trl_cp_len*100:.1f} cm")
        st.write(f"Trailer Cd: {Cd_trailer:.2f}  |  Frontal area: {A_trailer:.2f} m²  ({frontal_width:.2f} × {frontal_height:.2f} m)")
        st.write(f"Phase 1 Crr: {Crr_trailer:.5f}  |  Phase 2A Crr: {Crr_trl_p2:.5f}")
    st.markdown("---")
    st.markdown("**Combination**")
    _cc1, _cc2, _cc3 = st.columns(3)
    _cc1.write(f"Total mass: {m_total:,.0f} kg")
    _cc2.write(f"Rated GCM: {GCM:,.0f} kg")
    _cc3.write(f"GCM utilisation: {GCM_utilisation:.1f}%")
    st.caption(
        "Rolling resistance is estimated from tyre type, tyre loading, pressure and "
        "loaded-radius correction. Contact patch values are engineering approximations."
    )


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

    base_diff = base_vehicle_tyre_mass_kg - m_vehicle
    loaded_diff = loaded_vehicle_tyre_mass_kg - (m_vehicle + tow_ball_mass)
    c1, c2, c3 = st.columns(3)
    c1.metric("Base tyre load total", f"{base_vehicle_tyre_mass_kg:,.1f} kg", delta=f"{base_diff:+.1f} kg vs vehicle mass", delta_color="off")
    c2.metric("Loaded tyre load total", f"{loaded_vehicle_tyre_mass_kg:,.1f} kg", delta=f"{loaded_diff:+.1f} kg vs vehicle + ball", delta_color="off")
    c3.metric("Towball download", f"{tow_ball_mass:,.1f} kg")

    if m_vehicle > 0 and abs(base_diff) > 0.02 * m_vehicle:
        st.warning("The entered base individual tyre loads do not closely match the vehicle mass.")
    if (m_vehicle + tow_ball_mass) > 0 and abs(loaded_diff) > 0.02 * (m_vehicle + tow_ball_mass):
        st.warning("The loaded tyre loads do not closely match vehicle mass plus tow ball mass.")

    st.caption(
        "Connected tyre loads are derived from the TD-style axle load transfer calculation using wheelbase and rear axle to towball distance. "
        "Each connected axle load is split equally left/right for this first-order model."
    )

# ─── MASS CALCULATIONS ───────────────────────────────────────────────────────────

st.subheader("Mass Calculations")
_mc1, _mc2, _mc3 = st.columns(3)
_mc1.metric("Total Combination Mass", f"{m_total:,.0f} kg")
_mc2.metric(
    "GCM Utilisation", f"{GCM_utilisation:.1f}%",
    delta=f"{GCM_utilisation - 100:.1f}% over limit" if gcm_exceeded else None,
    delta_color="inverse",
)
_mc3.metric("Rated GCM", f"{GCM:,.0f} kg")

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
    Simulates level-road acceleration via stepped-speed Euler integration.
    At each speed step the gear giving the highest available tractive force is selected
    automatically using the engine RPM and torque curve from the vehicle profile.

    **Assumptions:** flat level road · no wind · no gradient · torque curve evaluated
    independently at each speed step. Aero drag basic (no yaw, no wind).
    """
)

# ── Simulation Inputs ─────────────────────────────────────────────────────────
_sa, _sb, _sc = st.columns(3)
sim_start_kmh  = _sa.number_input("Start speed (km/h)", value=0.0, min_value=0.0, step=1.0, key="sim_start")
sim_target_kmh = _sb.number_input("Target speed (km/h)", value=96.6, min_value=1.0, step=1.0, key="sim_target")
sim_step_kmh   = _sc.number_input("Speed step (km/h)", value=0.5, min_value=0.01, max_value=5.0, step=0.1,
                                   format="%.2f", key="sim_step")

# Phase 2A rolling resistance (loaded-radius corrected, trailer tyre-supported mass only)
F_rr_veh_p2 = Crr_veh_p2 * loaded_vehicle_tyre_total_N
F_rr_trl_p2 = Crr_trl_p2 * trailer_tyre_supported_mass * g

P_watts_p2 = peak_power_kW * 1000.0

# Build speed array
n_steps = math.ceil((sim_target_kmh - sim_start_kmh) / sim_step_kmh)
sim_speeds = [sim_start_kmh + i * sim_step_kmh for i in range(n_steps + 1)]
sim_speeds = [s for s in sim_speeds if s <= sim_target_kmh + 1e-9]
if not sim_speeds or abs(sim_speeds[-1] - sim_target_kmh) > 1e-6:
    sim_speeds.append(sim_target_kmh)

# Acceleration simulation loop
sim_rows      = []
sim_speed_out = []
sim_time_out  = []
sim_stopped   = False
cumtime       = 0.0

for idx, v_kmh in enumerate(sim_speeds):
    V_mps = v_kmh / 3.6

    F_aero_veh = 0.5 * air_density * Cd_vehicle * A_vehicle * V_mps ** 2
    F_aero_trl = 0.5 * air_density * Cd_trailer * A_trailer * V_mps ** 2
    F_res      = F_rr_veh_p2 + F_rr_trl_p2 + F_aero_veh + F_aero_trl

    g_rows, b_idx = select_best_gear(
        gear_ratios          = vp["gear_ratios"],
        final_drive_ratio    = final_drive_ratio,
        driveline_efficiency = driveline_efficiency,
        tyre_radius_m        = tyre_radius,
        idle_rpm             = vp["idle_rpm"],
        redline_rpm          = vp["redline_rpm"],
        torque_curve         = vp.get("torque_curve"),
        peak_power_W         = P_watts_p2,
        V_mps                = V_mps,
        fallback_torque_Nm   = vp["peak_torque_Nm"],
    )

    if b_idx is not None:
        _bs = g_rows[b_idx]
        best_F_engine = _bs["F_available (N)"]
        best_gear_n  = _bs["Gear"]
    else:
        best_F_engine = 0.0
        best_gear_n  = None

    best_F_avail = min(best_F_engine, F_traction_limit)
    traction_limited_sim = best_F_avail < best_F_engine

    F_net_sim = best_F_avail - F_res
    a_sim     = F_net_sim / m_total if m_total > 0 else 0.0

    sim_speed_out.append(v_kmh)
    sim_time_out.append(cumtime)
    sim_rows.append({
        "Speed (km/h)":        round(v_kmh, 2),
        "Gear":                best_gear_n,
        "F_engine_available (N)": round(best_F_engine, 1),
        "F_traction_limit (N)":   round(F_traction_limit, 1),
        "F_available (N)":     round(best_F_avail, 1),
        "Traction Limited":    traction_limited_sim,
        "F_rr Vehicle (N)":    round(F_rr_veh_p2, 1),
        "F_rr Trailer (N)":    round(F_rr_trl_p2, 1),
        "F_aero Vehicle (N)":  round(F_aero_veh, 1),
        "F_aero Trailer (N)":  round(F_aero_trl, 1),
        "F_resistance (N)":    round(F_res, 1),
        "F_net (N)":           round(F_net_sim, 1),
        "Acceleration (m/s²)": round(a_sim, 4),
        "Cumulative Time (s)": round(cumtime, 3),
    })

    if a_sim <= 0:
        sim_stopped = True
        break

    if idx < len(sim_speeds) - 1:
        dV = (sim_speeds[idx + 1] - v_kmh) / 3.6
        cumtime += dV / a_sim

# Milestone interpolation
T_48    = interp_time_at_speed(sim_speed_out, sim_time_out, 48.3)
T_64    = interp_time_at_speed(sim_speed_out, sim_time_out, 64.4)
T_96    = interp_time_at_speed(sim_speed_out, sim_time_out, 96.6)
T_64_96 = (T_96 - T_64) if (T_64 is not None and T_96 is not None) else None

def fmt_t(t):
    return f"{t:.2f} s" if t is not None else "Not reached"

def pf(t, lim):
    return ("✅ PASS" if t is not None and t <= lim else "❌ FAIL")

overall_pass = (
    T_48    is not None and T_48    <= 12
    and T_96    is not None and T_96    <= 30
    and T_64_96 is not None and T_64_96 <= 18
)

if sim_stopped and T_96 is None:
    st.warning(
        f"Simulation stopped at {sim_speed_out[-1]:.1f} km/h — net force reached zero "
        "before the target speed."
    )

_ac1, _ac2, _ac3, _ac4 = st.columns(4)
_ac1.metric("IVM to 48.3 km/h",    fmt_t(T_48),    delta="Limit: 12 s", delta_color="off")
_ac2.metric("IVM to 96.6 km/h",    fmt_t(T_96),    delta="Limit: 30 s", delta_color="off")
_ac3.metric("64.4 to 96.6 km/h",   fmt_t(T_64_96), delta="Limit: 18 s", delta_color="off")
_ac4.metric("Overall Result", "✅ PASS" if overall_pass else "❌ FAIL")

st.subheader("Acceleration Test Results")
st.dataframe(pd.DataFrame({
    "Test Target":    ["IVM to 48.3 km/h", "IVM to 96.6 km/h", "64.4 to 96.6 km/h"],
    "Predicted Time": [fmt_t(T_48), fmt_t(T_96), fmt_t(T_64_96)],
    "Limit (s)":      [12, 30, 18],
    "Pass / Fail":    [pf(T_48, 12), pf(T_96, 30), pf(T_64_96, 18)],
}), use_container_width=True, hide_index=True)

# Four plots
if len(sim_rows) > 1:
    df_sim = pd.DataFrame(sim_rows)
    _pl, _pr = st.columns(2)

    with _pl:
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        ax1.plot(df_sim["Cumulative Time (s)"], df_sim["Speed (km/h)"],
                 color="#1976D2", linewidth=2)
        for _tk, _vk2 in [(48.3, 12), (96.6, 30)]:
            ax1.axhline(_tk, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
            ax1.axvline(_vk2, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
        for _tv, _sv in [(T_48, 48.3), (T_96, 96.6)]:
            if _tv is not None:
                ax1.plot(_tv, _sv, "o", color="#E64A19", zorder=5)
                ax1.annotate(f"{_tv:.1f} s", (_tv, _sv),
                             textcoords="offset points", xytext=(6, -12),
                             fontsize=8, color="#E64A19")
        ax1.set_xlabel("Time (s)"); ax1.set_ylabel("Speed (km/h)")
        ax1.set_title("Speed vs Time", fontweight="bold")
        ax1.spines["top"].set_visible(False); ax1.spines["right"].set_visible(False)
        plt.tight_layout(); st.pyplot(fig1); plt.close(fig1)

    with _pr:
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.plot(df_sim["Speed (km/h)"], df_sim["Acceleration (m/s²)"],
                 color="#388E3C", linewidth=2)
        ax2.axhline(0, color="red", linestyle="--", linewidth=0.8)
        ax2.set_xlabel("Speed (km/h)"); ax2.set_ylabel("Acceleration (m/s²)")
        ax2.set_title("Acceleration vs Speed", fontweight="bold")
        ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)
        plt.tight_layout(); st.pyplot(fig2); plt.close(fig2)

    with _pl:
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        ax3.plot(df_sim["Speed (km/h)"], df_sim["F_engine_available (N)"],
                 color="#7B1FA2", linewidth=2, label="Engine-limited tractive force")
        ax3.plot(df_sim["Speed (km/h)"], df_sim["F_available (N)"],
                 color="#0288D1", linewidth=2, label="Final available force after traction limit")
        ax3.plot(df_sim["Speed (km/h)"], df_sim["F_resistance (N)"],
                 color="#E64A19", linewidth=2, linestyle="--", label="Total resistance")
        ax3.set_xlabel("Speed (km/h)"); ax3.set_ylabel("Force (N)")
        ax3.set_title("Tractive Force and Resistance vs Speed", fontweight="bold")
        ax3.legend(fontsize=8)
        ax3.spines["top"].set_visible(False); ax3.spines["right"].set_visible(False)
        plt.tight_layout(); st.pyplot(fig3); plt.close(fig3)

    with _pr:
        _gear_num = pd.to_numeric(df_sim["Gear"], errors="coerce").dropna()
        _spd_gear = df_sim.loc[_gear_num.index, "Speed (km/h)"]
        fig4, ax4 = plt.subplots(figsize=(6, 4))
        ax4.step(_spd_gear, _gear_num, color="#0288D1", linewidth=2, where="post")
        ax4.set_xlabel("Speed (km/h)"); ax4.set_ylabel("Gear")
        ax4.set_yticks(range(1, len(vp["gear_ratios"]) + 1))
        ax4.set_title("Selected Gear vs Speed", fontweight="bold")
        ax4.spines["top"].set_visible(False); ax4.spines["right"].set_visible(False)
        plt.tight_layout(); st.pyplot(fig4); plt.close(fig4)

    with st.expander("Simulation Data Table", expanded=False):
        st.caption(
            "Step-by-step output. Each row shows conditions at the start of that "
            "speed band. Cumulative time is the elapsed time to reach that speed."
        )
        st.dataframe(df_sim, use_container_width=True, hide_index=True)

else:
    st.info("Increase the simulation speed range (target > start) to run the simulation.")
