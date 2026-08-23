# Keyword research and prioritization

## Objective

Select search terms that are simultaneously:

- Relevant to the installed product
- Matched to the searcher's intent
- Supported by observable demand
- Feasible for the app's current authority
- Safe under store policy and trademark rules
- Appropriate for the exact store, country, and locale

A keyword is not good merely because its traffic is high or its difficulty is low.

## Candidate sources

Generate and normalize candidates from:

1. Verified product jobs and features
2. User problem language
3. Existing tracked keywords
4. Applyra related keywords
5. Applyra autocomplete
6. Applyra niche analysis
7. Direct competitor coverage
8. Top-chart category language
9. Search terms or analytics exports supplied by the user
10. Current metadata and reviews, when available

Start with 20–40 high-quality seeds per major market, not hundreds of weak synonyms.

## Hard gates

Reject before scoring when any is true:

- Relevance below 70/100
- Intent fit below 70/100
- Competitor trademark or confusing brand reference
- Feature not implemented or unavailable in the market
- Deceptive, exaggerated, or unverifiable claim
- Policy-sensitive term with no evidence or authorization
- Wrong audience, category, or task
- Literal translation that local users do not appear to search
- Term exists only because it is broad and popular

Document the rejection reason.

## Evidence fields

For each candidate keep:

```text
keyword
display_form
normalized_form
store
country
locale
source
traffic_score
difficulty_score
kei_score
kei_level
current_rank
previous_rank
rank_trend
top_apps
related_terms
relevance
intent_fit
product_fit
policy_risk
trademark_risk
opportunity_score
confidence
bucket
destination
decision
reason
observed_at
```

Never fill unavailable numeric metrics with zero.

## Opportunity score

Use this as a transparent prioritization aid, not as a guarantee.

### Inputs

- `R`: product relevance, 0–100
- `I`: search intent fit, 0–100
- `T`: Applyra traffic score, 0–100
- `F`: feasibility = `100 - difficulty_score`
- `G`: rank-gap value:
  - rank 1–3: 10
  - rank 4–10: 20
  - rank 11–30: 45
  - rank 31–50: 65
  - rank 51–100: 80
  - rank >100 or null: 100
- `D`: differentiation/proof strength, 0–100
- `M`: momentum, 0–100, only when sufficient history exists

### Weights

```text
R  0.25
I  0.25
T  0.15
F  0.15
G  0.10
D  0.07
M  0.03
```

Formula:

```text
Opportunity = sum(weight × available_input) / sum(available_weights)
```

Rules:

- Apply hard gates before calculating.
- If a value is missing, omit its weight and lower confidence.
- Do not manufacture `M` from one or two daily movements.
- Keep Applyra's KEI visible as a separate source metric; do not secretly blend it twice.
- A current top-ten term with high value belongs in `protect`, even if its rank-gap component is low.

## Confidence

| Level | Conditions |
|---|---|
| High | Product fit confirmed; Applyra traffic and difficulty available; rank/history or top apps available; market/locale exact |
| Medium | Product fit confirmed; at least one demand/competition metric missing or limited history |
| Low | Mostly qualitative, translated, or inferred; no reliable market metric |

Do not put low-confidence terms in the app name/title without explicitly flagging the bet.

## Buckets

### Protect

High relevance and value, current rank 1–10. Preserve metadata coverage and watch competitors.

### Grow

Current rank 11–50 with good intent and enough demand. Prioritize metadata/creative alignment and authority.

### Attack

Rank >50 or unranked, meaningful traffic, feasible difficulty, strong product differentiation.

### Long-tail

Lower demand but precise intent and good conversion fit. Useful in Apple's keyword field, Google descriptions, custom listings, and experiments.

### Reject

Wrong intent, weak demand evidence, unwinnable relative to app authority, unsupported feature, trademark/policy risk, or redundant term.

## Apple allocation

Decide at token and concept level:

1. App name: brand plus the strongest truthful category/use-case signal that fits.
2. Subtitle: secondary intent, differentiator, or concrete benefit.
3. Keyword field: unique, relevant terms not already covered by name/subtitle/company; maximum 100 UTF-8 bytes.
4. Description and promotional text: conversion and web-facing clarity, not a replacement for the indexed fields.

Do not automatically use a keyword-first app name. Compare brand equity, uniqueness, conversion clarity, and search evidence.

## Google Play allocation

There is no hidden keyword field. Use:

1. Title: brand plus primary category/use case.
2. Short description: primary benefit and secondary intent.
3. Full description: natural semantic coverage of selected clusters, features, proof, and use cases.
4. Custom store listings and experiments: intent-specific variants when available.

Never target a fixed keyword density. Natural relevance and comprehension outrank repetition.

## Per-market research

For every priority country/locale:

1. Reuse existing tracked data.
2. Run local autocomplete on 1–3 strongest seeds.
3. Inspect the best deduplicated candidates.
4. Compare local competitor rankings.
5. Decide whether the English concept translates, transliterates, or changes.
6. Mark unverified translations.

Do not copy metrics from `en-US` to `en-GB`, `es-ES` to `es-MX`, or one store to another.

## Output

Write `docs/aso/research/keyword-decisions.csv` and a concise summary containing:

- Primary keyword cluster
- Secondary cluster
- Protect/grow/attack/long-tail sets
- Rejected risky terms
- Platform allocation
- Market differences
- Data gaps
- Applyra quota used
