"""
ml/src/general_symptom_engine/evaluate.py

Evaluation metric calculation routines for binary classification.
"""

from typing import Dict, Any, Optional
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
)


def compute_binary_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: Optional[np.ndarray] = None
) -> Dict[str, Any]:
    """
    Computes accuracy, precision, recall, F1, confusion matrix, and ROC-AUC.
    """
    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    f1_macro = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist()

    roc_auc = None
    if y_proba is not None:
        try:
            # If 2D probability array passed (N, 2), extract positive class column
            if len(y_proba.shape) == 2 and y_proba.shape[1] == 2:
                p_pos = y_proba[:, 1]
            else:
                p_pos = y_proba
            roc_auc = float(roc_auc_score(y_true, p_pos))
        except Exception:
            roc_auc = None

    return {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "f1_macro": round(f1_macro, 4),
        "roc_auc": round(roc_auc, 4) if roc_auc is not None else None,
        "confusion_matrix": cm,
    }
