# Scoring

Scores summarise verified findings and coverage. They are computed by `scripts/compute_scores.py` from `findings.json` and `coverage-ledger.json`; they are never typed in. The same findings must always give the same numbers, otherwise a retest cannot tell real improvement from a different mood.

## Contents

1. What a score means
2. Severity model
3. Effort and quick wins
4. Finding confidence
5. Category scores
6. Evidence tier limits
7. Coverage rule
8. Judgment adjustments
9. Global score
10. Metrics reported beside the score
11. Worked example
12. Calibration anchors
13. Presenting scores

## 1. What a score means

A category score from 0 to 10 says how well the site serves first-time visitors in that area, judged from the evidence that was collected. It always travels with a confidence level and a coverage figure, because "no problems found" is only as good as the looking.

- A high score needs both a lack of serious problems and enough evidence. Without strong evidence the ceiling is lower, so no category earns a free ten.
- A category that could not be examined is "not assessed", not zero and not a default.
- Scores are for comparing a site with itself over time (see `RETEST.md`). They are not benchmarks across sites.

## 2. Severity model

Each confirmed finding gets three ratings, each with a written reason, and an overall severity.

**Impact** (what happens to a visitor who meets the problem):

| Score | Meaning |
|---|---|
| `cosmetic` | Noticed, but does not change what the visitor understands or does. |
| `minor` | Slows or irritates; the visitor still succeeds without help. |
| `major` | The visitor often needs several attempts, guesses wrong or abandons the task. |
| `blocking` | The visitor cannot complete the task or reach key information at all. |

**Frequency** (how many visitors meet it):

| Score | Meaning |
|---|---|
| `rare` | Only unusual situations or one narrow path. |
| `occasional` | Some personas or some paths. |
| `common` | Most personas or the main path. |
| `universal` | Every visitor passes through it. |

**Persistence** (what happens after the first time):

| Score | Meaning |
|---|---|
| `one_time` | Costs the visitor once; later visits are fine (for example learning what a label means). |
| `recurring` | Costs the visitor every time they use that part of the site. |

**Overall severity**: `minor`, `moderate`, `major`, `blocker`. The validator enforces only that overall severity is coherent with impact:

| Impact | Allowed overall severity |
|---|---|
| `cosmetic` | minor |
| `minor` | minor, moderate |
| `major` | moderate, major |
| `blocking` | major, blocker |

Starting point for the choice within the allowed range:

- `cosmetic`: minor.
- `minor` impact: minor, or moderate when it is common or universal and recurring.
- `major` impact: moderate when rare or occasional; major when common or universal.
- `blocking` impact: major when rare or occasional and off the main path; blocker when it stops a main-path task for common or universal visitors.

Only a blocking impact can produce a blocker, so a blocker always means "visitors cannot do something that matters". Say in the reason what they cannot do.

Severity is earned from evidence, not from how annoyed a persona sounded. Taste without a visitor consequence is not a finding.

## 3. Effort and quick wins

`remediation.effort` is the owner's cost to fix, not the importance:

| Effort | Typical meaning |
|---|---|
| `low` | A copy change, a label, a link, a setting; no design or development dependency; hours. |
| `medium` | A page or component change; days; one person. |
| `high` | A structural change (navigation, flow, content model) or several people over weeks. |

`quick_win` is derived, not chosen: effort is `low` and (severity is major or blocker, or severity is moderate with frequency common or universal). The validator rejects any other value. Quick wins are listed first in the report, because they are the cheapest improvement for the biggest effect.

## 4. Finding confidence

Confirmed findings carry their own confidence (`low`, `medium`, `high`), separate from the category confidence below.

- A confirmed finding needs at least `medium`. If the honest answer is `low`, the finding is `needs_validation`, with an exact open question.
- `high` needs at least two independent observed sessions (for example a persona session and a lens audit, or two personas) and `full` isolation.
- A confirmed finding needs at least one `observed` evidence item. Evidence that is only `inferred` supports `needs_validation`.
- Design, mobile and rendering-dependent WCAG findings need observed evidence at tier `rendered` or `provided`.
- An evidence item's tier cannot exceed the run's tier.

## 5. Category scores

Eight categories: clarity, navigation, trust, content, design, flows, mobile, accessibility.

1. **Penalties.** Each confirmed finding in the category adds a penalty by overall severity: blocker 3.0, major 1.5, moderate 0.6, minor 0.2. Penalties are sorted from largest to smallest and each is multiplied by 0.8 raised to its position (the first counts fully, the second 80 percent, the third 64 percent, and so on), so many small problems cannot outweigh one serious one and a long tail does not bury a good site.
2. **Raw score** = 10 minus the summed penalties, not below 0.
3. **Caps.** The final score cannot exceed the lowest applicable cap:
   - a confirmed blocker in the category: 4.0;
   - else a confirmed major problem: 6.5 (so a category with a major problem lands in "fair" at best);
   - coverage below 50 percent: 7.0;
   - the confidence ceiling: low 7.5, medium 9.0, high 9.5.
4. **Category confidence** starts from the highest level the evidence tier allows (section 6), then:
   - coverage below 50 percent sets it to low; coverage from 50 to 79 percent lowers it one level;
   - degraded isolation lowers it one level;
   - any `needs_validation` finding in the category limits it to medium.
5. **Computed score** = the lower of the raw score and the cap, rounded to one decimal.

`needs_validation` findings do not add penalties; they limit confidence and appear in the report as open questions. `rejected` findings do not count.

## 6. Evidence tier limits

The highest category confidence each evidence tier can support:

| Category | rendered | provided | text |
|---|---|---|---|
| clarity | high | high | medium |
| navigation | high | medium | medium |
| trust | high | high | medium |
| content | high | high | high |
| design | high | medium | not assessable |
| flows | high | low | low |
| mobile | high | low | not assessable |
| accessibility | high | low | low |

A category is **not assessed** (no score, a stated reason) when:

- the tier cannot support it (design and mobile under `text`);
- no unit that evidences it was tested or partially tested;
- for mobile: no tested or partial mobile viewport unit exists;
- for accessibility: the accessibility lens was not run.

The scorecard says why. Never fill a not-assessed category with a guess, and never fold it into the overall score as a default.

## 7. Coverage rule

Coverage is the share of the units that evidence a category that were actually done. A unit counts 1.0 when `tested`, 0.5 when `partial`, 0 when `blocked` or `untested`; `skipped` units are left out of the count.

| Category | Units that evidence it |
|---|---|
| clarity | `first_impression` units; the content_trust lens |
| navigation | `task` units; the heuristics lens |
| trust | the content_trust lens; `task` units |
| content | the content_trust lens; `exploration` units |
| design | the heuristics lens; `viewport` units |
| flows | `task`, `flow` and `state` units; the flows_forms lens |
| mobile | `viewport` units; the mobile_performance lens |
| accessibility | the accessibility lens |

A unit that evidences several categories counts for each. Skipping a unit with a reason keeps coverage honest in a different way: the skipped unit is listed in the report as a known gap.

## 8. Judgment adjustments

After computation the orchestrator may add an adjustment of at most plus or minus 1.0 to a category, with a written reason, in `adjustments.json`. Adjustments exist for evidence the penalty model cannot see.

Allowed reasons:

- a persona difficulty that clearly mattered but did not become a separate finding (for example repeated hesitation across tasks on one theme);
- the combined effect of several confirmed findings in one area that the decay understates;
- a strong, verified strength that the penalty model ignores (record it as a strength too).

Not allowed:

- to reach a target number or a nicer band;
- to compensate for a thin evidence tier (the tier limits apply to the final score);
- for taste, or for an impression the sessions did not show;
- to raise a score above a cap. Positive adjustments are clipped by the cap and the scorecard records "adjustment clipped by cap".

Each adjustment also carries a written `justification` for the category, in plain words. Without one, the script writes a factual default (counts, coverage and tier). Persona verdicts (`would_return`, `would_recommend`, one line each) go in the same file; they are opinions of simulated visitors, not statistics.

## 9. Global score

- The global score is the weighted average of final scores over the assessed categories, with the weights renormalised. The weights come from the site type's profile (`SITE-TYPES.md`, section 4).
- Bands: 9.0 and up excellent; 7.0 to 8.9 good; 5.0 to 6.9 fair; 3.0 to 4.9 poor; below 3.0 failing.
- **Global confidence** is the weighted mean of the category confidences, rounded.
- **Provisional**: the result is marked provisional when the assessed categories carry less than 60 percent of the weight, or the global confidence is low. A provisional score is shown with that label and never headlined without it.
- **Floor warning**: any assessed category at 4.0 or below is named beside the overall score, because an average can hide a failing trust or flows score. Say it in the report: "the overall score is fair, but trust is poor".
- If no category could be assessed, there is no global score and the band is "not rated".

## 10. Metrics reported beside the score

Task and first-impression metrics come straight from the ledger. They do not change the scores; they show what happened.

| Metric | Definition |
|---|---|
| Success rate | Tasks completed, with or without difficulty, divided by tasks attempted, leaving out blocked attempts |
| Difficulty rate | Completed with difficulty divided by completed |
| Abandon rate | Abandoned divided by attempted, leaving out blocked |
| Incorrect rate | Completed incorrectly (finished, but with the wrong result) divided by attempted, leaving out blocked |
| Blocked count | Attempts stopped by something outside the test (a wall, an error, the tier); reported separately and never counted as visitor failure |
| Path efficiency | For completed tasks, optimal steps divided by steps taken, capped at 1, averaged |
| First-click success | Share of tasks whose first click led along a valid route to the goal (judged by the orchestrator against the site map) |
| Five-second test | Per persona: understood what, audience and action (yes 1, partly or maybe 0.5, no 0), gut rating 1 to 5, would continue; averaged over personas |

With three personas these are small numbers. Report them as counts as well as rates ("6 of 9 tasks completed") so nobody reads a percentage as a statistic.

## 11. Worked example

The bakery example in `examples/bakery/` (text tier, full isolation, `lead-gen-local`, default profile).

| Category | Findings | Raw | Cap | Computed | Adjustment | Final | Confidence |
|---|---|---|---|---|---|---|---|
| clarity (18) | 1 major | 8.5 | major 6.5 | 6.5 | 0 | 6.5 | medium |
| navigation (12) | 1 major | 8.5 | major 6.5 | 6.5 | 0 | 6.5 | medium |
| trust (14) | 1 moderate | 9.4 | medium 9.0 | 9.0 | −1.0 | 8.0 | medium |
| content (12) | 1 major, 1 minor | 8.34 | major 6.5 | 6.5 | 0 | 6.5 | high |
| flows (16) | 1 major | 8.5 | major 6.5 | 6.5 | 0 | 6.5 | low |
| accessibility (8) | none confirmed, 1 needs validation | 10 | low 7.5 | 7.5 | 0 | 7.5 | low |
| design (8) | not assessed: text-only evidence | | | | | | |
| mobile (12) | not assessed: text-only evidence | | | | | | |

The content raw score is 10 − (1.5 + 0.2 × 0.8) = 8.34. The trust adjustment is justified by repeated difficulty for the skeptical persona. The weighted average over the assessed weight (80 of 100) is (18×6.5 + 12×6.5 + 14×8.0 + 12×6.5 + 16×6.5 + 8×7.5) ÷ 80 = 6.9, band fair, confidence medium, with a note that design and mobile were not assessed.

## 12. Calibration anchors

What a category score means in practice. Use these to check that adjustments and justifications are consistent.

| Score | A visitor of this kind of site would say |
|---|---|
| 9 to 10 | "No friction. I got what I came for and I trust this." Needs strong evidence across personas and, for design, mobile and accessibility, rendered evidence. |
| 7 to 8.9 | "Mostly fine. A few small snags, none that stopped me." No major problem confirmed. |
| 5 to 6.9 | "I got there, but I had to work for it." At least one major problem, or several moderate ones. |
| 3 to 4.9 | "I nearly gave up" or "I gave up". A blocker, or several majors. |
| 0 to 2.9 | "I could not do what I came to do." The category fails at its job. |

## 13. Presenting scores

- Always show the score with confidence and coverage, and say which categories were not assessed and why.
- Use the band word with the number ("6.9, fair").
- Compare runs only through `scripts/compare_runs.py`, which applies noise thresholds (0.7 for a category, 0.5 for the overall score). Smaller movements are noise from simulated testers.
- Do not compare scores across different sites, or across runs with a different evidence tier or weight profile. The comparison tool marks such runs not comparable.
- Never describe a score as a measure of conversion, revenue or real customer satisfaction. It is a structured expert-style reading from simulated visitors.
