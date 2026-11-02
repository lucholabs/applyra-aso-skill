# Measurement and experiments

## Separate the funnel

Applyra measures discoverability signals. Store analytics and product analytics measure later stages.

| Stage | Example metrics | Typical source |
|---|---|---|
| Search visibility | Keyword rank, visibility score, chart rank | Applyra |
| Store exposure | Impressions, product-page views | App Store Connect / Play Console |
| Store conversion | Downloads/installs, conversion rate | Store analytics |
| Activation | Onboarding completion, first value event | Product analytics |
| Quality | Retention, crashes, ratings, reviews | Product/store analytics |
| Monetization | Trials, subscriptions, revenue, refunds | Store/product analytics |

Do not use Applyra visibility as a substitute for conversion, retention, or revenue.

## Baseline

For a focused measurement question, collect only the baseline/metric required by that question. Full campaign or listing experiments should use the primary KPI and resource constraints in app context; keep target outcomes distinct from forecasts. A proposed checkpoint or weekly competitor report is not a scheduled automation.

Before changing metadata, tags, targeted pages, or creatives, save:

- Timestamp and repository commit
- Live default metadata by locale
- Apple app tags and their selected state, when available
- Apple Custom Product Pages and Product Page Optimization status, when available
- Google Play Custom Store Listings and experiment status, when available
- Tracked keywords and ranks
- 30-day and 90-day rank histories
- App visibility score history
- ASO Health and axes, separately from observed visibility
- Chart notes, detected app updates and store algorithm events returned with histories
- Competitors and their visibility
- Rating score and count
- Relevant store analytics, when available
- Product events, when available
- Seasonality, campaigns, featuring, pricing, and release events

Unknown live state must remain `unknown`; local files do not prove publication.

Request only history the plan exposes: Free includes seven days. Record unavailable days explicitly instead of treating a short history as a complete 30/90-day baseline.

## Notes and event comparisons

Read `list_notes` and the `events` in visibility/rank histories to align campaigns, metadata changes, releases and algorithm updates. To record an event in Applyra, the user must authorize `add_note` or `update_note`; otherwise keep the local change log. Notes accept 1–120 characters and today or a past date. Supply the actual event day explicitly (the default is today in UTC), and select `scope: market` for a change specific to the resolved market or `app` for an app-wide event. Do not record a planned release as already published.

Use the stable `note.id` for edits/removal, never its chart `number`: moving or deleting notes can renumber flags. `add_note` is not idempotent; check `list_notes` after an ambiguous timeout before retrying. `delete_note` requires specific authorization.

For an observed change, call `compare_events` with the resolved app and optional `keyword_id`. Windows are `7`, `14` or `30` days on each side; Free supports only 7, while longer windows require Unlimited. The event day is excluded. Visibility gains have a positive change; rank improvements have a negative change because lower ranks are better. This tool counts an unranked day as #101 and reports `unranked_days`; disclose that convention rather than presenting it as an observed #101 rank.

Read `measured_days`, `pending_days`, `hidden_days`, `history_start`, and `locked` before interpreting averages. Future days are pending and pre-plan days hidden, not zero. Read `alongside` for overlapping notes, releases and algorithm events. A before/after association does not establish causation; do not report an incomplete or locked comparison as a measured lift.

Sources: [Notes and events](https://www.applyra.io/docs/applications/notes-and-events), [MCP event tool contracts](https://github.com/applyra-io/mcp-server).

## Change log

For every change record:

```text
date
store
country
locale
surface
surface_id
version
field_or_asset
old_value
new_value
target_keyword_cluster
hypothesis
implementation_source
submitted_at
approved_at
published_at
measurement_start
confounders
rollback_value
```

A local file edit is not a published change. Keep local, submitted, approved, and published states distinct.

## Platform experiment facts

### Apple Product Page Optimization

- Up to three treatments.
- Tests can vary app icons, screenshots, and app previews.
- Tests run for a maximum of 90 days unless stopped earlier.
- Results appear after at least five first-time downloads are associated with the test.
- Use App Analytics estimated lift and confidence, not a homemade significance claim.
- A new app version or simultaneous page change can invalidate attribution.

### Apple Custom Product Pages

- Measure each page separately in App Analytics.
- Page metrics appear after at least five first-time downloads.
- Segment by source, territory, device, and downstream value when available.
- Compare page performance only when audiences and acquisition sources are sufficiently comparable.

### Google Play Custom Store Listings and experiments

- Keep each listing's targeting rule and acquisition source in the baseline.
- Measure conversion in Play Console/analytics, not through Applyra alone.
- Do not compare listings as though traffic were randomized when targeting differs.
- For controlled experiments, use Play Console's result and confidence reporting and record concurrent releases, campaigns, and listing edits.

## Evaluation checkpoints

Default checkpoints when no better cadence exists:

- D+7: detect breakage, indexing, routing, or severe negative movement
- D+14: early directional read
- D+28: primary review across multiple weekly cycles
- D+56 or D+90: durable trend and seasonality check

Use enough observations for the market's volume. Low-volume terms may need longer. Do not declare success from one day or from crossing only the platform's minimum reporting threshold.

## Decision model

### Keep

- Target terms improve or remain strong
- Conversion does not materially deteriorate
- Quality guardrails remain healthy
- Result is consistent across enough observations
- Routing sends the intended audience to the intended page

### Iterate

- Discoverability improves but conversion weakens
- One market improves while another declines
- Supporting terms move but primary intent remains unclear
- A targeted page converts but attracts lower-quality users
- Data is promising but insufficient

### Roll back or disable

- Material sustained decline relative to baseline
- Listing creates poor-fit installs or policy risk
- Core protected terms lose visibility without offsetting gains
- Conversion or quality guardrails deteriorate
- Published metadata contains an incorrect claim
- Targeted-page routing sends the wrong audience or deep link fails

Document uncertainty and confounders.

## Causality discipline

Account for:

- App release and bug fixes
- Paid acquisition
- Featuring
- Seasonality
- Competitor releases
- Rating changes
- Pricing/promotions
- Country availability
- Store algorithm or reporting changes
- Multiple simultaneous metadata or creative edits
- Changes in Custom Product Page, Custom Store Listing, or campaign targeting

Use “associated with” rather than “caused by” when control is weak.

## Output

Write:

- `.aso-private/<date>/baseline-raw.json` only when raw reproducibility is necessary (ignored)
- `docs/aso/data/<date>/baseline.json` with normalized/redacted evidence
- `docs/aso/surfaces/store-surface-plan.json`
- `docs/aso/experiments/experiment-plan.md`
- `docs/aso/experiments/change-log.csv`
- `docs/aso/reports/<date>-measurement-review.md`
