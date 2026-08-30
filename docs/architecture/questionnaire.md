# Adaptive Intelligent Questionnaire Architecture

This document describes the architectural design, branching rules engine, session lifecycle, and medical safety boundaries for the Adaptive Questionnaire subsystem in VertiCare AI.

---

## 1. System Overview & Purpose

The Adaptive Questionnaire is an intelligent, deterministic clinical screening tool designed to capture structured symptom data from patients presenting with vestibular complaints.

Rather than subjecting patients to a static survey with irrelevant questions, the system dynamically computes the next logical question based on prior responses.

```
[ Question Bank (PostgreSQL) ]
              │
              ▼
[ QuestionnaireSession (In-Progress) ] ◄───► [ Patient Submits Answer ]
              │
              ▼
[ Deterministic Branching Engine ]
              │
              ├──(Has Next Question)──► [ Next Target Question ] ──► (Repeat Loop)
              │
              └──(Terminal State reached)──► [ Mark COMPLETED ] ──► [ Generate Safe Screening Summary ]
```

---

## 2. Deterministic Branching Engine

> [!IMPORTANT]
> **No Runtime Generative AI / LLMs**
>
> In accordance with strict medical software safety principles, VertiCare AI does **NOT** use runtime LLMs to invent questions or generate nondeterministic clinical branches. All questions originate from a versioned, controlled question bank (`INITIAL_QUESTION_BANK`), and all branches follow explicit, explainable state transitions.

### Branching Mechanics
- **Boolean Branching (`Q_SPINNING`):**
  - `true` (spinning sensation) $\to$ `Q_POSITIONAL` (checks head movement triggers)
  - `false` (non-spinning) $\to$ `Q_NON_SPIN_TYPE` (characterizes unsteadiness, faintness, floating)
- **Single Choice Branching (`Q_NON_SPIN_TYPE`):**
  - `unsteadiness` $\to$ `Q_GAIT_DIFFICULTY`
  - `lightheaded` $\to$ `Q_ORTHOSTATIC`
  - `floating` / `vague` $\to$ `Q_EPISODE_DURATION_GEN`
- **Duration Branching (`Q_EPISODE_DURATION_POS`):**
  - `seconds` $\to$ `Q_HEAD_TURNS` (evaluates lateralized head turning triggers)
  - `minutes` $\to$ `Q_ASSOCIATED_SYMPTOMS`
  - `hours` $\to$ `Q_AUDITORY` (evaluates tinnitus, aural fullness, hearing loss)
- **Terminal State:**
  - `Q_FUNCTIONAL_IMPACT` $\to$ Terminal transition marks the session `COMPLETED`.

---

## 3. Session Lifecycle & Security

1. **Patient Ownership & Identity:** Session access is strictly restricted to the authenticated patient derived from JWT claims.
2. **Order Security:** Clients cannot skip questions or force arbitrary sequence progression. The backend verifies that the submitted `question_code` strictly matches `session.current_question_code`.
3. **Session Resumption:** If a patient leaves mid-assessment, returning to `/patient/questionnaire` restores their exact state and answer history.

---

## 4. Medical Scope & Non-Diagnostic Boundary Notice

> [!CAUTION]
> **Academic Prototype Notice**
>
> The Adaptive Questionnaire is an academic prototype designed for structured data gathering.
> - It does **NOT** formulate a medical diagnosis (such as Benign Paroxysmal Positional Vertigo, Meniere's Disease, or Vestibular Neuritis).
> - It does **NOT** prescribe medications, vestibular rehabilitation maneuvers, or alter medical treatment.
> - Summaries are intended solely for qualified clinician review during formal medical appointments.

