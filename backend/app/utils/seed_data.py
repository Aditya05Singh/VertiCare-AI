from typing import List, Dict, Any
from app.models.questionnaire import QuestionResponseType

# Adaptive Question Bank Definitions
# Grounded in vestibular clinical assessment protocols (e.g. Dizziness Handicap Inventory, HINTS principles)
QUESTION_BANK: List[Dict[str, Any]] = [
    {
        "id": "Q_SENSATION_TYPE",
        "text": "What best describes the sensation you are experiencing?",
        "category": "sensation",
        "response_type": QuestionResponseType.SINGLE_CHOICE,
        "order_index": 1,
        "options": [
            {"value": "true_spinning", "label": "True rotational spinning (the room or you are spinning)", "weight": 2.5},
            {"value": "lightheadedness", "label": "Lightheadedness / faintness (feeling like you might pass out)", "weight": 1.0},
            {"value": "unsteadiness", "label": "Imbalance / unsteadiness only when standing or walking", "weight": 1.5},
            {"value": "floating_tilt", "label": "Rocking, swaying, or floating sensation", "weight": 1.5}
        ],
        "parent_question_id": None,
        "branching_rule": None
    },
    {
        "id": "Q_EPISODE_DURATION",
        "text": "How long does a typical dizzy spell or vertigo episode last?",
        "category": "duration",
        "response_type": QuestionResponseType.SINGLE_CHOICE,
        "order_index": 2,
        "options": [
            {"value": "seconds", "label": "A few seconds to less than 1 minute", "weight": 1.0},
            {"value": "minutes_to_hours", "label": "Several minutes to a few hours (20 mins - 12 hours)", "weight": 2.0},
            {"value": "days_constant", "label": "Days of constant continuous dizziness/vertigo", "weight": 3.0}
        ],
        "parent_question_id": None,
        "branching_rule": None
    },
    {
        "id": "Q_TRIGGER_FACTORS",
        "text": "Which of the following specifically trigger or worsen your dizziness?",
        "category": "triggers",
        "response_type": QuestionResponseType.MULTI_CHOICE,
        "order_index": 3,
        "options": [
            {"value": "turning_in_bed", "label": "Turning over in bed or rolling to one side", "weight": 2.0},
            {"value": "looking_up_bending", "label": "Looking up at the ceiling or bending down", "weight": 2.0},
            {"value": "standing_up_rapidly", "label": "Standing up quickly from sitting/lying", "weight": 1.0},
            {"value": "head_movement_general", "label": "Quick head turns in any direction", "weight": 1.5},
            {"value": "visual_crowds", "label": "Busy visual environments (supermarkets, moving screens)", "weight": 1.2},
            {"value": "spontaneous_no_trigger", "label": "Occurs spontaneously with no clear physical trigger", "weight": 2.0}
        ],
        "parent_question_id": None,
        "branching_rule": None
    },
    {
        "id": "Q_OTOLOGIC_SYMPTOMS",
        "text": "Have you noticed any ear-related (otologic) symptoms accompanying the dizziness?",
        "category": "otologic",
        "response_type": QuestionResponseType.MULTI_CHOICE,
        "order_index": 4,
        "options": [
            {"value": "hearing_loss_unilateral", "label": "Reduced hearing or muffled sound in one ear", "weight": 3.0},
            {"value": "tinnitus_ringing", "label": "Ringing, buzzing, or hissing noise in ear(s)", "weight": 2.0},
            {"value": "aural_fullness", "label": "Feeling of fullness or pressure inside the ear", "weight": 2.0},
            {"value": "none", "label": "No ear symptoms at all", "weight": 0.0}
        ],
        "parent_question_id": None,
        "branching_rule": None
    },
    {
        "id": "Q_POSITIONAL_DETAILS",
        "text": "When turning your head or rolling in bed, does the intense spinning stop within 30-60 seconds if you remain completely still?",
        "category": "positional_branch",
        "response_type": QuestionResponseType.SINGLE_CHOICE,
        "order_index": 5,
        "options": [
            {"value": "yes_subsides_quickly", "label": "Yes, spinning is intense but stops in under 1 minute once still", "weight": 1.5},
            {"value": "no_continues_constant", "label": "No, spinning continues regardless of staying still", "weight": 2.5},
            {"value": "not_applicable", "label": "Head movements do not provoke my symptoms", "weight": 0.5}
        ],
        "parent_question_id": "Q_TRIGGER_FACTORS",
        "branching_rule": {
            "depends_on": "Q_TRIGGER_FACTORS",
            "condition": "contains_any",
            "values": ["turning_in_bed", "looking_up_bending"]
        }
    },
    {
        "id": "Q_NEUROLOGIC_RED_FLAGS",
        "text": "CRITICAL SAFETY CHECK: Are you experiencing any of the following neurological symptoms?",
        "category": "neurologic_red_flags",
        "response_type": QuestionResponseType.MULTI_CHOICE,
        "order_index": 6,
        "options": [
            {"value": "double_vision", "label": "Double vision (diplopia)", "weight": 4.0},
            {"value": "slurred_speech", "label": "Difficulty speaking or slurred speech (dysarthria)", "weight": 5.0},
            {"value": "facial_weakness_numbness", "label": "Facial droop, weakness, or numbness", "weight": 5.0},
            {"value": "limb_weakness_clumsiness", "label": "Weakness or loss of coordination in arm or leg", "weight": 5.0},
            {"value": "swallowing_difficulty", "label": "Sudden difficulty swallowing (dysphagia)", "weight": 4.0},
            {"value": "none_of_above", "label": "None of these symptoms are present", "weight": 0.0}
        ],
        "parent_question_id": None,
        "branching_rule": None
    },
    {
        "id": "Q_HEADACHE_MIGRAINE",
        "text": "Do you have a personal history of migraines, or do you experience throbbing headaches with light/sound sensitivity alongside dizziness?",
        "category": "migraine_branch",
        "response_type": QuestionResponseType.SINGLE_CHOICE,
        "order_index": 7,
        "options": [
            {"value": "yes_migraine_history", "label": "Yes, diagnosed migraine history or prominent migraine symptoms", "weight": 2.0},
            {"value": "mild_tension_headache", "label": "Only mild general headaches", "weight": 1.0},
            {"value": "no_headaches", "label": "No history of migraines or headaches", "weight": 0.0}
        ],
        "parent_question_id": None,
        "branching_rule": None
    },
    {
        "id": "Q_DAILY_IMPACT_DHI",
        "text": "Because of your dizziness, do you restrict your work, daily activities, or travel?",
        "category": "functional_impact",
        "response_type": QuestionResponseType.SINGLE_CHOICE,
        "order_index": 8,
        "options": [
            {"value": "severely_limited", "label": "Severely limited (unable to work, drive, or perform household chores)", "weight": 3.0},
            {"value": "moderately_limited", "label": "Moderately limited (need assistance with some activities)", "weight": 2.0},
            {"value": "mildly_limited", "label": "Mildly limited (manage most tasks with caution)", "weight": 1.0},
            {"value": "not_limited", "label": "Not limited (continue normal routines)", "weight": 0.0}
        ],
        "parent_question_id": None,
        "branching_rule": None
    }
]
