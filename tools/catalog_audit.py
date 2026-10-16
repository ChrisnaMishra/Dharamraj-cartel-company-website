#!/usr/bin/env python3
"""Offline quality checks for the Dharamraj Cartel static website.

Checks local HTML references and duplicate IDs without making network requests.
Run from the repository root: python3 tools/catalog_audit.py
"""
from __future__ import annotations

import argparse
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class PageAudit(HTMLParser):
    """Collect local references, element IDs, and images missing alt text."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[tuple[str, str]] = []
        self.ids: list[str] = []
        self.images_missing_alt = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            self.ids.append(element_id)

        if tag.lower() == "img" and "alt" not in values:
            self.images_missing_alt += 1

        for attribute in ("href", "src", "poster"):
            value = values.get(attribute)
            if value:
                self.references.append((attribute, value.strip()))


def local_target(root: Path, html_file: Path, raw_url: str) -> Path | None:
    """Return a local target path, or None for external/fragment-only URLs."""
    parsed = urlsplit(raw_url)
    if parsed.scheme or parsed.netloc or raw_url.startswith("//"):
        return None
    if not parsed.path:
        return None

    decoded_path = unquote(parsed.path)
    if decoded_path.startswith("/"):
        target = root / decoded_path.lstrip("/")
    else:
        target = html_file.parent / decoded_path

    target = target.resolve()
    root_resolved = root.resolve()
    try:
        target.relative_to(root_resolved)
    except ValueError:
        return None

    if target.is_dir():
        target = target / "index.html"
    return target


def audit_page(root: Path, html_file: Path) -> tuple[list[str], list[str], int]:
    parser = PageAudit()
    try:
        parser.feed(html_file.read_text(encoding="utf-8"))
        parser.close()
    except (OSError, UnicodeError) as error:
        return [f"{html_file.relative_to(root)}: unable to read HTML: {error}"], [], 0

    errors: list[str] = []
    warnings: list[str] = []
    duplicates = sorted(
        item for item, count in Counter(parser.ids).items() if count > 1
    )
    for item in duplicates:
        errors.append(f"{html_file.relative_to(root)}: duplicate id #{item}")

    for attribute, raw_url in parser.references:
        target = local_target(root, html_file, raw_url)
        if target is None:
            continue
        if not target.exists():
            errors.append(
                f"{html_file.relative_to(root)}: missing {attribute} target {raw_url}"
            )

    if parser.images_missing_alt:
        warnings.append(
            f"{html_file.relative_to(root)}: "
            f"{parser.images_missing_alt} image(s) have no alt attribute"
        )
    return errors, warnings, len(parser.references)


def main() -> int:
    argument_parser = argparse.ArgumentParser(
        description="Check local links/assets and duplicate IDs in website HTML."
    )
    argument_parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root (defaults to the current directory).",
    )
    args = argument_parser.parse_args()
    root = args.root.resolve()
    pages = sorted(root.glob("*.html"))
    if not pages:
        argument_parser.error(f"No HTML files found in {root}")

    error_count = 0
    warning_count = 0
    reference_count = 0
    for page in pages:
        errors, warnings, references = audit_page(root, page)
        reference_count += references
        for error in errors:
            print(f"ERROR: {error}")
        for warning in warnings:
            print(f"WARNING: {warning}")
        error_count += len(errors)
        warning_count += len(warnings)

    print(
        f"\nAudited {len(pages)} HTML page(s) and {reference_count} "
        f"local/remote reference(s): {error_count} error(s), "
        f"{warning_count} warning(s)."
    )
    return 1 if error_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
