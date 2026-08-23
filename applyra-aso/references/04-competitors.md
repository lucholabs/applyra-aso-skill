# Competitor analysis

## Purpose

Find discoverability and conversion gaps without copying competitors or mistaking category leaders for true substitutes.

## Competitor classes

Classify each app:

- **Direct** — same core job, audience, and expected outcome.
- **Adjacent** — overlaps one job but solves a different primary problem.
- **Aspirational** — category leader useful for quality benchmarks, not keyword parity.
- **Irrelevant** — appears for a term but does not satisfy the target intent.

Only direct competitors should drive core keyword-gap decisions.

## Discovery sequence

1. Call `list_competitors` for existing workspace relationships.
2. Use top apps from `inspect_keyword`.
3. Use `top_charts` after resolving valid categories with `list_top_chart_categories`.
4. Cross-check app function from store metadata and, when available, product pages.
5. Select 3–8 direct competitors per market.
6. Prepare additions for Applyra only when valuable; call `add_competitor` only with authorization.

## Comparison fields

| Dimension | Evidence |
|---|---|
| Store/country/locale | Exact Applyra/store context |
| App title and developer | Store metadata |
| Primary job | Listing and product evidence |
| Visibility score | Applyra |
| Rating and rating volume | Applyra/store |
| Shared keywords | Applyra tracked/inspection data |
| Terms competitor ranks for and app does not | Applyra |
| Terms both rank for | Applyra |
| Positioning promise | Metadata |
| Proof and differentiator | Metadata/screenshots/product |
| Localization depth | Store listing |
| Creative opening sequence | Screenshots/video |
| Pricing/monetization | Store/product evidence |
| Risk | Trademark, misleading claims, mismatch |

## Gap types

- **Coverage gap** — competitor ranks for a relevant term the app does not cover.
- **Authority gap** — term is covered, but the app ranks poorly due to installs/ratings/retention or category authority.
- **Intent gap** — app metadata targets a phrase but listing proof does not match the searcher's expected job.
- **Conversion gap** — app ranks but the first impression is weaker or unclear.
- **Localization gap** — competitor uses market-native positioning while the app uses literal translation.
- **Product gap** — competitor provides a capability the app lacks. This is a roadmap input, not a metadata keyword.
- **Data gap** — insufficient metrics; do not disguise it as an opportunity.

## Rules

- Never recommend competitor brand names in store metadata.
- Never copy sentences, visual composition, or unique creative claims.
- Do not infer installs or revenue from rating count alone.
- Do not call a keyword gap when the app cannot satisfy the intent.
- Separate an ASO fix from a product or authority problem.
- Preserve the market context for every comparison.

## Output

Write `docs/aso/research/competitor-gap.md` with:

1. Competitor set and classification
2. Market-by-market visibility comparison
3. Keyword overlap and gaps
4. Positioning and creative gaps
5. Product gaps excluded from metadata
6. Priority actions ranked by impact, confidence, and effort
7. Any proposed Applyra competitor changes awaiting approval
