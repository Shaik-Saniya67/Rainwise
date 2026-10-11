"""Shared RainWise calculation logic.

This single module is used by BOTH execution paths:
  * local mode  - the Streamlit app imports and calls it directly
  * AWS mode    - the Lambda handler imports and calls it

It uses only the Python standard library, so it packages into Lambda with no
extra dependencies.

Core formula (1 mm of rain on 1 m^2 of surface = 1 litre):

    harvestable_litres = roof_area_m2 * rainfall_mm * efficiency_percent / 100
"""
from __future__ import annotations

import math
from typing import Any, Mapping

STANDARD_TANKS_LITRES: tuple[int, ...] = (500, 1_000, 2_000, 5_000, 10_000, 20_000)
LARGEST_TANK_LITRES: int = STANDARD_TANKS_LITRES[-1]

# Accepted input ranges (sanity limits, not physical claims).
MAX_ROOF_AREA_M2 = 1_000_000.0   # 100 hectares
MAX_RAINFALL_MM = 5_000.0        # far beyond any single rainfall event
MIN_EFFICIENCY, MAX_EFFICIENCY = 0.0, 100.0

FORMULA = "harvestable litres = roof area (m²) × rainfall (mm) × efficiency (%) ÷ 100"


class ValidationError(ValueError):
    """Raised when inputs are missing, malformed or out of range.

    ``errors`` holds one human-readable message per problem.
    """

    def __init__(self, errors: list[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


def _as_number(value: Any, label: str, errors: list[str]) -> float | None:
    """Return ``value`` as a finite float, or record an error and return None."""
    # bool is a subclass of int; True/False must not pass as numbers.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{label} must be a number.")
        return None
    number = float(value)
    if not math.isfinite(number):
        errors.append(f"{label} must be a finite number.")
        return None
    return number


def validate_inputs(roof_area_m2: Any, rainfall_mm: Any, efficiency_percent: Any) -> tuple[float, float, float]:
    """Validate the three inputs and return them as floats.

    Rules:
      * roof area:  number, > 0 and <= MAX_ROOF_AREA_M2
      * rainfall:   number, >= 0 and <= MAX_RAINFALL_MM  (0 mm is a valid "no rain" case)
      * efficiency: number, >= 0 and <= 100               (0 % is accepted: nothing collected)
    """
    errors: list[str] = []
    area = _as_number(roof_area_m2, "Roof area", errors)
    rain = _as_number(rainfall_mm, "Rainfall", errors)
    eff = _as_number(efficiency_percent, "Collection efficiency", errors)

    if area is not None and not (0 < area <= MAX_ROOF_AREA_M2):
        errors.append(f"Roof area must be greater than 0 and at most {MAX_ROOF_AREA_M2:,.0f} m².")
    if rain is not None and not (0 <= rain <= MAX_RAINFALL_MM):
        errors.append(f"Rainfall must be between 0 and {MAX_RAINFALL_MM:,.0f} mm.")
    if eff is not None and not (MIN_EFFICIENCY <= eff <= MAX_EFFICIENCY):
        errors.append("Collection efficiency must be between 0 and 100 %.")

    if errors:
        raise ValidationError(errors)
    return area, rain, eff  # type: ignore[return-value]


def harvest_litres(roof_area_m2: float, rainfall_mm: float, efficiency_percent: float) -> float:
    """The core formula. Inputs are assumed already validated."""
    return roof_area_m2 * rainfall_mm * efficiency_percent / 100.0


def recommend_tank(litres: float) -> int | None:
    """Smallest standard tank >= ``litres``.

    Returns None when there is nothing to store (<= 0) or when the volume exceeds
    the largest standard tank.
    """
    if litres <= 0:
        return None
    for size in STANDARD_TANKS_LITRES:
        if litres <= size:
            return size
    return None


def format_litres(value: float) -> str:
    """12345.5 -> '12,345.5'; 8000.0 -> '8,000'."""
    rounded = round(value, 2)
    if rounded == int(rounded):
        return f"{int(rounded):,}"
    return f"{rounded:,.2f}".rstrip("0").rstrip(".")


def calculate(roof_area_m2: Any, rainfall_mm: Any, efficiency_percent: Any) -> dict[str, Any]:
    """Validate inputs, compute the harvest and recommend a tank.

    Returns a JSON-serialisable dict. Raises :class:`ValidationError` on bad input.
    """
    area, rain, eff = validate_inputs(roof_area_m2, rainfall_mm, efficiency_percent)
    litres = harvest_litres(area, rain, eff)
    tank = recommend_tank(litres)
    exceeded = litres > LARGEST_TANK_LITRES
    tanks_needed = math.ceil(litres / LARGEST_TANK_LITRES) if exceeded else None
    shown = format_litres(litres)

    if litres <= 0:
        reason = "no rainfall" if rain == 0 else "0% collection efficiency"
        message = (
            f"With {reason}, nothing would be collected, so no tank is needed for this event. "
            "Try a typical rainfall event for your area to see your potential."
        )
        recommendation = "Enter a rainfall amount above 0 mm and an efficiency above 0% to size a tank."
    elif exceeded:
        message = (
            f"Your roof could collect approximately {shown} litres from this rainfall event, "
            f"which is more than the largest standard tank ({LARGEST_TANK_LITRES:,} L)."
        )
        recommendation = (
            f"Plan for about {tanks_needed} tanks of {LARGEST_TANK_LITRES:,} L, or a larger storage system. "
            "Add a first-flush diverter and route overflow safely to a drain or recharge pit."
        )
    else:
        message = f"Your roof could collect approximately {shown} litres from this rainfall event."
        recommendation = (
            f"A {tank:,} L tank is the smallest standard size that fits this event. "
            "Add a first-flush diverter, a mesh inlet filter and a safe overflow outlet."
        )
        if litres / tank >= 0.9:
            recommendation += " The tank would be nearly full, so consider the next size up for headroom."

    return {
        "harvestable_litres": round(litres, 2),
        "harvestable_kl": round(litres / 1000.0, 3),
        "recommended_tank_litres": tank,
        "capacity_exceeded": exceeded,
        "largest_tanks_needed": tanks_needed,
        "message": message,
        "recommendation": recommendation,
    }


def result_from_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Convenience for the Lambda handler: calculate from a JSON-style mapping."""
    return calculate(
        payload.get("roof_area_m2"),
        payload.get("rainfall_mm"),
        payload.get("efficiency_percent"),
    )
