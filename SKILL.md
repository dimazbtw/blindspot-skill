---
name: blindspot
description: Blindspot tests a website the way real first-time visitors experience it, with zero knowledge of how it is supposed to work. Runs simulated personas through first-impression and task tests, sweeps the site with usability, content, trust, forms, mobile and accessibility checklists, tries to disprove every finding with an independent verifier, and produces an evidence-backed report with summary, critique, pros and cons, and 0-10 ratings per category. Use whenever someone asks to test, review, audit, critique, rate or get feedback on a website, landing page, web app, online store, or signup or checkout flow, including requests like "does my site make sense", "what would a customer think", "user testing", "UX review", "usability audit", "first impressions", "why aren't visitors converting", or a competitor site teardown. Also use to re-test a site after changes and measure improvement.
---

# Blindspot

People who build a website know what every button does, what every label means and where everything lives. Visitors know none of that. They arrive with a goal, a few seconds of patience and only what the page shows them. A site can look perfect to its builder and be confusing to almost everyone else, and the builder cannot see it because they cannot un-know what they know.

The name is the point: the builder's blind spot is the distance between what they know and what a visitor can see. This skill closes that gap. It looks at the site from the outside, as simulated visitors who have never seen it, collects evidence of where they get lost, tries hard to disprove its own findings, and only then compares what it saw with what the builder intended.

It is modelled on a staged audit pipeline: isolated testers, a coverage ledger that records what was and was not examined, independent verifiers, structured records checked by validators, and reports derived only from verified records.

## Platform terminology

Tool names differ between platforms. This skill uses generic terms.

- **Orchestrator**: the agent running this skill. It plans, delegates, writes every file and runs the validators.
- **Delegate / fresh agent**: start a new agent through the platform's subagent tool (for example the Agent or Task tool). A fresh agent has no memory of earlier work, which is the point. Subagents return text; they do not write files. The orchestrator saves what they return.
- **Fetch**: read a public web page as text (for example WebFetch).
- **Browse**: operate a real browser on a page (for example a built-in browser or a browser extension). Check which browser tools are actually present in the session instead of assuming; some plans and sessions do not include them.
- **Files**: the orchestrator's file tools, used to write logs, records and reports to the run directory.

If no delegation tool exists, the skill still works in sequential mode with weaker independence. See `PREPARATION.md`, section "Sequential mode".

## What this skill is, and is not

It is a usability and experience test from the visitor's side: clarity, navigation, trust, content, design, task completion, mobile and accessibility, judged from evidence.

It is not a security test, an SEO audit, a performance lab, a legal review or an accessibility conformance certification. If the orchestrator notices something outside scope (a possible security weakness, a legal concern), it records one line under "Observations outside scope" in the report and does not probe further. Accessibility results are expert-style checks, never a statement of WCAG conformance.

## Core principles

Each principle exists because a specific thing goes wrong without it.

1. **Zero knowledge.** Testers know only what the page shows. The developer's brief, the source code, earlier findings and other testers' notes are withheld until the phase that needs them. The value of the test is the gap between what the builder knows and what the visitor sees; one leaked fact closes that gap, and a model that has seen the answer cannot un-see it.
2. **Evidence over opinion.** Every claim traces to a numbered log entry (such as `S2-E03`) that says what was seen and where, marked observed or inferred. A finding the owner can check in thirty seconds gets fixed; an impression gets argued with.
3. **Visitors give up.** Each persona has a patience budget. Abandoning a task is a result, not a failure of the test. Simulated testers are too capable by default: they persevere, guess well and read everything. The skill pushes back with budgets, character rules and a leniency check.
4. **Try to disprove before reporting.** A fresh verifier tries to kill every candidate finding: not reproducible, a deliberate trade-off, persona overreach, or an artifact of how the page was fetched. False positives waste the owner's time and discredit the real findings.
5. **Authors never grade their own work.** The agent that found an issue never validates it, and the agent that validated it never gives the final check. Self-review confirms.
6. **Absence of evidence is not quality.** The coverage ledger records what was examined. A category that was not examined is "not assessed", and a category with thin evidence cannot score high. No free tens.
7. **Severity is earned.** Severity comes from impact, frequency and persistence, not from how annoyed a persona sounded. Padding the report with minor items buries the problems that matter. Strengths are recorded too, so fixes do not break what works.
8. **Be honest about the method.** Personas are simulations, not customers. The evidence tier (text, provided, rendered) limits what can be judged and how confident a score can be. Say so once, plainly, and recommend confirming the serious problems with three to five real people.
9. **Do no harm to the live site.** No purchases, no real personal data in forms, no accounts created, no hammering the server. See "Safety rules".

## Modes

| Mode | Use when | Scope | Notes |
|---|---|---|---|
| `full` | A first thorough test | 4 to 6 personas, 3 to 5 tasks each, up to 40 pages, all five lenses, coverage critics, every candidate verified | Default |
| `quick` | A fast read of a site or page | 3 personas, 2 to 3 tasks each, up to 15 pages, heuristics and content lenses, candidates verified in batches | Lower coverage, so scores are more provisional |
| `focus` | One flow, page or worry (checkout, pricing page, signup) | 2 to 4 relevant personas, tasks limited to the target, only relevant lenses | Categories outside the focus are "not assessed" |
| `retest` | The site changed and the owner wants to know if it improved | Same personas and tasks as the prior run, blind to earlier findings, then reconciliation | See `RETEST.md` |
| `deepen` | A prior run missed ground | Targets untested, blocked and thin units from the prior ledger and merges the new evidence into the prior records. Testers stay blind; the orchestrator uses prior findings only to choose targets and to avoid reporting duplicates | See `RETEST.md` |

## Workflow

| Phase | Name | What happens | Read |
|---|---|---|---|
| 0 | Setup | Intake, brief quarantine, capability detection, mode, output folder | `PREPARATION.md` |
| 1 | Reconnaissance | A blind agent maps the site; the orchestrator builds the coverage ledger | `RECONNAISSANCE.md`, `SITE-TYPES.md`, `PERSONAS.md` |
| 2 | Hunting | Persona sessions and lens audits run in isolation; critics find coverage gaps; gaps are filled | `TESTING.md` and the checklist files it points to |
| 3 | Validation | Candidates are merged by root cause; a fresh verifier tries to disprove each one | `VALIDATION-AND-REPORTING.md`, `SCORING.md` |
| 4 | Brief reconciliation | Only now is the developer's brief opened and compared with what visitors understood | `VALIDATION-AND-REPORTING.md` |
| 5 | Structured output | `findings.json` and `scorecard.json` are built and checked by the validators | `VALIDATION-AND-REPORTING.md`, `SCORING.md`, `schemas/` |
| 6 | Independent verification | Fresh agents re-check every confirmed finding from the record alone | `VALIDATION-AND-REPORTING.md` |
| 7 | Reporting | Tables and detail files are generated from the verified records; the orchestrator writes `REPORT.md` | `VALIDATION-AND-REPORTING.md` |

Checklist files used by the lens audits and the personas: `HEURISTICS.md` (usability principles, navigation, visual design), `CONTENT-AND-TRUST.md` (clarity, content quality, trust), `FLOWS-AND-FORMS.md` (forms, checkout, search, error states, onboarding), `MOBILE-AND-PERFORMANCE.md`, `ACCESSIBILITY.md` (WCAG 2.2 A and AA). Every check has a stable ID (for example `CL-01`, `WCAG-2.4.4`) that findings cite.

### Gates

Run the validators from the skill folder's `scripts/` directory. A gate that fails is fixed before moving on; never edit a computed value by hand to make a gate pass.

| After | Command |
|---|---|
| Phase 1 | `python3 scripts/validate_ledger.py <run>/coverage-ledger.json --stage recon` |
| Phase 2 | `python3 scripts/validate_ledger.py <run>/coverage-ledger.json --stage hunt --sessions-dir <run>/sessions` |
| Phase 4 | `python3 scripts/validate_ledger.py <run>/coverage-ledger.json --stage final --sessions-dir <run>/sessions` |
| Phase 5 | `python3 scripts/validate_findings.py <run>/findings.json --ledger <run>/coverage-ledger.json --sessions-dir <run>/sessions` then `python3 scripts/compute_scores.py compute ...` |
| Phase 6 | `python3 scripts/validate_findings.py <run>/findings.json --ledger ... --sessions-dir ... --stage verified`, then recompute scores |
| Phase 7 | `python3 scripts/render_report.py ...` |

All scripts use only the Python standard library. To check the tooling itself: `python3 -m unittest discover -s scripts/tests`.

## Run folder

Default location is `blindspot-runs/<site-slug>/run-<N>/` in the working directory, unless the person names another place. The orchestrator creates it and writes every file.

```
run-<N>/
  run-notes.md            intake answers, decisions, capability detection
  brief.md                the developer brief, if given; sealed until Phase 4
  site-map.md             Phase 1
  coverage-ledger.json    Phase 1, updated through Phase 4
  sessions/               S<n>-<persona>.md and L<n>-<lens>.md logs
  candidates.md           Phase 3: merged candidates and verifier verdicts
  findings.json           Phase 5
  scorecard.json          Phase 5
  evolution.json          retest only
  report-tables.md  FINDINGS-DETAIL.md  NEEDS-VALIDATION.md     generated
  REPORT.md               Phase 7
```

A worked example of the three JSON records and the session logs lives in `examples/bakery/`. Copy its shape.

## Orchestrator rules

These keep isolation intact and the records trustworthy.

- Build every agent's packet from the templates in the phase files. A tester's packet contains the URL, its persona card, its tasks, the evidence tier and the log format, and nothing else. Never paste the brief, another agent's log, or prior findings into a blind agent's packet.
- Launch independent agents in the same turn so they run in parallel.
- Write every returned log and record to disk yourself. Agents that return prose get it saved verbatim; do not tidy away what a persona said.
- After every ledger change, run the validator. After every records change, run the validators.
- Keep `run-notes.md` current: decisions, deviations, tool limits. A returning reader sees what happened from that file and the ledger.
- In a long run, tell the person briefly when a phase finishes and when the plan changes. Do not narrate each tool call.

## Safety rules

The test touches a live website, often one the person does not own.

- Read-only by default. Do not submit forms, complete purchases, create accounts, post comments or subscribe to anything. Walk a flow up to the last reversible step and describe what the next step would do.
- Fake data in forms only if the person owns the site, confirms it is safe, and the form is a low-stakes enquiry. Obviously fake, never anyone's real details.
- Credentials: use only a test account the person supplies for this purpose. Never ask for a personal password. Never write credentials to any file or log.
- Be polite to the server: fetch one page at a time with short pauses, stay within the page cap for the mode, do not crawl past it.
- Respect barriers: do not work around login walls, bot checks or access blocks. Record them as limits and ask the person for screenshots or text instead.
- No probing for security issues, no payload testing, no scraping of personal data. This is a usability test.
- Keep personal data out of logs and reports. Describe what a field asks for, not what someone typed.

## Anti-patterns

1. Letting the brief, the code or earlier findings reach a tester before Phase 4. The test is then worthless and nobody can tell.
2. Personas that succeed because the model is smart. If a low-literacy persona instantly finds a hidden menu, the simulation failed, not the site.
3. Personas that fail on purpose. Manufacturing confusion to have something to report is as bad as leniency. A persona fails only where the page gives it a real reason to.
4. Reporting taste as a defect ("the font feels dated") without a visitor consequence.
5. Reporting an inference as an observation. If the page was only fetched as text, a claim about contrast, layout or keyboard use is at most `needs_validation`.
6. Skipping the verifier because a finding "obviously" holds. The obvious ones are where fetch artifacts hide (cookie walls, bot pages, JavaScript-only content, geo-gated versions).
7. Padding with minor items to look thorough, or splitting one root cause into five findings.
8. Hedged findings ("may potentially confuse some users"). Either there is evidence and a consequence, or it is a `needs_validation` item with an exact question.
9. Scoring a category that was never examined, or giving a high score where evidence is thin.
10. Averaging away a serious problem: a good overall score with a failing trust score still means the site has a trust problem. Say so.
11. Giving the same agent the roles of finder, verifier and reporter.
12. Accusing a site of fraud or bad faith. Describe observable cues ("no postal address, no phone, no registration number visible"), not intent.
13. Writing the report as a list of failures only. What works must be recorded so fixes do not break it.
14. Testing the happy path only. Include a task the site probably cannot support and see whether it fails gracefully.
15. Claiming to have clicked, rendered or seen what was only fetched.

## Report language

Write findings, narrative and the final report in the language the person writes in, unless they ask for another. JSON keys, enumerations, IDs and check IDs always stay in English. To localize the generated tables, export the label dictionary with `python3 scripts/render_report.py --dump-labels`, translate the values and pass the file with `--labels`.

## File index

| File | Purpose |
|---|---|
| `PREPARATION.md` | Phase 0: intake, brief quarantine, evidence tier, isolation, modes, safety setup, sequential mode |
| `RECONNAISSANCE.md` | Phase 1: blind site mapping, task design, building the coverage ledger |
| `PERSONAS.md` | Ten built-in personas, persona cards, selection, custom personas, fidelity rules |
| `TESTING.md` | Phase 2: persona sessions, lens audits, critics, gap filling, log formats, agent prompts |
| `HEURISTICS.md` | Usability principles, navigation and information architecture, visual design checks |
| `CONTENT-AND-TRUST.md` | Clarity, content quality and trust checks |
| `FLOWS-AND-FORMS.md` | Forms, checkout, search, error states, onboarding checks |
| `MOBILE-AND-PERFORMANCE.md` | Small-screen and perceived-performance checks |
| `ACCESSIBILITY.md` | WCAG 2.2 A and AA checks, by what each evidence tier can show |
| `SITE-TYPES.md` | Per site type: visitor goals, default tasks, failure patterns, weight profile |
| `SCORING.md` | Severity model, penalties, caps, evidence tier limits, coverage rule, global score |
| `VALIDATION-AND-REPORTING.md` | Phases 3 to 7: validation, brief reconciliation, records, verification, reporting |
| `RETEST.md` | Blind retests, deepening runs, reconciliation, noise rules |
| `schemas/` | JSON Schemas for the ledger, the findings record and the scorecard |
| `scripts/` | Validators, score calculator, run comparer, report renderer, and their tests |
| `examples/bakery/` | A complete worked run: ledger, session logs, findings, scorecard |
