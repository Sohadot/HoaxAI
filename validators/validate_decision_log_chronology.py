#!/usr/bin/env python3
"""Validate DECISION_LOG.md chronological integrity by DEC append order."""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECISION_LOG = ROOT / "DECISION_LOG.md"

DEC_HEADER = re.compile(r"^## DEC-(\d+)\b", re.M)
DATE_LINE = re.compile(r"^\*\*Date:\*\*\s*(\d{4}-\d{2}-\d{2})\s*$", re.M)


def error(msg: str) -> None:
    print(f"ERROR: {msg}")


def parse_entries(text: str) -> list[tuple[int, str, int]]:
    """Return list of (dec_num, date_str, line_number) in file order."""
    entries: list[tuple[int, str, int]] = []
    headers = list(DEC_HEADER.finditer(text))
    seen: set[int] = set()
    for i, match in enumerate(headers):
        dec_num = int(match.group(1))
        line_no = text[: match.start()].count("\n") + 1
        if dec_num in seen:
            error(f"DEC-{dec_num:03d}: duplicate decision number at line {line_no}")
        seen.add(dec_num)
        block_end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        block = text[match.start() : block_end]
        date_match = DATE_LINE.search(block)
        if not date_match:
            error(f"DEC-{dec_num:03d}: missing or unparseable Date field (expected YYYY-MM-DD)")
            entries.append((dec_num, "", line_no))
            continue
        date_str = date_match.group(1)
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            error(f"DEC-{dec_num:03d}: invalid date '{date_str}' (expected YYYY-MM-DD)")
        entries.append((dec_num, date_str, line_no))
    return entries


def validate() -> bool:
    ok = True
    if not DECISION_LOG.is_file():
        error("DECISION_LOG.md missing")
        return False
    text = DECISION_LOG.read_text(encoding="utf-8")
    entries = parse_entries(text)
    if not entries:
        error("DECISION_LOG.md: no DEC entries found")
        return False
    prev_num = 0
    prev_date: str | None = None
    for dec_num, date_str, line_no in entries:
        if dec_num <= prev_num:
            error(
                f"DEC-{dec_num:03d} at line {line_no}: decision number must ascend "
                f"(previous DEC-{prev_num:03d})"
            )
            ok = False
        prev_num = dec_num
        if not date_str:
            ok = False
            continue
        if prev_date is not None and date_str < prev_date:
            error(
                f"DEC-{dec_num:03d} at line {line_no}: date {date_str} is earlier than "
                f"previous decision date {prev_date}"
            )
            ok = False
        prev_date = date_str
    return ok


def main() -> int:
    if validate():
        print("PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
