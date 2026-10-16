# Flows and forms: enquiry, signup, checkout, search, error states, onboarding

Used by the `flows_forms` lens and by every persona task that crosses a form or a multi-step journey. Findings cite the `FL` IDs below.

## Contents

1. How to use these checks
2. Checks (FL)
3. Testing flows without harm
4. What each tier can tell you

## 1. How to use these checks

- A flow is judged by whether a visitor can reach the end understanding what is asked, why, and what will happen. A form can be short and still fail if it asks for the wrong things in the wrong order.
- **Usual severity** is a starting point; final severity comes from `SCORING.md`.
- **Tier**: field counts, labels, instructions and promised next steps are readable from text. Behaviour (validation timing, error handling, state after submit) needs interaction, which these runs do not perform on live sites. Mark those `not_assessable` unless a rendered session saw the behaviour without submitting anything.

## 2. Checks (FL)

| ID | Check | Failure signals | Usual severity | Tier |
|---|---|---|---|---|
| FL-01 | The form asks only for what is needed for the first reply or step. | Many fields; phone, budget, date or account demanded up front; fields the business does not need yet. | moderate to major | text |
| FL-02 | Every field has a visible, persistent label. | Placeholder text used as the only label; labels that vanish on typing. | moderate to major | partial |
| FL-03 | Choices are explained so a first-time visitor can pick one. | Unexplained ranges, tiers or jargon in dropdowns; no guidance on what each option means. | moderate | text |
| FL-04 | Required and optional fields are clearly marked. | No marking, marking by colour only, everything required by default. | moderate | text |
| FL-05 | Input accepts natural formats and uses suitable field types. | Phone numbers rejected for spaces, rigid date formats, text fields where pickers belong. | moderate | partial |
| FL-06 | Validation is timely and kind: after the visitor finishes a field, next to the field, in plain words, keeping what was typed. | Errors on every keystroke, errors only in a banner, errors that wipe the form. | moderate to major | rendered |
| FL-07 | After a failed submit the visitor sees what to fix and focus goes to the first problem. | A page reload with no explanation; the first error is off screen. | moderate to major | rendered |
| FL-08 | Passwords: rules are visible up front, show and hide is offered, pasting and password managers work. | Rules revealed only after failure, paste blocked, no show option. | moderate to major | partial |
| FL-09 | Autofill and autocomplete are supported for common details. | Address, name and email fields that browsers cannot fill. | minor to moderate | partial |
| FL-10 | Multi-step flows show progress and allow going back without losing data. | No step count, back button loses entries, steps that cannot be revisited. | moderate to major | partial |
| FL-11 | An account is required only when it must be. | Forced registration before price, before browsing or before a simple purchase; no guest route. | moderate to major | text |
| FL-12 | Costs are shown before the last step: shipping, taxes, fees. | Totals that change at the end, shipping revealed in the final step. | major | text |
| FL-13 | Payment options and their trustworthiness are clear. | Methods not shown until late, unfamiliar processors with no explanation. | moderate | partial |
| FL-14 | The visitor is told what happens after submitting: reply time, confirmation, next step. | A submit button with no promise; no confirmation message or email; no timeframe. | moderate | text |
| FL-15 | Submitting is protected against double clicks and shows that it is working. | No loading state; a second click creates a second order or message. | moderate | rendered |
| FL-16 | Verification (captcha, codes) adds as little friction as possible and has an accessible alternative. | Hard image puzzles, codes that expire too fast, no alternative for people who cannot see or hear. | moderate to major | partial |
| FL-17 | Search tolerates typos and synonyms and returns useful results; zero results are handled. | Exact-match only, a "no results" page with no suggestions. | moderate | partial |
| FL-18 | Filters and sorting are understandable and reversible, and show how many results remain. | Hidden filters, filters that cannot be cleared, results that change with no feedback. | moderate | partial |
| FL-19 | Empty states guide the visitor: empty basket, no results, new account. | A blank page or "Nothing here" with no next step. | minor to moderate | partial |
| FL-20 | Error pages (404, 500) explain the problem and offer a way forward. | A bare technical page; no link home, no search, no route to the main action. | minor to moderate | text |
| FL-21 | Sessions and carts survive reasonable interruptions. | Basket emptied on reload, form lost after a pause, abrupt time-outs with no warning. | moderate to major | rendered |
| FL-22 | Cancelling, unsubscribing and deleting are as easy as signing up. | Sign-up in one click, cancellation by phone call or buried several pages deep. | moderate to major | text |
| FL-23 | Onboarding gets a new user to a first success quickly and asks for permissions in context. | Empty dashboards with no guidance, a long tour before use, permission requests at the first screen. | moderate to major | partial |
| FL-24 | Destructive actions need confirmation or can be undone. | Delete with no confirmation and no undo; confirmation that does not say what will be lost. | major | partial |
| FL-25 | File uploads state limits up front and give feedback. | Size or type limits revealed after failure; no progress; unclear errors. | moderate | partial |
| FL-26 | Help is reachable from inside the flow. | No support link, no contact route or explanation at the step where visitors get stuck. | moderate | text |

## 3. Testing flows without harm

The skill never completes a purchase, submits a form or creates an account on a live site (see `SKILL.md`, "Safety rules").

1. Walk the flow to the last reversible step, reading everything shown: fields, labels, instructions, totals, promises.
2. Stop before the irreversible action. Describe in the log what the next step would do, based on the page's own wording.
3. When the person owns the site and has said fake data is safe in a low-stakes enquiry form, a rendered session may submit obviously fake data once to observe validation and confirmation. Record that it happened and what data was used.
4. Check what can be seen without submitting: empty-form validation only when it happens before sending, the confirmation text promised near the button, the error page for a clearly non-existent URL.
5. Record the checks that could not be made (validation behaviour, confirmation after submit) as `not_assessable` with the reason. They are gaps in coverage, not passes.

## 4. What each tier can tell you

- `text`: field counts and labels, instructions, promised next steps, cost information, policy links, whether guest routes exist, wording of help and error pages as visible without triggering them.
- `rendered`: all of the above plus visible validation, behaviour of controls, progress indicators, loading states, focus movement, session behaviour without submitting.
- `provided`: only what is in the supplied screens.

A flow that was only read is described as read. Do not claim that validation, double-submit protection or session handling was tested if it was not.
