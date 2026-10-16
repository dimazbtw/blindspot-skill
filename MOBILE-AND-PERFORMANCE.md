# Mobile and perceived performance

Used by the `mobile_performance` lens, the `mobile-rusher` persona and `viewport` units. Findings cite the `MB` IDs below.

## Contents

1. Evidence and what it can support
2. Checks (MB)
3. Reference values
4. Procedure by tier

## 1. Evidence and what it can support

Layout, tap targets and loading cannot be judged from text. A finding in the `mobile` category needs observed evidence at tier `rendered` or `provided`; the validator enforces this. Under `text` evidence this lens can read content length, the number of form fields and the order of information, mark everything else `not_assessable`, and record what a proper mobile pass still needs. A text-visible problem that matters on phones (a nine-field form, for example) is reported under its natural category (here `flows`, check `FL-01`) rather than as a mobile finding.

Performance numbers (load time, layout shift, responsiveness) need measurement. Do not estimate them by feel. If the session's tools cannot measure, say that a measurement with Lighthouse, PageSpeed Insights or the browser's performance tools is needed and mark the check `not_assessable`.

## 2. Checks (MB)

| ID | Check | Failure signals | Usual severity | Tier |
|---|---|---|---|---|
| MB-01 | The layout works at phone widths (320 to 430 CSS pixels): nothing overlaps, nothing needs sideways scrolling. | Horizontal scroll, clipped or overlapping elements, content that runs off the screen. | major | rendered |
| MB-02 | Text is readable without zooming and zoom is not blocked. | Body text under about 16 pixels, pinch zoom disabled, very long lines. | moderate to major | rendered |
| MB-03 | Tap targets are large enough and spaced: at least 24 by 24 CSS pixels (WCAG minimum), ideally 44 to 48. | Tiny links, adjacent targets that cause mis-taps, close buttons that are hard to hit. | moderate | rendered |
| MB-04 | The primary action is visible or within thumb reach without hunting. | The main button below long content or in a top corner on a tall phone. | moderate to major | rendered |
| MB-05 | Navigation on small screens is discoverable and shallow. | An unlabelled menu icon, menus several levels deep, menu covering the page with no clear close. | moderate to major | rendered |
| MB-06 | Sticky and fixed elements leave room for the content. | A cookie banner, chat widget and sticky header together covering half the screen. | moderate to major | rendered |
| MB-07 | Interstitials and pop-ups do not block content on arrival. | A full-screen sign-up or app-install prompt before the visitor has seen anything. | moderate to major | rendered |
| MB-08 | Forms are practical on a phone: short, with the right keyboard and autofill. | Long forms, number fields that open the text keyboard, no autofill, fields hidden behind the keyboard. | moderate | partial |
| MB-09 | Tables, long content and media adapt. | Wide tables that need scrolling, images much larger than the screen, tiny diagrams. | moderate | rendered |
| MB-10 | Phone numbers, addresses and shares use native handlers. | A phone number that is not tappable, an address that does not open a map. | minor to moderate | partial |
| MB-11 | The page works in portrait and landscape. | Content locked to one orientation, layouts that break when rotated. | minor to moderate | rendered |
| MB-12 | Perceived loading: the main content appears quickly and there is feedback while waiting. | A blank screen for several seconds, content that appears long after the chrome, no progress or skeleton. | moderate to major | rendered |
| MB-13 | Interactions respond promptly. | Taps that take a noticeable moment to react, menus that stutter. | moderate | rendered |
| MB-14 | The page is visually stable while loading. | Content that jumps as images, fonts or ads load, causing mis-taps. | moderate | rendered |
| MB-15 | Heavy assets are used with restraint on constrained connections. | Autoplay video, huge images, many fonts and scripts for a simple page. | minor to moderate | rendered |
| MB-16 | The page degrades gracefully on a slow or dropped connection. | Blank states and no retry when something fails to load. | moderate | rendered |

## 3. Reference values

These are widely used guidance values, offered as reference points rather than pass marks for every site.

- Core Web Vitals "good" thresholds, measured at the 75th percentile of real visits: largest content visible within 2.5 seconds, interaction responsiveness within 200 milliseconds, layout shift score at or below 0.1. They are field-data concepts; a single manual observation is not a measurement of them.
- WCAG 2.2 minimum target size: 24 by 24 CSS pixels, with exceptions for spacing, inline text links and similar. Larger targets (44 to 48 pixels) are the usual recommendation for touch.
- Body text of about 16 CSS pixels is a common legibility baseline on phones.
- Default test viewports: 390 by 844 for a current phone, 360 by 800 for a common Android size, 320 by 568 for the smallest reflow check, 768 by 1024 for a tablet, 1440 by 900 for desktop.

## 4. Procedure by tier

### rendered

1. For each viewport unit, open the key pages at the assigned size. Record the viewport in each log entry.
2. Check the first screen: what is visible, what the main action is, what covers the content.
3. Scroll the page once, noting layout jumps, sticky elements and anything that overlaps.
4. Attempt the main task one-handed in the head: can the main action be reached, are targets distinguishable?
5. Rotate if orientation matters for the site's purpose.
6. For performance, observe what the tools expose and say how it was observed. Where there is no measurement, mark the check `not_assessable`.

### provided

Treat each supplied screenshot as one state at one size. Judge layout and targets from what is shown. Do not extrapolate to other sizes.

### text

Read the content length, the count of form fields, the order of information and whether contact details are given as plain text. Everything else is `not_assessable`. Record that the viewport units were skipped and why.
