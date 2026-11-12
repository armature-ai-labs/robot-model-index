# Robot Model Index

**AI models for robots, from LLMs to VLAs and world models: what each one does, how to get it, what it costs, whether you can use it commercially, what it runs on, and what the catch is. Every fact sourced and dated.**

An open catalog by [Armature AI Labs](https://github.com/armature-ai-labs), in the spirit of [Portkey Models](https://github.com/Portkey-AI/models) but built for robotics. It is also the model registry for [Commutator](https://github.com/armature-ai-labs/commutator), our open-source AI gateway for robots.

> Status: early. 3 starter entries, all still draft (unpublished until verified). Target: 60 verified entries by February 2027.

## Why this exists

Choosing models for a robot means answering questions no single site answers:

- **Can I use it commercially?** Licence chains are easy to get wrong. π0.5's code is Apache 2.0, but the model is built on PaliGemma, which brings the Gemma Terms of Use with it.
- **What does it cost, and until when?** Gemini Robotics ER 2 costs $1 / $5 per million tokens through 31 December 2026, then $2 / $10. Most price lists show only one of those.
- **Can I even get it?** Many headline robot models are partners-only or waitlisted.
- **Will it run on my robot's computer?** Vendor claims and real measurements on an 8 GB Jetson are different things.

## What's in an entry

| Area | Examples of fields |
|---|---|
| Identity | name, developer, roles (VLA, world model, embodied reasoning...), lifecycle (preview, released...) |
| Access | open weights, public API, waitlist, partners only |
| Licence chain | code, weights, base models, training data, commercial use (yes, conditional, no, unclear) with the reason |
| Robot interface | action output, action chunk, denoising steps, state and action dimensions, image size |
| Hardware fit | per device, marked measured by Armature, community-reported, vendor-claimed or untested |
| Benchmarks | score, settings, who ran it (vendor, independent, Armature) |
| Providers | endpoint name, regions, limits, free tier and data use, dated price periods, terms |
| Limitations | the catches, each with a source |

## Layout

```
models/<developer>/<model-id>.toml       what the model is (provider-independent)
providers/<provider>/<model-id>.toml     how one provider offers it, incl. pricing over time
licences/<licence-id>.toml               plain-language licence obligations
schema/                                  JSON Schemas for all three
scripts/validate.py                      schema + data-rule checks (runs in CI)
scripts/build.py                         builds the published JSON
scripts/weekly_check.py                  price cross-check and freshness report
```

## Using the data

Verified entries are published as static JSON on every merge to `main`:

- `https://armature-ai-labs.github.io/robot-model-index/index.json`: all models with their providers and today's price
- `https://armature-ai-labs.github.io/robot-model-index/models/<model-id>.json`: one model
- `https://armature-ai-labs.github.io/robot-model-index/licences.json`: licence summaries
- `https://armature-ai-labs.github.io/robot-model-index/meta.json`: build time, commit and counts

The website section at `armatureailabs.com/resources/robot-model-index` reads these files.

Build locally:

```bash
pip install -r requirements.txt
python scripts/validate.py
python scripts/build.py --include-drafts --out dist-preview
```

## Starter entries

| Entry | Why it's here |
|---|---|
| [Gemini Robotics ER 2](models/google-deepmind/gemini-robotics-er-2.toml) | Template for API models: preview status, price that doubles on a set date, two providers with different terms |
| [SmolVLA](models/huggingface/smolvla.toml) | Small open VLA with real community measurements on an 8 GB Jetson Orin Nano and a laptop GPU |
| [π0.5](models/physical-intelligence/pi0-5.toml) | Licence-chain example: Apache 2.0 code on a Gemma-licensed base |

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) first. The short version: primary sources only, every claim cites its source, prices carry dates, nothing is published until a maintainer verifies it. Request a model or report an error with the issue templates.

## Licence

Code and data: [Apache License 2.0](LICENSE). If you reuse the data, keep the [NOTICE](NOTICE) file, which credits Armature AI Labs.

**Not legal advice.** Licence and terms summaries are plain-language aids. Read the original licence and talk to a lawyer before relying on them.
