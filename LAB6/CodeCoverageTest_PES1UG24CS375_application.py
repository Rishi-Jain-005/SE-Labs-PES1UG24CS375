"""
Lab 6 - Code (Line) Coverage tests
SRN: PES1UG24CS375
Target module: amusement_park_ride_access.py
Goal: execute every line of the module at least once.
"""
import pytest
from amusement_park_ride_access import process_ride_admissions, inspect_safety_restraints


def make_group(ride_type="family", patrons=None, is_open=True, fast_lane=False):
    return {
        "is_open": is_open,
        "ride_type": ride_type,
        "has_fast_lane": fast_lane,
        "patrons": patrons if patrons is not None else [],
    }


def patron(height=150, health=False, child=False):
    return {"height_cm": height, "health_warning": health, "is_child": child}


# ---------- process_ride_admissions ----------

def test_single_adult_family_ride():
    result = process_ride_admissions([make_group("family", [patron()])], 5.0)
    assert result == {"total_revenue": 10.0, "status": "COMPLETED"}


def test_invalid_groups_type_raises():
    with pytest.raises(ValueError):
        process_ride_admissions("not a list", 5.0)


def test_closed_group_is_skipped():
    result = process_ride_admissions([make_group(is_open=False, patrons=[patron()])], 5.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_ADMISSIONS"}


def test_roller_coaster_adult():
    result = process_ride_admissions([make_group("roller_coaster", [patron()])], 5.0)
    assert result["total_revenue"] == 25.0


def test_water_ride_adult():
    result = process_ride_admissions([make_group("water_ride", [patron()])], 5.0)
    assert result["total_revenue"] == 18.0


def test_unknown_ride_type_rejected():
    result = process_ride_admissions([make_group("bumper_cars", [patron()])], 5.0)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_invalid_height_rejected():
    result = process_ride_admissions([make_group("family", [patron(height=0)])], 5.0)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_health_warning_on_roller_coaster_voids_group():
    patrons = [patron(), patron(health=True), patron()]
    result = process_ride_admissions([make_group("roller_coaster", patrons)], 5.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_ADMISSIONS"}


def test_health_warning_on_family_ride_only_rejects_that_patron():
    result = process_ride_admissions([make_group("family", [patron(), patron(health=True)])], 5.0)
    assert result == {"total_revenue": 10.0, "status": "COMPLETED"}


def test_too_short_patron_rejected():
    result = process_ride_admissions([make_group("family", [patron(height=119)])], 5.0)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_child_gets_discount():
    result = process_ride_admissions([make_group("roller_coaster", [patron(child=True)])], 5.0)
    assert result["total_revenue"] == 15.0


def test_fast_lane_fee_added():
    result = process_ride_admissions([make_group("family", [patron()], fast_lane=True)], 5.0)
    assert result["total_revenue"] == 15.0


def test_safety_audit_when_more_than_four_rejections():
    patrons = [patron(height=100) for _ in range(5)] + [patron()]
    result = process_ride_admissions([make_group("family", patrons)], 5.0)
    assert result == {"total_revenue": 10.0, "status": "SAFETY_AUDIT"}


# ---------- inspect_safety_restraints ----------

def test_restraints_no_data():
    assert inspect_safety_restraints([]) == "NO_DATA"


def test_restraints_emergency_lock():
    assert inspect_safety_restraints([[1, 0, 0]]) == "EMERGENCY_LOCK"


def test_restraints_safe_with_streak_reset():
    assert inspect_safety_restraints([[0, 1, 0, 1]]) == "SAFE"
