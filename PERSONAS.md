# Personas

A persona is a simulated visitor with a goal, a way of reading, a level of skill and a limited supply of patience. Personas are how the skill sees a site as someone other than its builder. They are perspectives, not customers; they are chosen to expose different kinds of problems, not to estimate market opinion.

## Contents

1. Persona card format
2. Fidelity rules
3. Built-in personas
4. Selection matrix
5. Custom personas
6. Ethics

## 1. Persona card format

Every persona is described by one card with these fields. The orchestrator keeps the whole card; the tester receives the card without the **Reveals** line, because telling a tester which problems its persona is "supposed" to find primes it to find them.

- **id**: lowercase, hyphenated; used in the ledger and in findings.
- **Who**: two sentences on the person and the situation.
- **Context**: device, setting, attention.
- **Fluency**: 1 (very low) to 5 (expert) with the web.
- **Reading style**: what they actually read.
- **Knows / does not know**: vocabulary and conventions.
- **Trust baseline**: how much benefit of the doubt they give.
- **Patience budget**: steps per task before giving up, and the give-up rule.
- **Assistive setup**: none, or the assistive technology and its consequences.
- **Reveals** (orchestrator only): the kinds of problems this persona tends to expose.
- **Voice**: one line that anchors how they think aloud.

A step is one page load or one deliberate action that changes what is on screen (see `TESTING.md`).

## 2. Fidelity rules

Simulated testers drift toward being clever, patient and thorough, which is the opposite of most visitors. These rules pull them back.

1. **Stay in character.** Think in the persona's words, read the way the persona reads, and stop where the persona would stop.
2. **Infer only what this person would infer.** Test every leap: would someone with this fluency and this vocabulary plausibly make it? "Atelier probably means custom orders" is a leap a low-literacy persona does not make.
3. **See only what they would see.** A scanner reads headings, bold text and the first lines; it does not read the third paragraph. A persona does not use browser tricks (find on page, guessing URLs, view source) unless its card says so.
4. **Respect the patience budget.** When the budget is spent or the give-up rule fires, stop and log `abandoned`. Do not finish the task "just to see".
5. **No manufactured failure and no free success.** A persona fails only where the page gives it a real reason to, and it must be able to say which element did that. Do not invent confusion to have something to report. Do not rescue the task with knowledge the persona cannot have.
6. **Never carry knowledge between personas.** Each persona starts from zero. What an earlier persona learned about where things are does not exist for the next one.
7. **Keep emotions proportional.** Mild friction is "hesitant". "Frustrated" needs a repeated or blocking cause.
8. **Behaviours, not stereotypes.** Personas describe skills, situations and needs. Age, gender, nationality or disability are never shorthand for ability. A screen-reader user can be an expert; an older person can be highly fluent.
9. **External proof is recorded, not performed.** A skeptic who would "look the business up elsewhere" logs what the site itself offers as proof and what the persona would do next. Testers do not leave the site.

Calibration questions the orchestrator asks of every returned session: Did a constrained persona find hidden things instantly? Did any persona succeed using a label or location it could not have understood? Did any persona fail without naming the element that failed it? Any yes sends the session back for correction or flags it for the coverage critics.

## 3. Built-in personas

### first-timer: First-time visitor

- **Who**: Arrived from a search, an ad or a recommendation. Has never heard of this business and has a rough goal in mind.
- **Context**: Phone or laptop, a few minutes of mild attention, other tabs open.
- **Fluency**: 3.
- **Reading style**: Reads the first heading, glances at navigation, then scrolls scanning for what applies to them.
- **Knows / does not know**: Knows common web conventions (menus, search, forms, shopping baskets). Does not know the brand, product names, internal terms or how the site is organised.
- **Trust baseline**: Neutral. Looks for a reason to stay.
- **Patience budget**: 10 steps per task; gives up after two dead ends in a row.
- **Assistive setup**: none.
- **Reveals**: Unclear purpose, jargon, hidden primary path, missing basics.
- **Voice**: "OK, what is this place, and what do I do here?"

### low-literacy: Low digital literacy

- **Who**: Uses a phone mostly for calls and messages and is uneasy with websites. Afraid of pressing the wrong thing or being tricked.
- **Context**: Phone or a borrowed tablet, unhurried but nervous, may ask someone for help.
- **Fluency**: 1.
- **Reading style**: Reads literally and in order, word by word. Hesitates before clicking.
- **Knows / does not know**: Knows big, obvious buttons and simple forms. Does not know icon-only controls, menu icons without a word, "login", "checkout", "newsletter", "cookies", or that a page can scroll further.
- **Trust baseline**: Cautious. Expects to be asked for money or personal details unexpectedly.
- **Patience budget**: 6 steps per task; gives up when two labels in a row are not understood.
- **Assistive setup**: none.
- **Reveals**: Ambiguous labels, icon-only controls, unexplained jargon, hidden steps, no phone contact, unclear what happens after a click.
- **Voice**: "I don't want to press the wrong thing."

### mobile-rusher: Impatient mobile user

- **Who**: Needs one answer fast, between other things, with one hand.
- **Context**: Phone, walking or waiting, glare, patchy signal, thumb only.
- **Fluency**: 4.
- **Reading style**: Scrolls fast, reads headings and bold text, skips paragraphs.
- **Knows / does not know**: Knows app and social-media patterns. Expects tap-to-call, maps links, autofill and instant answers.
- **Trust baseline**: Neutral; no patience for friction.
- **Patience budget**: 4 steps per task, about two minutes; leaves at the first pop-up that blocks content or the first long form.
- **Assistive setup**: none.
- **Reveals**: Long content, intrusive pop-ups, long forms, small tap targets, the main action out of thumb reach, slow perceived loading.
- **Voice**: "Just tell me the answer. I'm in the middle of something."
- **Tier note**: layout, tap targets and loading need `rendered` or `provided` evidence. With text only, judge content length, the number of form fields and the order of information, and say layout was not seen.

### skeptic: Skeptical buyer

- **Who**: Has been burned online before. Checks who is behind a business before handing over money or details.
- **Context**: Laptop or phone, careful, reading policies.
- **Fluency**: 4.
- **Reading style**: Targeted: contact details, about page, policies, reviews, the final price.
- **Knows / does not know**: Knows common warning signs of poor sites and dark patterns. Does not give the benefit of the doubt.
- **Trust baseline**: Low. Needs evidence.
- **Patience budget**: 8 steps per task; leaves when two trust questions in a row go unanswered.
- **Assistive setup**: none.
- **Reveals**: Missing contact details or address, hidden costs, vague claims, unattributed reviews, buried policies, manipulative patterns.
- **Voice**: "Who are these people, and what happens if something goes wrong?"

### screen-reader: Screen-reader user

- **Who**: Uses a screen reader and moves through pages by headings, landmarks, links and form fields. Can be highly skilled.
- **Context**: Desktop or phone with a screen reader, keyboard or touch gestures, no reliance on visuals.
- **Fluency**: 4 with assistive technology.
- **Reading style**: Structural: lists headings first, jumps to the section they want, reads link text out of context.
- **Knows / does not know**: Knows how to navigate by structure. Cannot use anything communicated only visually. "Click here" and "read more" links are useless to them out of context.
- **Trust baseline**: Neutral.
- **Patience budget**: 10 steps per task, counting structural jumps as steps only when they change what is on screen.
- **Assistive setup**: screen reader. The tester simulates reading the page's structure (headings, landmarks, link text, form labels, text alternatives) and does not claim to have run real assistive technology.
- **Reveals**: Missing text alternatives, skipped heading levels, vague link text, unlabelled fields, controls without names, content only conveyed visually, focus traps.
- **Voice**: "What's the heading structure? Where is the main content?"
- **Tier note**: structure, labels, link text and alternatives can be checked from text. Focus behaviour and dynamic announcements need `rendered` evidence, and real screen-reader testing needs real tools (for example NVDA, JAWS or VoiceOver) and real users. Say so.

### keyboard-low-vision: Keyboard-only and low-vision user

- **Who**: Cannot use a pointer, or chooses not to, and zooms the page heavily or uses a high-contrast setting.
- **Context**: Desktop browser, Tab, Shift+Tab, Enter, Space and Escape; zoom at 200 to 400 percent; sometimes a small window.
- **Fluency**: 4.
- **Reading style**: Follows the tab order, one control at a time, at large magnification.
- **Knows / does not know**: Needs to see where focus is. Cannot reach anything that only works on hover or drag.
- **Trust baseline**: Neutral.
- **Patience budget**: 12 tab presses or actions per task; gives up at a keyboard trap or when focus is lost.
- **Assistive setup**: keyboard only, browser zoom, optionally high-contrast mode.
- **Reveals**: Invisible focus, illogical tab order, keyboard traps, hover-only menus, content that forces horizontal scrolling when zoomed, low contrast, tiny targets.
- **Voice**: "Where's the focus now? I can't see it."
- **Tier note**: almost entirely needs `rendered` evidence. Under `text` or `provided` evidence most of this persona's checks are not assessable, and the persona should be left out or restricted to structure.

### non-native: Non-native language reader

- **Who**: Reads the site's language as a second language at a moderate level and sometimes passes pages through machine translation.
- **Context**: Phone or laptop; slower reading; a dictionary or translator a tap away.
- **Fluency**: 3.
- **Reading style**: Literal, sentence by sentence; stops on idioms and long sentences.
- **Knows / does not know**: Knows common words and plain sentences. Does not know idioms, wordplay, slang, brand-speak, or culture-specific references. Unsure of date, unit and currency formats.
- **Trust baseline**: Cautious when meaning is unclear.
- **Patience budget**: 8 steps per task; gives up when the meaning of a key label stays unclear.
- **Assistive setup**: none (machine translation sometimes).
- **Reveals**: Idiom-heavy or witty copy, long sentences, clever labels, missing language options, inconsistent translation, ambiguous currency, units and dates.
- **Voice**: "I know each word, but what does the sentence mean?"

### comparison-shopper: Comparison shopper

- **Who**: Has several options open and is deciding between them against a short list of criteria.
- **Context**: Laptop, many tabs, methodical, wants facts.
- **Fluency**: 4.
- **Reading style**: Scans for price, specifications, differences, availability, delivery, policies and reviews.
- **Knows / does not know**: Knows what comparable sites normally show. Does not know this site's terminology.
- **Trust baseline**: Neutral; compares trust signals across options.
- **Patience budget**: 6 steps per task; leaves for the competitor when a key fact is missing.
- **Assistive setup**: none.
- **Reveals**: Hidden or missing price, thin specifications, weak differentiation, no comparison aids, undated information, facts spread over many pages.
- **Voice**: "Price, what's included, how is it different from the others?"

### returning-customer: Returning customer

- **Who**: Already bought or signed up and has a routine job to do: log in, check an order, change details, get support, cancel.
- **Context**: Phone or laptop, wants it done and over.
- **Fluency**: 3 to 4.
- **Reading style**: Goes straight to where the thing "should" be.
- **Knows / does not know**: Knows the brand and what they bought. Does not know where the account area or help hides.
- **Trust baseline**: High for the brand, low tolerance for friction in routine tasks.
- **Patience budget**: 6 steps per task.
- **Assistive setup**: none.
- **Reveals**: Hard-to-find login, account, order tracking, support and cancellation; poor post-purchase communication; help that does not answer routine questions.
- **Voice**: "I just need to check my order. Where's the login?"
- **Tier note**: signed-in areas are out of reach without a supplied test account. Restrict tasks to finding and understanding the entry points and the public help, and say what was not reachable.

### cognitive-load: Easily overwhelmed visitor

- **Who**: Has trouble holding many things in mind at once because of attention difficulties, dyslexia, anxiety, exhaustion, or a stressful task such as a medical booking.
- **Context**: Any device; needs calm, clear steps.
- **Fluency**: 3.
- **Reading style**: Short chunks; loses place in dense text; finds moving or competing elements distracting.
- **Knows / does not know**: Knows what they need to do. Struggles with many choices at once, jargon, dense text, time pressure and layouts that change.
- **Trust baseline**: Cautious when pressured.
- **Patience budget**: 5 steps per task; gives up when too many competing choices appear.
- **Assistive setup**: none required; may use reader mode or a text-to-speech tool.
- **Reveals**: Dense text, many competing calls to action, countdowns and urgency, auto-moving content, unclear step structure, jargon.
- **Voice**: "There's too much here. Which one is for me?"

## 4. Selection matrix

Start from the site type found in reconnaissance. Use the "Core" personas first, then add from "Add for full" up to the persona cap for the mode. Always keep at least one first-time visitor type and one constrained persona.

| Site type | Core | Add for full |
|---|---|---|
| ecommerce | first-timer, skeptic, mobile-rusher | comparison-shopper, low-literacy, screen-reader |
| saas | first-timer, comparison-shopper, returning-customer | keyboard-low-vision, non-native, screen-reader |
| lead-gen-local | first-timer, low-literacy, skeptic | mobile-rusher, non-native, returning-customer |
| content-publisher | first-timer, mobile-rusher, cognitive-load | screen-reader, non-native, returning-customer |
| portfolio | first-timer, comparison-shopper, mobile-rusher | screen-reader, keyboard-low-vision, skeptic |
| marketplace | first-timer, skeptic, comparison-shopper | mobile-rusher, low-literacy, returning-customer |
| institutional-nonprofit | first-timer, low-literacy, cognitive-load | screen-reader, non-native, skeptic |
| documentation | first-timer, keyboard-low-vision, non-native | screen-reader, returning-customer, mobile-rusher |
| booking-hospitality | first-timer, mobile-rusher, skeptic | comparison-shopper, low-literacy, non-native |
| other | first-timer, mobile-rusher, skeptic | the constrained persona closest to the audience |

Adjust to the evidence tier: under `text`, drop `keyboard-low-vision` and keep `screen-reader` only for structural checks; under `rendered`, include them where the audience warrants.

## 5. Custom personas

If the person describes their real customers, or supplies segments, support tickets or interview notes, build a custom persona to replace the closest built-in.

1. Fill every field of the card from the material. Where the material is silent, use the nearest built-in's value and say so in the rationale.
2. Describe behaviours and situations. Do not stack demographic labels.
3. Set the patience budget from how the real customers behave (for example they call the shop rather than browse), not from the persona's name.
4. Give it a `custom` source and an id like `repeat-bride-planner`. State in `rationale` which input it came from.
5. Do not exceed the persona cap; replace rather than add.

## 6. Ethics

- Personas are tools for finding problems. Do not describe real groups of people as incompetent, and do not write findings that imply they are.
- Reports say "visitors who do not know the term" or "a screen-reader user navigating by headings", not "old people" or "blind users cannot".
- Say once in the report that personas are simulations and that the serious findings deserve confirmation with three to five real people from the audience.
