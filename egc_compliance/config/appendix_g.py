"""ASHRAE 90.1 Appendix G baseline system determination."""

from dataclasses import dataclass
from egc_compliance.models import OccupancyType, HeatingSystemType


@dataclass
class AppendixGSystem:
    """Appendix G baseline HVAC system definition."""
    system_name: str
    system_number: int
    heating_source: str  # "gas", "electric", "district"
    heating_cop: float
    cooling_eer: float
    description: str


def get_appendix_g_system(
    occupancy: OccupancyType,
    gfa_sqft: float,
    heating_type: HeatingSystemType
) -> AppendixGSystem:
    """
    Determine Appendix G baseline system per Table G3.1.1.

    System selection based on:
    - Building type (residential vs. non-residential)
    - Floor area
    - Heating energy source (fossil fuel vs. electric/other)
    """
    is_residential = (occupancy == OccupancyType.MULTIFAMILY_RESIDENTIAL)
    is_fossil_fuel = heating_type in [
        HeatingSystemType.GAS_BOILER,
        HeatingSystemType.GAS_FURNACE
    ]

    # Residential buildings
    if is_residential:
        if gfa_sqft <= 75000:
            if is_fossil_fuel:
                # System 1: PTAC with fossil fuel boiler
                return AppendixGSystem(
                    system_name="PTAC with gas boiler",
                    system_number=1,
                    heating_source="gas",
                    heating_cop=0.80,  # Gas boiler AFUE
                    cooling_eer=10.9,  # PTAC EER per Table 6.8.1-2
                    description="Packaged terminal air conditioner with gas-fired hot water boiler"
                )
            else:
                # System 2: PTHP
                return AppendixGSystem(
                    system_name="PTHP",
                    system_number=2,
                    heating_source="electric",
                    heating_cop=3.3,   # PTHP heating COP per Table 6.8.1-3
                    cooling_eer=10.9,  # PTHP cooling EER
                    description="Packaged terminal heat pump"
                )
        else:
            # Larger residential: System 3 or 4
            if is_fossil_fuel:
                # System 3: PSZ-AC with gas furnace
                return AppendixGSystem(
                    system_name="PSZ-AC with gas furnace",
                    system_number=3,
                    heating_source="gas",
                    heating_cop=0.80,  # Gas furnace AFUE
                    cooling_eer=11.2,  # Packaged AC EER
                    description="Packaged single-zone air conditioner with gas furnace"
                )
            else:
                # System 4: PSZ-HP
                return AppendixGSystem(
                    system_name="PSZ-HP",
                    system_number=4,
                    heating_source="electric",
                    heating_cop=3.4,   # PSZ-HP heating COP
                    cooling_eer=11.0,  # PSZ-HP cooling EER
                    description="Packaged single-zone heat pump"
                )

    # Non-residential buildings
    else:
        if gfa_sqft <= 25000 and occupancy != OccupancyType.HOSPITAL:
            if is_fossil_fuel:
                # System 3: PSZ-AC
                return AppendixGSystem(
                    system_name="PSZ-AC",
                    system_number=3,
                    heating_source="gas",
                    heating_cop=0.80,
                    cooling_eer=11.2,
                    description="Packaged single-zone air conditioner"
                )
            else:
                # System 4: PSZ-HP
                return AppendixGSystem(
                    system_name="PSZ-HP",
                    system_number=4,
                    heating_source="electric",
                    heating_cop=3.4,
                    cooling_eer=11.0,
                    description="Packaged single-zone heat pump"
                )
        elif 25000 < gfa_sqft <= 150000:
            if is_fossil_fuel:
                # System 5: Packaged VAV with reheat
                return AppendixGSystem(
                    system_name="Packaged VAV",
                    system_number=5,
                    heating_source="gas",
                    heating_cop=0.80,
                    cooling_eer=10.5,
                    description="Packaged VAV with gas-fired hot water reheat"
                )
            else:
                # System 6: Packaged VAV with PFP boxes
                return AppendixGSystem(
                    system_name="Packaged VAV with PFP",
                    system_number=6,
                    heating_source="electric",
                    heating_cop=3.3,
                    cooling_eer=10.5,
                    description="Packaged VAV with parallel fan-powered boxes and electric reheat"
                )
        else:
            # > 150,000 sf: System 7 or 8 (chilled water)
            if is_fossil_fuel:
                # System 7: VAV with reheat
                return AppendixGSystem(
                    system_name="VAV with boiler reheat",
                    system_number=7,
                    heating_source="gas",
                    heating_cop=0.80,
                    cooling_eer=12.5,  # Chiller COP
                    description="VAV with chilled water and gas-fired hot water reheat"
                )
            else:
                # System 8: VAV with PFP boxes
                return AppendixGSystem(
                    system_name="VAV with PFP boxes",
                    system_number=8,
                    heating_source="electric",
                    heating_cop=3.3,
                    cooling_eer=12.5,
                    description="VAV with chilled water and parallel fan-powered boxes"
                )
