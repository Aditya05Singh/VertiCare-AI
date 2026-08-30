import numpy as np
import pandas as pd
from typing import Tuple
from ml.features import FEATURE_COLUMNS


def generate_synthetic_dataset(n_samples: int = 3000, random_state: int = 42) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Generate synthetic vestibular symptom, questionnaire, and eye tracking data
    grounded in published clinical literature distributions.

    DISCLAIMER: This dataset is synthetic and intended exclusively for academic software demonstration
    and baseline engineering pipeline verification. It is NOT clinical trial patient data.
    """
    np.random.seed(random_state)
    records = []
    labels = []  # 0: Low Risk, 1: Medium Risk, 2: High Risk (Central or Severe Acute)

    for _ in range(n_samples):
        # Sample patient profile archetype
        archetype = np.random.choice(["benign_positional", "vestibular_migraine", "menieres", "acute_neuritis", "central_red_flag", "mild_orthostatic"], p=[0.30, 0.20, 0.15, 0.15, 0.08, 0.12])

        age = int(np.random.normal(52, 14))
        age = max(18, min(90, age))

        if archetype == "benign_positional":  # Low to Medium Risk
            diz = np.random.randint(4, 9)
            nau = np.random.randint(1, 6)
            unst = np.random.randint(2, 6)
            sleep = np.random.normal(7.0, 1.0)
            stress = np.random.randint(3, 8)
            spin = 1.0
            light = 0.0
            dur = 1.0  # seconds
            head_trig = 1.0
            spon_trig = 0.0
            hearing = 0.0
            tinnitus = 0.0
            neuro = 0.0
            impact = np.random.choice([1.0, 2.0])
            h_drift = np.random.uniform(0.01, 0.08)
            v_drift = np.random.uniform(0.01, 0.05)
            freq = np.random.choice([0.0, np.random.uniform(1.5, 3.5)], p=[0.4, 0.6])
            amp = np.random.uniform(0.01, 0.06) if freq > 0 else 0.0
            stability = np.random.uniform(65.0, 90.0)
            saccades = np.random.randint(1, 6)
            nystagmus = 1.0 if freq > 0 else 0.0
            risk_label = 0 if diz < 6 else 1

        elif archetype == "vestibular_migraine":  # Medium Risk
            diz = np.random.randint(3, 8)
            nau = np.random.randint(2, 7)
            unst = np.random.randint(3, 7)
            sleep = np.random.normal(6.0, 1.2)
            stress = np.random.randint(5, 10)
            spin = np.random.choice([0.0, 1.0])
            light = 1.0 if spin == 0.0 else 0.0
            dur = 2.0  # minutes to hours
            head_trig = np.random.choice([0.0, 1.0])
            spon_trig = 1.0
            hearing = 0.0
            tinnitus = np.random.choice([0.0, 1.0], p=[0.7, 0.3])
            neuro = 0.0
            impact = np.random.choice([1.0, 2.0, 3.0])
            h_drift = np.random.uniform(0.02, 0.10)
            v_drift = np.random.uniform(0.01, 0.06)
            freq = 0.0
            amp = 0.0
            stability = np.random.uniform(60.0, 85.0)
            saccades = np.random.randint(2, 7)
            nystagmus = 0.0
            risk_label = 1

        elif archetype == "acute_neuritis":  # Medium to High Risk
            diz = np.random.randint(7, 11)
            nau = np.random.randint(6, 11)
            unst = np.random.randint(6, 10)
            sleep = np.random.normal(5.0, 1.5)
            stress = np.random.randint(6, 10)
            spin = 1.0
            light = 0.0
            dur = 3.0  # days constant
            head_trig = 1.0
            spon_trig = 1.0
            hearing = 0.0
            tinnitus = 0.0
            neuro = 0.0
            impact = 3.0
            h_drift = np.random.uniform(0.12, 0.35)
            v_drift = np.random.uniform(0.02, 0.08)
            freq = np.random.uniform(2.0, 4.5)
            amp = np.random.uniform(0.08, 0.25)
            stability = np.random.uniform(30.0, 60.0)
            saccades = np.random.randint(5, 15)
            nystagmus = 1.0
            risk_label = 1 if diz < 8 else 2

        elif archetype == "central_red_flag":  # High Risk
            diz = np.random.randint(6, 11)
            nau = np.random.randint(4, 10)
            unst = np.random.randint(7, 11)
            sleep = np.random.normal(5.5, 1.5)
            stress = np.random.randint(6, 10)
            spin = np.random.choice([0.0, 1.0])
            light = 1.0 if spin == 0.0 else 0.0
            dur = np.random.choice([2.0, 3.0])
            head_trig = 0.0
            spon_trig = 1.0
            hearing = 0.0
            tinnitus = 0.0
            neuro = 1.0  # Diplopia / dysarthria / limb weakness
            impact = 3.0
            h_drift = np.random.uniform(0.10, 0.40)
            v_drift = np.random.uniform(0.08, 0.30)
            freq = np.random.uniform(1.0, 5.0)
            amp = np.random.uniform(0.05, 0.30)
            stability = np.random.uniform(20.0, 55.0)
            saccades = np.random.randint(6, 20)
            nystagmus = np.random.choice([0.0, 1.0], p=[0.3, 0.7])
            risk_label = 2

        else:  # mild_orthostatic / general dizziness -> Low Risk
            diz = np.random.randint(1, 5)
            nau = np.random.randint(1, 3)
            unst = np.random.randint(1, 4)
            sleep = np.random.normal(7.5, 0.8)
            stress = np.random.randint(2, 6)
            spin = 0.0
            light = 1.0
            dur = 1.0
            head_trig = 0.0
            spon_trig = 0.0
            hearing = 0.0
            tinnitus = 0.0
            neuro = 0.0
            impact = 0.0
            h_drift = np.random.uniform(0.01, 0.04)
            v_drift = np.random.uniform(0.01, 0.03)
            freq = 0.0
            amp = 0.0
            stability = np.random.uniform(85.0, 98.0)
            saccades = np.random.randint(0, 3)
            nystagmus = 0.0
            risk_label = 0

        row = [
            float(diz), float(nau), float(unst), float(max(0, sleep)), float(stress),
            float(spin), float(light), float(dur), float(head_trig), float(spon_trig),
            float(hearing), float(tinnitus), float(neuro), float(impact),
            float(h_drift), float(v_drift), float(freq), float(amp), float(stability),
            float(saccades), float(nystagmus), float(age)
        ]
        records.append(row)
        labels.append(risk_label)

    df = pd.DataFrame(records, columns=FEATURE_COLUMNS)
    y = np.array(labels, dtype=int)
    return df, y
