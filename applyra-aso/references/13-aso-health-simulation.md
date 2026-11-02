# ASO Health and metadata simulation

Read for listing audits, rewrites, and comparisons of proposed metadata. Contracts verified on 2026-11-02 against Applyra MCP 1.8.0 and the connected tool schemas.

## Interpret the listing audit

Call `get_aso_health` for the exact tracked market. Keep its 0–100 listing assessment separate from observed visibility, rank, and conversion. Its axes are coverage (searched vocabulary in indexed fields), targeting (competition relative to the app's maturity), and appeal (rating, assets and freshness). A text rewrite cannot fix a low appeal axis; prioritize the reported constraint rather than pursuing a higher score alone.

Preserve the returned maturity tier: 1 Emerging, 2 Growing, 3 Established. A targeting verdict depends on that tier; do not apply one difficulty cutoff to every app. Keep `reachable`, `ambitious`, and `out-of-reach` as source verdicts alongside the skill's own relevance decisions.

Data caveats:

- `report: null` means no audit, not zero. `targeting.assessable: false` means no searched term to grade, not a failed targeting score.
- Field state `empty` is a known blank; `missing` can mean the private iOS keyword field was never supplied. Obtain it from the repository, user or authorized App Store Connect source; do not invent it from public listings.
- `fields[].text` can be truncated. Retrieve full live text from `list_applications` before editing.
- API field `subtitle` means Google Play's short description when `store = GPLAY`.

Use `include_words: true` only for a detailed coverage diagnosis. Distinguish absent demand from pending data. An `in-phrase` word can be valuable even without standalone demand: check `phrases[]` before deleting it. Google Play's long-description statuses (`covered`, `missing`, `extra-reach`) describe coverage relationships, not a recommended repetition density.

Sources: [ASO Health](https://www.applyra.io/docs/concepts/aso-health), [official tool contracts](https://github.com/applyra-io/mcp-server/blob/main/src/server.ts).

## Check before scoring

1. Run the bundled validator on a complete package manifest, or use its platform validation function for supplied partial fields. The manifest CLI intentionally requires complete platform fields.
2. When connected and budget permits, call `check_metadata` on each candidate using `store`, `title`, `subtitle`, `description`, and iOS-only `kw_field` as applicable. Map manifest `name`/`short_description`/`full_description` to those API fields.
3. Resolve errors and read warnings even when `valid: true`. Preserve rule and severity; Apple and Google can treat the same promotional wording differently. This check does not prove App Review approval or product truth.
4. Only then use a simulation allowance on a meaningful candidate.

The checker reports UTF-16 lengths, formatting/policy findings, and keyword diagnostics. It complements local validation and consumes an API request even though it performs no store lookup.

The iOS keyword field allows 100 characters including separators, following [Apple’s product-page guide](https://developer.apple.com/app-store/product-page/) and Applyra’s checker. Use UTF-16 units; CJK and accented letters do not consume their UTF-8 byte length. Apple’s platform-version reference still says bytes, so cite the product-page guidance when explaining this correction.

## Simulate with comparable context

### Candidate packages

Recommend one package by default. When alternatives resolve a real tradeoff, add up to two: for example, protect existing intent, explore an evidenced keyword cluster, or emphasize a different verified benefit. Give each package one hypothesis and keep the complete fields together per platform/market. Do not assemble a final listing by independently picking the highest-scoring field from each package; revalidate the final combination.

Use [the candidate comparison template](../assets/metadata-comparison.template.json). For full packages, keep each candidate in its own complete metadata manifest under `docs/aso/metadata/candidates/` and validate it with the existing CLI. Only the chosen package becomes `metadata-manifest.json`. A single-field request can compare the supplied field inline and validate it through the platform validation function; do not invent the remaining fields to satisfy the manifest schema.

For each package record exact text or manifest reference, hypothesis, UTF-16 counts and limits, keyword-to-field coverage, protected/new/lost phrases, product evidence, validation warnings, comparable context and reason to choose or reject it. Distinguish literal token presence, inferred phrase coverage and coverage reported by Applyra; do not imply every possible word combination is indexed.

Compare alternatives locally before spending allowance. Reuse relevant saved runs; check/simulate only decision-relevant candidates within the account's remaining budget. Three written options do not authorize three simulations. When checks or simulations are unavailable, keep their results null with a reason and choose provisionally using product fit, protected phrases, readability and validation. Never score an untested candidate as zero or promise rank/install gains.

### Simulation procedure

Reuse `list_metadata_simulations` and `get_metadata_simulation` before spending another run. The list carries draft titles and scores; only the detail tool returns all four fields and the assumed context.

For an existing app, pass its numeric internal `app_id` and the changed fields:

```json
{ "app_id": 344, "title": "Example: Offline Journal" }
```

The ID above is illustrative; resolve the actual one. Omitted text and context come from that app's live listing. Explicitly pass the private iOS keyword field when known and not already available to Applyra. Keep unchanged rating, screenshot count, age and language coverage so a wording comparison measures wording.

Without `app_id`, pass `store`, `country`, and `lang`. The default context represents an unpublished app with no rating or screenshots and one language, so its global score cannot be compared with a real app's. Compare coverage, or supply evidenced context. Label hypothetical context overrides as scenarios; never describe them as observed improvements.

Each `simulate_metadata` call saves research history and consumes simulation/API allowance. It does not track keywords or submit metadata to a store. Apply the research governor in `01-applyra-mcp.md`, change something meaningful between calls, and stop when the decision is supported.

For every candidate retain:

- Exact draft, market, observation time, assumed context and baseline.
- Global and per-axis scores/deltas, keeping null deltas null.
- `flags[]`, request `notes[]`, and every `lost_phrases[]` entry with removed words, demand and tracked rank when returned.
- Decision and product/intent justification, including why any lost phrase is acceptable.

Do not choose a higher global score blindly. A removed word can break a valuable phrase even when the score rises. Reallocate or restore it where supported, revalidate, and simulate again only if allowance permits. `words_probed` and `words_fetched` describe research/cache work, not demand or predicted installs.

Save normalized results to `docs/aso/metadata/simulation-comparison.json` when simulation is in scope. Keep saved-run IDs private unless needed for the user's workflow; exclude account-wide drafts unrelated to the task.

Sources: [Metadata Simulator](https://www.applyra.io/docs/tools/metadata-simulator), [MCP metadata tools](https://www.applyra.io/docs/api/mcp-tools). Applyra's dashboard AI writer is not exposed as an MCP tool; the assistant writes the draft and Applyra scores it.
