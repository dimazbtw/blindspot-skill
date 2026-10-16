# Phase 1: Reconnaissance

Reconnaissance produces two things: a blind map of the site (`site-map.md`) and the coverage ledger that plans the rest of the run. It is blind on purpose. The mapper sees the site the way a visitor would, so what it infers about the site's purpose is itself evidence.

## Contents

1. Principles
2. The reconnaissance agent
3. Reconnaissance prompt
4. Required output: site-map.md
5. Orchestrator synthesis: building the ledger
6. Task design
7. Choosing personas
8. Unit rules and priorities
9. Gate

## 1. Principles

- The mapper receives the URL, the page cap, the evidence tier and optional comparable sites. It does not receive the brief, the person's description of what the site "is for", or any feature names. If the site's purpose cannot be inferred from the site, that is a clarity finding in the making.
- Mapping is read-only and polite. Fetch sequentially, stay within the cap, never submit anything.
- Observed facts and inferences are kept apart in the map, because the ledger and later phases lean on the difference.

## 2. The reconnaissance agent

Delegate one fresh agent. In sequential mode, run it first and write its output to `site-map.md` before anything else (see `PREPARATION.md`, section 9).

Packet contents: the prompt below with its placeholders filled; the site-type list from `SITE-TYPES.md` (names and one-line descriptions only); nothing else.

## 3. Reconnaissance prompt

```
You are mapping a website as an outsider would, before any testing. You know nothing
about the people who built it or what they intended. Report only what the pages show.

Site: {url}
Evidence tier: {tier}   (text = you can read page text only; rendered = you can browse)
Page cap: {cap}   Comparable sites for convention checks (may be empty): {comparables}
Site types to choose from: {site_type_list}

Work read-only. Do not submit forms, purchase, create accounts or log in. Fetch one page
at a time. Stop at the page cap.

Do this:
1. Open the home page. Record the title, main heading, subheading, primary navigation labels
   and the first call to action exactly as they appear.
2. Collect every link in the primary navigation, the footer and any secondary navigation.
3. Read /sitemap.xml and /robots.txt if they exist (read-only), to learn page structure.
4. Open one representative page per distinct page template (home, listing, detail, pricing,
   contact, FAQ, about, legal, account entry points, search results if search exists).
   Prefer breadth over depth.
5. Classify the site type and say why, in one or two sentences, using only what you saw.
6. State, as a hypothesis, who the site seems to be for and what it seems to want visitors to
   do. Label it "inferred". If you cannot tell, say so; that matters.
7. List primary conversion paths and multi-step flows (enquiry, signup, checkout, booking,
   contact, search, support). For each, say how many steps the shortest visible path takes
   from the home page and what the last reversible step is. Do not go past it.
8. List safely reachable states: a clearly non-existent URL for the 404 page, search with
   no results if search exists, empty or error states that need no submission.
9. Note rendering risks: pages whose content did not load as text, content that seems to
   depend on JavaScript, cookie or consent walls, bot checks, login walls, geo or language
   switches that changed what you saw.
10. If comparable sites were given, open their home page and one key flow each and summarise
    the conventions visitors would expect (labels, order, placement of the main action,
    information shown). Summarise; do not copy text.
11. Propose 8 to 12 candidate tasks in the customer's words, each stating a goal, not a
    feature or a menu label. For each, give the shortest visible path (list of page names)
    and its length in steps, or "no path found".
12. Note anything outside usability scope that you noticed in passing (security, legal),
    in one line each, without investigating.

Return exactly the sections listed in "Required output", in markdown. Every statement is
either "observed" (you saw it on a page, with the URL) or "inferred" (your reading of it).
```

## 4. Required output: site-map.md

The orchestrator saves the returned text as `site-map.md`. It must contain these sections; if one is missing, send the agent back for it.

1. **Overview**: site, date, tier, pages fetched out of cap.
2. **Site type and rationale**.
3. **Inferred audience and goal** (hypothesis, labelled inferred).
4. **Page inventory**: table with URL, template, purpose, reachable from, fetch status, JavaScript-dependent (yes, no, unknown).
5. **Navigation structure**: primary, secondary, footer, with exact labels.
6. **Primary conversion paths and flows**: each with shortest path, step count and last reversible step.
7. **Reachable states**: 404, empty search, other.
8. **Rendering risks and blocked areas**.
9. **Conventions benchmark** (if comparable sites were given).
10. **Candidate tasks**: goal text, shortest path, optimal steps.
11. **Observations outside scope**.

## 5. Orchestrator synthesis: building the ledger

Read `site-map.md` and build `coverage-ledger.json` following `schemas/ledger.schema.json`. The example in `examples/bakery/coverage-ledger.json` shows every unit type.

1. **Site block.** `url`, `slug`, `type` from the map, `inferred_audience` and `inferred_goal` copied from the hypothesis. Add `weight_profile` only to override the default for the site type (see `SCORING.md`).
2. **Run block.** From setup: number, mode, date, tier, isolation, language, `brief_present`, `brief_opened: false`, `prior_run`.
3. **Personas.** Section 7. Each gets `id`, `name`, `source` (builtin or custom) and a one-sentence `rationale` tied to this site.
4. **Units.** One unit per piece of intended work. Types:

| Type | One unit is | Fields to set at planning time |
|---|---|---|
| `first_impression` | One persona's five-second test of the main landing page | `personas`, `target` (URL), `priority` high |
| `task` | One persona attempting one customer goal | `personas`, `target` (goal text), `optimal_steps`, `priority` |
| `exploration` | One persona browsing without a goal | `personas`, `target` (areas), `priority` |
| `lens` | A checklist sweep over a group of pages | `lens`, `target` (page group), `priority` |
| `state` | An edge state (404, empty results, validation errors) | `target`, `priority` |
| `viewport` | A pass at one screen size over key pages | `viewport`, `target`, `priority` |
| `flow` | A multi-step flow walked end to end | `target`, `priority` |

All units start `untested`. Units the tier or the safety rules rule out are created as `skipped` with a reason, not omitted: a skipped unit documents a known gap, an omitted one hides it. Typical skips: viewport units under the `text` tier, form-validation states because forms are not submitted, authenticated areas without a test account.

5. **Counts to meet**, which `validate_ledger.py` enforces: each persona has exactly one `first_impression` unit and at least three `task` units (two in `quick` and `focus`); every lens has at least one unit (a skipped unit with a reason counts); in `quick` only heuristics and content_trust are required.
6. **Lens units.** One per lens by default. If the page inventory has more than about ten templates, split a lens by page group (for example "commerce pages" and "information pages") so no auditor is given more than it can examine properly.
7. **Flow and state units.** One flow unit per primary conversion path from the map. State units for 404, empty search and any other reachable state.
8. **Viewport units.** Under `rendered` or `provided` tiers, a mobile unit (and a desktop unit in `full`) over the home page plus the main flow. Under `text`, create them as skipped.
9. Number units sequentially: `U-001`, `U-002`, and so on.

## 6. Task design

Tasks decide what the test finds, so they get care.

- **State a goal, never a feature.** "Find out roughly what a custom cake costs", not "use the pricing page". A task that names a menu label or a feature tells the tester where to click and removes the thing being measured. `validate_ledger.py` warns when task text contains quotation marks or backticks, a sign that a UI label crept in.
- **Use the customer's words.** Draw tasks from the person's customer goals, the site type's defaults (`SITE-TYPES.md`) and the map's candidate tasks. Never from the brief.
- **Make them realistic and specific**: a number of guests, a date window, a location. Specific tasks produce specific evidence.
- **Include an anchor task** per persona: something that should be easy (opening hours, contact, what the business is). If a persona fails an anchor task, suspect an over-harsh simulation or a real, serious problem, and check which. If every persona sails through every hard task, suspect leniency.
- **Include a task the site may not support** (a question the site probably does not answer, such as price or delivery area). Whether the site fails gracefully, by saying so or offering a next step, is a finding in its own right.
- **Estimate `optimal_steps`** from the map's shortest visible path, counted as page loads or distinct deliberate actions from the starting page. Use `null` when no path exists. Efficiency in the scorecard is optimal over taken, capped at 1.
- **Cover the main conversion path** with at least one task per persona, and cover each primary flow with at least one task from some persona.

## 7. Choosing personas

Read `PERSONAS.md`. Use the selection matrix there with the site type from the map.

- `full`: 4 to 6, `quick`: 3, `focus`: 2 to 4 relevant to the target.
- Always include at least one first-time-visitor type and at least one constrained persona (low digital literacy, mobile rusher, cognitive load, non-native reader or an assistive technology persona), because the average visitor is the least informative one.
- If the person described their real customers, build a custom persona from that description in place of the closest built-in, and say so in the persona's `rationale`.

## 8. Unit rules and priorities

Priority tells the hunt gate what must be done before leaving Phase 2.

- **high**: the home page first impression, tasks on the primary conversion path, flows on that path, the core lenses (heuristics, content_trust, flows_forms) and any unit the person named as a worry.
- **medium**: secondary tasks, exploration, the accessibility and mobile lenses, 404 and other states, viewport units.
- **low**: legal and utility pages, rare states, desktop viewport when mobile is the main concern.

## 9. Gate

1. Save `site-map.md` and `coverage-ledger.json`.
2. Run `python3 scripts/validate_ledger.py <run>/coverage-ledger.json --stage recon`. Fix errors.
3. Tell the person the plan in two or three lines (personas, units, tier and its limit, agents about to launch) and continue to Phase 2 unless they asked to approve the plan first.
