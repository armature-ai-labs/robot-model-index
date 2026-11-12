"""Validate every entry in the Robot Model Index.

Errors fail CI. Warnings (stale entries, expired prices) are printed but don't fail,
unless --strict is passed.

Usage: python scripts/validate.py [--strict]
"""

from __future__ import annotations

import argparse
import sys

from jsonschema import Draft202012Validator, FormatChecker

from rmi import SPECIAL_LICENCES, STALE_AFTER_DAYS, ROOT, Entry, load_all, load_schema, parse_date, today


def iter_source_refs(node, path=""):
    """Yield (location, ref) for every 'sources' list of refs inside an entry, skipping the top-level source list."""
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}" if path else key
            if key == "sources" and path and isinstance(value, list) and all(isinstance(v, str) for v in value):
                for ref in value:
                    yield here, ref
            else:
                yield from iter_source_refs(value, here)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            yield from iter_source_refs(item, f"{path}[{i}]")


def check_entry(entry: Entry, schemas: dict, errors: list, warnings: list) -> bool:
    """Check one file. Returns False if it fails the schema (later rules assume a valid shape)."""
    data = entry.data
    validator = Draft202012Validator(schemas[entry.kind], format_checker=FormatChecker())
    schema_errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    for err in schema_errors:
        loc = "/".join(str(p) for p in err.path) or "(root)"
        errors.append(f"{entry.rel}: {loc}: {err.message}")
    if schema_errors:
        return False

    # Every source reference must point to a declared source in the same file.
    declared = {s["id"] for s in data.get("sources", [])}
    if len(declared) != len(data.get("sources", [])):
        errors.append(f"{entry.rel}: duplicate source ids")
    used = set()
    for loc, ref in iter_source_refs(data):
        used.add(ref)
        if ref not in declared:
            errors.append(f"{entry.rel}: {loc} refers to unknown source '{ref}'")
    for unused in sorted(declared - used):
        warnings.append(f"{entry.rel}: source '{unused}' is declared but never cited")

    # Community sources may back measurements only, never licences, access or pricing.
    community = {s["id"] for s in data.get("sources", []) if s["kind"] == "community"}
    if community:
        for loc, ref in iter_source_refs(data):
            if ref in community and not (loc.startswith("hardware") or loc.startswith("benchmarks") or loc.startswith("limitations")):
                errors.append(f"{entry.rel}: {loc} cites community source '{ref}'; only hardware fit, benchmarks and limitations may")

    # Verified entries need a verifier.
    if data.get("status") == "verified" and not data.get("verified_by"):
        errors.append(f"{entry.rel}: status is 'verified' but verified_by is empty")

    # Dates: nothing verified in the future; flag stale entries.
    last = parse_date(data["last_verified"])
    if last > today():
        errors.append(f"{entry.rel}: last_verified {last} is in the future")
    elif (today() - last).days > STALE_AFTER_DAYS:
        warnings.append(f"{entry.rel}: stale, last verified {last} ({(today() - last).days} days ago)")
    return True


def check_model_paths(models: list[Entry], errors: list) -> None:
    seen = {}
    for m in models:
        expected = ROOT / "models" / m.data["developer"] / f"{m.data['id']}.toml"
        if m.path != expected:
            errors.append(f"{m.rel}: should live at {expected.relative_to(ROOT)}")
        if m.data["id"] in seen:
            errors.append(f"{m.rel}: duplicate model id '{m.data['id']}' (also in {seen[m.data['id']]})")
        seen[m.data["id"]] = m.rel


def check_providers(providers: list[Entry], model_ids: set, errors: list, warnings: list) -> None:
    for p in providers:
        d = p.data
        expected = ROOT / "providers" / d["provider"] / f"{d['model']}.toml"
        if p.path != expected:
            errors.append(f"{p.rel}: should live at {expected.relative_to(ROOT)}")
        if d["model"] not in model_ids:
            errors.append(f"{p.rel}: model '{d['model']}' has no file in models/")

        periods = []
        for i, period in enumerate(d.get("pricing", [])):
            start = parse_date(period["effective_from"]) if "effective_from" in period else None
            end = parse_date(period["effective_to"]) if "effective_to" in period else None
            if start and end and end < start:
                errors.append(f"{p.rel}: pricing[{i}] ends before it starts")
            if period["unit"] != "free" and not any(k in period for k in ("input", "output")):
                errors.append(f"{p.rel}: pricing[{i}] has a paid unit but no input or output price")
            periods.append((start, end, i))
        # No overlapping periods.
        for a in periods:
            for b in periods:
                if a[2] < b[2]:
                    a_start, a_end = a[0] or parse_date("0001-01-01"), a[1] or parse_date("9999-12-31")
                    b_start, b_end = b[0] or parse_date("0001-01-01"), b[1] or parse_date("9999-12-31")
                    if a_start <= b_end and b_start <= a_end:
                        errors.append(f"{p.rel}: pricing[{a[2]}] and pricing[{b[2]}] overlap")
        # Warn when every published price has expired.
        if periods and all(e is not None and e < today() for _, e, _ in periods):
            warnings.append(f"{p.rel}: every pricing period has ended; add the current price")


def check_licence_refs(models: list[Entry], licence_ids: set, errors: list) -> None:
    for m in models:
        lic = m.data["licence"]
        refs = [("licence.code", lic["code"]), ("licence.weights", lic["weights"])]
        refs += [(f"licence.base_models[{i}]", b["licence"]) for i, b in enumerate(lic.get("base_models", []))]
        for loc, ref in refs:
            if ref not in licence_ids and ref not in SPECIAL_LICENCES:
                errors.append(f"{m.rel}: {loc} '{ref}' has no file in licences/ (or use one of {sorted(SPECIAL_LICENCES)})")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = ap.parse_args()

    entries = load_all()
    schemas = {k: load_schema(k) for k in ("model", "provider", "licence")}
    errors: list[str] = []
    warnings: list[str] = []

    valid = {kind: [e for e in kind_entries if check_entry(e, schemas, errors, warnings)] for kind, kind_entries in entries.items()}
    # Cross-file rules run on every file that passed the schema.
    check_model_paths(valid["model"], errors)
    model_ids = {m.data.get("id") for m in entries["model"]}
    check_providers(valid["provider"], model_ids, errors, warnings)
    check_licence_refs(valid["model"], {l.data["id"] for l in valid["licence"]}, errors)

    counts = {k: len(v) for k, v in entries.items()}
    drafts = sum(1 for v in entries.values() for e in v if e.data.get("status") == "draft")
    print(f"Checked {counts['model']} models, {counts['provider']} provider files, {counts['licence']} licences ({drafts} still draft).")
    for w in warnings:
        print(f"WARNING {w}")
    for e in errors:
        print(f"ERROR   {e}")
    if errors or (args.strict and warnings):
        print(f"\nFailed: {len(errors)} errors, {len(warnings)} warnings.")
        return 1
    print(f"\nOK: 0 errors, {len(warnings)} warnings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
