#!/usr/bin/env python3
"""Validate a coverage ledger.

Usage:
  python validate_ledger.py coverage-ledger.json --stage recon|hunt|final [--sessions-dir DIR]

Stages mirror the workflow gates:
  recon  after Phase 1: the plan is complete and well formed (nothing needs to be tested yet).
  hunt   before leaving Phase 2: every high-priority unit has been resolved.
  final  before Phase 5 onward: every unit is resolved and the brief, if any, has been reconciled.

Exit code 0 = valid (warnings allowed), 1 = errors, 2 = usage error.
Stdlib only. Run it after creating the ledger and after every update; the schema and
this script together are the contract the rest of the pipeline relies on.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schema_lite  # noqa: E402

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "schemas", "ledger.schema.json")

PERSONA_UNIT_TYPES = {"first_impression", "task", "exploration"}
LENSES = ["heuristics", "content_trust", "flows_forms", "mobile_performance", "accessibility"]
QUICK_LENSES = ["heuristics", "content_trust"]
RESOLVED = {"tested", "partial", "blocked", "skipped"}


def check(ledger: dict, stage: str = "recon", sessions_dir: str | None = None):
    """Return (errors, warnings, summary)."""
    errors: list[str] = []
    warnings: list[str] = []

    schema = schema_lite.load_schema(SCHEMA_PATH)
    errors.extend(schema_lite.validate(ledger, schema))
    if errors:
        return errors, warnings, {}

    run = ledger["run"]
    units = ledger["units"]
    persona_ids = [p["id"] for p in ledger["personas"]]
    persona_set = set(persona_ids)
    mode = run["mode"]
    tier = run["evidence_tier"]

    if len(persona_set) != len(persona_ids):
        errors.append("personas: duplicate persona id")

    seen_ids: set[str] = set()
    for unit in units:
        uid = unit["id"]
        if uid in seen_ids:
            errors.append(f"{uid}: duplicate unit id")
        seen_ids.add(uid)

        utype = unit["type"]
        status = unit["status"]

        if utype in PERSONA_UNIT_TYPES:
            plist = unit.get("personas", [])
            if not plist:
                errors.append(f"{uid}: {utype} units need at least one persona")
            for pid in plist:
                if pid not in persona_set:
                    errors.append(f"{uid}: unknown persona '{pid}'")
        if utype == "lens" and "lens" not in unit:
            errors.append(f"{uid}: lens units need a 'lens'")
        if utype == "viewport" and "viewport" not in unit:
            errors.append(f"{uid}: viewport units need a 'viewport'")

        if "outcome" in unit and utype != "task":
            errors.append(f"{uid}: 'outcome' is only valid on task units")
        if "steps_taken" in unit and utype != "task":
            errors.append(f"{uid}: 'steps_taken' is only valid on task units")
        if "five_second" in unit and utype != "first_impression":
            errors.append(f"{uid}: 'five_second' is only valid on first_impression units")

        if status in ("partial", "blocked", "skipped") and not unit.get("reason", "").strip():
            errors.append(f"{uid}: status '{status}' requires a 'reason'")

        if utype == "task" and ('"' in unit["target"] or "`" in unit["target"]):
            warnings.append(f"{uid}: task text contains quotes or backticks; state the customer's goal, not a UI label")

        if stage in ("hunt", "final"):
            if status in ("tested", "partial") and not unit.get("sessions"):
                errors.append(f"{uid}: status '{status}' requires at least one session reference")
            if status in ("tested", "partial") and utype == "task":
                if "outcome" not in unit:
                    errors.append(f"{uid}: tested task is missing 'outcome'")
                if unit.get("steps_taken") is None:
                    errors.append(f"{uid}: tested task is missing 'steps_taken'")
            if status in ("tested", "partial") and utype == "first_impression" and "five_second" not in unit:
                errors.append(f"{uid}: tested first_impression is missing 'five_second'")

        if sessions_dir and unit.get("sessions"):
            for sid in unit["sessions"]:
                matches = [f for f in os.listdir(sessions_dir) if f == f"{sid}.md" or f.startswith(f"{sid}-")]
                if not matches:
                    errors.append(f"{uid}: session '{sid}' has no log file in {sessions_dir}")

    # Persona completeness: one first impression and enough tasks each.
    min_tasks = 2 if mode in ("quick", "focus") else 3
    for pid in persona_ids:
        fi = [u for u in units if u["type"] == "first_impression" and pid in u.get("personas", [])]
        tasks = [u for u in units if u["type"] == "task" and pid in u.get("personas", [])]
        if len(fi) == 0:
            errors.append(f"persona '{pid}': no first_impression unit")
        if len(fi) > 1:
            errors.append(f"persona '{pid}': more than one first_impression unit")
        if len(tasks) < min_tasks:
            errors.append(f"persona '{pid}': needs at least {min_tasks} task units, has {len(tasks)}")

    # Lens coverage: a lens may be skipped, but only with a stated reason.
    required_lenses = QUICK_LENSES if mode == "quick" else LENSES
    for lens in required_lenses:
        lens_units = [u for u in units if u["type"] == "lens" and u.get("lens") == lens]
        if not lens_units:
            errors.append(f"lens '{lens}': no unit (add one, or a skipped unit with a reason)")

    # Viewport coverage depends on what the evidence tier can show.
    mobile_units = [u for u in units if u["type"] == "viewport" and u.get("viewport") == "mobile"]
    if tier in ("rendered", "provided") and mode != "quick" and not mobile_units:
        warnings.append("no mobile viewport unit although the evidence tier can show rendered pages")
    if tier == "text" and any(u["status"] == "tested" for u in units if u["type"] == "viewport"):
        errors.append("viewport units cannot be 'tested' with text-only evidence")

    # Stage gates.
    if stage == "hunt":
        for unit in units:
            if unit["priority"] == "high" and unit["status"] == "untested":
                errors.append(f"{unit['id']}: high-priority unit is still untested")
    if stage == "final":
        for unit in units:
            if unit["status"] == "untested":
                errors.append(f"{unit['id']}: still untested at final stage (test it, or mark skipped with a reason)")
        if run.get("brief_present") and not run.get("brief_opened"):
            errors.append("run: brief_present is true but brief_opened is false (Phase 4 reconciliation not done)")

    # Leniency heuristics: simulated testers tend to be too capable.
    tested_tasks = [u for u in units if u["type"] == "task" and u["status"] in ("tested", "partial") and "outcome" in u]
    if len(tested_tasks) >= 6 and all(u["outcome"] == "completed" for u in tested_tasks):
        warnings.append("leniency check: every task completed cleanly; audit sessions against persona patience budgets")
    persona_traits = {"low-literacy", "mobile-rusher", "cognitive-load", "non-native"}
    if tested_tasks and persona_set & persona_traits:
        if not any(u["outcome"] in ("abandoned", "blocked", "completed_with_difficulty", "completed_incorrectly") for u in tested_tasks):
            warnings.append("leniency check: constrained personas present but no task shows difficulty")

    by_status = Counter(u["status"] for u in units)
    by_type = Counter(u["type"] for u in units)
    by_priority = Counter(u["priority"] for u in units)
    summary = {
        "units": len(units),
        "by_status": dict(by_status),
        "by_type": dict(by_type),
        "by_priority": dict(by_priority),
        "personas": persona_ids,
        "stage": stage,
    }
    return errors, warnings, summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("ledger")
    parser.add_argument("--stage", choices=["recon", "hunt", "final"], default="recon")
    parser.add_argument("--sessions-dir")
    args = parser.parse_args(argv)

    try:
        with open(args.ledger, "r", encoding="utf-8") as handle:
            ledger = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read ledger: {exc}")
        return 2

    errors, warnings, summary = check(ledger, args.stage, args.sessions_dir)
    for warning in warnings:
        print(f"warning: {warning}")
    for error in errors:
        print(f"error: {error}")
    if summary:
        print(f"summary: {json.dumps(summary, sort_keys=True)}")
    if errors:
        print(f"INVALID ({len(errors)} error(s))")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
