#!/usr/bin/env python3
"""Compare two runs of the same site and write an evolution record.

Usage:
  python compare_runs.py --prior-scorecard run-1/scorecard.json --prior-findings run-1/findings.json \
         --current-scorecard run-2/scorecard.json --current-findings run-2/findings.json \
         --out run-2/evolution.json

How findings are matched: the testers in a retest are blind to earlier findings, so matching is
done by the orchestrator after validation. A current finding that is the same problem as a prior
one carries `persists_from: "run-<N>:P<k>"`. This script trusts that field, checks it, and derives:
  persisting   = current findings with a valid persists_from
  resolved     = prior confirmed findings that no current finding points to
  not_retested = prior confirmed findings the orchestrator lists with --not-retested because no unit of
                 the retest re-examined that part of the site (never reported as resolved)
  new          = current confirmed findings without a valid persists_from

A prior finding is only "resolved" if the retest actually looked where it lived. The script cannot know
that from the findings alone, so the orchestrator checks the ledger (see RETEST.md) and passes the prior
ids that were not re-examined as --not-retested P3,P5.

How scores are compared: simulated testers vary from run to run, so small score movements are
noise. A category counts as improved or regressed only when it moves by at least 0.7 points
(0.5 for the overall score, which averages out some of the noise). The comparison is flagged as
not strictly comparable when the evidence tier or weight profile changed.

Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

CATEGORY_NOISE = 0.7
GLOBAL_NOISE = 0.5
SEVERITY_ORDER = {"minor": 0, "moderate": 1, "major": 2, "blocker": 3}
PERSIST_PATTERN = re.compile(r"^run-([0-9]+):(P[0-9]+)$")


def _verdict(delta: float, threshold: float) -> str:
    if delta >= threshold:
        return "improved"
    if delta <= -threshold:
        return "regressed"
    return "within_noise"


def _delta(prior, current):
    if prior is None or current is None:
        return None
    return round(current - prior, 3)


def compare(prior_card: dict, prior_findings: dict, current_card: dict, current_findings: dict, not_retested=None) -> dict:
    warnings: list[str] = []
    not_retested = set(not_retested or [])
    prior_run = prior_card["run"]["number"]
    current_run = current_card["run"]["number"]
    if current_run <= prior_run:
        warnings.append(f"current run ({current_run}) is not later than the prior run ({prior_run})")
    if prior_card["site"]["slug"] != current_card["site"]["slug"]:
        warnings.append("the two scorecards are for different sites")

    comparable = True
    if prior_card["run"]["evidence_tier"] != current_card["run"]["evidence_tier"]:
        comparable = False
        warnings.append("evidence tier changed between runs; score movements may reflect the method, not the site")
    if prior_card["run"]["weight_profile"] != current_card["run"]["weight_profile"]:
        comparable = False
        warnings.append("weight profile changed between runs; the overall scores are not comparable")
    if prior_card["run"]["isolation"] != current_card["run"]["isolation"]:
        warnings.append("isolation level changed between runs; confidence is not directly comparable")

    categories = {}
    for name, prior_result in prior_card["categories"].items():
        current_result = current_card["categories"][name]
        if prior_result["status"] == "assessed" and current_result["status"] == "assessed":
            delta = round(current_result["final_score"] - prior_result["final_score"], 1)
            categories[name] = {
                "before": prior_result["final_score"],
                "after": current_result["final_score"],
                "delta": delta,
                "verdict": _verdict(delta, CATEGORY_NOISE),
            }
        else:
            categories[name] = {
                "before": prior_result.get("final_score"),
                "after": current_result.get("final_score"),
                "delta": None,
                "verdict": "not_comparable",
            }

    prior_global = prior_card["global"]["score"]
    current_global = current_card["global"]["score"]
    global_delta = None if prior_global is None or current_global is None else round(current_global - prior_global, 1)
    global_block = {
        "before": prior_global,
        "after": current_global,
        "delta": global_delta,
        "verdict": _verdict(global_delta, GLOBAL_NOISE) if global_delta is not None and comparable else "not_comparable",
    }

    prior_confirmed = {f["id"]: f for f in prior_findings["findings"] if f["verdict"] == "confirmed"}
    current_confirmed = [f for f in current_findings["findings"] if f["verdict"] == "confirmed"]

    persisting, new, referenced = [], [], set()
    for finding in current_confirmed:
        link = finding.get("persists_from")
        match = PERSIST_PATTERN.match(link) if link else None
        if match and int(match.group(1)) == prior_run and match.group(2) in prior_confirmed:
            prior_finding = prior_confirmed[match.group(2)]
            referenced.add(match.group(2))
            before = prior_finding["severity"]["overall_severity"]
            after = finding["severity"]["overall_severity"]
            change = "same"
            if SEVERITY_ORDER[after] > SEVERITY_ORDER[before]:
                change = "worsened"
            elif SEVERITY_ORDER[after] < SEVERITY_ORDER[before]:
                change = "improved"
            persisting.append({
                "id": finding["id"], "prior_id": match.group(2), "title": finding["title"],
                "severity_before": before, "severity_after": after, "severity_change": change,
            })
        else:
            if link:
                warnings.append(f"{finding['id']}: persists_from '{link}' does not match a confirmed finding of run {prior_run}; treated as new")
            new.append({"id": finding["id"], "title": finding["title"], "severity": finding["severity"]["overall_severity"]})

    for pid in sorted(not_retested):
        if pid not in prior_confirmed:
            warnings.append(f"--not-retested {pid} is not a confirmed finding of run {prior_run}; ignored")
        elif pid in referenced:
            warnings.append(f"{pid} is listed as not retested but a current finding persists from it; treated as persisting")

    def _summary(pid, f):
        return {"prior_id": pid, "title": f["title"], "severity": f["severity"]["overall_severity"]}

    resolved = [_summary(pid, f) for pid, f in prior_confirmed.items() if pid not in referenced and pid not in not_retested]
    not_retested_items = [_summary(pid, f) for pid, f in prior_confirmed.items() if pid not in referenced and pid in not_retested]

    def metric_deltas(prior_block: dict, current_block: dict, keys: list) -> dict:
        return {k: {"before": prior_block.get(k), "after": current_block.get(k), "delta": _delta(prior_block.get(k), current_block.get(k))} for k in keys}

    task_keys = ["success_rate", "abandon_rate", "incorrect_rate", "mean_efficiency", "first_click_success_rate"]
    fi_keys = ["understood_what", "understood_audience", "understood_action", "mean_gut_rating", "would_continue_rate"]

    return {
        "schema_version": "1.0",
        "site": current_card["site"]["slug"],
        "prior_run": prior_run,
        "current_run": current_run,
        "comparable": comparable,
        "warnings": warnings,
        "categories": categories,
        "global": global_block,
        "findings": {
            "resolved": resolved,
            "persisting": persisting,
            "not_retested": not_retested_items,
            "new": new,
            "counts": {"resolved": len(resolved), "persisting": len(persisting), "not_retested": len(not_retested_items), "new": len(new)},
        },
        "task_metrics": metric_deltas(prior_card["task_metrics"], current_card["task_metrics"], task_keys),
        "first_impression_metrics": metric_deltas(prior_card["first_impression_metrics"], current_card["first_impression_metrics"], fi_keys),
        "noise_thresholds": {"category": CATEGORY_NOISE, "global": GLOBAL_NOISE},
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for name in ("prior-scorecard", "prior-findings", "current-scorecard", "current-findings", "out"):
        parser.add_argument(f"--{name}", required=True)
    parser.add_argument("--not-retested", default="", help="comma-separated prior finding ids (for example P3,P5) that the retest did not re-examine")
    args = parser.parse_args(argv)
    not_retested = [x.strip() for x in args.not_retested.split(",") if x.strip()]
    try:
        loaded = {}
        for name in ("prior_scorecard", "prior_findings", "current_scorecard", "current_findings"):
            with open(getattr(args, name), "r", encoding="utf-8") as handle:
                loaded[name] = json.load(handle)
        evolution = compare(loaded["prior_scorecard"], loaded["prior_findings"], loaded["current_scorecard"], loaded["current_findings"], not_retested)
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"error: {exc}")
        return 2
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(evolution, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    counts = evolution["findings"]["counts"]
    print(f"wrote {args.out}: global {evolution['global']['verdict']} ({evolution['global']['delta']}); "
          f"resolved {counts['resolved']}, persisting {counts['persisting']}, not re-examined {counts['not_retested']}, new {counts['new']}")
    for warning in evolution["warnings"]:
        print(f"warning: {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
