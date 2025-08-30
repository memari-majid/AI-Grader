# CS AI Grader – Research Protocol (UVU Computer Science)

Version: 0.1 (Draft for IRB and pre-registration)

## 1. Overview and Aims

CS AI Grader assists grading of CS programming assignments with rubric-aligned, code-aware AI feedback.
This protocol specifies hypotheses, design, data collection, analysis, validity safeguards, and publication plan.

## 2. Hypotheses

- H1 Efficiency: AI+TA grading reduces time-to-completion by ≥25% vs TA-only.
- H2 Reliability: Criterion scores agree with faculty gold standard at ICC(2,k) ≥ 0.75 (or weighted κ ≥ 0.70).
- H3 Feedback Quality: Blind raters score AI+TA feedback higher on specificity/actionability by ≥0.3 SD.
- H4 Learning Impact: Resubmission improvement (tests passed, rubric scores) is larger with AI feedback (Δ≥0.4 SD).
- H5 Acceptance: Median TA satisfaction ≥4/5; ≥70% prefer AI+TA after study.

## 3. Study Design

- Participants: CS 1400 sections (instructors, TAs), consenting students.
- Assignments: 3 representative programming tasks (early, mid, late term).
- Design: Within-section crossover (preferred). Each submission randomly assigned to:
  - Control: TA-only (AI hidden)
  - Treatment: AI+TA (AI suggestions visible; TA edits)
  - Optional shadow AI-only scoring for agreement analyses (not used for grades)
- Gold Standard: Two senior graders independently score a stratified sample; adjudicate disagreements.

## 4. Procedure

1) Submission recorded; system runs unit tests and static analysis (radon MI/CC, flake8 counts, lines).
2) AI generates rubric-aligned scores and feedback (code-aware prompts).
3) Condition handling:
   - TA-only: TA grades without AI; AI runs in background for agreement metrics.
   - AI+TA: TA reviews/edits AI, finalizes scores/feedback.
4) Capture timestamps and edit diffs; store TA satisfaction rating per batch.
5) For a subset, faculty gold-standard scoring with adjudication.

## 5. Data Collected

- Identifiers: submission_id, student_id (hashed), grader_id, assignment_id, rubric_id/version, condition.
- AI output: criterion scores, feedback, coverage, parse success; prompt version.
- Human output: final scores/feedback; edit distance and score deltas vs AI.
- Code metrics: tests passed, MI, avg/max CC, flake8 counts, LOC.
- Telemetry: time-on-task (start/end, idle filtering), actions (generate, edit, save).
- TA feedback: Likert (usefulness, trust, workload) + free-text.
- Student learning: resubmission deltas (tests and rubric) for assignments allowing revisions.

## 6. Outcomes and Analyses

- Reliability: ICC(2,k) and quadratic-weighted κ between AI vs gold standard, AI+TA vs gold standard; 95% CIs via bootstrap.
- Efficiency: Mixed-effects model with condition (fixed), grader/assignment (random) on time-to-completion.
- Feedback Quality: Blind rubric scoring of specificity/actionability; mixed models by condition.
- Learning Impact: Mixed models on change scores (first vs final submission), random intercepts per student.
- Edit Behavior: % criteria modified; text similarity; qualitative coding of edit intents.
- Robustness: JSON coverage ≥95%, parse failure rate <1%, regeneration rate.
- Subgroup analysis: Prior performance deciles; assignment difficulty strata.

## 7. Sample Size and Power

- Pilot: n≈30 submissions to estimate variance and refine prompts/UI.
- Main: target 200–300 submissions to detect ICC≥0.75 vs 0.6 and 25% time reduction with 0.8 power (mixed models).

## 8. Validity and Ethics

- Pre-registration: OSF entry with hypotheses, outcomes, models, exclusions, and stopping rules.
- IRB and Consent: student consent for research use; de-identification; no AI-only scores used for official grades.
- Randomization: seed-logged; auditable assignment to conditions.
- Bias checks: subgroup parity (no systematic degradation for any group).
- Governance: changes to prompts/UI logged with timestamps; before/after comparisons.

## 9. Implementation Plan

- System toggles: TA-only vs AI+TA; shadow AI scoring.
- Research log: structured JSON/Parquet exports with timestamps and condition.
- Gold-standard UI: assignment queues, blind scoring, adjudication screen.
- CI gate: `python synthetic_eval.py --n 20` thresholds (coverage, pass-rate) in CI.
- Analysis notebooks: templates for reliability, efficiency, feedback quality, and learning impact.

## 10. Publication Plan

- Venue candidates: SIGCSE / ITiCSE / ASEE / CS education journals.
- Artifacts: pre-registered protocol, anonymized dataset (subject to IRB), analysis scripts, prompts.
- Reporting: CONSORT-style flow; threat to validity analysis; replication notes.

## 11. Risks and Mitigations

- Prompt drift → lock prompt versions per release; regression via CI synthetic gate.
- Overreliance on AI → always human-in-the-loop; audit edits; do not use AI-only for grades.
- Privacy → hash ids; strip PII; store keys securely.

---
Maintainer: UVU CS AI Grader Team
