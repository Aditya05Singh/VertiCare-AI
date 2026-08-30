import os
import json
from datetime import datetime, timezone
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import classification_report, accuracy_score
import xgboost as xgb

from ml.data_generator import generate_synthetic_dataset
from ml.features import FEATURE_COLUMNS


def train_and_save_model(
    output_dir: str = "backend/ml/saved_models",
    n_samples: int = 4000
):
    """
    Train an XGBoost Classifier on literature-guided synthetic feature distributions.
    Saves model artifact, RobustScaler, and transparent metadata JSON.
    """
    os.makedirs(output_dir, exist_ok=True)

    print("Generating synthetic literature-guided baseline dataset...")
    df, y = generate_synthetic_dataset(n_samples=n_samples, random_state=42)

    X = df[FEATURE_COLUMNS].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Robust scaling (outlier resistant)
    scaler = RobustScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("Training XGBoost Classifier...")
    model = xgb.XGBClassifier(
        n_estimators=150,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        objective="multi:softprob",
        num_class=3,
        random_state=42,
        eval_metric="mlogloss"
    )
    model.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    print(f"Model Training Complete. Test Accuracy: {acc * 100:.2f}%")

    # Save artifacts
    model_path = os.path.join(output_dir, "verticare_xgb_v1.json")
    scaler_path = os.path.join(output_dir, "verticare_scaler_v1.joblib")
    metadata_path = os.path.join(output_dir, "model_metadata.json")

    model.save_model(model_path)
    joblib.dump(scaler, scaler_path)

    metadata = {
        "model_name": "VertiCare-Ensemble-XGB",
        "model_version": "1.0.0",
        "architecture": "Gradient Boosted Decision Trees (XGBoost)",
        "features_used": FEATURE_COLUMNS,
        "n_features": len(FEATURE_COLUMNS),
        "training_samples": n_samples,
        "test_accuracy": round(float(acc), 4),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "disclaimer": (
            "This model was trained exclusively on literature-guided synthetic feature distributions "
            "for academic prototype software demonstration. It is NOT clinically validated for diagnosis."
        )
    }

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Artifacts successfully saved to {output_dir}")
    return model, scaler, metadata


if __name__ == "__main__":
    train_and_save_model()
