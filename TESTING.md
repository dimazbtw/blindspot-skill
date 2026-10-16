# Phase 2: Hunting

Hunting is where evidence is gathered. Two kinds of isolated agents work from the ledger: **persona testers**, who experience the site as a visitor, and **lens auditors**, who sweep it against a checklist. Coverage critics then look for what was missed, and further rounds fill the gaps. Nothing in this phase decides what is a real problem. That is Phase 3's job.

## Contents

1. Waves and isolation
2. Packet rules
3. Wave A: persona sessions
4. Persona tester prompt
5. Wave B: lens audits
6. Lens auditor prompt
7. Coverage critics
8. Wave C: gap filling and stop rules
9. After every wave: updating the ledger
10. Tier-specific procedures
11. Log writing rules

## 1. Waves and isolation

| Wave | Agents | Work from | Produces |
|---|---|---|---|
| A | One persona tester per persona | The persona's units: first impression, tasks, exploration | `S<n>-<persona>.md` logs |
| B | One lens auditor per lens unit (or page group) | The lens's units and its checklist file | `L<n>-<lens>.md` logs |
| Critics | One or two fresh agents | Ledger, site map, logs | A gap and leniency report (not findings) |
| C | New testers and auditors on new units | The gaps the critics found | More logs |

Waves A and B are independent and run in parallel. They do not see each other's work. Overlap between them is useful: when two kinds of agent reach the same problem independently, that is corroboration.

Sequential mode runs the same roles in order with the discipline in `PREPARATION.md`, section 9.

## 2. Packet rules

What an agent receives decides what it can find. Build every packet from the templates below.

**Always give**: the URL(s); the evidence tier and what it allows; the persona card without its **Reveals** line, or the checklist for the lens; the assigned unit list (task goals in customer words, or page groups); the log format; the safety rules.

**Never give**: the developer's brief or anything derived from it; the site map's findings about problems or its inferred audience and goal; any other agent's log; prior findings (except in `deepen`, where prior findings go only to the orchestrator); the optimal step counts or shortest paths; the ledger's outcome fields.

Why the site map is withheld from testers: it contains the shortest paths, and a tester that knows the path no longer experiences the site. The map is for the orchestrator.

## 3. Wave A: persona sessions

One fresh agent per persona. The agent plays only that persona and returns one session log. Protocol:

### 3.1 Adopt the persona

Start the log with a first-person restatement of who the persona is, what they want and how they read. This anchors the voice and makes drift visible.

### 3.2 Five-second test (first_impression unit)

Look at the main landing page the way someone glancing for five seconds would, then answer without looking further.

What counts as "seen":

- `text` tier: the page title, the first heading, the subheading or first paragraph (about sixty words), the primary navigation labels, and the first call-to-action label. Images are not seen unless they have a text alternative; say so.
- `rendered` or `provided` tier: what is visible in the first screen without scrolling, at the persona's usual screen size, plus what the eye goes to first.

Answers, in the persona's words:

1. What is this site, and what do they offer?
2. Who is it for?
3. What am I supposed to do here?
4. Gut rating from 1 to 5 and whether I would keep going (yes, maybe, no).

For each of the first three, record how clear it was to the persona: `yes` (a confident, specific answer), `partly` (vague or hedged), `no` (cannot answer). This is the persona's own clarity, not correctness. Whether the answer matches what the builder intended is judged in Phase 4.

### 3.3 Task attempts (task units)

For each assigned goal, start from the persona's entry point (normally the home page) and work toward the goal.

Before every action, in a line or two:

- **First click** (the first action only): what the persona picks and why. The orchestrator later judges whether it was on a path to the goal.
- **Cognitive walkthrough**, the four questions at each step: (1) Will the persona try to do the thing this step needs? (2) Will they notice the right control is there? (3) Will they connect that control with what they want? (4) After using it, will they see they are getting closer?
- **Information scent**: how strongly does the chosen label or link suggest it leads to the goal? Rate 0 (no clue), 1 (maybe), 2 (strong clue).

Counting steps: a step is one page load or one deliberate action that changes what is on screen (opening a menu counts; scrolling does not). Count from the starting page. Compare with the persona's patience budget after every step.

Log an entry at every moment of decision, hesitation, confusion, surprise or outcome, and at every step that changes the page. Routine confident steps can be one line.

Stop when:

- the goal is met, or the persona believes it is met;
- the patience budget or give-up rule is reached;
- a barrier outside the persona's control stops progress (a broken page, an error, a login wall).

Outcomes:

| Outcome | Meaning |
|---|---|
| `completed` | Reached the goal without notable trouble |
| `completed_with_difficulty` | Reached the goal, but with detours, backtracking, uncertainty or well over the usual number of steps |
| `completed_incorrectly` | Believes the goal is met but it is not: wrong page, wrong action, wrong understanding |
| `abandoned` | Gave up: budget spent, give-up rule fired, or the site does not offer what was sought |
| `blocked` | Could not proceed for a reason outside the persona's choice: error, broken link, wall |

For flows, reaching the last reversible step with a correct understanding of what the next step would do counts as completing the goal. Do not submit.

Use `abandoned` when the information simply is not on the site, and say so in the log. A site that cannot answer a basic question is a finding.

### 3.4 Exploration (exploration unit)

When assigned, browse the named areas without a goal for up to eight steps, driven by what would catch this persona's interest. Log what draws attention, what is confusing, what builds or erodes trust.

### 3.5 Persona verdict

End with the persona's summary: tasks and outcomes, whether they would return, whether they would recommend the site (yes, maybe, no), and one line in their voice.

### 3.6 Session log format

File name: `S<n>-<persona-id>.md`. Header, entries, summary.

```
# Session S1: First-time visitor (first-timer)

- Persona: first-timer
- Wave: A
- Evidence tier: text
- Patience budget: 10 steps per task, gives up after two dead ends in a row
- Brief access: none
- Units: U-001, U-004, U-005

### S1-E01 | five-second | https://example.test/
- **Action:** ...
- **Seen:** ...
- **What is it:** ...
- **Who is it for:** ...
- **Main action:** ...
- **Gut rating:** 3 of 5. **Would continue:** maybe.
- **Reaction:** hesitant
- **Thought:** "..."

### S1-E03 | task U-004 | step 3 | https://example.test/page
- **Action:** ...
- **Expected:** ...
- **Observed:** ...
- **Reaction:** confused
- **Thought:** "..."
- **Outcome:** completed with difficulty (8 steps)      <- only on the entry that ends the task

## Session summary
- Tasks: U-004 completed with difficulty, U-005 abandoned.
- Would return: maybe. Would recommend: no.
```

Rules for entries:

- The heading line is exact: `### <ID> | <type> | <detail> | <URL>`, with IDs `S<session>-E<two or more digits>` in order. Findings cite these IDs and the validator looks for them.
- `type` is `five-second`, `task U-nnn | step n`, or `explore | step n`.
- `Reaction` is one of `confident`, `satisfied`, `neutral`, `hesitant`, `confused`, `frustrated`, `delighted`, `gave_up`.
- `Seen`, `Observed` and `Action` are facts about the page. `Thought` is the persona's voice. Keep them apart.
- Quote labels and short phrases exactly, in quotation marks. Never copy paragraphs of the site's text; a label or a sentence is enough (200 characters at most).

## 4. Persona tester prompt

```
You are playing one simulated visitor to test a website. You are not an expert or an
auditor. You are this person, and you know only what this person would know.

PERSONA
{persona card, without the "Reveals" line}

SITE: {url}
EVIDENCE TIER: {tier}
{tier line: "You can read page text only; you cannot see images, layout or colour, and you
cannot click. Say what you could not see rather than guessing." OR "You can browse the site
with a real browser at {viewport}." OR "You have the supplied screenshots/HTML only."}

You have never seen this site. You have no brief, no site map, no notes from anyone else.
Do not use anything except what the pages show. Do not search elsewhere. Do not use tricks
your persona would not use (find on page, guessing URLs, view source).

YOUR WORK
1. Five-second test of {landing_url} (unit {unit_id}).
2. These goals, one at a time (units {task_units}). Start each from {entry_point}:
   {task goals in customer words}
3. {exploration instruction, if assigned}
4. A persona verdict.
Follow the protocol in the format below. Count steps. Stop when your patience budget or
give-up rule is reached; abandoning is a valid, useful result. Do not finish a task just
to see how it ends.

SAFETY
Read-only. Do not submit forms, make purchases, create accounts, sign up, or enter real
personal details. Walk a flow up to its last reversible step and say what the next step
would do. If you hit a login wall, bot check or error, log it and report the outcome as
blocked. Fetch one page at a time.

LOG FORMAT (return exactly this, in markdown)
{the session log format from TESTING.md section 3.6, with this session's ID and header}

Entry IDs run S{n}-E01, S{n}-E02 ... in order. Log every decision, hesitation, confusion
and outcome. Every statement about the page is something you saw, with the URL. Quote
labels exactly and briefly. Think aloud in your persona's own words.
```

## 5. Wave B: lens audits

A lens auditor sweeps assigned pages against one checklist. It has no persona; it is a careful reviewer who has also never seen the site. Its value is systematic coverage of things personas may not trip over.

| Lens | Checklist file | Check IDs |
|---|---|---|
| `heuristics` | `HEURISTICS.md` | `NN-1` to `NN-10`, `NV-01` to `NV-12`, `DS-01` to `DS-12` |
| `content_trust` | `CONTENT-AND-TRUST.md` | `CL-01` to `CL-12`, `CT-01` to `CT-13`, `TR-01` to `TR-14` |
| `flows_forms` | `FLOWS-AND-FORMS.md` | `FL-01` to `FL-26` |
| `mobile_performance` | `MOBILE-AND-PERFORMANCE.md` | `MB-01` to `MB-16` |
| `accessibility` | `ACCESSIBILITY.md` | `WCAG-x.y.z` |

Give each auditor its checklist file in full.

Check outcomes: `pass`, `fail`, `partial`, `not_assessable` (the tier cannot show it) and `n/a` (the thing does not exist on these pages).

What to log:

- an entry for every `fail` and `partial`, with the evidence;
- an entry for a `pass` that is notable, meaning a strength worth preserving or evidence for a decision elsewhere;
- everything else in the lens summary, compactly: IDs passed without notes, IDs `n/a`, IDs `not_assessable` with the reason.

An auditor does not pad to look thorough, and does not mark a check `fail` without something it saw. If it only suspects, the outcome is `not_assessable` with the question stated.

Entry format, file `L<n>-<lens>.md`:

```
# Lens session L2: Content and trust

- Lens: content_trust
- Wave: B
- Evidence tier: text
- Pages swept: home, collections, ...
- Brief access: none
- Units: U-015

### L2-E01 | CL-01 | fail | https://example.test/
- **Check:** (the checklist's wording)
- **Observed:** (what was seen)
- **Verdict:** fail
- **Note:** (optional: who this affects, what task)

## Lens summary
- Passed without notes: CL-02, CL-03, ...
- Not applicable: TR-06
- Not assessable at this tier: DS-01 (needs rendering), ...
```

## 6. Lens auditor prompt

```
You are reviewing a website against a checklist, as a careful outsider who has never seen
it and has been told nothing about it.

SITE: {url}
EVIDENCE TIER: {tier}   (what it can and cannot show: {tier line})
PAGES TO SWEEP: {page group}   (unit {unit_id})
LENS: {lens name}

CHECKLIST
{full text of the checklist file}

For each check, decide: pass, fail, partial, not_assessable or n/a. Rules:
- Judge only from what you saw on these pages. Cite the URL and where on the page.
- fail and partial need a concrete observation. If you only suspect something, the outcome
  is not_assessable and you state the exact question.
- Do not mark a check fail because it is missing a feature the site never promised.
  Judge against what a visitor would expect of this kind of page.
- The checklist is a floor. If you see a clear visitor problem it does not name, log it
  as an entry with the check ID "XX-00" and say what it is.
- Read-only. Do not submit forms or create accounts. One page at a time.

Return the lens log in exactly this format: {lens log format from TESTING.md section 5}.
Entry IDs run L{n}-E01, L{n}-E02 ... Log every fail and partial and every notable pass;
put the rest in the lens summary.
```

Entries with the placeholder ID `XX-00` are reviewed by the orchestrator in Phase 3. If the observation stands, it becomes a candidate without a check reference.

## 7. Coverage critics

After Waves A and B, the orchestrator updates the ledger (section 9) and delegates one or two critics, who judge the run's coverage and its realism, not the site.

Critics receive: the ledger, the site map, and the session logs. They do not produce findings.

```
You are auditing a website test for gaps and for simulation realism. Do not judge the site.

You have: the coverage ledger (what was planned and what was done), the site map, the
persona cards, and all session logs.

Report, in ranked order, at most ten items in each of these:

1. COVERAGE GAPS. Pages, templates, flows, states, personas, tasks or lenses that matter
   but are untested, skipped or thin. For each: the unit to add (type, target, persona or
   lens, priority) and why it matters.
2. THIN CATEGORIES. Categories (clarity, navigation, trust, content, design, flows, mobile,
   accessibility) where evidence is weak because few units covered them.
3. LENIENCY FLAGS. Sessions where a persona behaved more capably than its card allows:
   found something hidden at once, understood a label it could not, finished a task that its
   own log shows was confusing. Cite the entry IDs.
4. HARSHNESS FLAGS. Sessions where a persona failed without a visible cause on the page, or
   exaggerated a reaction. Cite entry IDs.
5. REDUNDANCY. Sessions that retraced the same path and added no new evidence.

Do not suggest fixes for the site. Do not propose findings.
```

The orchestrator reads the flags, sends flagged sessions back for correction when the flag is specific and justified, and turns gap suggestions into new units.

## 8. Wave C: gap filling and stop rules

1. For each justified gap, add a unit to the ledger (new ID, `untested`) and run a fresh agent on it with the same templates. Sessions continue the numbering.
2. Re-run the critics only if Wave C changed the plan materially.
3. Stop when any of these holds:
   - every high-priority unit is resolved (tested, partial, blocked or skipped with a reason) and the last round surfaced no moderate-or-worse issue that earlier rounds had not already seen;
   - the round cap for the mode is reached;
   - the page cap is reached.
4. A unit that cannot be done (blocked by a wall, an error, the tier) is marked `blocked` or `skipped` with the reason. Do not leave it `untested`.

## 9. After every wave: updating the ledger

The orchestrator does this itself, never the agents.

1. Save each returned log as `sessions/S<n>-<persona-id>.md` or `sessions/L<n>-<lens>.md`. Session IDs are sequential per prefix across the whole run.
2. For each unit the session covered, set `status` (`tested`, `partial`, `blocked`, `skipped`), `sessions`, and a `reason` for anything not `tested`.
3. For task units, copy `outcome` and `steps_taken` from the log. Set `first_click_correct` by comparing the first click in the log with the shortest paths in `site-map.md` (true if the click led along any valid route to the goal, false if not, null if there was no click).
4. For first-impression units, copy the three clarity values, the gut rating and `would_continue` into `five_second`.
5. Run `python3 scripts/validate_ledger.py <run>/coverage-ledger.json --stage hunt --sessions-dir <run>/sessions` after Wave C, and the same command with the earlier stage after earlier waves if you want an early check. Fix errors.

## 10. Tier-specific procedures

### text tier

- The only evidence is page text and structure as the fetch tool returns it. Content that loads through JavaScript, behind cookie walls or bot checks may be missing or different from what visitors see. Note every page where that is suspected, and treat claims about those pages with care (Phase 3's environment-artifact test checks this).
- Judge copy, labels, structure, links, form fields (as described), policies, contact routes and content completeness.
- Do not judge colour, layout, spacing, images, animation, focus, keyboard use, responsive behaviour or loading. Mark those checks `not_assessable`.
- Viewport units are `skipped`.

### rendered tier

- Browse with a real browser. Default screen sizes: desktop 1440 by 900, tablet 768 by 1024, mobile 390 by 844. Use 320 wide for reflow checks.
- For `keyboard-low-vision` and the accessibility lens: operate with Tab, Shift+Tab, Enter, Space and Escape; check that focus is visible and ordered; zoom to 200 and 400 percent and check for horizontal scrolling and clipped content.
- Look for what appears on hover or focus, pop-ups that cover content on arrival, and sticky elements that eat the viewport.
- Measure only what the tools actually measure; do not estimate load times by feel, and say when performance claims need a proper tool (Lighthouse, PageSpeed Insights or the browser's performance tools).
- Evidence entries record the viewport used.

### provided tier

- Evidence is the supplied screenshots, saved HTML or recordings. Treat each as what it shows and nothing more. A screenshot shows one state at one size.
- Say which screens and sizes were provided. Do not extrapolate to other sizes or states.
- Mark checks that need interaction `not_assessable`.

## 11. Log writing rules

- IDs sequential and unique; heading lines exactly as specified.
- Short exact quotations only. No copying of paragraphs; excerpts in findings are capped at 200 characters.
- No personal data. If a page shows someone's personal details, describe the kind of data, not the data.
- No credentials, ever.
- No claim of having clicked, rendered or seen what was only fetched.
- Every statement about the page is observed (with a URL) or marked as inferred.
