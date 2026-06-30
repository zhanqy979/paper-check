---
name: pc-paper-review-grounded
description: Use when generating, checking, calibrating, or rewriting concise academic peer-review comments from a manuscript, screenshots, reviewer forms, tables, figures, or an existing review draft. Apply this PC paper-check skill whenever review claims must be objective, traceable to supplied materials, and free of invented experiments, data, contributions, defects, citations, baselines, metrics, or technical conclusions.
---

# PC Paper Review Grounded

## Skill purpose

Generate, check, or rewrite academic review comments that are objective, concise, and traceable to the manuscript or user-provided materials. Treat the supplied paper, screenshots, tables, review form, or draft review as the only evidence base unless the user explicitly asks for external literature comparison.

## When to use

Use this skill for:

- Writing a new conference or journal review from a paper, screenshot set, review form, or extracted manuscript text.
- Checking an existing review for factuality, calibration, tone, consistency, and template compliance.
- Rewriting a review to be more professional, concise, grounded, or aligned with a venue form.
- Filling review sections such as strengths, weaknesses, recommended changes, ratings, TPC comments, or expertise.

Do not write factual claims about the paper from memory or plausible domain expectations. If the evidence is not in the manuscript or user materials, state that it is not reported, unclear, not sufficiently specified, or cannot be verified from the manuscript.

## Required inputs

Before drafting a review, identify the available evidence:

- Manuscript source, PDF text, screenshots, tables, figures, or user-provided excerpts.
- Any required venue template, review form, rating scale, or screenshot of review options.
- Any existing review draft to check or rewrite.
- User preference for output language or format.

If the user requests a specific conference/system template, table options, or rating scale but has not provided it, ask for the template or screenshot before producing the final formatted review. If no specific template is provided, use the default template below.

## Review workflow

1. Extract evidence before judging. Locate the title, abstract, research topic, claimed contributions, method/system/theory/framework, experimental setup, baselines, datasets, channel/system models, parameters, metrics, figures, tables, and stated conclusions.
2. Run the factuality checklist. Mark each review-relevant claim as supported, missing, unclear, or unverifiable from the manuscript.
3. Draft only evidence-backed comments. Use cautious language for missing or uncertain information.
4. Select only the most important points. Strong Aspects, Weak Aspects, and Recommended Changes should be point-form, usually about 6 items each and never more than 8 items each.
5. Calibrate the recommendation against the criticism strength.
6. Check the final text for technical misstatements, unsupported numbers, misplaced baseline references, overclaiming, and AI-like boilerplate.

## Grounded review principle

All review statements must be based on objective facts from the paper or user-provided material. Contributions, experimental settings, data, figures, algorithms, system configurations, baselines, metrics, and conclusions must be verified before being described as facts.

Use uncertainty wording when evidence is absent or incomplete:

- "not reported"
- "unclear"
- "not sufficiently specified"
- "cannot be verified from the manuscript"
- "the manuscript does not provide enough evidence to support this claim"

Never invent experiments, datasets, citations, claimed contributions, missing baselines, numerical results, or author intent.

## Factuality checklist

Before generating or finalizing a review, check:

- Whether the title, abstract, authorship information, and research topic are mutually consistent.
- Whether the manuscript actually proposes a method, system, theory, experiment, or survey/framework.
- Whether experiments exist. If experiments exist, do not write "no experiments"; instead evaluate scope, statistical support, baselines, settings, or reporting quality.
- Whether every number quoted in the review matches the corresponding table, figure, or text.
- Whether baselines, datasets, channel models, parameters, evaluation metrics, and system settings mentioned in the review truly appear in the manuscript.
- Whether claims such as "standard-compliant", "5G NR-compliant", "AI-RAN", or "ISAC" are substantively supported by the main text.
- Whether each criticism maps to a concrete manuscript location or to a clearly missing item.

## No technical misstatement rule

Avoid technically inaccurate criticism:

- If the paper has experiments, write about limited scope, insufficient statistical support, missing baselines, or unclear settings rather than "no experiments".
- If only some training details are missing, do not say "all training details are missing".
- If a standard sequence is used but remapped or modified, describe it as a "standard-inspired or modified setting" rather than completely non-compliant.
- If only a small number of random sequences is evaluated, write "insufficient statistical support for general conclusions" rather than implying the authors must exhaustively test all permutations.
- If a claim is plausible but unsupported by supplied materials, mark it as unverifiable instead of asserting it.

## Recommendation calibration

Match the recommendation to the evidence and criticism strength:

- Weak Accept: The core contribution, experiments, and results are mostly sound, with issues that can reasonably be improved.
- Borderline: Strengths and weaknesses are close; acceptance depends on venue standards and reviewer tolerance.
- Weak Reject: The topic is valuable, but evidence, method, experiments, writing, or consistency problems are substantial.
- Strong Reject: The manuscript has severe inconsistencies, lacks a basic contribution, lacks effective validation, is clearly out of scope, or appears incomplete/patched together.

Do not give an accept recommendation after listing many severe unresolved problems. Do not give an overly harsh recommendation when the main issues are additional experiments, clarification, and presentation.

## Default review template

Use this template unless the user provides a different one:

1. Review Recommendation
2. Strong Aspects
3. Weak Aspects
4. Recommended Changes
5. Ratings
6. Summary Justification for Recommendation
7. Comments to the TPC
8. Expertise

Default to English review text. Provide Chinese only if the user requests Chinese or a translation.

## Conciseness and output formatting rules

- Write Strong Aspects, Weak Aspects, and Recommended Changes as point-form lists.
- Include only the most important issues, usually about 6 points and at most 8 points per section.
- Do not pile up minor copyediting issues unless the user asks for a detailed line-by-line review.
- If the user requests `txt`, `md`, or another format, follow that format.
- If the user requests the form `1. aaaa: bbbbb.`, write every list item as a numbered item with a short title followed by one explanatory sentence.
- Write Comments to the TPC as a natural paragraph unless the user requests bullets.
- When useful, include manuscript locations or section/table/figure references in the comment, but do not fake exact line numbers.

## Tone and wording guidance

Use professional, restrained reviewer language. Prefer:

- "limited evidence"
- "not sufficiently justified"
- "requires stronger validation"
- "the current evidence is not enough to support this claim"
- "the manuscript would benefit from"
- "this weakens the strength of the conclusion"

Avoid exaggerated, adversarial, or AI-like phrases such as:

- "fatal flaw"
- "fundamentally undermines"
- "zero contribution"
- "course project"
- "obviously"
- "clearly proves"
- "must be rejected"

## Review checking mode

When the user provides an existing review for checking, focus on:

- Whether quoted numbers match the manuscript's tables and figures.
- Whether a value has been attributed to the wrong baseline, method, dataset, metric, or scenario.
- Whether the review criticizes content that the manuscript actually reports.
- Whether the review makes over-inferences beyond the supplied evidence.
- Whether the final recommendation matches the stated strengths and weaknesses.
- Whether the wording sounds formulaic, exaggerated, or AI-generated.

Return concrete corrections and replacement wording rather than only general advice.

## Safe vs unsafe review statements

Use safe, evidence-grounded wording:

- Safe: "The manuscript reports experiments, but the evaluation appears limited to a small number of settings, which weakens the generality of the conclusion."
- Unsafe: "The paper has no experiments."

- Safe: "The training hyperparameters are not sufficiently specified in the provided manuscript."
- Unsafe: "All training details are missing."

- Safe: "The standard-compliance claim cannot be verified from the manuscript because the mapping and parameter choices are not fully specified."
- Unsafe: "The system is completely non-compliant with the standard."

- Safe: "The result in Table 2 supports an improvement under the reported setting, but the manuscript does not establish whether the gain generalizes to other channel conditions."
- Unsafe: "The method is universally superior."

- Safe: "The review draft attributes this number to the wrong baseline; revise it to match the table before submission."
- Unsafe: "The authors manipulated the results."
