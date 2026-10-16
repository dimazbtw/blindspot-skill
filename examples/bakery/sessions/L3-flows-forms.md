# Lens session L3 — Flows and forms

- Lens: flows_forms
- Wave: B
- Evidence tier: text
- Flows swept: bespoke cake inquiry (home to the last step of the form), contact form, 404 page
- Brief access: none
- Safety: no form was submitted
- Units: U-016, U-020, U-021

### L3-E01 | FL-01 | fail | https://brightleaf-bakery.example/atelier/bespoke-orders
- **Check:** The form asks only for what is needed for the first reply.
- **Observed:** Nine fields: name, email, phone (required), event date, number of guests, cake type, budget range (required), allergies and a free-text brief.
- **Verdict:** fail

### L3-E02 | FL-03 | fail | https://brightleaf-bakery.example/atelier/bespoke-orders
- **Check:** Choices are explained so a first-time user can pick one.
- **Observed:** The budget range lists four ranges with no description of what each range buys and no price information elsewhere.
- **Verdict:** fail

### L3-E03 | FL-14 | pass | https://brightleaf-bakery.example/atelier/bespoke-orders
- **Check:** The user is told what happens after submitting.
- **Observed:** Text above the submit button reads "We reply within 24 hours" and names the next step.
- **Verdict:** pass

### L3-E04 | FL-20 | partial | https://brightleaf-bakery.example/this-page-does-not-exist
- **Check:** The 404 page explains the problem and offers a way forward.
- **Observed:** A friendly message and a link to the home page; no search and no link to the order route.
- **Verdict:** partial

## Lens summary

- Not assessable at this tier: inline validation timing, error message wording and behaviour after submit.
