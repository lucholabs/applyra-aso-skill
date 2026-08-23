# Apple App Store metadata and discovery surfaces

## Verify before live publication

Apple can change fields, limits, availability, and product-page features. Re-check the current App Store Connect Help and App Review Guidelines before a live submission. The bundled validator enforces the metadata limits below; it does not publish anything.

## Current hard limits

| Field | Limit |
|---|---:|
| App name | 2–30 Unicode characters |
| Subtitle | 30 Unicode characters |
| Keywords | 100 UTF-8 bytes |
| Promotional text | 170 Unicode characters |
| Description | 4,000 Unicode characters |
| What's New | 4,000 Unicode characters |

Apple's keyword field is byte-limited. Non-ASCII locales can reach 100 bytes well before 100 visible characters.

## App name

Create multiple candidate structures before selecting:

1. `Brand — Category`
2. `Brand: Primary Job`
3. A distinctive brand-only name when brand recognition and conversion evidence justify it

Score candidates on:

- Brand distinctiveness
- Primary intent clarity
- Applyra demand and feasibility
- Readability and truncation risk
- Trademark and policy safety
- Consistency with the installed app name
- Conversion promise

Do not blindly place a generic keyword before the brand. The best structure depends on brand equity, product identity, and search evidence.

## Subtitle

Use the subtitle to add one of:

- Secondary search intent
- Differentiating capability
- Concrete user outcome
- Audience qualifier

Avoid slogans that communicate no searchable meaning. Avoid repeating the exact app-name phrase.

## Keyword field

Rules:

- Maximum 100 UTF-8 bytes.
- Use comma-separated terms with no unnecessary spaces.
- Remove exact duplicates.
- Do not include the app name or company name when already indexed.
- Do not include names of competing apps or companies.
- Avoid irrelevant high-traffic terms.
- Preserve meaningful multiword concepts when tokenization or language requires it.
- Do not assume stemming, singular/plural behavior, or cross-localization; treat those as testable hypotheses.
- Validate every locale independently.

Keep a human-readable source list outside the field so compressed tokens remain explainable.

## Promotional text

Use for current, truthful highlights that can change without a new version. It should:

- Complement rather than repeat the description opening.
- Avoid time-sensitive promises that will become false.
- Avoid rankings, unsupported awards, artificial scarcity, or price claims that vary by territory.

## Description

The description is a conversion and web-discovery surface. Structure it as:

1. Clear value proposition
2. Primary jobs and use cases
3. Verified capabilities
4. Differentiators and proof
5. How it works
6. Privacy/security or regulated-service explanation when relevant
7. Pricing/subscription disclosure where appropriate
8. Support and required legal context

Use plain text. Do not describe future features as current. Do not add unsupported testimonials.

## What's New

For updates:

- Name meaningful user-visible improvements.
- Avoid generic “bug fixes” when concrete details are safe to disclose.
- Do not claim a fix not present in the build.
- Keep localizations consistent with the actual release diff.

## App tags

Apple app tags are a separate discovery surface, not a free-form keyword field.

Current operating rules:

- Tags are derived from the app's `en-US` App Store metadata, artificial intelligence, and human curation.
- Apple applies selected tags by default; authorized App Store Connect users can review and deselect tags.
- Developers cannot assume they can create arbitrary custom tags.
- Tags currently appear only on the United States App Store.
- Deselecting all tags can reduce discoverability.

For an audit:

1. Record the tags currently selected in App Store Connect, or mark them `unknown` when live access is unavailable.
2. Check each tag against implemented functionality and target intent.
3. Recommend deselection only for irrelevant, misleading, sensitive, or poor-fit tags.
4. Review the `en-US` name, subtitle, category, and description because those inputs influence tag assignment.
5. Keep tag decisions separate from Applyra keyword metrics; a store tag and a typed search query are not equivalent evidence.

## Custom Product Pages

Apple currently permits up to 70 Custom Product Pages per app. Each page can have its own screenshots, app previews, promotional text, keywords, localizations, and unique URL.

Use a Custom Product Page only when there is a distinct audience, feature, campaign, or search-intent hypothesis. For each page record:

- Reference name and status
- Audience and market
- Localizations
- Unique message and product proof
- Screenshots, previews, and promotional text
- Assigned approved keywords, when search visibility is intended
- Unique URL and acquisition source
- Optional app deep link and its tested destination
- Primary metric, guardrails, and rollback/disable plan

Important constraints:

- The page and associated metadata must be approved before users can see it.
- Keyword assignment comes from the latest approved app-version keywords.
- Use a unique keyword set for each page so the most relevant page is selected.
- Without an eligible link or search keyword assignment, the default product page remains the normal destination.
- An optional app deep link can route users on iOS/iPadOS 18 or later to specific in-app content; test it and prefer secure universal links.
- Do not create, publish, disable, or delete a page without explicit authorization and an App Store Connect-capable tool.

## Product Page Optimization

Product Page Optimization is an experiment surface for the default iOS/iPadOS product page, not for Custom Product Pages.

Current operating rules:

- Test up to three treatments.
- Eligible treatment assets include app icons, screenshots, and app previews.
- Treatments can be localized.
- A test runs for up to 90 days or until manually stopped.
- Results appear after at least five first-time downloads are associated with the test.
- App icons used in a treatment must already be included in the live app binary.
- Releasing a new version while a test is running can confound results.

Define one coherent hypothesis per test and use App Analytics confidence/lift results. Do not infer statistical significance from Applyra rank movement.

## Localization

Research each priority market. A translated category phrase may not be the phrase users type.

For each locale:

- Preserve brand spelling.
- Validate characters and keyword bytes.
- Check punctuation and script.
- Confirm product availability and claims.
- Mark keyword choices as data-backed or translation-only.
- Do not assume one App Store localization indexes another.
- Localize Custom Product Pages and Product Page Optimization treatments intentionally; do not inherit English creative assumptions automatically.

## File layout

When Fastlane is the existing convention, typical files are:

```text
fastlane/metadata/<locale>/
├── name.txt
├── subtitle.txt
├── keywords.txt
├── promotional_text.txt
├── description.txt
├── release_notes.txt
├── privacy_url.txt
├── support_url.txt
└── marketing_url.txt
```

App tags, Custom Product Pages, and Product Page Optimization may live outside standard Fastlane metadata or require separate App Store Connect/API workflows. Document them in `docs/aso/surfaces/store-surface-plan.json`; do not invent a repository format that the delivery tooling cannot consume.

## Validation

Run both manifest and repository-directory validation. Treat byte-limit errors as blockers. Treat duplicate/overlap warnings as decisions requiring explanation. Treat live tags, page status, approval state, and experiment state as `unknown` unless read from App Store Connect or a current export.
