"""Build the published JSON from the TOML entries.

Outputs (in --out, default dist/):
  index.json            every published model with its providers and current price
  models/<id>.json      one file per model
  licences.json         licence summaries
  meta.json             build time, version and counts

Only entries with status = "verified" are published, unless --include-drafts is given
(used for preview builds, never for the public site).

Usage: python scripts/build.py [--out dist] [--include-drafts]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path

from rmi import ROOT, current_price, load_all

SCHEMA_VERSION = "0.1.0"


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist")
    ap.add_argument("--include-drafts", action="store_true")
    args = ap.parse_args()

    def publishable(d: dict) -> bool:
        return args.include_drafts or d.get("status") == "verified"

    entries = load_all()
    providers_by_model: dict[str, list[dict]] = {}
    for p in entries["provider"]:
        if publishable(p.data):
            d = dict(p.data)
            d["current_price"] = current_price(d)
            providers_by_model.setdefault(d["model"], []).append(d)

    models = []
    for m in entries["model"]:
        if publishable(m.data):
            d = dict(m.data)
            d["providers"] = sorted(providers_by_model.get(d["id"], []), key=lambda x: x["provider"])
            models.append(d)
    models.sort(key=lambda d: d["id"])
    licences = sorted((l.data for l in entries["licence"] if publishable(l.data)), key=lambda d: d["id"])

    out = ROOT / args.out
    (out / "models").mkdir(parents=True, exist_ok=True)
    meta = {
        "schema_version": SCHEMA_VERSION,
        "built_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "commit": git_commit(),
        "includes_drafts": args.include_drafts,
        "counts": {"models": len(models), "providers": sum(len(m["providers"]) for m in models), "licences": len(licences)},
        "licence": "Apache-2.0",
        "source": "https://github.com/armature-ai-labs/robot-model-index",
        "disclaimer": "Licence and terms summaries are not legal advice. Check each source before relying on it.",
    }
    (out / "index.json").write_text(json.dumps({"meta": meta, "models": models}, indent=2, ensure_ascii=False))
    (out / "licences.json").write_text(json.dumps({"meta": meta, "licences": licences}, indent=2, ensure_ascii=False))
    (out / "meta.json").write_text(json.dumps(meta, indent=2))
    for m in models:
        (out / "models" / f"{m['id']}.json").write_text(json.dumps(m, indent=2, ensure_ascii=False))

    print(f"Built {meta['counts']} into {out.relative_to(ROOT)}/ (drafts included: {args.include_drafts})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
