# AI Grader Research Design (Department of Computer Science)

This document outlines protocols to evaluate AI-assisted grading reliability and usability, redesigned for a general AI Grader.

## Scientific Goals and Hypotheses

Primary hypotheses:
- H1: The AI Grader’s criterion-level feedback improves grading quality (specificity, alignment) compared to baseline TA feedback alone.
- H2: With rubric-aligned prompting and guardrails, AI-suggested scores correlate strongly with faculty gold-standard scores (ρ ≥ 0.75).
- H3: Iterative human-in-the-loop revision reduces time-to-completion per assignment without degrading inter-rater reliability.

Secondary hypotheses:
- H4: AI feedback increases student revision quality (effect size d ≥ 0.4) across assignments.
- H5: Domain-tailored rubrics (CS) yield higher AI–faculty agreement than generic rubrics.

Outcomes and metrics:
- Agreement with gold standard: Pearson/Spearman correlation, Cohen’s/Conger’s kappa (for categorical bins), ICC(2,k).
- Reliability: Inter-rater reliability across AI, TA(s), faculty.
- Feedback quality: Rubric-aligned specificity via blinded rubric; linguistic markers (concreteness, actionability).
- Efficiency: Time-on-task logs; number of iterations to finalize.
- Student learning: Pre/post or first/second submission deltas scored by faculty.

## Study Design Overview

Designs to consider (select per course/IRB constraints):
- Within-subjects crossover: Each assignment graded by AI+TA and TA-only in counterbalanced order; faculty gold standard as reference.
- Between-subjects: Sections randomized to AI+TA vs TA-only.
- Blinded evaluation: Faculty graders blind to source (AI vs TA); feedback anonymized.

Sampling:
- Courses: CS1, Data Structures, Software Engineering (varied rubric types: correctness, style, design, tests).
- N≥100 assignments per condition to power correlation/kappa detection (pilot N≥30).

Data collection:
- Store: rubric id/version, submission text/artifacts, AI outputs (scores/feedback), human edits, timestamps, final grades.
- Instrument: per-step timestamps for time-on-task; number and nature of edits.

Analysis plan:
- Agreement: ICC, weighted kappa (ordinal 0–3), correlation with CIs via bootstrapping.
- Feedback quality: blinded rubric scoring; compare means via mixed models (account for section/instructor random effects).
- Efficiency: time comparisons via mixed effects; nonparametric tests if needed.
- Multiple comparisons control: Holm–Bonferroni.

Threats to validity and mitigations:
- Construct validity: Ensure rubrics operationalize constructs; pilot and expert review.
- Internal validity: Randomization/blocking; pre-registration of analysis.
- External validity: Multiple courses/levels; diverse assignments.
- AI variance: Fix model version; log prompts/params; deterministic settings when possible.

Ethics/IRB:
- Obtain IRB approval; student consent; de-identify data; secure storage.

Pre-registration:
- Register hypotheses and analysis on OSF; include power analysis and stopping rules.
