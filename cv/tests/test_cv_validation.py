import pytest
import math
from cv.src.validation import validate_feature_dict, is_finite_number


def test_is_finite_number():
    assert is_finite_number(0.0) is True
    assert is_finite_number(12.345) is True
    assert is_finite_number(-100) is True
    assert is_finite_number(float("nan")) is False
    assert is_finite_number(float("inf")) is False
    assert is_finite_number(float("-inf")) is False
    assert is_finite_number("string") is False
    assert is_finite_number(None) is False


def test_validate_feature_dict_valid():
    payload = {
        "horizontal_amplitude": 0.05,
        "vertical_amplitude": 0.02,
        "horizontal_velocity_mean": 0.12,
        "vertical_velocity_mean": 0.04,
        "direction_changes_h": 4,
        "blink_count": 2,
    }
    is_valid, err = validate_feature_dict(payload)
    assert is_valid is True
    assert err is None


def test_validate_feature_dict_unrecognized_key():
    payload = {
        "horizontal_amplitude": 0.05,
        "unsupported_key_name": 123.0
    }
    is_valid, err = validate_feature_dict(payload)
    assert is_valid is False
    assert "Unrecognized feature name" in err


def test_validate_feature_dict_nan_value():
    payload = {
        "horizontal_amplitude": float("nan")
    }
    is_valid, err = validate_feature_dict(payload)
    assert is_valid is False
    assert "non-finite value" in err

