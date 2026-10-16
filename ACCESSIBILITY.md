# Accessibility: WCAG 2.2 Level A and AA checks

Used by the `accessibility` lens and the `screen-reader` and `keyboard-low-vision` personas. Findings cite the criteria below as `WCAG-x.y.z`.

## Contents

1. What this is and is not
2. How evidence tiers limit the checks
3. Criteria
4. Procedure by tier

## 1. What this is and is not

This is a set of expert-style checks against the Web Content Accessibility Guidelines 2.2, Level A and AA. It finds barriers that real visitors would meet. It is not a conformance audit and never produces a statement such as "this site is WCAG compliant" or "this site fails WCAG". Conformance needs full page coverage, assistive-technology testing and often legal context.

- Automated tools find only part of the problems. This skill's checks complement them, they do not replace them. Recommend running an automated checker (for example axe, WAVE or Lighthouse) and testing with a screen reader and keyboard alone.
- The persona sessions simulate assistive-technology users. They are not real users of assistive technology and cannot show how a specific tool behaves. Say so in the report.
- Criterion 4.1.1 (Parsing) was removed in WCAG 2.2 and is not checked.

## 2. How evidence tiers limit the checks

The Tier column says what evidence can settle each criterion.

- `text`: can be judged from page text and structure.
- `partial`: sometimes visible in text or markup, often not. If the fetched content shows the answer, judge it; otherwise mark `not_assessable` and state the question.
- `rendered`: needs the page rendered or interacted with, or screenshots supplied. Under `text` evidence these cannot be confirmed; at most they become `needs_validation` with the exact question.

The validator refuses to confirm a finding that cites a `rendered` criterion without observed `rendered` or `provided` evidence. The set of rendered-only criteria in `scripts/validate_findings.py` and the Tier column here are kept identical by a test.

## 3. Criteria

| ID | Criterion (level) and what to look for | Failure signals | Usual severity | Tier |
|---|---|---|---|---|
| WCAG-1.1.1 | Non-text content (A): informative images have useful text alternatives; decorative images are ignored; icon-only controls have names. | Missing or filename-like alternatives, images that carry text with no equivalent, unnamed icon buttons. | major | partial |
| WCAG-1.2.1 | Audio-only and video-only, prerecorded (A): a transcript or equivalent exists for media that carries content. | Podcast or silent video with no text alternative. | moderate | partial |
| WCAG-1.2.2 | Captions, prerecorded (A): videos with speech have captions. | Speech video with no captions. | major | partial |
| WCAG-1.2.3 | Audio description or media alternative, prerecorded (A): visual information in video is available in another form. | Video that depends on what is shown with no description or transcript. | moderate | partial |
| WCAG-1.2.4 | Captions, live (AA): live media has captions. | Live streams with no captions. | moderate | partial |
| WCAG-1.2.5 | Audio description, prerecorded (AA): video has audio description where needed. | Video whose meaning is visual only. | moderate | partial |
| WCAG-1.3.1 | Info and relationships (A): structure is in the markup: real headings, lists, table headers, labels tied to fields. | Headings that are only bold text, skipped heading levels, layout tables, fields without associated labels. | major | partial |
| WCAG-1.3.2 | Meaningful sequence (A): the reading order makes sense without the styling. | Content order that scrambles when linearised. | moderate | partial |
| WCAG-1.3.3 | Sensory characteristics (A): instructions do not rely only on shape, colour, size, position or sound. | "Click the green button on the right." | minor to moderate | text |
| WCAG-1.3.4 | Orientation (AA): content is not locked to one orientation. | A page that works only in portrait or only in landscape. | moderate | rendered |
| WCAG-1.3.5 | Identify input purpose (AA): fields for personal data declare their purpose. | Name, email or address fields without autocomplete purpose. | minor | partial |
| WCAG-1.4.1 | Use of colour (A): colour is not the only way to convey meaning. | Links, errors or status told apart by colour alone. | moderate | rendered |
| WCAG-1.4.2 | Audio control (A): audio that plays automatically for more than three seconds can be paused or stopped. | Auto-playing audio with no control. | moderate | rendered |
| WCAG-1.4.3 | Contrast, minimum (AA): text has at least 4.5 to 1 against its background, 3 to 1 for large text. | Pale grey on white, text over busy images. | moderate to major | rendered |
| WCAG-1.4.4 | Resize text (AA): text can be enlarged to 200 percent without loss of content or function. | Clipped or overlapping text at 200 percent. | moderate | rendered |
| WCAG-1.4.5 | Images of text (AA): real text is used instead of pictures of text where possible. | Headings and buttons made as images. | minor to moderate | rendered |
| WCAG-1.4.10 | Reflow (AA): at a 320 pixel wide viewport (400 percent zoom) content does not need two-way scrolling. | Horizontal scrolling or hidden content at 400 percent zoom. | major | rendered |
| WCAG-1.4.11 | Non-text contrast (AA): interface components and key graphics have at least 3 to 1 contrast. | Faint input borders, icons that disappear against the background. | moderate | rendered |
| WCAG-1.4.12 | Text spacing (AA): content survives increased line, paragraph, letter and word spacing. | Text that clips or overlaps when spacing is increased. | minor to moderate | rendered |
| WCAG-1.4.13 | Content on hover or focus (AA): extra content that appears can be dismissed, hovered and persists. | Tooltips and menus that vanish when the pointer moves toward them or cannot be closed. | moderate | rendered |
| WCAG-2.1.1 | Keyboard (A): everything that works with a pointer works with the keyboard. | Hover-only menus, controls that cannot be reached or operated by keyboard. | major to blocker | rendered |
| WCAG-2.1.2 | No keyboard trap (A): focus can always move away. | A modal or widget that traps focus. | blocker | rendered |
| WCAG-2.1.4 | Character key shortcuts (A): single-key shortcuts can be turned off or remapped. | Single-letter shortcuts that fire while typing. | minor | rendered |
| WCAG-2.2.1 | Timing adjustable (A): time limits can be turned off, adjusted or extended. | Session time-outs with no warning or extension. | major | partial |
| WCAG-2.2.2 | Pause, stop, hide (A): moving, blinking or auto-updating content lasting over five seconds can be paused. | Auto-advancing carousels or tickers with no pause control. | moderate | rendered |
| WCAG-2.3.1 | Three flashes or below threshold (A): nothing flashes more than three times a second. | Flashing animations. | blocker | rendered |
| WCAG-2.4.1 | Bypass blocks (A): a way to skip repeated navigation (skip link or landmarks). | No skip link and no landmarks. | moderate | partial |
| WCAG-2.4.2 | Page titled (A): each page has a descriptive title. | Identical or empty titles across pages. | minor to moderate | text |
| WCAG-2.4.3 | Focus order (A): the focus order keeps meaning and operability. | Focus that jumps around the page or behind a modal. | major | rendered |
| WCAG-2.4.4 | Link purpose in context (A): link text makes sense in context. | "Click here" and "read more" repeated with no context. | moderate | text |
| WCAG-2.4.5 | Multiple ways (AA): more than one way to find pages (menu, search, sitemap). | Pages reachable only through a single path. | minor | text |
| WCAG-2.4.6 | Headings and labels (AA): headings and labels describe their topic or purpose. | Vague headings, labels such as "Field 1". | moderate | text |
| WCAG-2.4.7 | Focus visible (AA): the keyboard focus indicator can be seen. | Focus outline removed with nothing in its place. | major | rendered |
| WCAG-2.4.11 | Focus not obscured, minimum (AA): the focused item is not entirely hidden by other content. | Sticky headers or banners covering the focused control. | moderate | rendered |
| WCAG-2.5.1 | Pointer gestures (A): gestures with several points or paths have a single-pointer alternative. | Pinch-only or swipe-only controls. | moderate | rendered |
| WCAG-2.5.2 | Pointer cancellation (A): actions do not fire on press and can be aborted. | Buttons that act on pointer-down with no way to cancel. | minor | rendered |
| WCAG-2.5.3 | Label in name (A): the accessible name contains the visible label. | Visible "Search" with an accessible name of "Go". | moderate | partial |
| WCAG-2.5.4 | Motion actuation (A): functions triggered by shaking or tilting have an alternative. | Shake-to-undo with no button. | minor | rendered |
| WCAG-2.5.7 | Dragging movements (AA): anything done by dragging can be done with a single pointer. | Drag-only sorting or sliders. | moderate | rendered |
| WCAG-2.5.8 | Target size, minimum (AA): targets are at least 24 by 24 CSS pixels, with exceptions. | Tiny, tightly packed controls. | moderate | rendered |
| WCAG-3.1.1 | Language of page (A): the page's language is declared. | No language attribute, wrong language declared. | minor to moderate | partial |
| WCAG-3.1.2 | Language of parts (AA): passages in another language are marked. | Foreign phrases read in the wrong voice. | minor | partial |
| WCAG-3.2.1 | On focus (A): moving focus does not cause an unexpected change of context. | Menus that navigate on focus. | moderate | rendered |
| WCAG-3.2.2 | On input (A): changing a field does not cause an unexpected change of context without warning. | A dropdown that navigates away on selection. | moderate | rendered |
| WCAG-3.2.3 | Consistent navigation (AA): repeated navigation is in the same order on every page. | Menu order that changes between pages. | minor to moderate | text |
| WCAG-3.2.4 | Consistent identification (AA): the same function has the same name. | One function labelled differently on different pages. | minor to moderate | text |
| WCAG-3.2.6 | Consistent help (A): help mechanisms appear in the same relative place across pages. | Contact or help link that moves from page to page. | minor | text |
| WCAG-3.3.1 | Error identification (A): errors are identified and described in text. | Errors shown only by colour or by an unexplained icon. | major | partial |
| WCAG-3.3.2 | Labels or instructions (A): fields have labels or instructions. | Fields with no label, format requirements not stated. | major | text |
| WCAG-3.3.3 | Error suggestion (AA): known errors come with a suggestion for fixing them. | "Invalid input" with no hint. | moderate | partial |
| WCAG-3.3.4 | Error prevention for legal, financial and data submissions (AA): such submissions can be reversed, checked or confirmed. | Payment or deletion with no review step. | major | partial |
| WCAG-3.3.7 | Redundant entry (A): information already given in a process is not demanded again. | Re-typing the same address in consecutive steps. | moderate | partial |
| WCAG-3.3.8 | Accessible authentication, minimum (AA): signing in does not depend on a cognitive test; pasting and password managers work. | Blocked paste, puzzles with no alternative. | major | partial |
| WCAG-4.1.2 | Name, role, value (A): custom controls expose their name, role and state. | Clickable elements with no role or name; widgets that do not report state. | major | partial |
| WCAG-4.1.3 | Status messages (AA): status messages are announced without moving focus. | Success or error messages that appear silently. | moderate | rendered |

## 4. Procedure by tier

### text

1. Check structure and wording: headings and their order, link text, labels and instructions, page titles, consistent naming, text alternatives where the fetched content shows them.
2. For `partial` criteria, judge only what the fetched content shows. If markup is not visible, say the markup was not seen.
3. Mark every `rendered` criterion `not_assessable` and list those IDs in the lens summary. Under `text` evidence, accessibility confidence is capped low in the scorecard (see `SCORING.md`).
4. A suspicion about a `rendered` criterion becomes a `needs_validation` finding with the exact question, as with a carousel that may move on its own.

### rendered

1. Run the structure checks as for `text`, now with the rendered page and its accessible structure.
2. Keyboard: from the top of the page, use Tab, Shift+Tab, Enter, Space and Escape to reach and operate the main navigation, the main call to action and the main form. Note where focus disappears, jumps, is hidden or is trapped.
3. Zoom to 200 percent and then 400 percent; check for clipping, overlapping and sideways scrolling.
4. Check contrast on the main text, links, buttons and form borders. State how it was measured. Do not estimate contrast by eye for a finding.
5. Observe moving content for at least ten seconds.
6. Check hover and focus content, and sticky elements over focused controls.

### provided

Judge only what the supplied screens and markup show. State what was not supplied.
