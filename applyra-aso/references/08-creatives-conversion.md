# Creatives and conversion

## Objective

Turn search relevance into a qualified install. Metadata earns attention; creatives prove the promise. Keep default listings, targeted listings, and experiments as separate surfaces with separate audiences and measurement.

## Intent-to-creative mapping

For each major keyword cluster, define:

| Search intent | User question | Proof needed | Store surface | Screenshot/frame | Metric |
|---|---|---|---|---|---|

The first three screenshots should usually cover:

1. Primary outcome or job
2. How the app delivers it
3. Strongest differentiator or trust proof

Adapt this sequence when the product category requires onboarding, safety, eligibility, or compliance proof first.

## Screenshot rules

- One core message per frame.
- Show real product UI or a faithful, clearly composited representation.
- Keep headings readable at store thumbnail size.
- Use benefits backed by visible features.
- Localize text, imagery, examples, and layout—not only strings.
- Preserve safe areas and device-specific specifications.
- Do not show impossible states, fake balances, fake ratings, fabricated awards, false notifications, or unavailable features.
- Do not claim `#1`, `best`, guaranteed results, or a price that is not universally true.
- Do not imitate a competitor's distinctive visual system.
- Do not create assets for unsupported form factors.

## Apple discovery and conversion surfaces

### Default product page

Use the default screenshots and previews for the broadest high-value intent. Keep the first frames compatible with users who arrive through browse, brand search, category search, featuring, or an unqualified external link.

### App tags

Audit selected App Store tags for relevance and proof. Tags are currently United States-only and are selected from Apple-generated candidates; the workflow may recommend deselection but must not pretend arbitrary tags can be created.

### Product Page Optimization

Use Product Page Optimization for controlled tests of the default iOS/iPadOS product page:

- Up to three treatments.
- App icon, screenshots, and app previews are eligible treatment assets.
- Treatments can be localized.
- A test runs up to 90 days or until manually stopped.
- Results appear after at least five first-time downloads are associated with the test.
- Alternate icons must already exist in the live binary.
- A new app version or simultaneous listing change can confound the test.

Record control, treatment, traffic proportion, localizations, target lift, start/stop dates, App Analytics result, and decision. Do not use PPO for Custom Product Pages.

### Custom Product Pages

Use Custom Product Pages for distinct audiences, features, campaigns, or search-intent clusters:

- Up to 70 pages per app.
- Each page can vary screenshots, previews, promotional text, keywords, and localizations.
- Each page has a unique URL.
- Approved keywords can route relevant App Store searches to a page; use unique keyword sets per page.
- An optional approved deep link can route users on iOS/iPadOS 18 or later to specific in-app content.
- Page metrics appear after at least five first-time downloads.

For each page, ensure the acquisition message, page creative, metadata, and in-app landing experience form one coherent path.

### Other Apple surfaces

Consider, when applicable:

- App previews
- In-App Events
- Promoted In-App Purchases

Treat each as a separate hypothesis and verify current eligibility, fields, and specifications before implementation.

## Google Play discovery and conversion surfaces

### Default store listing

Use for the broadest product positioning and markets not routed to a targeted listing.

### Custom Store Listings

Use Custom Store Listings for justified market, search, campaign, URL, or user-state variants:

- Up to 50 listings.
- Targeting may use country/region, unique URL, search keyword, Google Ads ad group, or eligible user state.
- App name, icon, descriptions, screenshots, and other graphic assets can differ.
- They are not automatically translated.
- Country targeting cannot overlap across multiple Custom Store Listings.

Create a target-conflict map before recommending multiple pages. Align listing copy, visuals, campaign creative, and user expectation.

### Store listing experiments

Use Play Console experiments for controlled creative or listing hypotheses. Record the exact listing, audience, treatment, metric, guardrails, and concurrent changes. Do not mix experiment evidence with Applyra keyword-rank evidence.

### Other Google Play surfaces

Consider, when applicable:

- Phone/tablet/Chromebook/TV/Watch screenshots
- Feature graphic
- Promo video
- Promotional content

Verify current eligibility and asset specifications before production.

## Store-surface plan

Write `docs/aso/surfaces/store-surface-plan.json` from the bundled template. Keep these states distinct:

- `observed`
- `proposed`
- `implemented-local`
- `submitted`
- `approved`
- `published-verified`
- `disabled`
- `unknown`

Never infer a live page, tag, or experiment from local files alone.

## Creative brief output

Write `docs/aso/creatives/screenshot-brief.md` with:

- Target store/country/locale
- Store surface and surface identifier
- Audience and search intent
- Frame order
- Heading and optional subheading
- Exact product screen or flow to show
- Proof requirement
- Localization notes
- Accessibility/legibility notes
- Policy risks
- Asset dimensions to verify against current store specifications
- Experiment hypothesis

## Experiment backlog

For each candidate:

```text
Hypothesis
Audience/store/market/surface
Control
Treatment
Primary metric
Guardrail metrics
Expected mechanism
Minimum data condition
Decision rule
Rollback plan
Confounders
```

Prioritize experiments by expected impact, confidence, effort, and reversibility. Do not claim statistical significance without the experiment platform's evidence.
