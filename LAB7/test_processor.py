import math

from hypothesis import given, settings, strategies as st
from processor import (
    validate_height_and_fastpass,
    compute_dispatch_throughput,
    resolve_safety_restraint_code,
)


# --------------------------------------------------------------------------
# Part 1: "No crash" fuzz tests (text + None, the To-Do functions)
# --------------------------------------------------------------------------

@given(st.text() | st.none())
def test_validate_height_and_fastpass_no_crash(s):
    try:
        result = validate_height_and_fastpass(s)
        assert isinstance(result, str)
    except Exception as e:
        assert False, f"validate_height_and_fastpass crashed with: {type(e).__name__}: {e}"


@given(st.text() | st.none())
def test_compute_dispatch_throughput_safe(s):
    try:
        result = compute_dispatch_throughput(s)
        # valid input -> finite float, invalid input -> error string
        assert isinstance(result, (float, str))
        if isinstance(result, float):
            assert math.isfinite(result)
    except Exception as e:
        assert False, f"compute_dispatch_throughput crashed with: {type(e).__name__}: {e}"


@given(st.text() | st.none())
def test_resolve_safety_restraint_code_safe(s):
    try:
        result = resolve_safety_restraint_code(s)
        assert isinstance(result, str)
    except Exception as e:
        assert False, f"resolve_safety_restraint_code crashed with: {type(e).__name__}: {e}"


# --------------------------------------------------------------------------
# Part 2: Extra fuzzing - other input types (ints, lists, bytes, floats ...)
# --------------------------------------------------------------------------

anything = st.one_of(
    st.none(), st.integers(), st.floats(), st.booleans(),
    st.binary(), st.lists(st.integers()), st.text(),
)


@given(anything)
def test_validate_any_type_no_crash(x):
    assert isinstance(validate_height_and_fastpass(x), str)


@given(anything)
def test_throughput_any_type_no_crash(x):
    assert isinstance(compute_dispatch_throughput(x), (float, str))


@given(anything)
def test_restraint_any_type_no_crash(x):
    assert isinstance(resolve_safety_restraint_code(x), str)


# --------------------------------------------------------------------------
# Part 3: Property tests on VALID / structured inputs (correct behaviour)
# --------------------------------------------------------------------------

@given(st.integers(min_value=120, max_value=250), st.sampled_from(["YES", "NO", "yes", " No "]))
def test_valid_tall_rider_is_approved(h, p):
    out = validate_height_and_fastpass(f"{h}:{p}")
    assert out.startswith(f"Height {h}cm: Approved")


@given(st.integers(min_value=1, max_value=119), st.sampled_from(["YES", "NO"]))
def test_short_rider_is_denied(h, p):
    assert validate_height_and_fastpass(f"{h}:{p}").startswith(f"Height {h}cm: Denied")


@given(st.integers(max_value=0) | st.integers(min_value=301))
def test_out_of_range_height_rejected(h):
    assert validate_height_and_fastpass(f"{h}:YES").startswith("Invalid")


@given(st.text(max_size=10).filter(lambda t: t.strip().upper() not in ("YES", "NO")))
def test_bad_fastpass_value_rejected(p):
    assert validate_height_and_fastpass(f"150:{p}").startswith("Invalid")


@given(st.integers(min_value=0, max_value=10_000),
       st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False))
def test_valid_throughput_matches_formula(riders, mins):
    result = compute_dispatch_throughput(f"{riders}/{mins}")
    assert isinstance(result, float)
    assert result == round(riders / mins, 2)
    assert result >= 0


@given(st.integers(min_value=0, max_value=1000))
def test_zero_cycle_time_rejected(riders):
    assert isinstance(compute_dispatch_throughput(f"{riders}/0"), str)


@given(st.sampled_from(["nan", "inf", "-inf", "NaN", "Infinity", "1e999"]))
def test_non_finite_values_rejected(bad):
    assert isinstance(compute_dispatch_throughput(f"{bad}/2"), str)
    assert isinstance(compute_dispatch_throughput(f"10/{bad}"), str)


@given(st.sampled_from(["CST", "WTR", "DRP", "WHL"]),
       st.text(alphabet="ABCDEFGHIJ0123456789", max_size=5))
def test_known_zone_codes_resolve(prefix, suffix):
    code = prefix + ("_" + suffix if suffix else "")
    result = resolve_safety_restraint_code(code)
    assert not result.startswith("Invalid")
    # case-insensitivity + whitespace tolerance
    assert resolve_safety_restraint_code(f"  {code.lower()}  ") == result


@given(st.text(max_size=12).filter(lambda t: t.strip().upper().split("_")[0] not in ("CST", "WTR", "DRP", "WHL")))
def test_unknown_zone_codes_rejected(code):
    assert resolve_safety_restraint_code(code).startswith("Invalid")
