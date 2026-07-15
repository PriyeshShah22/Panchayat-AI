"""Canonical building and flat rules for this society deployment."""
from __future__ import annotations

import re

WINGS = ("A", "B", "C", "D")
FLOORS = range(1, 5)
FLATS_PER_FLOOR = range(1, 5)
FLAT_PATTERN = re.compile(r"^([1-4])0([1-4])$")


def normalize_wing(value: str) -> str:
    return value.strip().upper()


def is_valid_wing(value: str) -> bool:
    return normalize_wing(value) in WINGS


def normalize_flat(value: str) -> str:
    return value.strip()


def is_valid_flat(value: str) -> bool:
    return bool(FLAT_PATTERN.fullmatch(normalize_flat(value)))


def floor_for_flat(value: str) -> int:
    match = FLAT_PATTERN.fullmatch(normalize_flat(value))
    if not match:
        raise ValueError("Flat must be between 101-104, 201-204, 301-304, or 401-404")
    return int(match.group(1))


def all_flat_numbers() -> list[str]:
    return [f"{floor}0{unit}" for floor in FLOORS for unit in FLATS_PER_FLOOR]
