# Model Evaluation Summary & Benchmark Comparison

This report details the cross-validation and holdout evaluation results for the **`verticare-risk-v1`** model pipeline.

---

## 1. Candidate Comparison Results

| Algorithm | 5-Fold CV Macro F1 | Test Accuracy | Test Macro F1 | Test Macro Precision | Test Macro Recall | Test ROC-AUC (ovr) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Logistic Regression** *(Selected)* | **0.8251** | **90.83%** | **0.9075** | **0.9060** | **0.9090** | **0.9809** |
| **Gradient Boosting** | 0.6372 | 80.00% | 0.7225 | 0.7742 | 0.6974 | 0.9270 |
| **Random Forest** | 0.4573 | 73.33% | 0.4949 | 0.5346 | 0.5032 | 0.8871 |

---

## 2. Selection Rationale

- **Selected Model:** `LogisticRegression` within Scikit-Learn `Pipeline`.
- **Reason:** Achieved the highest cross-validation Macro F1 score (`0.8251`), balanced recall across all 3 risk tiers (`LOW`, `MEDIUM`, `HIGH`), and excellent probabilistic calibration for continuous risk score calculation.

---

## 3. Confusion Matrix (Holdout Test Set $N=120$)

$$\begin{pmatrix} 11 & 1 & 0 \\ 1 & 63 & 5 \\ 0 & 4 & 35 \end{pmatrix}$$

- Row 0: True `LOW` ($N=12$) $\to$ 11 correctly classified, 1 classified as `MEDIUM`.
- Row 1: True `MEDIUM` ($N=69$) $\to$ 63 correctly classified, 1 as `LOW`, 5 as `HIGH`.
- Row 2: True `HIGH` ($N=39$) $\to$ 35 correctly classified, 4 as `MEDIUM`, 0 as `LOW`.

---

## 4. Software Verification Notice

> [!NOTE]
> Training and evaluation metrics were generated using the controlled software verification dataset (`synthetic_benchmark_demo_dataset`) for software architecture validation. These metrics demonstrate algorithmic correctness and do not represent clinical trial outcomes.

