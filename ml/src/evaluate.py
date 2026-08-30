from typing import Dict, Any, List
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
)
from ml.src.config import RISK_CLASSES


def compute_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray = None
) -> Dict[str, Any]:
    """
    Computes standard multiclass classification metrics using macro averaging.
    """
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average="macro", zero_division=0)
    rec = recall_score(y_true, y_pred, average="macro", zero_division=0)
    f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2]).tolist()

    roc_auc = None
    if y_proba is not None:
        try:
            # Multi-class One-vs-Rest ROC-AUC
            roc_auc = float(roc_auc_score(y_true, y_proba, multi_class="ovr", average="macro"))
        except Exception:
            roc_auc = None

    return {
        "accuracy": round(float(acc), 4),
        "macro_precision": round(float(prec), 4),
        "macro_recall": round(float(rec), 4),
        "macro_f1": round(float(f1), 4),
        "roc_auc_macro": round(float(roc_auc), 4) if roc_auc is not None else None,
        "confusion_matrix": cm,
        "classes": RISK_CLASSES
    }

