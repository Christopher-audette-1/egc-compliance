"""EnergyPlus output parser - extracts energy results from CSV/ESO files."""

import csv
import re
from pathlib import Path
from typing import Dict, Any


class ParseError(Exception):
    """Raised when EnergyPlus output cannot be parsed."""
    pass


def parse_eplusout_csv(csv_path: str | Path) -> Dict[str, float]:
    """
    Parse eplusout.csv for annual energy totals.

    Args:
        csv_path: Path to eplusout.csv

    Returns:
        Dict with energy values in kWh:
            - total_electricity_kwh
            - total_gas_kwh
            - heating_kwh
            - cooling_kwh
            - dhw_kwh
            - lighting_kwh
            - plug_loads_kwh
    """
    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise ParseError(f"CSV file not found: {csv_path}")

    results = {
        "total_electricity_kwh": 0.0,
        "total_gas_kwh": 0.0,
        "heating_kwh": 0.0,
        "cooling_kwh": 0.0,
        "dhw_kwh": 0.0,
        "lighting_kwh": 0.0,
        "plug_loads_kwh": 0.0,
    }

    try:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Look for annual run period rows
                if 'RunPeriod' not in row.get('', ''):
                    continue

                # Extract meter values (in Joules)
                for key, value in row.items():
                    key_lower = key.lower()

                    # Facility meters
                    if 'electricity:facility' in key_lower and '[j]' in key_lower:
                        results["total_electricity_kwh"] = float(value) / 3_600_000
                    elif 'naturalgas:facility' in key_lower and '[j]' in key_lower:
                        results["total_gas_kwh"] = float(value) / 3_600_000

                    # End-use meters
                    elif 'heating:' in key_lower and '[j]' in key_lower:
                        results["heating_kwh"] = float(value) / 3_600_000
                    elif 'cooling:' in key_lower and '[j]' in key_lower:
                        results["cooling_kwh"] = float(value) / 3_600_000
                    elif 'waterheater' in key_lower and '[j]' in key_lower:
                        results["dhw_kwh"] = float(value) / 3_600_000
                    elif 'lights' in key_lower and '[j]' in key_lower:
                        results["lighting_kwh"] = float(value) / 3_600_000
                    elif 'equipment' in key_lower and '[j]' in key_lower:
                        results["plug_loads_kwh"] = float(value) / 3_600_000

        # Validate we got some data
        if results["total_electricity_kwh"] == 0 and results["total_gas_kwh"] == 0:
            raise ParseError("No energy data found in CSV (all meters are zero)")

        return results

    except Exception as e:
        if isinstance(e, ParseError):
            raise
        raise ParseError(f"Failed to parse CSV: {str(e)}")


def parse_eplustbl_htm(htm_path: str | Path) -> Dict[str, float]:
    """
    Fallback parser for eplustbl.htm (HTML summary table).

    Args:
        htm_path: Path to eplustbl.htm

    Returns:
        Dict with total energy in kWh
    """
    htm_path = Path(htm_path)

    if not htm_path.exists():
        raise ParseError(f"HTML table file not found: {htm_path}")

    try:
        with open(htm_path, 'r') as f:
            content = f.read()

        # Look for Site Energy Use table
        # Pattern: <td align="right">123.45</td> following "Total Site Energy"
        pattern = r'Total Site Energy.*?<td align="right">([\d.]+)</td>'
        match = re.search(pattern, content, re.DOTALL)

        if match:
            # Value is typically in GJ, convert to kWh
            gj_value = float(match.group(1))
            kwh_value = gj_value * 277.778  # 1 GJ = 277.778 kWh

            return {
                "total_electricity_kwh": kwh_value,  # Approximate
                "total_gas_kwh": 0.0,
                "heating_kwh": 0.0,
                "cooling_kwh": 0.0,
                "dhw_kwh": 0.0,
                "lighting_kwh": 0.0,
                "plug_loads_kwh": 0.0,
            }

        raise ParseError("Could not find Site Energy Use table in HTML")

    except Exception as e:
        if isinstance(e, ParseError):
            raise
        raise ParseError(f"Failed to parse HTML: {str(e)}")
