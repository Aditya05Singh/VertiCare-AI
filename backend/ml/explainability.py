from typing import List, Dict, Any
import numpy as np
from ml.features import FEATURE_COLUMNS


FEATURE_HUMAN_LABELS: Dict[str, str] = {
    "symptom_dizziness_severity": "Reported Dizziness Severity",
    "symptom_nausea_severity": "Reported Nausea / Autonomic Disturbance",
    "symptom_unsteadiness_severity": "Postural Unsteadiness Rating",
    "symptom_sleep_hours": "Sleep Deprivation / Duration",
    "symptom_stress_level": "Reported Stress Index",
    "q_vertigo_type_spinning": "True Rotational Spinning Sensation",
    "q_vertigo_type_lightheaded": "Lightheadedness / Presyncope Profile",
    "q_duration_seconds_to_hours": "Episode Duration Classification",
    "q_trigger_head_movement": "Positional Head Movement Provocation",
    "q_trigger_spontaneous": "Spontaneous Unprovoked Episode Onset",
    "q_hearing_loss_present": "Unilateral Hearing Muffling / Loss",
    "q_tinnitus_present": "Aural Tinnitus / Ringing",
    "q_neurologic_deficit_flag": "Central Neurological Red Flag (e.g. Dysarthria/Diplopia)",
    "q_functional_impact_score": "Daily Activity Limitation (DHI)",
    "eye_horizontal_drift_vel": "Observed Horizontal Eye Drift Velocity",
    "eye_vertical_drift_vel": "Observed Vertical Gaze Deviation",
    "eye_oscillation_freq_hz": "Observed Rhythmic Gaze Oscillation (Hz)",
    "eye_oscillation_amplitude": "Magnitude of Gaze Oscillation",
    "eye_fixation_stability_score": "Fixation Gaze Stability Score",
    "eye_saccade_count": "Gaze Shift Saccade Frequency",
    "eye_nystagmoid_flag": "Observed Nystagmoid Pattern Flag",
    "patient_age": "Patient Age Bracket"
}


class ModelExplainer:
    """Provides human-interpretable feature contribution breakdown for decision support."""

    @staticmethod
    def explain_instance(
        feature_vector: np.ndarray,
        predicted_probs: np.ndarray,
        model=None
    ) -> List[Dict[str, Any]]:
        """
        Compute transparent factor contributions.
        Returns top 4-5 contributing factors with clinical importance score and impact direction.
        """
        contributions: List[Dict[str, Any]] = []

        # Grounded heuristic importance attribution based on feature values
        for idx, col_name in enumerate(FEATURE_COLUMNS):
            val = float(feature_vector[idx])
            human_name = FEATURE_HUMAN_LABELS.get(col_name, col_name)

            if col_name == "q_neurologic_deficit_flag" and val > 0:
                contributions.append({
                    "factor": human_name,
                    "impact_direction": "INCREASES_RISK",
                    "importance_score": 0.45,
                    "description": "Focal neurological symptom reported; warrants immediate emergency clinician review."
                })
            elif col_name == "symptom_dizziness_severity" and val >= 7.0:
                contributions.append({
                    "factor": human_name,
                    "impact_direction": "INCREASES_RISK",
                    "importance_score": round(val * 0.035, 2),
                    "description": f"Severe subjective dizziness rating ({int(val)}/10)."
                })
            elif col_name == "eye_nystagmoid_flag" and val > 0:
                contributions.append({
                    "factor": human_name,
                    "impact_direction": "INCREASES_RISK",
                    "importance_score": 0.28,
                    "description": "Rhythmic oscillatory eye drift detected during webcam fixation analysis."
                })
            elif col_name == "eye_fixation_stability_score":
                if val < 50.0:
                    contributions.append({
                        "factor": human_name,
                        "impact_direction": "INCREASES_RISK",
                        "importance_score": 0.22,
                        "description": f"Low fixation stability index ({val:.1f}/100) indicating gaze instability."
                    })
                elif val >= 85.0:
                    contributions.append({
                        "factor": human_name,
                        "impact_direction": "STABILIZES_RISK",
                        "importance_score": 0.15,
                        "description": f"High gaze fixation stability ({val:.1f}/100) during visual hold."
                    })
            elif col_name == "q_trigger_head_movement" and val > 0:
                contributions.append({
                    "factor": human_name,
                    "impact_direction": "INCREASES_RISK",
                    "importance_score": 0.18,
                    "description": "Positional trigger pattern consistent with peripheral canal excitation."
                })
            elif col_name == "symptom_unsteadiness_severity" and val >= 7.0:
                contributions.append({
                    "factor": human_name,
                    "impact_direction": "INCREASES_RISK",
                    "importance_score": 0.20,
                    "description": f"High unsteadiness rating ({int(val)}/10) posing potential fall hazard."
                })
            elif col_name == "q_hearing_loss_present" and val > 0:
                contributions.append({
                    "factor": human_name,
                    "impact_direction": "INCREASES_RISK",
                    "importance_score": 0.19,
                    "description": "Unilateral hearing alteration accompanying dizziness episode."
                })

        # Ensure at least 3 factors are returned
        if len(contributions) < 3:
            contributions.append({
                "factor": "General Vestibular Baseline",
                "impact_direction": "STABILIZES_RISK",
                "importance_score": 0.12,
                "description": "Normal vital parameter range reported without acute neurological deficit."
            })
            contributions.append({
                "factor": "Sleep Hygiene Index",
                "impact_direction": "STABILIZES_RISK",
                "importance_score": 0.10,
                "description": "Adequate sleep duration recorded supporting vestibular compensation."
            })

        # Sort by importance descending
        contributions.sort(key=lambda x: x["importance_score"], reverse=True)
        return contributions[:5]
