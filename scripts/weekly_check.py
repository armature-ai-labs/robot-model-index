"""Weekly freshness report.

1. Compares each provider's current price with the Portkey Models database (MIT licence,
   https://github.com/Portkey-AI/models). Portkey stores prices in US cents per token;
   this converts them to US dollars per million tokens.
2. Lists entries that are stale or whose prices have expired or change within 30 days.

It never edits data. A human checks the developer's own page and updates the entry.
Writes a Markdown report to stdout (the workflow posts it as the job summary).

Usage: python scripts/weekly_check.py [--offline]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import urllib.request

from rmi import STALE_AFTER_DAYS, current_price, load_all, parse_date, today

PORTKEY_URL = "https://raw.githubusercontent.com/Portkey-AI/models/main/pricing/{provider}.json"
CENTS_PER_TOKEN_TO_USD_PER_MILLION = 1_000_000 / 100  # = 10,000


def fetch_portkey(provider: str, cache: dict) -> dict:
    if provider not in cache:
        with urllib.request.urlopen(PORTKEY_URL.format(provider=provider), timeout=30) as resp:
            cache[provider] = json.load(resp)
    return cache[provider]


def portkey_prices(entry: dict) -> dict:
    cfg = entry.get("pricing_config", {})
    payg = cfg.get("pay_as_you_go", {})
    batch = cfg.get("batch_config", {})
    def usd(node):
        return None if node is None else round(node.get("price", 0) * CENTS_PER_TOKEN_TO_USD_PER_MILLION, 4)
    return {
        "input": usd(payg.get("request_token")),
        "output": usd(payg.get("response_token")),
        "cached_input": usd(payg.get("cache_read_input_token")),
        "batch_input": usd(batch.get("request_token")),
        "batch_output": usd(batch.get("response_token")),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="skip the Portkey comparison")
    args = ap.parse_args()

    entries = load_all()
    lines = [f"# Robot Model Index weekly check ({today()})", ""]

    # 1. Price cross-check
    lines += ["## Prices compared with Portkey Models", ""]
    if args.offline:
        lines.append("Skipped (offline).")
    else:
        cache: dict = {}
        rows = []
        for p in entries["provider"]:
            cc = p.data.get("cross_check")
            if not cc:
                continue
            ours = current_price(p.data) or {}
            try:
                theirs_all = fetch_portkey(cc["portkey_provider"], cache)
                theirs = portkey_prices(theirs_all[cc["portkey_key"]])
            except Exception as exc:  # network error or missing key
                rows.append(f"| {p.rel} | could not read Portkey: {exc} | | |")
                continue
            for field, value in theirs.items():
                if value is None or field not in ours:
                    continue
                flag = "same" if abs(ours[field] - value) < 1e-6 else "**different**"
                rows.append(f"| {p.rel} | {field} | ours ${ours[field]} / Portkey ${value} | {flag} |")
        lines += ["| File | Field | Price (USD per 1M tokens) | Result |", "|---|---|---|---|"] + (rows or ["| none | | | |"])
        lines += ["", "A difference means one side is out of date. Check the developer's pricing page, not Portkey, before changing anything."]

    # 2. Freshness
    lines += ["", "## Needs attention", ""]
    todo = []
    for kind_entries in entries.values():
        for e in kind_entries:
            age = (today() - parse_date(e.data["last_verified"])).days
            if age > STALE_AFTER_DAYS:
                todo.append(f"- {e.rel}: last verified {age} days ago")
            if e.data.get("status") == "draft":
                todo.append(f"- {e.rel}: still draft (not published)")
    soon = today() + dt.timedelta(days=30)
    for p in entries["provider"]:
        for i, period in enumerate(p.data.get("pricing", [])):
            if "effective_to" in period:
                end = parse_date(period["effective_to"])
                if end < today():
                    todo.append(f"- {p.rel}: pricing[{i}] ended on {end}")
                elif end <= soon:
                    todo.append(f"- {p.rel}: pricing[{i}] ends on {end}; the next price takes over after that")
    lines += todo or ["Nothing due."]
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
