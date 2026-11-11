import math

MIN_HEIGHT_CM = 120      # minimum height to be allowed on the ride
MAX_HEIGHT_CM = 300      # anything above this is treated as bad data


def validate_height_and_fastpass(rider_spec):
    """Input format 'Height:FastPass', e.g. '140:YES'.
    Returns a status string; never raises on bad input."""
    if not isinstance(rider_spec, str):
        return "Invalid input: rider spec must be text like 140:YES"

    parts = rider_spec.strip().split(':')
    if len(parts) != 2:
        return "Invalid input: expected exactly one ':' (format Height:YES/NO)"
    height_str, pass_str = parts

    try:
        height = int(height_str.strip())
    except (ValueError, OverflowError):
        return "Invalid input: height must be a whole number"

    if not (0 < height <= MAX_HEIGHT_CM):
        return f"Invalid input: height must be between 1 and {MAX_HEIGHT_CM} cm"

    pass_map = {"YES": True, "NO": False}
    key = pass_str.strip().upper()
    if key not in pass_map:
        return "Invalid input: FastPass must be YES or NO"
    has_fastpass = pass_map[key]

    eligible = height >= MIN_HEIGHT_CM
    status = "FastPass Priority" if has_fastpass else "Standard Entry"
    return f"Height {height}cm: {'Approved' if eligible else 'Denied'} ({status})"


def compute_dispatch_throughput(ride_metric_str):
    """Input format 'riders/mins', e.g. '48/2.5'.
    Returns riders per minute (float) or an error string; never raises."""
    if not isinstance(ride_metric_str, str):
        return "Invalid input: metric must be text like 48/2.5"

    parts = ride_metric_str.split('/')
    if len(parts) != 2:
        return "Invalid input: expected exactly one '/' (format riders/mins)"

    try:
        riders = float(parts[0].strip())
        cycle_mins = float(parts[1].strip())
    except (ValueError, OverflowError):
        return "Invalid input: riders and minutes must be numbers"

    # float() happily accepts 'nan', 'inf', '1e999' -> reject them
    if not (math.isfinite(riders) and math.isfinite(cycle_mins)):
        return "Invalid input: values must be finite numbers"
    if riders < 0:
        return "Invalid input: riders cannot be negative"
    if cycle_mins <= 0:
        return "Invalid input: cycle time must be greater than 0"  # avoids ZeroDivisionError

    try:
        rate = riders / cycle_mins
    except (ZeroDivisionError, OverflowError):
        return "Invalid input: could not compute throughput"
    if not math.isfinite(rate):
        return "Invalid input: throughput out of range"
    return round(rate, 2)


def resolve_safety_restraint_code(zone_code):
    """Zone code like 'CST_01' or 'WTR_A'. Returns restraint type or an error string."""
    if not isinstance(zone_code, str):
        return "Invalid input: zone code must be text like CST_01"

    code = zone_code.strip().upper()
    if not code:
        return "Invalid input: zone code is empty"

    prefix = code.split('_')[0]     # 'CST_01' -> 'CST'; rejects 'CSTXYZ'
    restraint_types = {
        "CST": "Over-the-Shoulder Harness",
        "WTR": "Lap Bar and Seatbelt",
        "DRP": "Hydraulic Shoulder Vest",
        "WHL": "Manual Safety Bar",
    }
    if prefix not in restraint_types:
        return f"Invalid input: unknown zone prefix '{prefix[:10]}'"
    return restraint_types[prefix]


def main():
    print("==== Running validate_height_and_fastpass ====")
    r_input = input("Enter rider spec (Height:FastPass, e.g. 140:YES): ")
    print(validate_height_and_fastpass(r_input))

    print("\n==== Running compute_dispatch_throughput ====")
    t_input = input("Enter riders/mins (e.g. 48/2.5): ")
    print("Throughput (riders/min):", compute_dispatch_throughput(t_input))

    print("\n==== Running resolve_safety_restraint_code ====")
    z_input = input("Enter ride zone code (e.g. CST_01, WTR_A): ")
    print("Restraint:", resolve_safety_restraint_code(z_input))


if __name__ == "__main__":
    main()
