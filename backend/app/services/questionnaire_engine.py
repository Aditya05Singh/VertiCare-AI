from typing import Any, Optional, Dict, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.questionnaire import (
    QuestionnaireQuestion,
    QuestionnaireSession,
    QuestionnaireAnswer,
    QuestionType,
    SessionStatus
)
from app.services.question_bank import INITIAL_QUESTION_BANK


class QuestionnaireEngine:
    @staticmethod
    def seed_question_bank(db: Session) -> None:
        """Seed the controlled question bank into PostgreSQL if not already populated."""
        for item in INITIAL_QUESTION_BANK:
            existing = db.query(QuestionnaireQuestion).filter(
                QuestionnaireQuestion.question_code == item["question_code"]
            ).first()
            if not existing:
                q = QuestionnaireQuestion(
                    question_code=item["question_code"],
                    version=item["version"],
                    category=item["category"],
                    question_type=item["question_type"],
                    question_text=item["question_text"],
                    options=item["options"],
                    branching_rules=item["branching_rules"],
                    display_order=item["display_order"],
                    active=item["active"]
                )
                db.add(q)
            else:
                existing.question_text = item["question_text"]
                existing.options = item["options"]
                existing.branching_rules = item["branching_rules"]
                existing.display_order = item["display_order"]
                existing.active = item["active"]
        db.commit()

    @staticmethod
    def get_first_question_code() -> str:
        """Returns the initial root question code for the adaptive questionnaire."""
        return "Q_SPINNING"

    @staticmethod
    def validate_answer(question: QuestionnaireQuestion, answer: Any) -> Any:
        """
        Validate submitted answer against the question's configured QuestionType and options.
        Raises HTTP 422 on malformed or illegal values.
        """
        if answer is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Answer is required for question '{question.question_code}'."
            )

        q_type = question.question_type

        if q_type == QuestionType.BOOLEAN:
            if isinstance(answer, bool):
                return answer
            if isinstance(answer, str) and answer.lower() in ("true", "yes", "1"):
                return True
            if isinstance(answer, str) and answer.lower() in ("false", "no", "0"):
                return False
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Expected boolean answer for '{question.question_code}', got '{answer}'."
            )

        elif q_type == QuestionType.SINGLE_CHOICE:
            valid_values = [opt["value"] for opt in question.options]
            if str(answer) not in valid_values:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid option '{answer}' for '{question.question_code}'. Allowed: {valid_values}"
                )
            return str(answer)

        elif q_type == QuestionType.MULTI_CHOICE:
            if not isinstance(answer, list):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Expected list of options for multi-choice question '{question.question_code}'."
                )
            valid_values = [opt["value"] for opt in question.options]
            cleaned = []
            for item in answer:
                if str(item) not in valid_values:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Invalid option '{item}' for '{question.question_code}'."
                    )
                cleaned.append(str(item))
            return cleaned

        elif q_type == QuestionType.NUMBER:
            try:
                num = float(answer)
                return num
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Expected numeric answer for '{question.question_code}'."
                )

        elif q_type == QuestionType.TEXT:
            text_str = str(answer).strip()
            if len(text_str) > 500:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Text answer exceeds maximum length of 500 characters."
                )
            return text_str

        return answer

    @staticmethod
    def determine_next_question_code(
        question: QuestionnaireQuestion,
        answer: Any
    ) -> Optional[str]:
        """
        Deterministic Rule-Based Branching Engine.
        Returns next question code or None if terminal state is reached.
        """
        rules = question.branching_rules or {}
        rule_type = rules.get("type", "default")

        if rule_type == "terminal":
            return None

        if rule_type == "boolean":
            ans_bool = bool(answer)
            if ans_bool:
                return rules.get("true", rules.get("default"))
            else:
                return rules.get("false", rules.get("default"))

        elif rule_type == "single_choice":
            ans_str = str(answer)
            choices = rules.get("choices", {})
            if ans_str in choices:
                return choices[ans_str]
            return rules.get("default")

        elif rule_type == "default":
            return rules.get("next")

        return None
