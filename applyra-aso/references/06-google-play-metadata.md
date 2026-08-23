# Google Play metadata and discovery surfaces

## Verify before live publication

Google can change fields, limits, targeting options, and policy. Re-check current Play Console Help and Google Play Developer Program Policies before a live submission. The bundled validator enforces the hard metadata limits below; it does not publish anything.

## Current hard limits

| Field | Limit |
|---|---:|
| Title | 30 Unicode characters |
| Short description | 80 Unicode characters |
| Full description | 4,000 Unicode characters |

The current Android Publisher API listings schema exposes localized release notes but does not publish a universal hard character limit. The validator therefore does not fail release-note length by default. When a verified Play Console or delivery-tool limit applies, pass `--android-release-notes-limit <n>` explicitly.

## Search mechanics

Google Play does not have Apple's hidden keyword field. Search relevance comes from the listing as a whole and broader app-quality signals. Use target concepts naturally in:

- Title
- Short description
- Full description
- Localized Custom Store Listings when applicable

Do not set a mechanical keyword-density target. Repetition that harms readability or appears manipulative is a failure.

## Title

Use a distinctive brand plus the strongest truthful category or primary job. It must:

- Be recognizable and readable.
- Describe the app accurately.
- Avoid rank/performance claims such as `#1`, `best`, or `top`.
- Avoid price/promotional information or install calls to action.
- Avoid excessive capitalization, emoji, and decorative punctuation.
- Avoid confusing similarity to another app or developer.

Generate multiple candidates and evaluate them with the same data and intent criteria used for Apple, but do not assume the same winner.

## Short description

In one sentence or compact phrase:

- State the primary user benefit.
- Include the strongest secondary concept naturally.
- Differentiate without vague superlatives.
- Match the first screenshots.
- Avoid repeating the title word-for-word.

## Full description

Recommended structure:

1. Opening value proposition
2. Primary use cases
3. Key verified features
4. Differentiators and proof
5. How the app works
6. Privacy/security/regulated-service explanation when relevant
7. Monetization and subscription clarity
8. Support or eligibility details

Use headings and concise bullets where they improve scanning. Avoid:

- Keyword blocks
- Repetitive synonyms
- Unattributed testimonials
- False urgency
- Rankings or award claims without evidence
- Features unavailable in the target country
- References to competitor brands
- Language that implies official affiliation without authorization

## Release notes

Describe the actual build. Keep them useful and localized. Do not use release notes as a keyword-stuffing surface. Apply a workflow-specific length limit only after verifying it in the target Play Console/API/delivery path.

## Custom Store Listings

Google Play currently permits up to 50 Custom Store Listings. They are targeted listing variants, not merely translated copies of the default listing.

A Custom Store Listing can customize:

- App name
- Icon
- Short and full descriptions
- Screenshots and other graphic assets

Current targeting can include:

- Country or region
- Unique Custom Store Listing URL
- Google Ads ad group IDs
- Search keywords
- User state, where eligible

Operational rules:

- One country can be targeted by only one Custom Store Listing at a time.
- Custom Store Listings are not automatically translated. Choose a default language and add intentional translations for the target audience.
- Contact details, privacy policy, and app category remain shared rather than variant-specific.
- The app's distribution/testing state can restrict available targeting combinations.
- Use a unique listing only when the audience, market, acquisition source, or search intent justifies a distinct promise and creative treatment.

For each proposed listing record:

- Internal name and status
- Targeting method and exact values
- Countries/locales
- Audience and search intent
- Metadata and creative differences from the default listing
- Acquisition URL/campaign mapping
- Primary metric and guardrails
- Translation coverage
- Conflict check against other listings
- Publication and rollback owner

Do not create or publish Custom Store Listings without explicit authorization and a Play Console-capable tool.

## Store listing experiments

When Play Console supports the intended experiment:

- Define one variable or coherent treatment hypothesis.
- Choose the audience and listing surface before writing assets.
- Align title, short description, screenshots, icon, and feature graphic with the same intent.
- Define the primary metric before launch.
- Keep release, paid acquisition, pricing, and other listing changes separate where possible.
- Use Play Console experiment evidence rather than declaring success from Applyra rankings alone.

## File layout

When Fastlane Supply is the existing convention:

```text
fastlane/metadata/android/<locale>/
├── title.txt
├── short_description.txt
├── full_description.txt
├── changelogs/
│   └── <version_code>.txt
└── images/
```

Custom Store Listings and experiments may require additional tooling or Play Console/API workflows. Document them in `docs/aso/surfaces/store-surface-plan.json`; do not create a parallel format that the repository cannot publish.

## Validation

Treat length, missing required fields, control characters, and forbidden terms as blockers or high-priority findings. Treat keyword repetition heuristics as warnings that need human/context review. Treat live Custom Store Listing targets, publication status, and experiment state as `unknown` unless read from Play Console or a current export.
