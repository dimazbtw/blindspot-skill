# Heuristics: usability principles, navigation and visual design

Used by the `heuristics` lens. Three checklists: the ten classic usability heuristics (`NN`), navigation and information architecture (`NV`) and visual design (`DS`). Findings cite these IDs in `heuristic_refs`.

## Contents

1. How to use these checks
2. Usability heuristics (NN)
3. Navigation and information architecture (NV)
4. Visual design (DS)
5. Pairing checks with persona evidence

## 1. How to use these checks

- Each check is a question about what a visitor experiences, not a rule to enforce. A check fails only when you saw a concrete instance and can say who it affects.
- **Usual severity** is a starting point. The final severity comes from impact, frequency and persistence in `SCORING.md`.
- **Tier** says what evidence can answer the check: `text` (judged from page text and structure), `partial` (sometimes judgeable from text or markup, otherwise `not_assessable`), `rendered` (needs the page rendered or screenshots supplied). The visual design checks all need rendering; a design finding without rendered or provided evidence cannot be confirmed.
- Judge against what visitors expect of this kind of page, not against a perfect site.

## 2. Usability heuristics (NN)

Ten widely used principles for judging interfaces, phrased here for websites.

| ID | Check | Failure signals | Usual severity | Tier |
|---|---|---|---|---|
| NN-1 | Visibility of system status: the site tells visitors where they are and what is happening (loading, progress, saved, sent). | No feedback after a click or submit; no progress shown in a multi-step flow; visitors cannot tell whether an action worked. | moderate to major | partial |
| NN-2 | Match with the real world: labels, copy and order use words and concepts the visitor already has. | Internal jargon, brand-speak labels, technical terms, unexplained abbreviations, menus named after the organisation's structure. | moderate to major | text |
| NN-3 | User control and freedom: visitors can undo, go back, cancel and leave easily. | No way back from a step, entries cannot be edited, modals that trap, no cancel, forced sign-up before browsing. | moderate to major | partial |
| NN-4 | Consistency and standards: the same thing is named, looks and behaves the same everywhere, and follows web conventions. | One service with several names, the logo does not link home, unusual controls, inconsistent button styles. | minor to moderate | partial |
| NN-5 | Error prevention: the design prevents mistakes before they happen. | Free text where choices would do, no confirmation on destructive actions, ambiguous options, constraints revealed only after submitting. | moderate to major | partial |
| NN-6 | Recognition rather than recall: needed information and options are visible or easy to retrieve. | Having to remember a code or name from an earlier page, options hidden in menus, icons without labels. | minor to moderate | partial |
| NN-7 | Flexibility and efficiency: works for newcomers and frequent visitors. | No search on a large site, no saved details, no quick repeat of a common action, long paths for routine tasks. | minor to moderate | partial |
| NN-8 | Aesthetic and minimalist design: every element earns its place; irrelevant material does not compete with relevant. | Many equal-weight calls to action, walls of text, decorative clutter, competing banners. | moderate | partial |
| NN-9 | Help with errors: messages say what went wrong and how to fix it in plain words; error pages help. | Messages like "Error 500" or "Invalid input", messages far from the field, input lost after an error. | moderate to major | partial |
| NN-10 | Help and documentation: help is easy to find, task-focused and short. | No answers to obvious questions, help that restates the interface, help buried in the footer only, outdated pages. | minor to moderate | text |

## 3. Navigation and information architecture (NV)

| ID | Check | Failure signals | Usual severity | Tier |
|---|---|---|---|---|
| NV-01 | Reachability: every important page is reachable from the home page in a few clicks; key tasks take three clicks or fewer. | Core pages four or more levels deep, pages reachable only through search or a footer link. | moderate to major | text |
| NV-02 | Labels use the visitor's vocabulary and set the right expectation (information scent). | Labels that do not hint at what is behind them; a label that leads somewhere unexpected; menu items named for the organisation. | moderate to major | text |
| NV-03 | Primary navigation is the same on every page. | Menu items, order or behaviour change between pages without reason. | minor to moderate | text |
| NV-04 | Location is clear: the current section is marked and breadcrumbs exist where depth needs them. | No active state, deep pages with no breadcrumb, visitors cannot tell where they are. | minor to moderate | partial |
| NV-05 | The primary action is reachable from every page. | The only way to the main action is the home page; no persistent button or link. | moderate to major | text |
| NV-06 | The menu is a manageable size and its groups match how visitors think. | Many top-level items, items that fit several groups, "Other" or "Resources" as a dumping ground. | minor to moderate | text |
| NV-07 | Search exists where the site is large enough to need it, and is easy to find. | A large catalogue or help centre with no search, or search hidden. | moderate | text |
| NV-08 | Links look like links and link text makes sense out of context. | "Click here", "read more", links indistinguishable from plain text. | minor to moderate | partial |
| NV-09 | No dead ends: every page offers a sensible next step. | Pages that end with no next action or related link; empty or placeholder sections. | moderate | text |
| NV-10 | The back button and URLs behave: back returns to the previous view, and pages have stable, shareable addresses. | Back button breaks flows, pages with no unique URL, redirect loops. | moderate to major | partial |
| NV-11 | The footer is a safety net: contact, policies, key links and help are there. | Missing contact or policies, a footer with only social icons. | minor to moderate | text |
| NV-12 | Related content is linked: informational pages lead to the next relevant action. | Articles or product pages that never link to the thing a reader would want next. | minor to moderate | text |

## 4. Visual design (DS)

All of these need `rendered` or `provided` evidence. Under `text` evidence, mark them `not_assessable`.

| ID | Check | Failure signals | Usual severity | Tier |
|---|---|---|---|---|
| DS-01 | Visual hierarchy: the most important element is the most prominent and the reading order is clear. | The eye lands on decoration; headings and body text look alike; the key message is small or pale. | moderate to major | rendered |
| DS-02 | One clear primary action per view; secondary actions look secondary. | Several buttons of equal weight, the main button blends into the page. | moderate to major | rendered |
| DS-03 | Typography is legible: size, line length, line height and weight suit the content. | Small or light text, very long lines, cramped lines, too many typefaces. | moderate | rendered |
| DS-04 | Text and controls contrast with their background, and colour is not the only carrier of meaning. | Pale grey on white, text over busy images, status shown by colour alone. | moderate to major | rendered |
| DS-05 | Spacing and grouping show what belongs together. | Related items far apart, unrelated items touching, uneven rhythm. | minor to moderate | rendered |
| DS-06 | Components are consistent: buttons, forms, cards and links look and behave alike. | Several button styles for the same action, inconsistent form fields. | minor to moderate | rendered |
| DS-07 | Imagery supports the message: relevant, clear, not generic filler, not carrying essential text. | Stock photos that say nothing, hero images that hide the product, text embedded in images. | minor to moderate | rendered |
| DS-08 | Density suits the task: neither cluttered nor empty. | Crowded pages with competing elements, huge empty areas hiding content. | moderate | rendered |
| DS-09 | Interactive elements look interactive and states are clear. | Clickable items that look static, disabled items that look active, no hover or pressed feedback. | moderate | rendered |
| DS-10 | The first screen communicates purpose and the next step. | A first screen that is a carousel, a video or a logo with no words. | moderate to major | rendered |
| DS-11 | Motion is purposeful and does not distract or block. | Auto-playing carousels and videos, parallax that hides content, animations that delay use. | minor to moderate | rendered |
| DS-12 | Polish: no broken layout, misalignment, overlapping, or placeholder assets. | Overlapping elements, broken images, inconsistent logos, unstyled sections. | moderate | rendered |

## 5. Pairing checks with persona evidence

A heuristic failure is strongest when a persona hit it. When both exist, cite both in the finding: the persona entries show the consequence, the lens entry shows the cause. A heuristic failure no persona touched is still reported if it has a plausible visitor consequence, but with lower frequency; a persona's difficulty with no matching check is reported as a candidate with its own root cause. Do not report the same root cause under several IDs as separate findings; cite the IDs as references on one finding.
