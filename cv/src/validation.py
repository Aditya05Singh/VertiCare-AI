import math
from typing import Dict, Any, List, Tuple, Optional

ALLOWED_CV_FEATURE_NAMES = {
    "horizontal_amplitude",
    "vertical_amplitude",
    "horizontal_velocity_mean",
    "vertical_velocity_mean",
    "horizontal_velocity_max",
    "vertical_velocity_max",
    "direction_changes_h",
    "direction_changes_v",
    "blink_count",
    "blink_rate_per_min",
    "valid_ratio",
    "total_frames",
    "valid_frames",
}


def is_finite_number(val: Any) -> bool:
    """Check that value is an integer or float that is neither NaN nor Infinite."""
    if isinstance(val, (int, float)):
        if math.isnan(val) or math.isinf(val):
            return False
        return True
    return False


def validate_feature_dict(features: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate a dictionary of numerical CV features.
    Ensures all keys are recognized and all values are finite numerical floats/ints.
    """
    if not isinstance(features, dict) or len(features) == 0:
        return False, "Feature dictionary must be a non-empty object."

    if len(features) > 50:
        return False, "Feature payload exceeds maximum allowed size (50 features)."

    for key, val in features.items():
        if key not in ALLOWED_CV_FEATURE_NAMES:
            return False, f"Unrecognized feature name: '{key}'."

        if not is_finite_number(val):
            return False, f"Feature '{key}' has non-finite value '{val}'."

    return True, None

