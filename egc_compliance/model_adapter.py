"""
Model Adapter — Bridges BuildingCollector flat schema → IDFGenerator nested payload.

BuildingCollector produces a flat schema:
    {"geometry": {"footprint_sqft": 8000, "stories": 4}, "envelope": {...}, ...}

IDFGenerator expects a nested payload:
    {"project": {...}, "stories": [...], "constructions": [...], "hvac_equipment": [...], ...}

This adapter converts between the two. Called by ScenarioEngine before each IDFGenerator
instantiation so scenario modifications (envelope R-values, HVAC COP, etc.) flow through.
"""

import math
from typing import Dict, Any


def u2r(u_value: float) -> float:
    """Convert U-value (Btu/h·ft²·°F) to R-value (h·ft²·°F/Btu). Returns 0 if u_value <= 0."""
    if u_value and u_value > 0:
        return round(1.0 / u_value, 2)
    return 0.0


def schema_to_idf_payload(building_model: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert BuildingCollector flat schema to IDFGenerator nested payload.

    Reads scenario-modified flat keys first (written by _apply_appendix_g_rules,
    _generate_code_2022_idf, _apply_retrofit_measures), then falls back to
    original flat envelope/systems values, then to sensible defaults.

    Args:
        building_model: Flat schema dict from BuildingCollector (may have been
                        modified in-place by scenario generators)

    Returns:
        Nested payload dict compatible with IDFGenerator
    """
    geom = building_model.get('geometry', {})
    envelope = building_model.get('envelope', {})
    systems = building_model.get('systems', {})
    lighting = building_model.get('lighting', {})

    # ── Geometry ─────────────────────────────────────────────────────────────
    try:
        footprint_sqft = float(geom.get('footprint_sqft', 0) or 0)
    except (TypeError, ValueError):
        footprint_sqft = 0.0

    try:
        num_stories = int(geom.get('stories', 1) or 1)
    except (TypeError, ValueError):
        num_stories = 1

    if footprint_sqft <= 0:
        footprint_sqft = 10000.0

    depth = round(math.sqrt(footprint_sqft / 1.5), 2)
    width = round(footprint_sqft / depth, 2)

    width_m = round(width * 0.3048, 3)
    depth_m = round(depth * 0.3048, 3)

    floor_to_floor_m = 4.0
    floor_to_ceiling_m = 3.0

    if num_stories == 1:
        story_labels = ['Ground']
    elif num_stories == 2:
        story_labels = ['Ground', 'Upper']
    elif num_stories == 3:
        story_labels = ['Ground', 'Mid', 'Top']
    else:
        story_labels = ['Ground'] + [f'Floor_{i}' for i in range(2, num_stories)] + ['Top']

    stories = []
    for label in story_labels:
        w = round(width_m, 2)
        d = round(depth_m, 2)
        verts = [[0.0, d], [0.0, 0.0], [w, 0.0], [w, d]]
        stories.append({
            "name": f"Story_{label}",
            "floor_to_floor_height": floor_to_floor_m,
            "floor_to_ceiling_height": floor_to_ceiling_m,
            "spaces": [{
                "name": f"Zone_{label}",
                "width": w,
                "depth": d,
                "vertices": verts,
            }]
        })

    # ── Constructions ────────────────────────────────────────────────────────
    # Prefer pre-populated constructions[] list (written by scenario generators).
    # Otherwise read flat envelope keys (original BuildingCollector output).
    _existing_constructions = building_model.get('constructions') or []
    _ec = _existing_constructions[0] if _existing_constructions else {}

    # Wall R-value: prefer r_value keys over u_value (adapter converts u→r)
    if 'wall_r_value' in _ec:
        wall_r = float(_ec['wall_r_value'])
    elif 'wall_r_value' in envelope:
        wall_r = float(envelope['wall_r_value'])
    elif 'wall_u_value' in envelope:
        wall_r = u2r(float(envelope['wall_u_value']))
    else:
        wall_r = u2r(0.064)  # ~R-15.6 default

    if 'roof_r_value' in _ec:
        roof_r = float(_ec['roof_r_value'])
    elif 'roof_r_value' in envelope:
        roof_r = float(envelope['roof_r_value'])
    elif 'roof_u_value' in envelope:
        roof_r = u2r(float(envelope['roof_u_value']))
    else:
        roof_r = u2r(0.048)  # ~R-20.8 default

    if 'slab_r_value' in _ec:
        slab_r = float(_ec['slab_r_value'])
    elif 'slab_r_value' in envelope:
        slab_r = float(envelope['slab_r_value'])
    else:
        slab_r = 0.0

    constructions = [{
        "name": "ExteriorWall",
        "wall_r_value": wall_r,
        "roof_r_value": roof_r,
        "slab_r_value": slab_r,
    }]

    # ── Windows ──────────────────────────────────────────────────────────────
    _existing_windows = building_model.get('window_defs') or []
    _ew = _existing_windows[0] if _existing_windows else {}

    win_u = float(_ew.get('u_factor') or envelope.get('window_u_factor', 0.57))
    win_shgc = float(_ew.get('shgc') or envelope.get('window_shgc', 0.40))
    win_wwr = float(envelope.get('window_to_wall_ratio', 0.40))

    window_defs = [{
        "name": "ExteriorWindow",
        "u_factor": win_u,
        "shgc": win_shgc,
        "wwr": win_wwr,
    }]

    # ── HVAC Equipment ───────────────────────────────────────────────────────
    _existing_hvac = building_model.get('hvac_equipment') or []
    _eh = _existing_hvac[0] if _existing_hvac else {}

    # Scenario generators may write 'heating_cop' or 'heating_efficiency'
    heating_cop = (
        float(_eh['heating_cop'])            if _eh.get('heating_cop')          else
        float(_eh['heating_efficiency'])     if _eh.get('heating_efficiency')   else
        float(systems['heating_cop'])        if systems.get('heating_cop')      else
        float(systems['heating_efficiency']) if systems.get('heating_efficiency') else
        3.3
    )
    cooling_eer = (
        float(_eh['cooling_eer'])    if _eh.get('cooling_eer')    else
        float(systems['cooling_eer']) if systems.get('cooling_eer') else
        11.5
    )
    equip_type = _eh.get('equipment_type') or systems.get('equipment_type') or 'IdealLoads'

    hvac_equipment = [{
        "name": "HVAC_System",
        "equipment_type": equip_type,
        "heating_cop": heating_cop,
        "cooling_eer": cooling_eer,
    }]

    # ── Lighting ─────────────────────────────────────────────────────────────
    lpd = float(
        building_model.get('project', {}).get('lighting_lpd') or
        lighting.get('lpd_w_per_sf') or
        1.0
    )

    # ── Project Metadata ─────────────────────────────────────────────────────
    _proj = building_model.get('project', {})
    conditioned_area_ft2 = (
        _proj.get('conditioned_area_ft2') or
        footprint_sqft * num_stories
    )

    project = {
        "name": _proj.get('name') or building_model.get('name', 'Building'),
        "building_type": _proj.get('building_type') or building_model.get('building_type', 'Office'),
        "conditioned_area_ft2": conditioned_area_ft2,
        "lighting_lpd": lpd,
        "infiltration_ach": float(building_model.get('infiltration', {}).get('ach', 0.4)),
    }

    return {
        "project": project,
        "stories": stories,
        "constructions": constructions,
        "window_defs": window_defs,
        "hvac_equipment": hvac_equipment,
    }
