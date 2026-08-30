from typing import List, Dict, Any
from app.models.questionnaire import QuestionType

INITIAL_QUESTION_BANK: List[Dict[str, Any]] = [
    {
        "question_code": "Q_SPINNING",
        "version": "v1.0",
        "category": "sensation",
        "question_type": QuestionType.BOOLEAN,
        "question_text": "Does the dizziness feel like you or the room is actively spinning around?",
        "options": [],
        "branching_rules": {
            "type": "boolean",
            "true": "Q_POSITIONAL",
            "false": "Q_NON_SPIN_TYPE",
            "default": "Q_POSITIONAL"
        },
        "display_order": 1,
        "active": True
    },
    {
        "question_code": "Q_POSITIONAL",
        "version": "v1.0",
        "category": "positional",
        "question_type": QuestionType.BOOLEAN,
        "question_text": "Is the spinning sensation triggered or noticeably worsened by changing head position (such as rolling over in bed, lying down, or tilting your head upward)?",
        "options": [],
        "branching_rules": {
            "type": "boolean",
            "true": "Q_EPISODE_DURATION_POS",
            "false": "Q_EPISODE_DURATION_GEN",
            "default": "Q_EPISODE_DURATION_GEN"
        },
        "display_order": 2,
        "active": True
    },
    {
        "question_code": "Q_NON_SPIN_TYPE",
        "version": "v1.0",
        "category": "sensation",
        "question_type": QuestionType.SINGLE_CHOICE,
        "question_text": "Which of the following best describes your predominant dizziness sensation?",
        "options": [
            {"value": "unsteadiness", "label": "Constant unsteadiness or difficulty walking in a straight line"},
            {"value": "lightheaded", "label": "Lightheadedness or faintness upon standing up"},
            {"value": "floating", "label": "Floating, swimming, or rocking sensation (like being on a boat)"},
            {"value": "vague", "label": "Vague disorientation, brain fog, or head heaviness"}
        ],
        "branching_rules": {
            "type": "single_choice",
            "choices": {
                "unsteadiness": "Q_GAIT_DIFFICULTY",
                "lightheaded": "Q_ORTHOSTATIC",
                "floating": "Q_EPISODE_DURATION_GEN",
                "vague": "Q_EPISODE_DURATION_GEN"
            },
            "default": "Q_EPISODE_DURATION_GEN"
        },
        "display_order": 3,
        "active": True
    },
    {
        "question_code": "Q_EPISODE_DURATION_POS",
        "version": "v1.0",
        "category": "timing",
        "question_type": QuestionType.SINGLE_CHOICE,
        "question_text": "When the spinning sensation is triggered by head movement, how long does the intense spinning typically last before subsiding?",
        "options": [
            {"value": "seconds", "label": "Brief — A few seconds up to 1 minute"},
            {"value": "minutes", "label": "Short — 1 to 20 minutes"},
            {"value": "hours", "label": "Prolonged — 20 minutes to several hours"}
        ],
        "branching_rules": {
            "type": "single_choice",
            "choices": {
                "seconds": "Q_HEAD_TURNS",
                "minutes": "Q_ASSOCIATED_SYMPTOMS",
                "hours": "Q_AUDITORY"
            },
            "default": "Q_ASSOCIATED_SYMPTOMS"
        },
        "display_order": 4,
        "active": True
    },
    {
        "question_code": "Q_EPISODE_DURATION_GEN",
        "version": "v1.0",
        "category": "timing",
        "question_type": QuestionType.SINGLE_CHOICE,
        "question_text": "How long do dizziness episodes typically last when they occur?",
        "options": [
            {"value": "brief", "label": "Brief — Under 1 minute"},
            {"value": "hours", "label": "Episodes lasting 20 minutes to several hours"},
            {"value": "days", "label": "Continuous severe dizziness lasting several days"},
            {"value": "constant", "label": "Persistent / chronic sensation for months"}
        ],
        "branching_rules": {
            "type": "single_choice",
            "choices": {
                "brief": "Q_ASSOCIATED_SYMPTOMS",
                "hours": "Q_AUDITORY",
                "days": "Q_INFECTION_RECENT",
                "constant": "Q_GAIT_DIFFICULTY"
            },
            "default": "Q_ASSOCIATED_SYMPTOMS"
        },
        "display_order": 5,
        "active": True
    },
    {
        "question_code": "Q_HEAD_TURNS",
        "version": "v1.0",
        "category": "positional",
        "question_type": QuestionType.SINGLE_CHOICE,
        "question_text": "Does the spinning sensation occur specifically when turning your head to one particular side?",
        "options": [
            {"value": "right", "label": "Noticeably triggered when turning to the right"},
            {"value": "left", "label": "Noticeably triggered when turning to the left"},
            {"value": "both", "label": "Equally noticeable on both sides"},
            {"value": "unsure", "label": "Unsure / not specific to side"}
        ],
        "branching_rules": {
            "type": "default",
            "next": "Q_ASSOCIATED_SYMPTOMS"
        },
        "display_order": 6,
        "active": True
    },
    {
        "question_code": "Q_AUDITORY",
        "version": "v1.0",
        "category": "associated_symptoms",
        "question_type": QuestionType.MULTI_CHOICE,
        "question_text": "During or near your dizziness episodes, have you noticed any of the following ear or hearing changes? (Select all that apply)",
        "options": [
            {"value": "tinnitus", "label": "Ringing, roaring, or buzzing noise in an ear"},
            {"value": "aural_fullness", "label": "Sensation of fullness or pressure in an ear"},
            {"value": "hearing_loss", "label": "Fluctuating or reduced hearing ability in an ear"},
            {"value": "none", "label": "No ear or hearing symptoms"}
        ],
        "branching_rules": {
            "type": "default",
            "next": "Q_ASSOCIATED_SYMPTOMS"
        },
        "display_order": 7,
        "active": True
    },
    {
        "question_code": "Q_INFECTION_RECENT",
        "version": "v1.0",
        "category": "triggers",
        "question_type": QuestionType.BOOLEAN,
        "question_text": "Did your severe dizziness begin shortly following a viral illness, cold, flu, or ear infection?",
        "options": [],
        "branching_rules": {
            "type": "default",
            "next": "Q_ASSOCIATED_SYMPTOMS"
        },
        "display_order": 8,
        "active": True
    },
    {
        "question_code": "Q_ORTHOSTATIC",
        "version": "v1.0",
        "category": "triggers",
        "question_type": QuestionType.BOOLEAN,
        "question_text": "Does the lightheadedness occur primarily within a few seconds after quickly standing up from sitting or lying down?",
        "options": [],
        "branching_rules": {
            "type": "default",
            "next": "Q_ASSOCIATED_SYMPTOMS"
        },
        "display_order": 9,
        "active": True
    },
    {
        "question_code": "Q_GAIT_DIFFICULTY",
        "version": "v1.0",
        "category": "functional_impact",
        "question_type": QuestionType.SINGLE_CHOICE,
        "question_text": "How would you describe your ability to walk safely when symptoms are present?",
        "options": [
            {"value": "normal", "label": "Walk normally without assistance"},
            {"value": "slight_drift", "label": "Slight unsteadiness / drift, but walk independently"},
            {"value": "support_needed", "label": "Need to touch walls, furniture, or use support to balance"},
            {"value": "bedbound", "label": "Unable to walk or stand safely during episodes"}
        ],
        "branching_rules": {
            "type": "default",
            "next": "Q_ASSOCIATED_SYMPTOMS"
        },
        "display_order": 10,
        "active": True
    },
    {
        "question_code": "Q_ASSOCIATED_SYMPTOMS",
        "version": "v1.0",
        "category": "associated_symptoms",
        "question_type": QuestionType.MULTI_CHOICE,
        "question_text": "Which of the following symptoms accompany or precede your dizziness? (Select all that apply)",
        "options": [
            {"value": "nausea", "label": "Nausea or stomach distress"},
            {"value": "headache", "label": "Throbbing headache or migraine features"},
            {"value": "photosensitivity", "label": "Sensitivity to bright lights or visual motion"},
            {"value": "oscillopsia", "label": "Visual jumping / objects seem to bobble when moving"},
            {"value": "neck_pain", "label": "Neck stiffness or soreness"},
            {"value": "none", "label": "None of the above"}
        ],
        "branching_rules": {
            "type": "default",
            "next": "Q_FUNCTIONAL_IMPACT"
        },
        "display_order": 11,
        "active": True
    },
    {
        "question_code": "Q_FUNCTIONAL_IMPACT",
        "version": "v1.0",
        "category": "functional_impact",
        "question_type": QuestionType.SINGLE_CHOICE,
        "question_text": "Overall, how significantly does this dizziness impact your daily life, work, or routine?",
        "options": [
            {"value": "mild", "label": "Mild — Noticeable but does not restrict daily tasks or work"},
            {"value": "moderate", "label": "Moderate — Interferes with driving, focus, or demanding activities"},
            {"value": "severe", "label": "Severe — Prevents routine self-care, work, or basic daily activities"}
        ],
        "branching_rules": {
            "type": "terminal"
        },
        "display_order": 12,
        "active": True
    }
]

