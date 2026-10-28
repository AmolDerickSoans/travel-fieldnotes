#!/usr/bin/env python3
"""Check local report references and an optional planning manifest.

Standard-library only. Does not fetch URLs, inspect pixels, decode QR codes,
verify travel facts, or certify privacy. Date-language flags require human review.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


class ReportParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.anchors: set[str] = set()
        self.references: list[tuple[str, str, str, int]] = []
        self.visible: list[str] = []
        self.hidden_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag in {"script", "style", "template"}:
            self.hidden_depth += 1
        if values.get("id"):
            self.ids.append(values["id"])
            self.anchors.add(values["id"])
        if tag == "a" and values.get("name"):
            self.anchors.add(values["name"])
        for attr in ("src", "href"):
            if attr in values:
                self.references.append((tag, attr, values[attr] or "", self.getpos()[0]))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag in {"script", "style", "template"}:
            self.hidden_depth = max(0, self.hidden_depth - 1)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "template"}:
            self.hidden_depth = max(0, self.hidden_depth - 1)

    def handle_data(self, data: str) -> None:
        if not self.hidden_depth:
            self.visible.append(data)


def add(findings: list[dict], severity: str, code: str, detail: str) -> None:
    findings.append({"severity": severity, "code": code, "detail": detail})


def parse_report(path: Path) -> ReportParser:
    parser = ReportParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def audit_html(path: Path, findings: list[dict]) -> None:
    try:
        parser = parse_report(path)
    except (OSError, UnicodeError, ValueError) as exc:
        add(findings, "error", "report_unreadable", f"Cannot read report: {exc}")
        return
    for identifier, count in Counter(parser.ids).items():
        if count > 1:
            add(findings, "error", "duplicate_id", f"ID {identifier!r} occurs {count} times.")
    cache: dict[Path, ReportParser] = {path.resolve(): parser}
    seen: set[tuple[str, str]] = set()
    for tag, attr, value, line in parser.references:
        if (attr, value) in seen:
            continue
        seen.add((attr, value))
        try:
            uri = urlsplit(value)
        except ValueError:
            add(findings, "error", "invalid_reference", f"Line {line}: malformed {attr} URL.")
            continue
        if uri.scheme and uri.scheme.lower() != "file":
            continue  # Network URLs, data URLs and application links are not checked.
        if uri.netloc and not (uri.scheme == "file" and uri.netloc == "localhost"):
            continue
        if not value.strip():
            add(findings, "error" if attr == "src" else "warning", "empty_reference",
                f"Line {line}: {tag} has an empty {attr}.")
            continue
        raw_path = unquote(uri.path)
        target = (Path(raw_path) if uri.scheme == "file" or raw_path.startswith("/")
                  else path.parent / raw_path) if raw_path else path
        target = target.resolve()
        if not target.exists() or (attr == "src" and not target.is_file()):
            add(findings, "error", "missing_local_asset",
                f"Line {line}: local {attr} target does not exist: {raw_path!r}.")
            continue
        if not uri.fragment:
            continue
        if target.suffix.lower() not in {".html", ".htm", ".svg"}:
            continue  # PDF view fragments and similar formats have different semantics.
        try:
            if target not in cache:
                cache[target] = parse_report(target)
            anchor = unquote(uri.fragment)
            if anchor not in cache[target].anchors:
                add(findings, "error", "missing_fragment",
                    f"Line {line}: fragment {anchor!r} is absent from {raw_path or path.name!r}.")
        except (OSError, UnicodeError, ValueError) as exc:
            add(findings, "error", "target_unreadable", f"Cannot inspect linked document: {exc}")
    visible = re.sub(r"\s+", " ", " ".join(parser.visible))
    patterns = [
        ("relative_schedule", r"\b(?:next|upcoming)\s+(?:scheduled\s+)?(?:sale|release|departure|opening|event|week|month|year)\b"),
        ("volatile_availability", r"\b(?:currently available|available now|sold out|last tickets|last rooms|book now)\b"),
        ("relative_date", r"\b(?:today|tomorrow|yesterday|this (?:week|month|year))\b"),
        ("time_limited_offer", r"\b(?:free cancellation (?:before|until)|sale ends|offer ends|book by|valid until)\b"),
    ]
    for code, pattern in patterns:
        for match in list(re.finditer(pattern, visible, flags=re.I))[:5]:
            excerpt = visible[max(0, match.start() - 45):match.end() + 90]
            add(findings, "warning", code,
                f"Review freshness or clarify the reference date; this is not a finding of factual staleness: {excerpt!r}")


def iso_date(value: object, where: str, findings: list[dict]) -> date | None:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        add(findings, "error", "invalid_date", f"{where} must be an ISO YYYY-MM-DD date.")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        add(findings, "error", "invalid_date", f"{where} is not a valid calendar date.")
        return None


def amount(value: object, where: str, findings: list[dict]) -> Decimal | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        add(findings, "error", "invalid_amount", f"{where} must be a non-negative finite JSON number.")
        return None
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        number = Decimal("NaN")
    if not number.is_finite() or number < 0:
        add(findings, "error", "invalid_amount", f"{where} must be a non-negative finite JSON number.")
        return None
    return number


def text_field(record: dict, key: str, where: str, findings: list[dict]) -> None:
    if not isinstance(record.get(key), str) or not record[key].strip():
        add(findings, "error", "missing_field", f"{where}.{key} must be a non-empty string.")


def records(manifest: dict, key: str, findings: list[dict]) -> list:
    value = manifest.get(key, [])
    if not isinstance(value, list):
        add(findings, "error", "invalid_collection", f"{key} must be an array.")
        return []
    return value


def audit_manifest(manifest: object, as_of: date, findings: list[dict]) -> None:
    if not isinstance(manifest, dict):
        add(findings, "error", "invalid_manifest", "Manifest must be a JSON object.")
        return
    budgets = records(manifest, "budgets", findings)
    party = manifest.get("party_size")
    party_ok = isinstance(party, int) and not isinstance(party, bool) and party > 0
    if "party_size" in manifest or budgets:
        if not party_ok:
            add(findings, "error", "invalid_party_size", "party_size must be an integer greater than zero.")
    if "currency" in manifest or budgets:
        text_field(manifest, "currency", "manifest", findings)
    for i, stay in enumerate(records(manifest, "stays", findings)):
        where = f"stays[{i}]"
        if not isinstance(stay, dict):
            add(findings, "error", "invalid_record", f"{where} must be an object.")
            continue
        start = iso_date(stay.get("check_in"), where + ".check_in", findings)
        end = iso_date(stay.get("check_out"), where + ".check_out", findings)
        nights = stay.get("nights")
        if not isinstance(nights, int) or isinstance(nights, bool) or nights <= 0:
            add(findings, "error", "invalid_nights", f"{where}.nights must be a positive integer.")
        elif start and end and (end - start).days != nights:
            add(findings, "error", "night_count_mismatch",
                f"{where}: dates imply {(end - start).days} nights, manifest says {nights}.")
        if start and end and end <= start:
            add(findings, "error", "invalid_stay_order", f"{where}: check_out must follow check_in.")
    for i, budget in enumerate(budgets):
        where = f"budgets[{i}]"
        if not isinstance(budget, dict):
            add(findings, "error", "invalid_record", f"{where} must be an object.")
            continue
        text_field(budget, "name", where, findings)
        items = budget.get("items")
        total = amount(budget.get("group_total"), where + ".group_total", findings)
        per_person = amount(budget.get("per_person"), where + ".per_person", findings)
        if not isinstance(items, list) or not items:
            add(findings, "error", "invalid_items", f"{where}.items must be a non-empty array.")
            continue
        values = []
        valid = True
        for j, item in enumerate(items):
            item_where = f"{where}.items[{j}]"
            if not isinstance(item, dict):
                add(findings, "error", "invalid_record", f"{item_where} must be an object.")
                valid = False
                continue
            text_field(item, "label", item_where, findings)
            value = amount(item.get("group_amount"), item_where + ".group_amount", findings)
            if value is None:
                valid = False
            else:
                values.append(value)
        if valid and total is not None and abs(sum(values, Decimal(0)) - total) > Decimal("0.01"):
            add(findings, "error", "budget_sum_mismatch",
                f"{where}: items sum to {sum(values, Decimal(0))}, group_total is {total}.")
        if party_ok and total is not None and per_person is not None:
            if abs(total / party - per_person) > Decimal("0.01"):
                add(findings, "error", "per_person_mismatch",
                    f"{where}: group_total / party_size is {total / party}, per_person is {per_person}.")
    for i, claim in enumerate(records(manifest, "claims", findings)):
        where = f"claims[{i}]"
        if not isinstance(claim, dict):
            add(findings, "error", "invalid_record", f"{where} must be an object.")
            continue
        text_field(claim, "label", where, findings)
        text_field(claim, "status", where, findings)
        checked = iso_date(claim.get("checked_on"), where + ".checked_on", findings)
        valid_until = (iso_date(claim["valid_until"], where + ".valid_until", findings)
                       if claim.get("valid_until") is not None else None)
        if checked and checked > as_of:
            add(findings, "warning", "future_check_date", f"{where}: checked_on is after --as-of; review the evidence date.")
        if valid_until and valid_until < as_of:
            add(findings, "warning", "expired_validity", f"{where}: declared validity ended on {valid_until}; recheck before presenting as current.")
        if checked and valid_until and valid_until < checked:
            add(findings, "warning", "validity_before_check", f"{where}: validity ended before the recorded check; this may be historical evidence.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="Local HTML report to inspect")
    parser.add_argument("--as-of", required=True, help="Review date, YYYY-MM-DD")
    parser.add_argument("--manifest", type=Path, help="Optional planning manifest JSON")
    args = parser.parse_args(argv)
    findings: list[dict] = []
    as_of = iso_date(args.as_of, "--as-of", findings)
    audit_html(args.report.resolve(), findings)
    if args.manifest:
        try:
            manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            add(findings, "error", "manifest_unreadable", f"Cannot read manifest: {exc}")
        else:
            if as_of:
                audit_manifest(manifest, as_of, findings)
    errors = sum(item["severity"] == "error" for item in findings)
    warnings = sum(item["severity"] == "warning" for item in findings)
    print(json.dumps({"ok": errors == 0, "as_of": args.as_of, "errors": errors,
                      "warnings": warnings, "findings": findings,
                      "scope": "Local src/href targets, HTML/SVG fragments, duplicate IDs, declared manifest arithmetic and dates. No network, pixel, QR, privacy or factual verification."}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
