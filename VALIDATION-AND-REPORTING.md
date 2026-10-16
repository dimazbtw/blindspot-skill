# Phases 3 to 7: validation, reconciliation, records, verification, reporting

Hunting produces candidates. This file turns them into verified findings and a report. The pipeline is built so that no claim reaches the report unless a fresh agent failed to disprove it, a validator accepted its record, and a second fresh agent re-checked it from the record alone.

## Contents

1. Overview
2. Phase 3: validation
3. Phase 4: brief reconciliation
4. Phase 5: structured output
5. Phase 6: independent verification
6. Phase 7: reporting
7. Final checks before delivering
8. Degraded isolation (sequential mode)

## 1. Overview

| Phase | Input | Who | Output | Gate |
|---|---|---|---|---|
| 3 Validation | Session logs, ledger | Orchestrator merges; fresh verifier agents test | `candidates.md` with verdicts | none (judgment) |
| 4 Brief reconciliation | Verified candidates, brief | Orchestrator; one fresh reconciler if a brief exists | gap table in `candidates.md`, `brief_opened` set | `validate_ledger.py --stage final` |
| 5 Structured output | Verified candidates | Orchestrator | `findings.json`, `adjustments.json`, `scorecard.json` | `validate_findings.py`, `compute_scores.py` |
| 6 Independent verification | `findings.json`, cited log entries | Fresh agents, new ones | verification records | `validate_findings.py --stage verified` |
| 7 Reporting | Verified records | Orchestrator | generated tables, `REPORT.md` | final checks (section 7) |

Roles never overlap: the agent that found a problem never verifies it, and the agent that verified it in Phase 3 never gives the Phase 6 check.

## 2. Phase 3: validation

### 2.1 Collect candidates

Read every session log in `sessions/`. A candidate is any of:

- a persona entry with a hesitant, confused, frustrated or gave_up reaction and a named cause;
- a lens entry with verdict `fail` (or `partial` with a visitor consequence);
- a pattern in a persona's session summary;
- a critic's coverage or leniency flag that points to a real page problem.

Write `candidates.md`, one block per candidate:

```
## C3: <short title in the visitor's terms>
- Category: clarity
- Seen in: S1-E01, S2-E01, L2-E01
- Personas: first-timer, low-literacy
- Claim: <one or two sentences: what the page shows and what the visitor could not do>
- Checks: CL-01, CL-03
- Proposed root cause: <draft, one sentence>
```

### 2.2 Merge by root cause

One root cause, one candidate. The same missing sentence seen by three personas and one lens is a single candidate with four entries. Rules:

- Merge when fixing one thing would fix all of them (same element, same missing information, same label).
- Keep separate when the fix differs, even on the same page.
- Do not split a root cause across categories to look thorough. Choose the category where the visitor feels it; cite the other checks in `heuristic_refs`.
- Record which sessions saw it. The count of independent sessions matters for confidence (`high` needs at least two observed sessions and full isolation).
- A lens failure no persona touched is still a candidate if there is a plausible visitor consequence. Mark that frequency honestly; do not inflate it.
- A persona difficulty that matches no check is a candidate with its own root cause.

### 2.3 Verifier agents

Delegate fresh agents to try to disprove candidates. Cover every candidate that could become `moderate` or worse, one per candidate. In `quick` mode, minor candidates may go in batches of up to five. The finder never verifies its own candidate.

Packet: the site URL, the evidence tier, the candidate block, the cited log entries copied verbatim, `site-map.md`, and the cards (without the Reveals line) of the personas involved. Not the brief, not other candidates, not other verifiers' verdicts.

```
You are verifying one candidate usability problem on a website. Your job is to try to
disprove it. Assume the finder may be wrong. You know nothing about what the site's
owner intended.

Site: {url}   Evidence tier: {tier}
Candidate: {candidate block}
Cited log entries (verbatim): {entries}
Site map: {site-map}
Persona cards involved: {cards}

Work read-only. Do not submit anything. If the tier is text, you can read page text only;
say so wherever it limits what you can conclude.

Run these seven tests, one line of reasoning each:
1. REPRODUCIBLE: Go to the cited location and look again. Is what the entry says there?
2. PERSONA OVERREACH: Would a visitor with that persona's fluency, vocabulary and patience
   really fail here, or did the simulated tester behave worse than the card allows?
3. INTENT: Could this be a deliberate trade-off that works for visitors (for example a
   contact form instead of a phone number for a clear reason the page states)?
4. BASELINE: How do comparable sites, or common web conventions, handle this? Is the
   claim an unusual standard?
5. IMPACT: Name the concrete consequence for a visitor. If you cannot, say so.
6. SEVERITY: Propose impact (cosmetic, minor, major, blocking), frequency (rare,
   occasional, common, universal), persistence (one_time, recurring), each with a reason.
7. ENVIRONMENT ARTIFACT: Could what was seen come from how the page was fetched (cookie
   or consent wall, bot page, JavaScript-only content, geo or language version, a stale
   cache)? Look at the page a second way if you can.

Return, in this format:

CANDIDATE C#
VERDICT: CONFIRMED | NEEDS_VALIDATION | REJECTED
REJECTION CLASS (if REJECTED): not_reproducible | intended_design | persona_overreach |
  environment_artifact | factually_wrong | duplicate | below_bar | out_of_scope
TESTS: 1..7, one line each
SEVERITY PROPOSAL: impact / frequency / persistence with reasons
CONFIDENCE: medium or high, with the reason
ROOT CAUSE: one sentence: <page or component> <lacks or does something specific>, which <consequence>
INTENDED BEHAVIOR: what the site seems to be trying to do
BASELINE: what comparable sites or conventions do, or "not checked" with the reason
OPEN QUESTION and RESOLUTION PATH (only if NEEDS_VALIDATION): a yes-or-no question and who or what can answer it
CORRECTIONS: anything in the candidate text that is wrong or overstated
```

### 2.4 Handling verdicts

- **CONFIRMED**: becomes a confirmed finding in Phase 5.
- **NEEDS_VALIDATION**: used when an exact fact is unresolved (for example "does the carousel move on its own?") and cannot be settled with the evidence tier at hand. It needs an open question that can be answered yes or no and a resolution path (a rendered check, the site owner, a real-user session, an analytics query). It carries no severity and does not affect penalties; it limits category confidence.
- **REJECTED**: recorded in `findings.json` with its class and a reason. Rejections show the owner what was considered and why it was dropped, and protect the report from re-raising the same item.
- A verdict the orchestrator doubts goes to a second fresh verifier; never override a verdict silently. Disagreement that remains becomes `needs_validation`.
- Typical rejections: a persona that failed on purpose (`persona_overreach`), a fetch artifact (`environment_artifact`), a convention that is fine (`below_bar`), a trade-off that works (`intended_design`).
- Update `candidates.md` with the verdict and the verifier's text. Keep rejected candidates in the file.

Corroboration: a candidate seen by two independent sessions (a persona and a lens, or two personas) is stronger than one seen once. A single-session candidate can still be confirmed if the verifier reproduced it, but its confidence is `medium` at most.

## 3. Phase 4: brief reconciliation

Until now the developer's brief has been sealed. It is opened here so that it can show gaps between what the builder meant and what visitors understood, and never earlier.

### Without a brief

Skip the opening. Derive any gap only from the reconnaissance hypothesis (`inferred_goal`): if the page appears to push one action but visitors consistently understood another, record a gap with `source: inferred_goal`. `brief_opened` stays false and is not an error because `brief_present` is false.

### With a brief

1. Set `run.brief_opened` to true in the ledger and note the time in `run-notes.md`.
2. Delegate one fresh reconciler. Packet: the brief, the confirmed and needs_validation candidates (titles, claims and verdicts), the persona five-second results and task outcomes from the ledger, the persona summaries. Not the raw session logs.

```
You have the developer's brief and a summary of what simulated first-time visitors
understood. Compare them.

For each intention in the brief (audience, main message, key features, key actions, claims):
  - what visitors actually understood or did (cite candidate or ledger evidence),
  - MATCH | PARTIAL | MISMATCH | NOT_TESTED,
  - for MISMATCH or PARTIAL: one sentence stating intended and perceived.

Then list brief items that no persona ever discovered or used (hidden features), and
candidates that the brief explains as deliberate (say what the trade-off is, but do not
reject anything: a visitor's confusion is real whatever the intent).

Do not suggest new problems unless they follow directly from a gap. Do not soften findings.
```

3. Use the output:
   - Add a `gap` object (`source: "brief"`, `intended`, `perceived`) to each confirmed finding it explains, and update `intended_behavior` with the brief's wording.
   - A brief item that nobody discovered becomes a new candidate. It goes through the Phase 3 verifier before it can become a finding; the brief itself is never evidence of a visitor problem.
   - The brief never rejects a finding and never lowers a severity. It can raise attention (an item the owner calls core that no visitor found) but severity still comes from visitor evidence.
   - Put the gap table in `candidates.md` under "Brief reconciliation".
4. Run `python3 scripts/validate_ledger.py <run>/coverage-ledger.json --stage final --sessions-dir <run>/sessions`. It fails if `brief_present` is true and `brief_opened` is false, and if any unit is unresolved.

## 4. Phase 5: structured output

Write `findings.json` following `schemas/findings.schema.json`; the bakery example is the model. Number confirmed findings `P1`, `P2`... in severity order (blockers first), then needs_validation, then rejected. Strengths are `ST1`... .

### 4.1 Writing the fields

| Field | Guidance |
|---|---|
| `title` | The visitor's problem in plain words, 120 characters at most. Not the fix, not a check name. |
| `description` | What the page shows. Observable facts only. |
| `user_impact` | What the visitor cannot do, understand or trust because of it. |
| `root_cause` | One sentence: `<page or component> <lacks or does something specific>, which <consequence for the visitor>`. The sentence a developer could act on. |
| `intended_behavior` | What the site seems to be trying to do, so a reader sees why this is a problem and not a working trade-off. |
| `heuristic_refs` | Every check ID that applies (usually one to four). Check IDs come from the checklist files. |
| `evidence` | At least one `observed` item; each has the real `log_ref` from a session log, the page URL, a short location, a short excerpt (200 characters at most) and what it shows. The item's `tier` is the tier at which it was observed. Use `inferred` for the inferences. |
| `reproduction` | Steps a stranger can follow from the home page, then what should happen and what does. |
| `affected_personas` | Persona ids that met it in the sessions. |
| `severity` | All three ratings with reasons, and the overall severity (`SCORING.md`). The verifier's proposal is the starting point. |
| `confidence` | `medium` or `high` with a reason (`high` needs two observed sessions and full isolation). |
| `baseline_comparison` | What comparable sites or conventions do. If none was checked, say "no comparable site was checked; judged against general web convention". |
| `remediation` | A strategy that tells the owner what to change, an effort level, and where words are the fix, `copy_changes` with the location, the text now (`before`) and a suggested replacement (`after`). |
| `quick_win` | Derived (`SCORING.md`, section 3). |
| `found_by` | Session ids that surfaced it. |
| `gap` | Only after Phase 4. |
| `persists_from` | Retest only (`RETEST.md`). |

Write findings with evidence and a consequence, or as `needs_validation` with an exact question. Do not write hedged findings ("may potentially confuse some users"). Do not report taste. Do not describe intent or bad faith: describe what is visible.

Strengths are recorded with evidence, why they work and a `preserve_note` (what not to break while fixing other things). A report with only failures hides what to protect.

### 4.2 Adjustments

After the first validator pass, decide whether any category needs a judgment adjustment. Write `adjustments.json` (see `scripts/compute_scores.py` and `SCORING.md`, section 8): per-category `adjustment` (at most plus or minus 1.0), `reason` and `justification`; `persona_verdicts` (one per persona: `would_return`, `would_recommend`, `one_line`); and an optional `global_note`.

### 4.3 Run the gates

```
python3 scripts/validate_findings.py <run>/findings.json --ledger <run>/coverage-ledger.json --sessions-dir <run>/sessions
python3 scripts/compute_scores.py compute --findings <run>/findings.json --ledger <run>/coverage-ledger.json --adjustments <run>/adjustments.json --out <run>/scorecard.json
python3 scripts/compute_scores.py validate <run>/scorecard.json
```

Fix errors in the record, never in the validator or the computed numbers. Common errors and their causes:

- a `log_ref` that does not exist (wrong ID, or the heading line in the log is malformed);
- evidence at a higher tier than the run;
- a design, mobile or rendering-dependent WCAG finding without observed `rendered` or `provided` evidence: downgrade it to `needs_validation`, or leave it out;
- `quick_win` that differs from the derived value;
- severity incoherent with impact;
- `high` confidence with one session, or under degraded isolation.

## 5. Phase 6: independent verification

Fresh agents that have seen nothing of Phase 3 re-check the confirmed findings from the record alone. The point is to catch what the finder, the Phase 3 verifier and the orchestrator all agreed on and all got slightly wrong.

Delegate one agent per blocker or major finding and one per batch of up to five others. Packet: the finding JSON, the cited log entries verbatim, the URL, the tier. Not `candidates.md`, not the Phase 3 verdicts, not the other findings.

```
You are checking a finished usability finding against its own evidence. You did not
write it. Your job is to find what is wrong with it. Assume nothing.

Site: {url}   Evidence tier: {tier}
Finding(s): {JSON}
Cited log entries (verbatim): {entries}

Check, for each finding:
1. Do the cited entries actually say what the description and evidence items claim?
2. Is the root cause one accurate sentence, and does it follow from the evidence?
3. Do the three severity ratings follow from the reasons given? Is the overall severity
   coherent with the impact?
4. Can the reproduction steps be followed from the home page and do they lead to the
   problem? You may look at the page once, read-only, to check.
5. Does anything claim more than the evidence tier allows (layout, contrast, keyboard use
   from text, for example), or present an inference as an observation?
6. Is the remediation plausible, and the effort level honest?
7. Does the text accuse anyone of bad intent, or describe taste without a visitor
   consequence?

Return, for each finding:
FINDING P#
VERDICT: VERIFIED | CORRECTED | REJECTED
CORRECTIONS: a list of exact changes (field and new text); empty if VERIFIED
NOTES: one or two sentences on what you checked
REASON (if REJECTED): why the evidence does not support the finding
```

Then the orchestrator:

1. Applies each correction to `findings.json` and adds a `verification` object to the finding: `{"status": "verified" or "corrected", "notes": "...", "corrections": [...]}`.
2. Turns a REJECTED finding into a `rejected` record with a class and the reason, and removes it from the confirmed list.
3. Runs `python3 scripts/validate_findings.py ... --stage verified`, which requires a verification record on every confirmed finding.
4. Recomputes `scorecard.json` with the same command as in section 4.3. Scores follow the corrected record.

If any finding was rejected or its severity changed, run the independent check on the changed items again before reporting.

## 6. Phase 7: reporting

### 6.1 Generate the tables

```
python3 scripts/render_report.py --findings <run>/findings.json --scorecard <run>/scorecard.json --ledger <run>/coverage-ledger.json --out-dir <run> [--evolution <run>/evolution.json] [--labels labels.json]
```

It writes `report-tables.md` (scorecard, task results, first impressions, findings, quick wins, strengths, evolution), `FINDINGS-DETAIL.md` (every confirmed finding in full, plus the rejected candidates) and `NEEDS-VALIDATION.md` (every open question). These are derived from the verified JSON; do not retype numbers.

### 6.2 Write REPORT.md

The orchestrator writes `REPORT.md` itself, in the person's language, and pastes the generated tables in. It should be readable in five minutes; detail lives in the generated files.

1. **Header**: site, date, run number, mode, evidence tier and what it limits, isolation level, personas used.
2. **Verdict in brief**: three to five sentences. The overall score with its band and confidence ("6.9, fair, medium confidence"), the biggest thing visitors experience, the two or three things to fix first. If the result is provisional or a category is weak ("fair overall, but trust is poor"), say so here.
3. **Scorecard**: the table from `report-tables.md`, with the not-assessed categories and their reasons.
4. **First impressions and task results**: the generated tables, then two sentences of reading ("only one of three personas could say what the site sells").
5. **What works**: the strengths, each with why it works and what to preserve.
6. **What to fix first**: quick wins first, then the other findings by severity. For each: the ID, the visitor's problem, the root cause, the fix, the effort. Link to `FINDINGS-DETAIL.md` for evidence.
7. **Pros and cons**: at most five of each, each pointing to a finding or strength ID. Not a restatement of the tables: the summary a busy person remembers.
8. **How simulated visitors felt**: one line per persona from the persona verdicts, labelled as simulation.
9. **Brief versus reality** (only if a brief was given): the gap table in plain words, with the intention, what visitors understood, and the finding ID.
10. **Open questions**: the needs-validation items with their resolution path, linking to `NEEDS-VALIDATION.md`.
11. **What was and was not tested**: pages covered, units skipped or blocked with reasons, categories not assessed, and what a rendered or real-user pass would add.
12. **Observations outside scope**: one line each, no investigation.
13. **How to read this report**: personas are simulations, not customers; the tier limits what could be judged; accessibility results are expert-style checks, not a conformance statement; the serious findings deserve confirmation with three to five real people from the audience.
14. **Next steps**: fix the quick wins and the top problems, then retest (`RETEST.md`). For retests, replace "what to fix first" by the evolution section (`RETEST.md`, section 6).

Writing rules for the report:

- Every statement traces to the records. Do not add findings that are not in `findings.json`.
- State uncertainty once, where it applies, and plainly. No hedge-stacking.
- Lead with what matters to the owner, not with method.
- Describe observable cues, not intent. Never accuse a site of fraud or bad faith.
- Describe groups of visitors by situation ("visitors who do not know the term"), never by age, nationality or disability as a shorthand for ability.
- Use the same IDs as the records (`P3`, `ST2`, `S2-E03`, `CL-01`), so the owner can look anything up.

### 6.3 Deliver

Give the person `REPORT.md` first and, in the way the platform gives files to people, the generated `FINDINGS-DETAIL.md` and `NEEDS-VALIDATION.md`. If the report is for others (a team, a client), say so and use whatever shareable form the platform offers. Keep the run folder; a later retest needs it.

The closing message is short: the overall score and band with confidence, the top two or three problems in a sentence each, how far to trust it (tier and coverage in one clause), and one next step (fix the quick wins, then retest). Do not recap the process.

### 6.4 Language and labels

Findings, narrative and the report follow the person's language. JSON keys, enumerations and IDs stay in English. To localise the generated tables, run `python3 scripts/render_report.py --dump-labels > labels.json`, translate the values, and pass `--labels labels.json`. Missing keys fall back to English. Free text inside the records appears as written.

## 7. Final checks before delivering

- Every validator gate passed after the last change to the records.
- `scorecard.json` was computed, not edited, and `compute_scores.py validate` says OK.
- Every number in `REPORT.md` appears in the generated tables or the records.
- No finding in `REPORT.md` is missing from `findings.json`, and none is a rejected candidate.
- The brief appears nowhere before Phase 4: not in packets, not in logs, not in the ledger notes of earlier phases.
- The report names the evidence tier and what it limits, the categories not assessed, and the skipped units.
- No credentials, personal data or invented quotations appear anywhere in the run folder.
- Check IDs in findings exist in the checklist files.
- Strengths are included.

## 8. Degraded isolation (sequential mode)

Without a delegation tool the same steps run one after another in one context. Verification is then weaker, and the skill says so rather than hiding it.

- Run each verification role after a clean break: re-read only the inputs listed for that role, write the seven tests (or the seven checks) explicitly before the verdict, and take the position of someone trying to disprove.
- Do not mark any finding `high` confidence; the validator refuses it.
- The scorecard lowers category confidence by one level, as `isolation: degraded` is recorded in the ledger.
- Say in the report, in the method note, that the roles shared one context and that this lowers the independence of the verification.
- Offer to re-run Phases 3 and 6 with fresh agents when the platform allows it.
