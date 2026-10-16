# Phase 0: Setup

Setup decides what the run can honestly claim. It fixes the evidence tier, the isolation level, the mode and the safety limits, and it seals the developer's brief so it cannot contaminate the test.

## Contents

1. Intake
2. Sealing the brief
3. Detecting capabilities: evidence tier and isolation
4. Choosing the mode
5. Output folder and run number
6. Safety setup
7. Language
8. Run notes
9. Sequential mode (no delegation tool)

## 1. Intake

Ask once, in one short message. Do not interview. Everything except the URL has a default.

Questions, in this order:

1. **Which site?** URL (required). More than one if the person wants a comparison or a specific flow tested.
2. **Who is it for, and what should it get people to do?** (for example sell cakes, collect enquiries, onboard trial users). Optional. If unanswered, the blind reconnaissance infers both from the site, and failing to infer them is itself a finding.
3. **What should customers be able to do?** Optional. Customer goals such as "find the price", "contact someone", "check delivery to my area". These become tasks. They must be goals, never feature names.
4. **Is there a developer brief?** What the site is meant to do and communicate. Optional. If it exists it is sealed until Phase 4 (see section 2).
5. **Anything to focus on or avoid?** A flow, a page, a worry, or areas that are off limits.
6. **Comparable sites?** Optional, up to three, used only to establish what conventions visitors are used to.

Opening line example: "I'll test this as first-time visitors who know nothing about the site, then report what they understood and where they got stuck. Anything you can tell me about the audience, the goal and what customers should be able to do helps; if you have a brief of what the site is meant to communicate, hand it over and I'll keep it sealed until the end."

If the person says "just go", proceed blind with defaults: infer audience and goal, use the site type's default tasks, mode `full` (or `quick` if the request sounds casual or the site is a single page).

## 2. Sealing the brief

The brief is the single most contaminating input. Handle it like this.

- If it arrives as an attached file, copy it into the run folder as `brief.md` (or its original name) without reading it. A file copy does not put its contents in context.
- If it arrives pasted into the chat, it is already visible. Save it verbatim to `brief.md`, say "stored, sealed until after testing", and do not use it. When writing task lists, persona choices or agent packets, work only from the person's customer goals and the blind reconnaissance.
- Set `run.brief_present: true` and `run.brief_opened: false` in the ledger. Phase 4 flips the second flag.
- Never put the brief, a summary of it, or a hint from it into any agent packet before Phase 4.

If the person gives goals in the middle of a sentence about features ("the site has a quote calculator they should use"), keep only the goal ("work out roughly what it would cost") and drop the feature name from anything a tester sees.

## 3. Detecting capabilities: evidence tier and isolation

Look at the tools actually present in the session. Do not assume and do not promise what is not there.

### Evidence tier

| Tier | When | What it can show |
|---|---|---|
| `rendered` | Browser tools are present and can open the site | Layout, visuals, interaction, keyboard use, focus, responsive behaviour, real clicking |
| `provided` | The person supplies screenshots, saved HTML or recordings | What is in the material; no interaction beyond it |
| `text` | Only a page fetch tool is present | Page text, structure, labels, links, form fields as described in the text; no rendering, no interaction |

Rules:

- Use the best tier available for the primary flows. Record that tier as `run.evidence_tier`. Individual evidence items record their own tier.
- Do not mix without saying so. If only some pages could be browsed, note it in `run-notes.md`.
- If neither a browser nor a fetch tool can reach the site (login wall, bot block, no network), say so plainly and ask the person for screenshots or the page text. Do not pretend.
- Tell the person in one line which tier applies and what it limits. Example: "I can read the pages but not render them, so design, mobile and keyboard checks will be marked not assessed rather than guessed."
- A tier that cannot show something caps what the scorecard can claim. The caps are in `SCORING.md`.

If a browser tool is available but the person's plan or session requires enabling it first, say what is missing and continue with the best tier that works now. Offer to redo the rendered checks later.

### Isolation

| Level | When |
|---|---|
| `full` | A delegation tool is present, so every role (recon agent, each persona tester, each lens auditor, critics, verifiers) runs in a fresh agent |
| `degraded` | No delegation tool; roles run one after another in the same context (see section 9) |

Record it as `run.isolation`. It limits confidence: the validators refuse `high` confidence findings under degraded isolation, and the score calculator lowers category confidence.

## 4. Choosing the mode

Pick from the request, then confirm in the opening reply.

| Request sounds like | Mode |
|---|---|
| "test my site", "full review", "audit" | `full` |
| "quick look", "first impressions", "is this clear?", a single landing page | `quick` |
| "check my checkout", "just the pricing page" | `focus` |
| "I changed things, did it improve?", "run it again" | `retest` |
| "go deeper", "what did you miss?", "cover the rest" | `deepen` |

Caps by mode:

| | full | quick | focus | retest | deepen |
|---|---|---|---|---|---|
| Pages fetched or browsed (recon + testing) | 40 | 15 | 15 | as prior | 40 |
| Personas | 4 to 6 (default 5) | 3 | 2 to 4 | as prior | add new ones |
| Tasks per persona | 3 to 5 | 2 to 3 | 2 to 3 on the target | as prior | 2 to 4 |
| Lens audits | all five | heuristics, content_trust | relevant only | as prior | missing or thin lenses |
| Coverage critics | 1 or 2 | 0 or 1 | 0 or 1 | 1 | 1 |
| Gap-filling rounds (Wave C) | up to 2 | up to 1 | up to 1 | up to 1 | up to 2 |

If a plan would launch more than about twenty agents, state it in two or three lines before launching (personas, lenses, estimated agents), then continue unless the person asked to approve first.

## 5. Output folder and run number

1. The root is `blindspot-runs/<site-slug>/` in the working directory, unless the person names a place. The slug is the lowercase host name, for example `brightleaf-bakery.example`.
2. Look for existing `run-N` folders. The new run is the highest N plus one, or 1.
3. If a prior run exists and the mode is not `retest` or `deepen`, still make a new run, and mention the prior run. Never overwrite a run.
4. For `retest` and `deepen`, find the prior run's `coverage-ledger.json`, `findings.json` and `scorecard.json`. If they are not on disk, ask the person to attach them. Without them a retest cannot be reconciled; fall back to a fresh `full` run and say so.
5. Create the folder with a `sessions/` subfolder. Create `run-notes.md` (section 8).

## 6. Safety setup

Read "Safety rules" in `SKILL.md` and apply it. Setup-specific steps:

- Write the safety stance into `run-notes.md`: no form submissions, no purchases, no accounts, fake data only with the owner's explicit permission.
- If the person wants an authenticated area tested, ask for a test account created for this purpose. Note that credentials are never written to files. Use them only in the browser session.
- If the site is not the person's own, say once that the test is read-only and limited to public pages.
- Set the page cap for the mode and pause between fetches.

## 7. Language

Set `run.language` to the language tag of the person's own words (for example `en`, `pt`). Free text in records and reports is written in that language. Keys, enums, IDs and check IDs stay English.

Detect the language from what the person wrote themselves, not from pasted material. A question in Portuguese about an English site is a Portuguese run.

## 8. Run notes

Create `run-notes.md` with these headings and keep it current:

```
# Run notes

## Request
(the person's words, one or two lines)

## Intake answers
URL(s): ...
Audience and goal (stated): ...
Customer goals (stated): ...
Brief: none | sealed in brief.md
Focus or exclusions: ...
Comparable sites: ...

## Capabilities
Evidence tier: rendered | provided | text   (and why)
Isolation: full | degraded   (and why)
Browser tools present: ...
Delegation tool present: ...

## Mode and caps
Mode: ...   Pages cap: ...   Personas: ...

## Safety
(one or two lines)

## Decisions and deviations
(timestamped lines added as the run goes)
```

## 9. Sequential mode (no delegation tool)

Without fresh agents the roles cannot be isolated, but the discipline can still be mostly kept. Use this protocol and mark `run.isolation: degraded`.

1. Run the roles strictly one at a time, in phase order. Write each role's complete output to its file before starting the next.
2. Before starting a role, re-read only that role's packet (the template with its inputs) from the files, not the other roles' logs. Treat anything you remember from earlier roles about what the site "really" does as contaminated and set it aside. For a persona, answer only from what that persona would have seen at that step.
3. Run persona sessions in this order: first-timer-type personas first, assistive and constrained personas after. Do not let a later persona benefit from the way an earlier one found the path.
4. The verifier role (Phase 3) starts from the candidate record only: re-fetch the evidence, do not reread the session narrative before forming a view.
5. Do not open the brief before Phase 4. In sequential mode, if the brief was pasted into the chat, say in `run-notes.md` that the orchestrator saw it and name the safeguards used.
6. Expect more leniency, more agreement and fewer rejections than a real isolated run. Say so in the report's method note: independence was reduced, so confidence is capped at medium and the strongest findings are those backed by evidence the owner can check directly.
7. Suggest to the person that critical findings be re-checked in an environment with delegation, or by real users.
