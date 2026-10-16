# Retest and deepen runs

A first run answers "what do visitors struggle with?". Later runs answer two different questions: "did my changes help?" (retest) and "what did the first run not look at?" (deepen). They are built differently because they must not contaminate each other's evidence.

## Contents

1. The two modes
2. Preconditions
3. Retest procedure
4. Matching findings across runs
5. Comparing runs and the noise rules
6. Reporting a retest
7. Deepen procedure
8. Pitfalls

## 1. The two modes

| | `retest` | `deepen` |
|---|---|---|
| Question | Did the site improve? | What was missed? |
| Site state | Changed since the prior run | The same as the prior run |
| Testers | Blind to prior findings, scores and the change list | Blind to prior findings and scores |
| Personas and tasks | Same as the prior run, so results are comparable | New: targets the prior run's gaps |
| Output | New run with its own records, plus `evolution.json` | New run that merges the prior records with new evidence |
| Scores | Compared with noise thresholds | Recomputed over the merged evidence; not a before-and-after |

If the site changed and the person also wants more coverage, do a retest first, then a deepen run on the result. Mixing the two makes any movement uninterpretable.

## 2. Preconditions

- A prior run folder with `coverage-ledger.json`, `findings.json`, `scorecard.json` and `sessions/`. If any is missing, ask the person to attach them. Without them a retest cannot be reconciled; fall back to a fresh `full` run, and say it is not a retest.
- The prior records must have passed their gates (verified stage). Do not retest against a half-finished run.
- Retest: ask the person what changed (a short list, or "I don't remember"). Treat the answer as sealed material like a brief (see below). If the site did not change at all, say a retest would measure only simulation noise, and offer a deepen run instead.

## 3. Retest procedure

1. **Setup** (`PREPARATION.md`): mode `retest`, a new run folder (`run-N+1`), `prior_run` set to the previous number. The same evidence tier as before if possible; if it differs, say the comparison will be marked not strictly comparable.
2. **Seal the change list.** Save the owner's description as `brief.md` under a heading "Changes since run N" and set `brief_present` to true. It is opened only in Phase 4, like a brief. It must not reach any tester, any verifier in Phase 3, or the reconnaissance agent.
3. **Fresh blind reconnaissance** (`RECONNAISSANCE.md`). The site changed, so the map, the shortest paths and the optimal step counts may have changed. Do not reuse the prior `site-map.md` for this.
4. **Build the ledger by reusing the prior plan.**
   - Same personas (same ids, same cards).
   - Same task goals, copied exactly from the prior ledger so that outcomes are comparable. Update `optimal_steps` from the new map.
   - Same lens units and viewport units, same priorities.
   - Add units for pages or flows that are new since the prior run, noted `new since run N`. Do not drop a prior unit because it seems fixed; a retest has to look where the problems were.
   - Reset every status to `untested`; clear sessions, outcomes and measurements.
5. **Blind pass** (Phases 2 and 3 as in `TESTING.md` and `VALIDATION-AND-REPORTING.md`). Tester and verifier packets contain no prior findings, no prior scores and no change list.
6. **Matching** (section 4) against the prior confirmed findings.
7. **Regression checks.** For each prior confirmed finding that no current candidate matches, decide whether the retest actually looked where it lived:
   - If a retest task covering the same goal ran and was completed without difficulty, or a retest lens unit examined the same check on the same page and passed, that is positive evidence of resolution. Note the log entry (`candidates.md`, "Resolution evidence": prior id, retest log ref).
   - If neither exists, add a targeted unit and run it as gap filling: a lens unit with `notes: "regression check for run-N:Pk"`, whose packet names only the page and the check IDs (from the prior finding's `heuristic_refs`), never the prior finding's text or severity. For a task-based problem, add the same task with the same persona.
   - If no unit can cover it (the page is gone, the flow is unreachable, the tier is lower than before), the finding is **not re-examined**. A page that no longer exists is not proof that the problem was fixed, because the content may have moved.
8. **Phases 4 to 7** as usual, including the sealed change list in Phase 4: it can explain why a problem persists ("the owner changed the label, but the label is still unclear") and is never used to excuse one.
9. **Compare** (section 5), then report (section 6).

## 4. Matching findings across runs

The orchestrator, not the testers, matches findings, after validation. A current finding that is the same problem as a prior one carries `persists_from: "run-<N>:P<k>"`.

- **Same root cause** means the same element or page area and the same missing or wrong thing. Different words, a different persona or a different severity do not matter.
- **Test**: would the prior finding's recommended change also fix this one? If yes, link them. If the page changed but the problem moved with it, link them.
- Do not match on category alone. Two clarity problems on different pages are two problems.
- A partly fixed problem persists, with the current severity. The comparison reports the severity change (improved, same, worsened).
- When in doubt, do not link. The result is a prior item listed as resolved (if there is positive evidence) or not re-examined, and a current item listed as new. Both are visible to the reader, and a wrong link would hide a regression.
- Only confirmed findings are matched. Needs-validation and rejected items are not part of the comparison.

## 5. Comparing runs and the noise rules

List the prior ids that the retest did not re-examine: every prior confirmed finding that has neither a `persists_from` link nor positive resolution evidence. Then:

```
python3 scripts/compare_runs.py \
  --prior-scorecard <prior-run>/scorecard.json --prior-findings <prior-run>/findings.json \
  --current-scorecard <run>/scorecard.json --current-findings <run>/findings.json \
  --not-retested P3,P5 --out <run>/evolution.json
```

The script derives, from the records:

- **persisting**: current findings with a valid `persists_from`, with the severity change;
- **resolved**: prior confirmed findings that no current finding points to and that the orchestrator did not list as not re-examined;
- **not re-examined**: the ones listed in `--not-retested`, never reported as resolved;
- **new**: current confirmed findings without a valid link.

Score comparison rules, because simulated testers vary from run to run:

- A category is "improved" or "regressed" only if it moves by at least 0.7 points. The overall score needs at least 0.5. Anything smaller is "within noise" and is not reported as a change.
- The comparison is flagged as not strictly comparable when the evidence tier or the weight profile changed, and carries a warning when isolation changed. Do not present score movements from such a comparison as the site's doing.
- Categories not assessed in either run are "not comparable".
- Findings are stronger evidence than scores. A resolved moderate finding, with a retest log showing the task now works, says more than a 0.4 movement in a score.
- Task metrics and first-impression metrics come with counts. With a handful of tasks, one different outcome moves a rate a lot. Say "8 of 9 tasks completed, against 6 of 9", not only "89 percent against 67".
- If very little changed on the site, expect no movement. Report it as no measurable change, not as a failure of the changes.
- A regression is a category that moved down past the threshold, or a new confirmed moderate-or-worse finding in an area the owner changed. Name it plainly.

## 6. Reporting a retest

`render_report.py` adds the evolution tables when given `--evolution`. In `REPORT.md`, replace "what to fix first" with:

1. **Result in brief**: did it improve? One to three sentences with the overall movement and the verdict (improved, within noise, regressed, or not comparable), and the number of resolved, persisting, new and not re-examined problems.
2. **What got better**: resolved findings, each with the retest evidence (what the page now shows or the task that now works).
3. **What persists**: persisting findings with the severity change, and what the owner changed (from the sealed list) if it did not solve the problem.
4. **What is new**: new findings, including any caused by the changes.
5. **Not re-examined**: the prior findings the retest could not check, and why.
6. **Scores and metrics**: the evolution table, with the noise thresholds stated once.
7. **Caveats**: the same personas and tasks were used; simulated testers vary; a different tier or isolation limits the comparison.
8. **Next steps**: the top remaining problems; whether another retest is worth it and after what changes.

The rest of `REPORT.md` (strengths, pros and cons, open questions, coverage, method note) is written as usual for the current run.

## 7. Deepen procedure

A deepen run adds evidence to the same state of the site. It is additive: it never discards the prior run's records.

1. **Setup**: mode `deepen`, new folder `run-N+1`, `prior_run` set. Copy the prior `coverage-ledger.json`, `findings.json`, `sessions/` and `site-map.md` into the new folder. Prior units keep their statuses, sessions and measurements. Prior findings keep their ids, verdicts and verification records.
2. **Choose targets** from the prior ledger and records:
   - units that were `untested`, `blocked`, `partial` or `skipped` with a reason that no longer applies (for example the person has now supplied screenshots or a rendered tier is now available);
   - categories with low confidence or low coverage in the prior scorecard;
   - the coverage critic's unaddressed gaps;
   - templates in the page inventory that no unit touched;
   - personas not yet used, chosen to add a perspective (`PERSONAS.md`).
3. **Add new units** for those targets (new `U-` ids, `untested`) and run them with the usual templates. New sessions continue the numbering after the highest existing `S` and `L` ids. Testers stay blind: the orchestrator uses the prior findings to choose targets and to avoid duplicate reporting at merge time, but never gives them to testers.
4. **Validate** new candidates as usual (Phase 3). A candidate that matches an existing finding is added to that finding's evidence and `found_by` (and may raise its confidence); it is not reported twice.
5. **Brief**: if the prior run had a brief, it is already open. A new brief is sealed until Phase 4 as usual.
6. **Records**: new findings take the next `P` ids. Re-verify only new or changed findings (Phase 6). Recompute `scorecard.json` over the merged ledger and findings, with the run block saying `mode: deepen`.
7. **Report**: say what was added, what was found, and how the scores moved because of added coverage (a category that was "not assessed" may now have a score; a higher coverage may raise confidence). State that the movement reflects more evidence, not a change to the site. Do not run `compare_runs.py` on a deepen run as a before-and-after, and do not call the movement an improvement.

## 8. Pitfalls

1. Telling testers what changed, or what was found last time. They will confirm it, and a retest becomes a checklist run.
2. Reusing the prior site map after the site changed. The shortest paths and first-click judgments will be wrong.
3. Changing personas or task wording between runs and then comparing scores.
4. Declaring a finding resolved because nothing matched it. Positive evidence, or "not re-examined".
5. Reporting a 0.3 movement as progress.
6. Comparing runs with different evidence tiers as if they were equal: a run that could not see rendering will miss problems the earlier one found.
7. Linking findings by category instead of by root cause, which hides regressions.
8. Treating a deepen run as a retest, or the reverse.
