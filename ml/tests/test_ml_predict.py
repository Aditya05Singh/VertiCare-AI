import pytest
from ml.src.predict import RiskPredictor
from ml.src.feature_engineering import extract_features_from_modalities


def test_risk_predictor_predict_valid_inputs():
    feat = extract_features_from_modalities(
        health_check={"dizziness_severity": 8, "imbalance_severity": 7, "nausea": True},
        questionnaire_answers=[{"question_code": "Q_POSITIONAL", "answer": True}],
        cv_features={"horizontal_amplitude": 0.08, "horizontal_velocity_mean": 0.50}
    )

    pred = RiskPredictor.predict(feat)
    assert pred["risk_level"] in ("LOW", "MEDIUM", "HIGH")
    assert 0.0 <= pred["risk_score"] <= 1.0
    assert pred["model_name"] is not None
    assert pred["model_version"] is not None
    assert len(pred["contributing_factors"]) > 0
    assert "Not a medical diagnosis" in pred["notice"]


def test_risk_predictor_predict_low_severity():
    feat = extract_features_from_modalities(
        health_check={"dizziness_severity": 1, "imbalance_severity": 0, "nausea": False}
    )
    pred = RiskPredictor.predict(feat)
    assert pred["risk_level"] in ("LOW", "MEDIUM", "HIGH")
    assert isinstance(pred["risk_score"], float)
