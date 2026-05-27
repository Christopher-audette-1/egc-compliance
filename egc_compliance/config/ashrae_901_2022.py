"""ASHRAE 90.1-2022 prescriptive code minimum requirements by climate zone."""

from dataclasses import dataclass
from egc_compliance.models import ClimateZone


@dataclass
class CodeMinimums:
    """Prescriptive minimum requirements for one climate zone."""
    wall_r_ci_min: float          # Minimum continuous insulation R-value
    wall_r_cavity_min: float      # Minimum cavity R-value (alternative path)
    roof_r_min: float
    slab_r_min: float
    slab_depth_ft_min: float
    window_u_max: float
    window_shgc_max: float
    heating_eff_min: float        # AFUE or COP lower bound
    cooling_eer_min: float
    dhw_ef_min: float
    lpd_max_w_per_sqft: float


# ASHRAE 90.1-2022 Table 5.5-1 through 5.5-8 (Envelope)
# ASHRAE 90.1-2022 Table 6.8.1 (HVAC Equipment Efficiency)
# ASHRAE 90.1-2022 Table 9.6.1 (Lighting Power Density - Multifamily)

ASHRAE_901_2022_MINIMUMS: dict[ClimateZone, CodeMinimums] = {
    ClimateZone.CZ_1A: CodeMinimums(
        wall_r_ci_min=3.8, wall_r_cavity_min=13,
        roof_r_min=25,
        slab_r_min=0, slab_depth_ft_min=0,
        window_u_max=0.50, window_shgc_max=0.25,
        heating_eff_min=0.80, cooling_eer_min=12.0, dhw_ef_min=0.80,
        lpd_max_w_per_sqft=0.60
    ),
    ClimateZone.CZ_2A: CodeMinimums(
        wall_r_ci_min=3.8, wall_r_cavity_min=13,
        roof_r_min=25,
        slab_r_min=0, slab_depth_ft_min=0,
        window_u_max=0.50, window_shgc_max=0.25,
        heating_eff_min=0.80, cooling_eer_min=12.0, dhw_ef_min=0.80,
        lpd_max_w_per_sqft=0.60
    ),
    ClimateZone.CZ_2B: CodeMinimums(
        wall_r_ci_min=3.8, wall_r_cavity_min=13,
        roof_r_min=25,
        slab_r_min=0, slab_depth_ft_min=0,
        window_u_max=0.50, window_shgc_max=0.25,
        heating_eff_min=0.80, cooling_eer_min=12.0, dhw_ef_min=0.80,
        lpd_max_w_per_sqft=0.60
    ),
    ClimateZone.CZ_3A: CodeMinimums(
        wall_r_ci_min=3.8, wall_r_cavity_min=13,
        roof_r_min=25,
        slab_r_min=0, slab_depth_ft_min=0,
        window_u_max=0.50, window_shgc_max=0.25,
        heating_eff_min=0.80, cooling_eer_min=12.0, dhw_ef_min=0.80,
        lpd_max_w_per_sqft=0.60
    ),
    ClimateZone.CZ_3B: CodeMinimums(
        wall_r_ci_min=3.8, wall_r_cavity_min=13,
        roof_r_min=25,
        slab_r_min=0, slab_depth_ft_min=0,
        window_u_max=0.50, window_shgc_max=0.40,
        heating_eff_min=0.80, cooling_eer_min=12.0, dhw_ef_min=0.80,
        lpd_max_w_per_sqft=0.60
    ),
    ClimateZone.CZ_3C: CodeMinimums(
        wall_r_ci_min=3.8, wall_r_cavity_min=13,
        roof_r_min=25,
        slab_r_min=0, slab_depth_ft_min=0,
        window_u_max=0.50, window_shgc_max=0.40,
        heating_eff_min=0.80, cooling_eer_min=12.0, dhw_ef_min=0.80,
        lpd_max_w_per_sqft=0.60
    ),
    ClimateZone.CZ_4A: CodeMinimums(
        wall_r_ci_min=7.5, wall_r_cavity_min=13,
        roof_r_min=30,
        slab_r_min=10, slab_depth_ft_min=2.0,
        window_u_max=0.42, window_shgc_max=0.40,
        heating_eff_min=0.80, cooling_eer_min=12.0, dhw_ef_min=0.80,
        lpd_max_w_per_sqft=0.60
    ),
    ClimateZone.CZ_4B: CodeMinimums(
        wall_r_ci_min=7.5, wall_r_cavity_min=13,
        roof_r_min=30,
        slab_r_min=10, slab_depth_ft_min=2.0,
        window_u_max=0.42, window_shgc_max=0.40,
        heating_eff_min=0.80, cooling_eer_min=12.0, dhw_ef_min=0.80,
        lpd_max_w_per_sqft=0.60
    ),
    ClimateZone.CZ_4C: CodeMinimums(
        wall_r_ci_min=7.5, wall_r_cavity_min=13,
        roof_r_min=30,
        slab_r_min=10, slab_depth_ft_min=2.0,
        window_u_max=0.42, window_shgc_max=0.40,
        heating_eff_min=0.80, cooling_eer_min=12.0, dhw_ef_min=0.80,
        lpd_max_w_per_sqft=0.60
    ),
    ClimateZone.CZ_5A: CodeMinimums(
        wall_r_ci_min=7.5, wall_r_cavity_min=13,
        roof_r_min=30,
        slab_r_min=10, slab_depth_ft_min=2.0,
        window_u_max=0.42, window_shgc_max=0.40,
        heating_eff_min=0.80, cooling_eer_min=12.0, dhw_ef_min=0.80,
        lpd_max_w_per_sqft=0.60
    ),
    ClimateZone.CZ_5B: CodeMinimums(
        wall_r_ci_min=7.5, wall_r_cavity_min=13,
        roof_r_min=30,
        slab_r_min=10, slab_depth_ft_min=2.0,
        window_u_max=0.42, window_shgc_max=0.40,
        heating_eff_min=0.80, cooling_eer_min=12.0, dhw_ef_min=0.80,
        lpd_max_w_per_sqft=0.60
    ),
    ClimateZone.CZ_5C: CodeMinimums(
        wall_r_ci_min=7.5, wall_r_cavity_min=13,
        roof_r_min=30,
        slab_r_min=10, slab_depth_ft_min=2.0,
        window_u_max=0.42, window_shgc_max=0.40,
        heating_eff_min=0.80, cooling_eer_min=12.0, dhw_ef_min=0.80,
        lpd_max_w_per_sqft=0.60
    ),
    ClimateZone.CZ_6A: CodeMinimums(
        wall_r_ci_min=13.0, wall_r_cavity_min=13,
        roof_r_min=35,
        slab_r_min=10, slab_depth_ft_min=4.0,
        window_u_max=0.38, window_shgc_max=0.40,
        heating_eff_min=0.80, cooling_eer_min=12.0, dhw_ef_min=0.80,
        lpd_max_w_per_sqft=0.60
    ),
    ClimateZone.CZ_6B: CodeMinimums(
        wall_r_ci_min=13.0, wall_r_cavity_min=13,
        roof_r_min=35,
        slab_r_min=10, slab_depth_ft_min=4.0,
        window_u_max=0.38, window_shgc_max=0.40,
        heating_eff_min=0.80, cooling_eer_min=12.0, dhw_ef_min=0.80,
        lpd_max_w_per_sqft=0.60
    ),
    ClimateZone.CZ_7: CodeMinimums(
        wall_r_ci_min=15.0, wall_r_cavity_min=13,
        roof_r_min=35,
        slab_r_min=15, slab_depth_ft_min=4.0,
        window_u_max=0.36, window_shgc_max=0.40,
        heating_eff_min=0.80, cooling_eer_min=12.0, dhw_ef_min=0.80,
        lpd_max_w_per_sqft=0.60
    ),
    ClimateZone.CZ_8: CodeMinimums(
        wall_r_ci_min=15.0, wall_r_cavity_min=13,
        roof_r_min=35,
        slab_r_min=15, slab_depth_ft_min=4.0,
        window_u_max=0.34, window_shgc_max=0.40,
        heating_eff_min=0.80, cooling_eer_min=12.0, dhw_ef_min=0.80,
        lpd_max_w_per_sqft=0.60
    ),
}
