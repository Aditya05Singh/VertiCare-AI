import pytest
from ml.src.feature_engineering import extract_features_from_modalities, identify_contributing_factors
from ml.src.config import ALL_FEATURE_COLUMNS


def test_extract_features_all_modalities():
    hc = {
        "dizziness_severity": 6,
        "imbalance_severity": 5,
        "stress_level": 4,
        "sleep_hours": 8.0,
        "triggers": ["head_movement", "stress"],
        "episode_duration": "minutes",
        "hydration_level": "good",
        "medication_adherence": "full",
        "nausea": True,
        "headache": False,
    }

    q_answers = [
        {"question_code": "Q_SPINNING", "answer": True},
        {"question_code": "Q_POSITIONAL", "answer": True},
        {"question_code": "Q_FUNCTIONAL_IMPACT", "answer": "moderate"},
    ]

    cv_feats = {
        "horizontal_amplitude": 0.05,
        "horizontal_velocity_mean": 0.32,
        "direction_changes_h": 4,
        "blink_rate_per_min": 16.0,
    }
    cv_qual = {"valid_ratio": 0.95}

    features = extract_features_from_modalities(
        health_check=hc,
        questionnaire_answers=q_answers,
        cv_features=cv_feats,
        cv_quality=cv_qual
    )

    for col in ALL_FEATURE_COLUMNS:
        assert col in features

    assert features["dizziness_severity"] == 6.0
    assert features["q_spinning"] is True
    assert features["q_positional"] is True
    assert features["cv_horizontal_amplitude"] == 0.05
    assert features["cv_valid_ratio"] == 0.95


def test_extract_features_missing_modalities_graceful_defaults():
    # Only health check provided; questionnaire and CV are None
    hc = {"dizziness_severity": 3}
    features = extract_features_from_modalities(health_check=hc)

    for col in ALL_FEATURE_COLUMNS:
        assert col in features

    assert features["dizziness_severity"] == 3.0
    assert features["q_spinning"] is False
    assert features["cv_horizontal_amplitude"] == 0.0


def test_identify_contributing_factors():
    feat = {
        "dizziness_severity": 8.0,
        "imbalance_severity": 7.0,
        "q_positional": True,
        "has_nausea": True,
    }
    factors = identify_contributing_factors(feat)
    assert len(factors) > 0
    assert any("dizziness" in f.lower() for f in factors)
    assert any("position" in f.lower() for f in factors)
