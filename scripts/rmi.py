"""Shared helpers for Robot Model Index scripts: load TOML entries and schemas."""

from __future__ import annotations

import datetime as dt
import json
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "schema"

# Licence values that are allowed without a matching file in licences/.
SPECIAL_LICENCES = {"proprietary", "not-stated", "not-disclosed", "unverified"}

STALE_AFTER_DAYS = 60


@dataclass
class Entry:
    kind: str  # "model", "provider" or "licence"
    path: Path
    data: dict

    @property
    def rel(self) -> str:
        return str(self.path.relative_to(ROOT))


def load_schema(kind: str) -> dict:
    return json.loads((SCHEMA_DIR / f"{kind}.schema.json").read_text())


def _load_dir(kind: str, folder: str) -> list[Entry]:
    entries = []
    for path in sorted((ROOT / folder).rglob("*.toml")):
        with path.open("rb") as fh:
            entries.append(Entry(kind, path, tomllib.load(fh)))
    return entries


def load_all() -> dict[str, list[Entry]]:
    return {
        "model": _load_dir("model", "models"),
        "provider": _load_dir("provider", "providers"),
        "licence": _load_dir("licence", "licences"),
    }


def parse_date(value: str) -> dt.date:
    """Accept YYYY-MM-DD or YYYY-MM (treated as the first of the month)."""
    if len(value) == 7:
        value += "-01"
    return dt.date.fromisoformat(value)


def today() -> dt.date:
    return dt.date.today()


def current_price(provider: dict, on: dt.date | None = None) -> dict | None:
    """Return the pricing period that applies on a date, or None."""
    on = on or today()
    for period in provider.get("pricing", []):
        start = parse_date(period["effective_from"]) if "effective_from" in period else dt.date.min
        end = parse_date(period["effective_to"]) if "effective_to" in period else dt.date.max
        if start <= on <= end:
            return period
    return None
