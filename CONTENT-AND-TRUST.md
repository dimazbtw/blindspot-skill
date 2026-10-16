# Content and trust: clarity, content quality, credibility

Used by the `content_trust` lens and by the five-second test. Three checklists: clarity and value proposition (`CL`), content quality (`CT`) and trust and credibility (`TR`). These are where the builder's knowledge hides the most problems.

## Contents

1. How to use these checks
2. Clarity and value proposition (CL)
3. Content quality (CT)
4. Trust and credibility (TR)
5. Curse-of-knowledge patterns
6. Wording trust findings

## 1. How to use these checks

- Judge from the text the page shows, as someone who has never heard of the business. Anything that only makes sense to a person who already knows it is a failure of the page, not of the visitor.
- **Usual severity** is a starting point. Final severity comes from `SCORING.md`.
- **Tier**: nearly all of these are judgeable from text. Checks about images, layout and styling need rendered or provided evidence.

## 2. Clarity and value proposition (CL)

| ID | Check | Failure signals | Usual severity | Tier |
|---|---|---|---|---|
| CL-01 | The purpose of the site is stated in plain words at the top of the page: what it is and what it offers. | A slogan or brand line with no noun naming the product or service; the visitor cannot say what is sold. | major | text |
| CL-02 | The audience is identifiable: who this is for. | Generic copy that could be for anyone; no sign of the customer's situation. | moderate | text |
| CL-03 | One primary action is obvious. | No call to action, or several competing ones; the main action is a vague label. | major | text |
| CL-04 | The benefit or difference is stated, not only features or history. | Lists of features, awards or years in business without saying what it means for the visitor. | moderate | text |
| CL-05 | Jargon, acronyms and internal names are explained or avoided. | Unexplained product names, tiers, abbreviations or process terms. | moderate to major | text |
| CL-06 | Labels describe what the visitor gets or does, not the organisation's own vocabulary. | Section and button names taken from the brand or the org chart (for example a studio-style name for the ordering page). | moderate to major | text |
| CL-07 | The main imagery or media communicates the offer. | Hero images that show mood, not product; video-only explanation with no text. | moderate | partial |
| CL-08 | How much it costs, and how pricing works, is discoverable and unambiguous. | No price or range anywhere; "contact us for pricing" on everything; fees revealed late; unclear free-trial limits. | major | text |
| CL-09 | After each call to action, the visitor is told what happens next. | A button with no hint of the next step; a form that does not say whether anyone will reply. | moderate | text |
| CL-10 | Terminology is consistent: one name for one thing. | The same service named differently in the menu, headings, footer and forms. | minor to moderate | text |
| CL-11 | A page makes sense for someone who lands on it directly, with no earlier context. | Pages that assume the visitor saw the home page or a previous step; undefined "it" and "this". | moderate | text |
| CL-12 | Claims are specific and checkable, not vague superlatives. | "The best", "world-class", "innovative", "trusted by thousands" with nothing behind them. | minor to moderate | text |

## 3. Content quality (CT)

| ID | Check | Failure signals | Usual severity | Tier |
|---|---|---|---|---|
| CT-01 | The pages answer the questions a visitor of this kind of site is likely to have. | Missing price, availability, delivery area, opening hours, contact, returns, specifications, how it works. | major | text |
| CT-02 | Content is easy to scan: informative headings, short paragraphs, lists where useful. | Long unbroken blocks, headings that say nothing, key facts buried in paragraphs. | moderate | text |
| CT-03 | Reading level and sentence length suit the audience. | Long, formal or technical sentences for a general audience; heavy nominalisation. | moderate | text |
| CT-04 | Facts are consistent across pages. | Different prices, hours, names or addresses in different places. | moderate to major | text |
| CT-05 | Content is current. | Old copyright years, expired offers, past events presented as upcoming, undated news. | minor to moderate | text |
| CT-06 | No placeholder or broken content. | Lorem ipsum, TODO notes, empty sections, dead links, missing downloads. | moderate to major | text |
| CT-07 | Spelling and grammar are clean. | Typos in headings or calls to action, mixed-up words, machine-translation artefacts. | minor to moderate | text |
| CT-08 | Calls to action and links say what they do. | "Submit", "Learn more", "Click here" where a verb and object would do. | minor to moderate | text |
| CT-09 | Media that carries content has a text equivalent. | Information only in an image, a video with no transcript or captions, a PDF as the only source of key facts. | moderate | partial |
| CT-10 | Localisation is complete and consistent. | Mixed languages, missing language switch, ambiguous currency, units or date formats. | moderate | text |
| CT-11 | No thin or duplicated pages. | Near-identical pages, stub pages, pages that repeat the home page. | minor to moderate | text |
| CT-12 | Help, policy and error copy is plain and answers real worries. | Legalese in place of answers, FAQs that dodge the actual questions, unhelpful error wording. | moderate | text |
| CT-13 | Tone is consistent and fits the audience. | Playful on one page and bureaucratic on the next; casual tone for a serious task. | minor | text |

## 4. Trust and credibility (TR)

Describe only what is visible on the pages. Do not guess at intent.

| ID | Check | Failure signals | Usual severity | Tier |
|---|---|---|---|---|
| TR-01 | The organisation is identifiable: name, address and, where relevant, registration details, plus an about page. | No postal address, no company name, no about page, nothing that shows who is behind the site. | moderate to major | text |
| TR-02 | There is a real, direct contact route besides a form. | A form as the only contact; no phone, no email, no live address. | moderate to major | text |
| TR-03 | Policies are findable before the visitor commits. | Returns, shipping, cancellation, privacy and terms missing or only reachable at the last step. | moderate to major | text |
| TR-04 | Social proof is credible: attributed, dated and verifiable. | Quotes with first names only, no dates, no source; ratings with no count; reviews that read as written by the business. | moderate | text |
| TR-05 | The total cost is clear before the last step. | Fees, shipping or taxes appearing late; a price that changes between pages. | major | text |
| TR-06 | Payment and data-entry cues are visible. | No sign of payment methods or of a secure checkout where money changes hands; sensitive details requested on an unexplained page. | moderate to major | partial |
| TR-07 | The site looks professionally maintained. | Broken layout, mismatched branding, errors, stock photos that contradict the story, placeholder text. | minor to moderate | partial |
| TR-08 | Manipulative patterns are absent. | Fake urgency or scarcity, pre-ticked add-ons, confirm-shaming wording, hidden unsubscribe or cancel, forced account creation, pricing that drips in. | moderate to major | partial |
| TR-09 | Consent and cookie choices are fair. | "Reject" harder or smaller than "Accept", pre-ticked categories, banners that block the content with no way past. | moderate | partial |
| TR-10 | Claims such as awards, certifications and "as seen in" are substantiated. | Logos with no link or context, numbers with no source or date. | minor to moderate | text |
| TR-11 | People and story are shown where they matter. | A service business with no people, no history and no faces. | minor to moderate | text |
| TR-12 | Requests for personal data are justified. | A phone number or ID demanded with no reason; no privacy note near the form. | moderate | text |
| TR-13 | Handoffs to third parties are explained. | Sudden jump to another domain for payment or booking with no warning. | minor to moderate | text |
| TR-14 | Review and rating signals look authentic. | Only five-star ratings, no dates or distribution, identical phrasing, no replies to criticism. | minor to moderate | partial |

## 5. Curse-of-knowledge patterns

These are the usual ways a builder's knowledge leaks into a page. The lens auditor and every persona look for them.

- A **slogan in place of a sentence**: the page says how the business feels, not what it does.
- **Organisation-shaped navigation**: menus named after teams, studios, "solutions" or "resources" rather than what visitors want.
- **Insider terms**: product tiers, codenames, process stages and abbreviations used as if known.
- **Assumed context**: "as you know", "our usual process", a pricing page that depends on a plan explained elsewhere.
- **Icon-only controls** and symbols whose meaning the builder never has to learn.
- **Hidden gestures and states**: hover-only menus, swipe-only carousels, things that appear on scroll.
- **Features described, not outcomes**: "AI-powered scheduling" instead of "book appointments without phone calls".
- **Self-referential proof**: "trusted by our customers" without naming one.
- **Dead-end honesty**: the answer to the visitor's first question lives in a PDF, a footer or a phone call.
- **Defaults nobody chose**: placeholder footers, "Welcome to our website", copyright years from the launch.

## 6. Wording trust findings

Trust findings are easy to get wrong because they edge toward accusation. Write only what is observable.

- Say "no postal address, phone number or registration details appear on any page", not "this looks like a scam".
- Say "reviews carry first names only, with no dates or source", not "the reviews are fake".
- Say "price appears only at the final step", not "hides the price".
- State the visitor's consequence: what they cannot check, decide or do.
- A missing trust signal is a finding about the page, never a statement about the people running it.
