# Competitor monitoring

Read when comparing competitors across time. For one-time selection and gap analysis use [competitor analysis](04-competitors.md). Monitoring is a comparison workflow, not an implied background job.

## Watchlist and budget

Reuse the user's existing competitors and context. Select the small set relevant to the requested decision, market and interval. A proposed watchlist may be saved locally; changing Applyra relationships needs authorization. Fetch only the dimensions needed and reuse saved research. Follow the shared account queue, request budget and history limits in [the MCP guide](01-applyra-mcp.md).

## Snapshots

Save normalized snapshots to `docs/aso/data/<date>/competitor-snapshot.json` using [the snapshot template](../assets/competitor-snapshot.template.json). Use task-controlled filenames, public app identity and exact store/country/locale. Record requested dimensions and each observation's source time, retrieval time, source and value. A source's cached observation time may differ from when it was fetched.

Possible dimensions:

- Public metadata from `list_competitors` or a dated store listing. Do not imply public access to a competitor's hidden iOS keyword field.
- Shared keyword ranks from available tracked histories or inspections; record the queried set and top-N coverage. Lack of an app in the top 20 inspection results does not prove it is outside the top 100.
- Rating aggregate and count, with comparable store scope.
- Chart rank from `top_charts`, keeping category and collection fixed.
- Asset URL/content hash and a visual inspection when available. A changed URL alone does not prove a changed screenshot; an unchanged URL does not prove identical content.
- Price/trial/paywall only from current observed evidence, with currency, territory and eligibility. Price changes do not prove the competitor's intent.

Private fields, review text, revenue estimates, historical screenshots and a competitor's experiment winner are not supplied by these Applyra calls. Use an authorized additional source or mark unknown. Do not imply a historical listing exists merely because current metadata is available.

## Compare and decide

Join observations by app, store, country/locale and dimension (including keyword/chart category/collection as applicable). Compare only compatible units, query coverage and source scope. Preserve the old snapshot; add the new one.

Classify each comparison as `changed`, `unchanged`, `new-observation`, `not-comparable` or `unknown`. Missing observations are unknown rather than deletion. With only one snapshot, establish a baseline and state that change cannot yet be measured. Record old/new value and both observation times, avoiding causal conclusions from a coincidence. A cached old response is not a fresh confirmation of stability.

Separate observed changes from hypotheses and prioritize actions by relevance, confidence and effort. Do not automatically chase a new competitor keyword or rewrite copy after a one-day rank movement. A product gap must remain a product action, not an unsupported claim.

## Report and cadence

Write `docs/aso/reports/<date>-competitor-update.md` when a saved report is requested: period/coverage, changes, unchanged comparable observations, data gaps, opportunities, threats and action owners. Suggest a weekly or release-based cadence when useful; create a schedule/notification only if requested and the environment provides that capability. Do not claim a manual report will keep running.
