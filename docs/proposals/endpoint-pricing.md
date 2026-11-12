# Proposal: prices and capabilities per endpoint

Status: proposal only, 12 November 2026. No schema or runtime change is included.

## Problem

Gemini Developer API offers standard and streaming ER 2 endpoints. Their dated
input/output prices match, but only standard supports caching and batch requests.
The current provider schema gives a variant only an `id` and `notes`. The builder
adds one provider-level `current_price`, including cache and batch fields.

A reader can follow the scope notes in the draft entry. Software cannot reliably
choose a streaming price without also seeing fields for unsupported features.
Creating another provider identity for the same provider would hide the issue.

## Proposed shape

Keep one provider file per model/provider, with the actual standard endpoint in
`provider_model_id`. Add optional structured fields to each variant:

- `sources`: references declared in that provider file.
- `pricing`: the same dated price-period shape used at provider level.
- `limits`: variant-specific token or request limits, when published.
- `capabilities`: explicit support for cache, batch, Live API, code execution and
  structured output. Allow supported, unsupported and unknown states.

Provider-level pricing applies only to `provider_model_id`. A variant must not
silently inherit it. With no explicit variant prices, its current price is
unknown, even when prose suggests equality. Repeating equal input/output prices
is safer than accidentally inheriting unsupported cache or batch charges.

The builder would add a separate `current_price` to each variant. A streaming
variant in this example would contain only input/output prices. Source references
and the independent date periods must survive into generated JSON.

If a variant has different access, free-tier or contractual terms, leave it
uncatalogued until those fields can be represented too. This proposal does not
assert that ER 2 has such a difference.

## Validation and compatibility

Keep existing files valid. A reviewed implementation should:

1. Reuse the pricing-period definition rather than maintain two diverging shapes.
2. Check variant source references, duplicate endpoint IDs and overlapping periods.
3. Reject priced cache/batch fields when that variant marks them unsupported.
4. Preserve unknowns instead of copying provider limits or access assumptions.
5. Include tests for a standard/streaming pair, independent date transitions and
   an unpriced variant, plus unchanged output for files without variants.
6. Update contributors and JSON consumers together, including website readers.

This requires a separate implementation review. It does not authorize a website
redesign or new compare, price-history or stack-builder UI.

## Example that motivates the proposal

The official pricing page lists ER 2 standard and streaming input/output amounts
through 31 December 2026 and from 1 January 2027. Cache and batch prices appear
only for standard. The model page explicitly marks streaming cache and batch as
unsupported. Both pages were opened on 12 November 2026.

- [Gemini Developer API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [ER 2 streaming capabilities](https://ai.google.dev/gemini-api/docs/models/gemini-robotics-er-2-streaming-preview)

The existing gap-fix data PR keeps these distinctions in notes while everything
is draft. This proposal makes the distinction safe for future automated readers.
