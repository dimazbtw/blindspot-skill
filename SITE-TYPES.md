# Site types

Every site is classified once, in reconnaissance, as one of ten types. The type decides which tasks are realistic, which pages and states matter most, which personas make the best starting set and which weight profile the scorecard uses.

## Contents

1. How to use this file
2. Type list for the reconnaissance agent
3. The ten types
4. Weight profile mapping
5. Mixed and unusual sites

## 1. How to use this file

- The reconnaissance agent sees only section 2 (names and one-line descriptions). It classifies the site from what it sees, never from the brief.
- The orchestrator uses sections 3 and 4 when building the ledger: default tasks, critical pages and states, persona starting sets and the weight profile.
- Default tasks are starting points. Rewrite them with specifics from the site (quantities, dates, places) and state them as goals in the customer's words. A task never names a menu label or a feature.
- Every persona gets one anchor task (something that should be easy). Every site gets at least one probe task, a goal the site may not support, to see whether it fails gracefully.

## 2. Type list for the reconnaissance agent

Paste this list into the reconnaissance packet and nothing else from this file.

- `ecommerce`: sells physical or digital goods through a basket and checkout.
- `saas`: software or an online tool people sign up for, usually with plans, a trial and an account area.
- `lead-gen-local`: a local or professional service whose goal is an enquiry, call, quote or visit (trades, clinics, studios, agencies, bakeries).
- `content-publisher`: news, a blog, a magazine or a media site whose goal is reading, subscribing or returning.
- `portfolio`: a person's or studio's showcase of work whose goal is to get hired or contacted.
- `marketplace`: connects buyers and sellers or providers, with listings, profiles and trust mechanisms.
- `institutional-nonprofit`: an organisation, public body, school, club or charity that informs, enrols, recruits or raises money.
- `documentation`: reference or help material for a product, API or subject, used to get a specific answer.
- `booking-hospitality`: hotels, restaurants, events, venues and services where the goal is to reserve a date or a table.
- `other`: anything that does not fit; say what it is.

## 3. The ten types

For each type: what visitors want, default task goals (the anchor is marked **A**, the probe **P**), pages and states that matter, typical failure patterns and the starting personas. Tasks below are written as goals; adapt them to the site.

### ecommerce

- **Visitor goals**: find a product that fits a need, compare, check the real total cost, pay with confidence, track an order, return something.
- **Default tasks**: find a product for a described need and a budget; check the delivery cost and time to a named place; compare two similar products; find out what happens if the item does not fit; start the purchase and stop at the last reversible step (flow); **A** find a way to contact the shop; **P** find out if it ships to a country the site does not mention.
- **Critical pages and states**: home, category listing, product page, basket, checkout entry, delivery and returns policies, contact, order tracking entry, 404, empty search.
- **Failure patterns**: price or total revealed late; shipping only visible at the last step; thin product detail (size, material, stock); forced account before checkout; policies buried; filters that hide products; no reviews or unattributed ones; cookie banner blocking the product on phones.
- **Personas**: first-timer, skeptic, mobile-rusher; then comparison-shopper, low-literacy, screen-reader.
- **Weight profile**: `transactional`.

### saas

- **Visitor goals**: understand what the product does and whether it fits, see the price and plan limits, try it, get started, find help.
- **Default tasks**: work out what the product does for a described situation; find what it costs for a team of a stated size; find out what the free trial includes and when it ends; start a sign-up and stop at the first reversible step (flow); find the way to log in as an existing customer (returning-customer); **A** find a way to talk to someone; **P** find out whether the product integrates with a tool the site does not mention.
- **Critical pages and states**: home, product or features, pricing, sign-up entry, login entry, documentation or help entry, contact, 404.
- **Failure patterns**: feature lists instead of outcomes; "contact sales" in place of any price; plan names without explanation; a trial with hidden limits; sign-up demanding a card without saying so; jargon; login hidden for returning customers; claims with no proof.
- **Personas**: first-timer, comparison-shopper, returning-customer; then keyboard-low-vision, non-native, screen-reader.
- **Weight profile**: `app`.

### lead-gen-local

- **Visitor goals**: know what the business does, whether it serves them, roughly what it costs, how to get in touch, whether to trust it.
- **Default tasks**: find out whether the business offers a described service in a named place; find a rough price for a described job; get in touch to ask a question (flow, stop before sending); find opening hours and the address; **A** find a phone number or email; **P** find out whether a service the site does not mention is offered.
- **Critical pages and states**: home, services, pricing or "how it works", contact, about, FAQ, reviews or portfolio, 404.
- **Failure patterns**: no statement of what the business does; no prices or ranges; a form as the only contact route; long enquiry forms; no postal address or phone; brand names for services; unattributed testimonials; opening hours missing or contradictory.
- **Personas**: first-timer, low-literacy, skeptic; then mobile-rusher, non-native, returning-customer.
- **Weight profile**: `default`.

### content-publisher

- **Visitor goals**: find a specific piece or topic, read it comfortably, trust the source, subscribe or come back.
- **Default tasks**: find an article on a described topic; find the most recent coverage of a topic; find out who writes the content and who is behind the site; subscribe to updates and stop before submitting (flow); **A** find the contact or about page; **P** find an article older than a stated year.
- **Critical pages and states**: home, article page, category or tag listing, search, about and authors, subscribe entry, 404, empty search.
- **Failure patterns**: intrusive pop-ups and ad clutter; no dates or authors; weak search and archive; walls of text; paywall or sign-up surprises; auto-playing media; inconsistent navigation between sections.
- **Personas**: first-timer, mobile-rusher, cognitive-load; then screen-reader, non-native, returning-customer.
- **Weight profile**: `content`.

### portfolio

- **Visitor goals**: see good examples quickly, judge style and fit, learn what working together involves, get in touch.
- **Default tasks**: find examples of work relevant to a described project; find out what the person or studio does and for whom; find out how a project starts and roughly what it costs; get in touch (flow, stop before sending); **A** find an email address; **P** find out whether the person takes on a type of work not shown.
- **Critical pages and states**: home, work index, a project page, about, services, contact, 404.
- **Failure patterns**: work without context (no role, no outcome); images with no text; hidden navigation and gestures; clever labels; no statement of availability or process; contact buried.
- **Personas**: first-timer, comparison-shopper, mobile-rusher; then screen-reader, keyboard-low-vision, skeptic.
- **Weight profile**: `content`.

### marketplace

- **Visitor goals**: find a good listing or provider, judge whether it is trustworthy, understand fees and protection, complete the transaction, sell or offer something.
- **Default tasks**: find a listing that fits a described need; judge whether a seller or provider can be trusted; find out who pays what in fees and what happens if something goes wrong; start a purchase or contact and stop at the last reversible step (flow); find out how to list something to sell; **A** find help or support; **P** find out how disputes are handled if the site does not say.
- **Critical pages and states**: home, search and results, listing page, seller or provider profile, how it works, fees, safety or protection, contact, 404, empty search.
- **Failure patterns**: unclear fees and who pays; weak trust signals on listings; reviews with no source; forced sign-up before browsing; filters that do not narrow; two sides of the market served by one confusing home page.
- **Personas**: first-timer, skeptic, comparison-shopper; then mobile-rusher, low-literacy, returning-customer.
- **Weight profile**: `transactional`.

### institutional-nonprofit

- **Visitor goals**: understand what the organisation does, find a service, form or contact, enrol, volunteer, donate, find official information.
- **Default tasks**: find out what the organisation does and who it serves; find the right form or service for a described situation; find how to donate, join or enrol and stop at the last reversible step (flow); find a contact route for a described question; **A** find an address and opening hours; **P** find information that the site likely keeps in a document or not at all.
- **Critical pages and states**: home, services or programmes, how to get involved, donate or join, news, contact, accessibility statement, 404, search.
- **Failure patterns**: navigation shaped like the organisation chart; jargon and acronyms; key facts in PDFs; many calls to action of equal weight; out-of-date news; forms with unclear purpose; no plain statement of who it is for.
- **Personas**: first-timer, low-literacy, cognitive-load; then screen-reader, non-native, skeptic.
- **Weight profile**: `default`.

### documentation

- **Visitor goals**: get a specific answer or instruction fast, learn a concept, find an example, check a limit or a parameter.
- **Default tasks**: find how to do a described task; find the meaning and default of a described setting; find a working example for a described case; find out what changed in the latest version; **A** find the search or the table of contents; **P** find an answer the documentation probably does not cover.
- **Critical pages and states**: docs home, getting-started, a reference page, a guide, search and its empty state, version selector, 404, contact or community entry.
- **Failure patterns**: no clear starting point; assumed knowledge; search that misses synonyms; examples that cannot be copied or that are outdated; unclear versioning; headings that do not say what a section answers; dead links.
- **Personas**: first-timer, keyboard-low-vision, non-native; then screen-reader, returning-customer, mobile-rusher.
- **Weight profile**: `content`.

### booking-hospitality

- **Visitor goals**: check availability and price for a date, see what is included, trust the venue, book or reserve, change or cancel.
- **Default tasks**: check availability and price for described dates and guests; find what is included and what is extra; find the cancellation and change policy; start a booking and stop at the last reversible step (flow); find location and how to get there; **A** find a phone number or email; **P** find whether a request outside the standard options (dietary, accessibility, a late arrival) can be met.
- **Critical pages and states**: home, availability or booking entry, room or menu or offer pages, prices, policies, location, contact, reviews, 404.
- **Failure patterns**: price visible only after dates and details; availability widget unusable on phones; policies after payment; photos with no information; taxes and fees at the end; confirmation unclear; no phone route.
- **Personas**: first-timer, mobile-rusher, skeptic; then comparison-shopper, low-literacy, non-native.
- **Weight profile**: `transactional`.

### other

- **Visitor goals**: whatever the inferred audience came to do. If the site's purpose cannot be inferred, that is the first finding.
- **Default tasks**: work out what the site is for; do the main thing the page seems to invite; find a way to contact someone (**A**); find something the site probably does not support (**P**); find the most important policy or help.
- **Critical pages and states**: home, the main action's pages, contact, help, 404.
- **Failure patterns**: unclear purpose; unclear next step; missing basics (contact, policies, pricing); inconsistent naming.
- **Personas**: first-timer, mobile-rusher, skeptic; then the constrained persona closest to the audience.
- **Weight profile**: `default`.

## 4. Weight profile mapping

The scorecard weights categories by site type. The mapping lives in `scripts/compute_scores.py` (`SITE_TYPE_PROFILE`) and is repeated here so the orchestrator can explain it. Weights are percentages of an average over the categories that were assessed.

| Site type | Profile |
|---|---|
| ecommerce, marketplace, booking-hospitality | `transactional` |
| saas | `app` |
| content-publisher, portfolio, documentation | `content` |
| lead-gen-local, institutional-nonprofit, other | `default` |

| Category | default | transactional | app | content |
|---|---|---|---|---|
| clarity | 18 | 14 | 16 | 16 |
| navigation | 12 | 12 | 14 | 16 |
| trust | 14 | 18 | 8 | 10 |
| content | 12 | 10 | 10 | 22 |
| design | 8 | 6 | 10 | 10 |
| flows | 16 | 22 | 24 | 4 |
| mobile | 12 | 12 | 8 | 14 |
| accessibility | 8 | 6 | 10 | 8 |

A weight profile can be overridden in the ledger (`site.weight_profile`) when a site clearly behaves like another type, for example a bakery that is mostly an online shop. State the override and the reason in `run-notes.md`. Changing the profile between runs makes the overall scores not comparable (the comparison tool says so).

## 5. Mixed and unusual sites

- **Mixed sites** (a publisher with a shop, a restaurant with bookings): classify by the main goal the home page pushes, add tasks for the secondary purpose, and say in `run-notes.md` which type was chosen and why.
- **Single-page sites**: still make a lens unit per lens, and use the sections as the "pages" in the page inventory.
- **Web apps behind a login**: without a supplied test account only the public surface is testable. Restrict tasks to finding and understanding the entry points, pricing and help, and mark the signed-in areas as skipped units with the reason.
- **Sites in several languages**: test the language the person asked for, record the others as not examined, and note any language-switch problems as findings.
- **Competitor teardowns**: classify and test as usual. Findings describe what visitors experience on that site; the report says it is an outside view and the competitor's intent is unknown.
