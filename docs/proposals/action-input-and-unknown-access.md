# Proposal: action inputs and unverified access

Status: proposal only, 12 November 2026. No active schema changes.

## Action trajectories as inputs

Cosmos 3's official model reference lists action arrays as generator inputs as
well as generated outputs. Current `modalities.input` has `robot-state` but no
`actions`. Future control trajectories must not be relabelled as current state.

Add `actions` to that input enum. Keep `robot-state` for observed state. A later
structured interface can specify trajectory dimensions, time units, horizon and
embodiment when sources publish them. Unknown settings should stay absent.

A reviewed implementation should validate both values, retain old entries and
carry action-input information into generated JSON. Until then, draft Cosmos 3
can omit the optional modalities object and explain its interface in sourced
notes without claiming an incomplete object is exhaustive.

Source, opened 12 November 2026:
[NVIDIA Cosmos 3 model reference](https://docs.nvidia.com/cosmos/latest/cosmos3/model_reference.html).

## Model exists, access is not established

The pi0.7 announcement and paper establish a model. The later Pi API beta post
offers company models through a waitlist but does not name a pi0.7 endpoint.
Neither observation proves public, partner-only, research-only or unavailable
access for that exact model. Current `access.type` requires one of those factual
claims and has no unverified value.

Add an `unverified` model-access value, requiring a sourced note explaining the
bounded checks and remaining gap. Do not allow it together with a confirmed
access type for the same route. It must not create a provider route, a free price
or an inferred entitlement. A provider should still require an actual named
model/service mapping before it can be catalogued.

The maintainer should choose whether such records remain draft-only. Test the
chosen publication rule and update contribution instructions before adoption.
Until then, pi0.7 is reported as researched but withheld from model TOML, rather
than forced into an unsupported access classification.

Sources, opened 12 November 2026:

- [pi0.7 announcement](https://www.pi.website/blog/pi07)
- [pi0.7 paper](https://www.pi.website/download/pi07.pdf)
- [Pi API beta announcement](https://www.pi.website/blog/api-beta)
- [Pi API waitlist](https://www.pi.website/waitlist)

These are separate vocabulary additions for review, not permission to implement
them inside a data batch or to release any model as verified.
