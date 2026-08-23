# ASO localization

## Principle

Localization is market research plus adaptation, not word-for-word translation. A grammatically correct phrase can still be a poor search term.

## Market selection

Prioritize markets using available evidence:

- Existing users, installs, revenue, or retention
- Applyra tracked apps and keyword visibility
- Product language support
- Store availability
- Customer support capability
- Legal or service availability
- Competitive opportunity
- Localization cost and quality

Do not create a store promise in a language the product cannot reasonably support without clearly documenting the mismatch.

## Locale workflow

For every target locale:

1. Confirm store and country.
2. Confirm the app UI supports the language or document the gap.
3. Gather local seed terms from user intent, competitor language, autocomplete, and Applyra.
4. Inspect the best candidates with exact market parameters.
5. Choose concepts, not literal translations.
6. Draft metadata under local limits.
7. Run automated validation.
8. Run linguistic risk checks.
9. Mark evidence level.
10. Record who or what reviewed it.

## Evidence labels

- `data-backed`: local Applyra metrics and market evidence.
- `market-informed`: local competitors/autocomplete but incomplete metrics.
- `translated-unvalidated`: translation only; no reliable local search evidence.
- `blocked`: cannot publish safely due to product, legal, or linguistic gap.

Never present translated-unvalidated keyword choices as measured opportunities.

## Preservation rules

Do not translate unless product style explicitly does:

- Brand name
- Legal entity name
- URLs
- Email addresses
- Product codes
- Blockchain/network/token symbols
- API names and protocol names
- Registered marks
- Usernames and identifiers

Use a glossary for domain terms with one approved translation per locale.

## Automated checks

Run or manually verify:

- Character/byte limits
- Empty or duplicate fields
- Placeholder parity
- Format specifier parity
- URL and email preservation
- Numeral and currency correctness
- Mixed-script contamination
- Accidental source-language carryover
- RTL direction and punctuation
- CJK byte budget for Apple keywords
- Untranslated brand atoms
- Prohibited claims
- Locale-to-country mismatch

## Linguistic review

For high-priority markets, obtain native or expert review of:

- Search naturalness
- Product meaning
- Tone/register
- Cultural sensitivity
- Legal/financial/medical wording
- Screenshot readability
- Call-to-action appropriateness

Machine fluency is not proof of correct domain meaning.

## Fallback behavior

When native review or local metrics are unavailable:

- Produce a conservative localization.
- Label it `translated-unvalidated`.
- Keep regulated claims minimal.
- Avoid committing the app title to a low-confidence keyword.
- Add a concrete validation task to the experiment plan.
