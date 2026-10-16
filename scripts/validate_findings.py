#!/usr/bin/env python3
"""Validate a findings record.

Usage:
  python validate_findings.py findings.json [--ledger coverage-ledger.json]
         [--sessions-dir sessions] [--stage structured|verified]

Stages:
  structured  after Phase 5: schema plus every semantic rule below.
  verified    after Phase 6: additionally, every confirmed finding carries a verification record.

The JSON Schema checks shape. This script checks the rules a schema cannot express:
  - ids are unique;
  - a confirmed finding has at least one observed (not merely inferred) evidence item;
  - evidence never claims a tier the run could not produce;
  - design, mobile and rendering-dependent WCAG findings are backed by rendered or provided evidence;
  - severity components are coherent with the overall severity;
  - quick_win equals its derived value;
  - confidence is at least medium, and high needs two independent sessions and full isolation;
  - every log_ref points to a real entry in the session logs (when --sessions-dir is given).

Exit code 0 = valid (warnings allowed), 1 = errors, 2 = usage error. Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schema_lite  # noqa: E402

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "schemas", "findings.schema.json")

# Overall severity allowed for each impact level. Only a blocking impact can produce a blocker.
IMPACT_ALLOWS = {
    "cosmetic": {"minor"},
    "minor": {"minor", "moderate"},
    "major": {"moderate", "major"},
    "blocking": {"major", "blocker"},
}

# WCAG criteria that cannot be judged without seeing the page rendered or interacting with it.
RENDERED_ONLY_WCAG = {
    "1.3.4", "1.4.1", "1.4.2", "1.4.3", "1.4.4", "1.4.5", "1.4.10", "1.4.11", "1.4.12", "1.4.13",
    "2.1.1", "2.1.2", "2.1.4", "2.2.2", "2.3.1", "2.4.3", "2.4.7", "2.4.11",
    "2.5.1", "2.5.2", "2.5.4", "2.5.7", "2.5.8", "3.2.1", "3.2.2", "4.1.3",
}
VISUAL_CATEGORIES = {"design", "mobile"}
TIER_RANK = {"text": 0, "provided": 1, "rendered": 2}
LOG_HEADING = re.compile(r"^###\s+([SL][0-9]+-E[0-9]{2,3})\b", re.MULTILINE)


def expected_quick_win(finding: dict) -> bool:
    """A quick win is a low-effort fix for a problem that matters."""
    severity = finding["severity"]["overall_severity"]
    frequency = finding["severity"]["frequency"]["score"]
    effort = finding["remediation"]["effort"]
    if effort != "low":
        return False
    return severity in ("major", "blocker") or (severity == "moderate" and frequency in ("common", "universal"))


def collect_log_refs(sessions_dir: str) -> set[str]:
    refs: set[str] = set()
    for name in os.listdir(sessions_dir):
        if name.endswith(".md"):
            with open(os.path.join(sessions_dir, name), "r", encoding="utf-8") as handle:
                refs.update(LOG_HEADING.findall(handle.read()))
    return refs


def _check_evidence(owner: str, evidence: list, run_tier: str | None, log_refs: set[str] | None, errors: list[str]):
    for index, item in enumerate(evidence):
        label = f"{owner}.evidence[{index}]"
        prefix = item["log_ref"].split("-E")[0]
        if prefix != item["session"]:
            errors.append(f"{label}: log_ref '{item['log_ref']}' does not belong to session '{item['session']}'")
        if run_tier is not None and TIER_RANK[item["tier"]] > TIER_RANK[run_tier]:
            errors.append(f"{label}: tier '{item['tier']}' is higher than the run's evidence tier '{run_tier}'")
        if log_refs is not None and item["log_ref"] not in log_refs:
            errors.append(f"{label}: log_ref '{item['log_ref']}' not found in the session logs")


def check(record: dict, ledger: dict | None = None, sessions_dir: str | None = None, stage: str = "structured"):
    """Return (errors, warnings, summary)."""
    errors: list[str] = []
    warnings: list[str] = []

    schema = schema_lite.load_schema(SCHEMA_PATH)
    errors.extend(schema_lite.validate(record, schema))
    if errors:
        return errors, warnings, {}

    run_tier = ledger["run"]["evidence_tier"] if ledger else None
    isolation = ledger["run"]["isolation"] if ledger else "full"
    persona_ids = {p["id"] for p in ledger["personas"]} if ledger else None
    ledger_sessions = None
    if ledger:
        ledger_sessions = {s for u in ledger["units"] for s in u.get("sessions", [])}
    log_refs = collect_log_refs(sessions_dir) if sessions_dir else None

    seen: set[str] = set()
    for finding in record["findings"]:
        fid = finding["id"]
        if fid in seen:
            errors.append(f"{fid}: duplicate finding id")
        seen.add(fid)

        verdict = finding["verdict"]
        if "persists_from" in finding and record["run"] == 1:
            errors.append(f"{fid}: persists_from is not allowed in run 1")

        for sid in finding.get("found_by", []):
            if ledger_sessions is not None and sid not in ledger_sessions:
                warnings.append(f"{fid}: found_by session '{sid}' is not referenced by any ledger unit")

        if verdict == "rejected":
            continue

        _check_evidence(fid, finding["evidence"], run_tier, log_refs, errors)
        if persona_ids is not None:
            for pid in finding.get("affected_personas", []):
                if pid not in persona_ids:
                    errors.append(f"{fid}: unknown persona '{pid}' in affected_personas")

        if verdict == "needs_validation":
            continue

        # Confirmed findings from here on.
        evidence = finding["evidence"]
        observed = [e for e in evidence if e["kind"] == "observed"]
        if not observed:
            errors.append(f"{fid}: a confirmed finding needs at least one observed evidence item (use needs_validation for inference)")

        needs_visual = finding["category"] in VISUAL_CATEGORIES
        for ref in finding.get("heuristic_refs", []):
            if ref.startswith("WCAG-") and ref[5:] in RENDERED_ONLY_WCAG:
                needs_visual = True
        if needs_visual and not any(e["kind"] == "observed" and e["tier"] in ("rendered", "provided") for e in evidence):
            errors.append(f"{fid}: design, mobile and rendering-dependent accessibility findings need observed evidence at tier 'rendered' or 'provided'")

        severity = finding["severity"]
        impact = severity["impact"]["score"]
        overall = severity["overall_severity"]
        if overall not in IMPACT_ALLOWS[impact]:
            errors.append(f"{fid}: overall severity '{overall}' is not coherent with impact '{impact}' (allowed: {sorted(IMPACT_ALLOWS[impact])})")

        if finding["quick_win"] != expected_quick_win(finding):
            errors.append(f"{fid}: quick_win should be {expected_quick_win(finding)} given severity, frequency and effort")

        confidence = finding["confidence"]["score"]
        if confidence == "low":
            errors.append(f"{fid}: confirmed findings need at least medium confidence (use needs_validation otherwise)")
        if confidence == "high":
            sessions = {e["session"] for e in observed}
            if len(sessions) < 2:
                errors.append(f"{fid}: high confidence needs observed evidence from at least two independent sessions")
            if isolation == "degraded":
                errors.append(f"{fid}: high confidence is not allowed when isolation is degraded")

        if stage == "verified" and "verification" not in finding:
            errors.append(f"{fid}: missing verification record at stage 'verified'")
        if "verification" in finding and finding["verification"]["status"] == "corrected" and not finding["verification"].get("corrections"):
            errors.append(f"{fid}: a corrected verification must list its corrections")

    strength_ids: set[str] = set()
    for strength in record["strengths"]:
        sid = strength["id"]
        if sid in strength_ids:
            errors.append(f"{sid}: duplicate strength id")
        strength_ids.add(sid)
        _check_evidence(sid, strength["evidence"], run_tier, log_refs, errors)

    verdicts = Counter(f["verdict"] for f in record["findings"])
    severities = Counter(f["severity"]["overall_severity"] for f in record["findings"] if f["verdict"] == "confirmed")
    summary = {
        "verdicts": dict(verdicts),
        "confirmed_by_severity": dict(severities),
        "quick_wins": [f["id"] for f in record["findings"] if f["verdict"] == "confirmed" and f["quick_win"]],
        "strengths": len(record["strengths"]),
    }
    return errors, warnings, summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("findings")
    parser.add_argument("--ledger")
    parser.add_argument("--sessions-dir")
    parser.add_argument("--stage", choices=["structured", "verified"], default="structured")
    args = parser.parse_args(argv)

    try:
        with open(args.findings, "r", encoding="utf-8") as handle:
            record = json.load(handle)
        ledger = None
        if args.ledger:
            with open(args.ledger, "r", encoding="utf-8") as handle:
                ledger = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read input: {exc}")
        return 2

    errors, warnings, summary = check(record, ledger, args.sessions_dir, args.stage)
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
