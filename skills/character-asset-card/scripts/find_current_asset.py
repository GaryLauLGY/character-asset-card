#!/usr/bin/env python3
"""Resolve an adopted asset from an explicit index; never search historical files."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def resolve(index: dict, name: str, style: str | None = None) -> dict:
    if index.get("schema") != "character-asset-current/1":
        raise ValueError("Unsupported current-asset index schema")
    needle = name.casefold().strip()
    candidates = [e for e in index["entries"] if e.get("selectable") is True and
                  needle in {str(x).casefold().strip() for x in
                             [e["id"], e["name"], e["folder"], *e.get("aliases", [])]}]
    if style is not None:
        candidates = [e for e in candidates if style.casefold().strip() in
                      {e["style"].casefold().strip(), e["folder"].casefold().strip()}]
    elif len(candidates) > 1:
        adopted = {str(k).casefold().strip(): v for k, v in index.get("defaults", {}).items()}
        if needle in adopted:
            candidates = [e for e in candidates if e["id"] == adopted[needle]]
    if len(candidates) != 1:
        choices = "; ".join(e["folder"] for e in candidates)
        raise ValueError(f"Expected one current asset, found {len(candidates)}. "
                         f"Specify an exact style or folder. {choices}")
    entry = candidates[0]
    root = Path(index["library_root"]).resolve(strict=True)
    for ref in [entry["primary"], *entry.get("sources", []), *entry.get("boards", [])]:
        raw = Path(ref["path"])
        path = raw if raw.is_absolute() else root / raw
        path = path.resolve(strict=True)
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f"Asset is outside the current library: {raw}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != ref["sha256"]:
            raise ValueError(f"Asset fingerprint changed: {raw}")
    return entry


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("index", type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--style", help="Exact style or folder from the index")
    args = parser.parse_args()
    try:
        entry = resolve(json.loads(args.index.read_text(encoding="utf-8")), args.name, args.style)
        print(json.dumps(entry, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
