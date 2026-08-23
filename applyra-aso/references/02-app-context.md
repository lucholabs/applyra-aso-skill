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

Write `docs/aso/context/app-context.yaml` with:

```yaml
app:
  name:
  ios_bundle_id:
  ios_app_store_id:
  android_package_name:
  platforms: []
  primary_category:
  secondary_category:
  stage: draft|prelaunch|live
  current_version:

audience:
  primary:
  secondary:
  jobs_to_be_done: []
  pains: []
  desired_outcomes: []

product:
  one_sentence_value:
  differentiators: []
  verified_features: []
  unavailable_or_future_features: []
  offline_capabilities: []
  integrations: []
  monetization:
  pricing:
  account_required:
  geographic_restrictions: []

localization:
  app_locales: []
  store_locales: []
  priority_markets: []

compliance:
  vertical:
  regulated_claims: []
  third_party_services: []
  privacy_sensitive_features: []
  prohibited_or_unverified_claims: []

sources:
  repository_commit:
  inspected_paths: []
  live_store_checked_at:
  applyra_checked_at:
```

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
