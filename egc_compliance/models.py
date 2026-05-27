"""Domain models for EGC compliance analysis."""

from enum import Enum
from pydantic import BaseModel, Field


class ClimateZone(str, Enum):
    """ASHRAE climate zones."""
    CZ_1A = "1A"
    CZ_2A = "2A"
    CZ_2B = "2B"
    CZ_3A = "3A"
    CZ_3B = "3B"
    CZ_3C = "3C"
    CZ_4A = "4A"
    CZ_4B = "4B"
    CZ_4C = "4C"
    CZ_5A = "5A"
    CZ_5B = "5B"
    CZ_5C = "5C"
    CZ_6A = "6A"
    CZ_6B = "6B"
    CZ_7 = "7"
    CZ_8 = "8"


class OccupancyType(str, Enum):
    """Building occupancy types."""
    MULTIFAMILY_RESIDENTIAL = "multifamily_residential"
    OFFICE = "office"
    RETAIL = "retail"
    SCHOOL = "school"
    HOSPITAL = "hospital"
    HOTEL = "hotel"
    WAREHOUSE = "warehouse"
    OTHER = "other"


class HeatingSystemType(str, Enum):
    """Heating system types."""
    GAS_BOILER = "gas_boiler"
    GAS_FURNACE = "gas_furnace"
    ELECTRIC_BASEBOARD = "electric_baseboard"
    ASHP = "ashp"  # Air-source heat pump
    GSHP = "gshp"  # Ground-source heat pump
    DISTRICT_STEAM = "district_steam"
    DISTRICT_HW = "district_hot_water"


class CoolingSystemType(str, Enum):
    """Cooling system types."""
    PTAC = "ptac"
    SPLIT_DX = "split_dx"
    CHILLED_WATER = "chilled_water"
    VRF = "vrf"
    EVAPORATIVE = "evaporative"
    NONE = "none"


class DHWSystemType(str, Enum):
    """Domestic hot water system types."""
    GAS_STORAGE = "gas_storage"
    GAS_TANKLESS = "gas_tankless"
    ELECTRIC_STORAGE = "electric_storage"
    ELECTRIC_TANKLESS = "electric_tankless"
    HEAT_PUMP_WH = "heat_pump_water_heater"
    DISTRICT = "district"


class EnvelopeData(BaseModel):
    """Building envelope characteristics."""
    wall_r_value_ci: float = Field(..., description="Continuous insulation R-value (h·ft²·°F/BTU)")
    wall_r_value_cavity: float = Field(..., description="Cavity insulation R-value")
    roof_r_value: float = Field(..., description="Total roof R-value")
    slab_r_value: float = Field(..., description="Slab edge insulation R-value (0 if none)")
    slab_depth_ft: float = Field(..., description="Slab insulation depth in feet (0 if none)")
    window_u_factor: float = Field(..., description="Overall window U-factor (BTU/h·ft²·°F)")
    window_shgc: float = Field(..., description="Solar heat gain coefficient (0–1)")
    window_to_wall_ratio: float = Field(..., description="WWR as fraction (0–1)")


class HVACData(BaseModel):
    """HVAC system characteristics."""
    heating_type: HeatingSystemType
    heating_efficiency: float = Field(..., description="AFUE (0–1) or COP; units per heating_type")
    cooling_type: CoolingSystemType
    cooling_efficiency: float = Field(..., description="EER or COP; units per cooling_type")
    dhw_type: DHWSystemType
    dhw_efficiency: float = Field(..., description="EF (0–1) or COP for HPWH")


class LightingData(BaseModel):
    """Lighting characteristics."""
    lpd_w_per_sqft: float = Field(..., description="Lighting power density W/ft²")
    fraction_led: float = Field(..., description="0–1; used for cost-payback calcs")


class UtilityMonth(BaseModel):
    """Monthly utility data."""
    year: int
    month: int = Field(..., description="1–12")
    electricity_kwh: float
    gas_kwh: float = Field(..., description="All gas converted to kWh equivalent")
    electricity_cost_usd: float | None = None
    gas_cost_usd: float | None = None


class UtilityData(BaseModel):
    """Utility billing data."""
    months: list[UtilityMonth] = Field(..., description="Must have ≥ 12 consecutive months")
    weather_normalized_eui_kwh_per_sqft: float = Field(..., description="From Audette platform")
    electricity_rate_usd_per_kwh: float
    gas_rate_usd_per_kwh: float


class RetrofitECM(BaseModel):
    """One energy conservation measure in the retrofit package."""
    name: str
    description: str
    # Overrides for the Retrofit scenario IDF — any field not set inherits as-built
    heating_type: HeatingSystemType | None = None
    heating_efficiency: float | None = None
    cooling_type: CoolingSystemType | None = None
    cooling_efficiency: float | None = None
    dhw_type: DHWSystemType | None = None
    dhw_efficiency: float | None = None
    wall_r_value_ci: float | None = None
    roof_r_value: float | None = None
    slab_r_value: float | None = None
    window_u_factor: float | None = None
    window_shgc: float | None = None
    lpd_w_per_sqft: float | None = None


class BuildingModel(BaseModel):
    """Complete building data model."""
    # Identity
    building_uid: str
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    climate_zone: ClimateZone
    occupancy_type: OccupancyType

    # Physical
    gfa_sqft: float = Field(..., description="Gross floor area in square feet")
    stories: int
    year_built: int
    floor_to_floor_height_ft: float = 10.0

    # Systems
    envelope: EnvelopeData
    hvac: HVACData
    lighting: LightingData
    plug_load_density_w_per_sqft: float

    # Utility & financial
    utility: UtilityData

    # Retrofit package (list of ECMs to combine)
    retrofit_ecms: list[RetrofitECM]


class SimulationScenario(str, Enum):
    """EnergyPlus simulation scenarios."""
    AS_BUILT = "as_built"
    DOE_REF = "doe_ref"
    CODE_MIN = "code_min"
    RETROFIT = "retrofit"


class EndUseBreakdown(BaseModel):
    """Energy end-use breakdown."""
    space_heating_kwh: float
    space_cooling_kwh: float
    dhw_kwh: float
    lighting_kwh: float
    plug_loads_kwh: float

    def total_gas_kwh(self, heating_is_gas: bool, dhw_is_gas: bool) -> float:
        """Returns heating + DHW if system is gas, else 0."""
        total = 0.0
        if heating_is_gas:
            total += self.space_heating_kwh
        if dhw_is_gas:
            total += self.dhw_kwh
        return total

    def total_elec_kwh(self, heating_is_gas: bool, dhw_is_gas: bool) -> float:
        """Returns cooling + lighting + plugs + (heating if electric) + (DHW if electric)."""
        total = self.space_cooling_kwh + self.lighting_kwh + self.plug_loads_kwh
        if not heating_is_gas:
            total += self.space_heating_kwh
        if not dhw_is_gas:
            total += self.dhw_kwh
        return total


class ScenarioResult(BaseModel):
    """Results for one simulation scenario."""
    scenario: SimulationScenario
    raw_ep_total_kwh: float
    calibrated_total_kwh: float
    weather_normalized_total_kwh: float
    eui_kwh_per_sqft: float = Field(..., description="Final weather-normalized EUI")
    end_uses_kwh_per_sqft: EndUseBreakdown = Field(..., description="Weather-normalized per-sqft")
    end_uses_mwh: EndUseBreakdown = Field(..., description="Weather-normalized absolute MWh")
    annual_energy_cost_usd: float
    annual_gas_mwh: float
    annual_elec_mwh: float


class PrescriptiveCheck(BaseModel):
    """One prescriptive compliance check."""
    name: str
    requirement: str = Field(..., description="Human-readable threshold (e.g. 'R-13 + CI R-7.5')")
    actual_value: str = Field(..., description="Human-readable actual value")
    passes: bool


class ComplianceReport(BaseModel):
    """Complete compliance analysis report."""
    scenarios: dict[SimulationScenario, ScenarioResult]
    prescriptive_checks: list[PrescriptiveCheck]
    calibration_factor: float
    weather_normalization_factor: float
    baseline_period_label: str = Field(..., description="e.g. 'Mar 2025 – Feb 2026'")
    code_minimum_eui: float = Field(..., description="From code_min scenario")
