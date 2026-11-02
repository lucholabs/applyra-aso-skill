# Product truth and app context

## Goal

Build a compact, evidence-backed model of the app before doing ASO. Metadata must describe the product that users can install now, not a roadmap, pitch deck, or intended feature.

## Repository inspection

Inspect, when present:

- Root and nested `AGENTS.md`
- `package.json`, workspace files, native project files
- iOS bundle identifiers and Android application IDs
- Expo/React Native config
- Feature flags and remote config
- Navigation routes and onboarding
- Paywalls, subscriptions, IAP/SKU definitions
- Localization catalogs
- Privacy policy, terms, support, and compliance documents
- Existing Fastlane/Supply/store metadata
- Screenshots and marketing assets
- Analytics event definitions
- Release notes and changelog
- Tests that demonstrate a user-facing capability
- Country or platform restrictions

Do not infer functionality from filenames alone. Trace the user flow or implementation sufficiently to confirm it.

## Required context fields

For a full run, write `docs/aso/context/app-context.yaml` using [the canonical context template](../assets/app-context.template.yaml). Reuse existing context and preserve extra project fields. For a focused question, inspect only the product and market facts needed to answer it; no context file is required.

The template covers app identity/stage, audience/jobs, implemented and unavailable features, monetization, markets/locales, store surfaces, compliance, business goals, resources and dated sources. An app repository is useful evidence, not a prerequisite. Without one, use user-provided product facts, a live demo, store listings or official product documentation; label the evidence level and ask only about claims whose ambiguity changes the result. Do not treat a competitor listing as proof of the target app's features.

## Business goals and constraints

Capture the primary goal with metric name, definition/denominator, store/market, baseline and period, target and deadline, and evidence source. Treat a user target as an objective, not a forecast. If unavailable, keep the baseline/target null and propose what to measure.

Capture available budget and currency, team capacity, design/localization support, analytics sources, release schedule, review lead time and other constraints. Keep private commercial figures in ignored local evidence or the user's established private workspace; a public context file should contain only approved summaries or private references.

Use these inputs to choose work: a solo developer with no designer may need a copy fix before a new preview; low traffic may favor one coherent candidate over a multi-treatment test. Select one primary KPI per decision, with quality guardrails. Do not infer installs or revenue from visibility. If the user already supplied these facts, reuse them rather than repeating an intake interview.

## Claim-evidence matrix

For every material store claim, capture:

| Claim | User value | Evidence | Availability | Confidence | Allowed in metadata |
|---|---|---|---|---|---|
| Example capability | Why it matters | File, test, live flow, or official document | iOS/Android/countries | High/medium/low | Yes/no/qualified |

Rules:

- High confidence: directly implemented and testable.
- Medium: implemented but gated, region-limited, or dependent on a third party.
- Low: documentation-only, roadmap, or unclear.
- Only high-confidence claims may be stated without qualification.
- Medium-confidence claims must include the real limitation.
- Low-confidence claims must not appear in store metadata.

## App identity resolution

1. Extract the iOS bundle ID and Android package name from the repository.
2. Call `list_applications`.
3. Match by store identifier first, then title/developer/market.
4. If the same app is tracked in multiple countries or languages, treat each tracking entry as a separate ASO market context.
5. If no match exists, do not call `add_application` without authorization.

## Audience and intent

Do not use demographics alone. Define:

- What problem triggers the search?
- What task does the person expect to complete?
- What alternatives do they compare?
- What proof removes hesitation?
- What causes a poor-fit install or uninstall?

Every target keyword must map to a concrete expected job.

## Platform and market truth

A feature can be valid on one platform and absent on another. A service can be legal or available in one country and blocked in another. Build a matrix when needed:

| Feature/claim | iOS | Android | Countries | Dependency | Metadata consequence |
|---|---|---|---|---|---|

Do not reuse a global description when these differences materially affect the user promise.
