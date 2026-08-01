#!/usr/bin/env python3
"""Build the static website and inject its public URL."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site"
OUTPUT = ROOT / "dist"
TEXT_SUFFIXES = {".html", ".xml", ".txt", ".json", ".webmanifest"}


def validated_url(value: str) -> str:
    candidate = value.rstrip("/")
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise argparse.ArgumentTypeError("site URL must be an absolute http or https URL")
    return candidate


def build(site_url: str) -> None:
    if not SOURCE.is_dir():
        raise SystemExit(f"Site source not found: {SOURCE}")

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    shutil.copytree(SOURCE, OUTPUT)

    replacements = 0
    for path in OUTPUT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        if "__SITE_URL__" not in text:
            continue
        path.write_text(text.replace("__SITE_URL__", site_url), encoding="utf-8")
        replacements += 1

    remaining = []
    for path in OUTPUT.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            if "__SITE_URL__" in path.read_text(encoding="utf-8"):
                remaining.append(str(path.relative_to(OUTPUT)))

    if remaining:
        raise SystemExit(f"Unresolved site URL placeholders: {', '.join(remaining)}")

    files = sum(1 for path in OUTPUT.rglob("*") if path.is_file())
    print(f"Built {files} files for {site_url} and updated {replacements} text files.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--site-url",
        default="http://localhost:8000",
        type=validated_url,
        help="Public base URL used in canonical and structured metadata.",
    )
    args = parser.parse_args()
    build(args.site_url)


if __name__ == "__main__":
    main()

