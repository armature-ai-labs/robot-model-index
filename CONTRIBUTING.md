# Contributing to the Robot Model Index

Thanks for helping. The index is only useful if every fact in it can be checked, so contributions follow a few strict rules.

## The data rules

1. **Primary sources only** for what a model is, how to get it, what it costs, its licence and its terms: developer docs, model cards, licence files, pricing pages, papers, source code.
2. **Community sources** (independent benchmarks, measurements) are allowed only in `hardware.fit`, `benchmarks` and `limitations`, and must be marked `kind = "community"`. The validator enforces this.
3. **Every claim cites a source** declared in the same file (`sources = ["s1"]`). The validator rejects references to undeclared sources.
4. **Dates on everything that changes.** Prices carry `effective_from` and `effective_to` where the provider publishes them. Every file carries `last_verified`.
5. **No guessing.** If something isn't published, say so (`"not disclosed"`, `"not-stated"`, `"unverified"`) or leave the field out. Don't fill gaps from memory or from aggregator sites.
6. **Plain language.** Write summaries and terms so a robotics engineer, not a lawyer, can understand them. Licence summaries are never legal advice.
7. **Drafts first.** New and changed entries start as `status = "draft"`. Only a maintainer sets `status = "verified"`, after the checklist below. Only verified entries are published.

AI tools may draft entries. A human must still check every claim against its source before it's verified.

## Where things go

| Folder | One file per | Holds |
|---|---|---|
| `models/<developer>/<model-id>.toml` | model | What the model is, regardless of who serves it: roles, access, licence chain, robot interface, hardware fit, benchmarks, limitations |
| `providers/<provider>/<model-id>.toml` | model and provider | How one provider offers it: endpoint name, access, regions, limits, pricing periods, terms |
| `licences/<licence-id>.toml` | licence | Plain-language obligations of a licence that models refer to |

Schemas live in `schema/`. Copy an existing entry as a starting point:
- `models/google-deepmind/gemini-robotics-er-2.toml`: closed API model with dated pricing across two providers
- `models/huggingface/smolvla.toml`: small open VLA with community hardware measurements
- `models/physical-intelligence/pi0-5.toml`: open VLA with a licence chain (Apache 2.0 code built on a Gemma-licensed base)

## Workflow

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python scripts/validate.py                    # must pass
python scripts/build.py --include-drafts --out dist-preview   # look at the JSON
python scripts/weekly_check.py                # optional: price cross-check
```

Commit with a sign-off (Developer Certificate of Origin):

```bash
git commit -s -m "Add GR00T N1.7"
```

The `-s` adds `Signed-off-by: Your Name <you@example.com>`, confirming you wrote the change or have the right to submit it under Apache 2.0. See https://developercertificate.org/.

## Verification checklist (maintainers)

Before changing `status` to `verified` and filling in `verified_by`:

- [ ] Opened every source URL and confirmed each claim that cites it says what the entry says
- [ ] Prices match the provider's own pricing page today, including start and end dates
- [ ] Licence chain checked: code, weights, every base model, training data
- [ ] `commercial_use` and its reason are supported by the licence files, and say "conditional" or "unclear" whenever there is doubt
- [ ] Access type matches reality (public API, waitlist, partners only, open weights)
- [ ] Community measurements state hardware, software version and settings
- [ ] `last_verified` set to today
- [ ] `python scripts/validate.py --strict` passes

## Requesting a model or reporting an error

Use the issue templates: **Request a model** or **Correction**. Corrections that could cause unsafe or unlawful use go through private reporting (see [SECURITY.md](SECURITY.md)).
