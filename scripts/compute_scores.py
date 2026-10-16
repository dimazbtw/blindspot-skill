#!/usr/bin/env python3
"""Compute the scorecard from the findings record and the coverage ledger.

Usage:
  python compute_scores.py compute --findings findings.json --ledger coverage-ledger.json \
         --out scorecard.json [--adjustments adjustments.json]
  python compute_scores.py validate scorecard.json

Why scores are computed and not typed in: the same findings must always produce the same
numbers, otherwise a retest cannot tell real improvement from a different mood. The script
turns confirmed findings into penalties, applies caps for the strongest problem and for thin
coverage, limits confidence by the evidence tier, and reports task and first-impression metrics
straight from the ledger. The orchestrator may then add a bounded judgment adjustment (at most
one point, with a reason) and a written justification per category. See SCORING.md for the rules.

adjustments.json (all keys optional):
  {
    "categories": {"clarity": {"adjustment": -0.5, "reason": "...", "justification": "..."}},
    "persona_verdicts": [{"persona": "...", "would_return": "no", "would_recommend": "no", "one_line": "..."}],
    "global_note": "..."
  }

Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schema_lite  # noqa: E402

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "schemas", "scorecard.schema.json")

CATEGORIES = ["clarity", "navigation", "trust", "content", "design", "flows", "mobile", "accessibility"]

WEIGHT_PROFILES = {
    "default":       {"clarity": 18, "navigation": 12, "trust": 14, "content": 12, "design": 8, "flows": 16, "mobile": 12, "accessibility": 8},
    "transactional": {"clarity": 14, "navigation": 12, "trust": 18, "content": 10, "design": 6, "flows": 22, "mobile": 12, "accessibility": 6},
    "app":           {"clarity": 16, "navigation": 14, "trust": 8,  "content": 10, "design": 10, "flows": 24, "mobile": 8,  "accessibility": 10},
    "content":       {"clarity": 16, "navigation": 16, "trust": 10, "content": 22, "design": 10, "flows": 4,  "mobile": 14, "accessibility": 8},
}

SITE_TYPE_PROFILE = {
    "ecommerce": "transactional",
    "marketplace": "transactional",
    "booking-hospitality": "transactional",
    "saas": "app",
    "content-publisher": "content",
    "portfolio": "content",
    "documentation": "content",
    "lead-gen-local": "default",
    "institutional-nonprofit": "default",
    "other": "default",
}

# Highest confidence each evidence tier can support per category (None = cannot be assessed).
TIER_CAP = {
    "clarity":       {"rendered": "high", "provided": "high",   "text": "medium"},
    "navigation":    {"rendered": "high", "provided": "medium", "text": "medium"},
    "trust":         {"rendered": "high", "provided": "high",   "text": "medium"},
    "content":       {"rendered": "high", "provided": "high",   "text": "high"},
    "design":        {"rendered": "high", "provided": "medium", "text": None},
    "flows":         {"rendered": "high", "provided": "low",    "text": "low"},
    "mobile":        {"rendered": "high", "provided": "low",    "text": None},
    "accessibility": {"rendered": "high", "provided": "low",    "text": "low"},
}

# Which ledger units evidence which category.
CATEGORY_SOURCES = {
    "clarity":       [("type", "first_impression"), ("lens", "content_trust")],
    "navigation":    [("type", "task"), ("lens", "heuristics")],
    "trust":         [("lens", "content_trust"), ("type", "task")],
    "content":       [("lens", "content_trust"), ("type", "exploration")],
    "design":        [("lens", "heuristics"), ("type", "viewport")],
    "flows":         [("type", "task"), ("type", "flow"), ("type", "state"), ("lens", "flows_forms")],
    "mobile":        [("type", "viewport"), ("lens", "mobile_performance")],
    "accessibility": [("lens", "accessibility")],
}

PENALTY = {"blocker": 3.0, "major": 1.5, "moderate": 0.6, "minor": 0.2}
DECAY = 0.8
# Without strong evidence a category cannot score high: absence of problems is not proof of quality.
CONFIDENCE_CEILING = {"low": 7.5, "medium": 9.0, "high": 9.5}
CAP_BLOCKER = 4.0
CAP_MAJOR = 6.5
CAP_THIN_COVERAGE = 7.0
THIN_COVERAGE = 0.5
GOOD_COVERAGE = 0.8
FLOOR = 4.0
CONFIDENCE = ["low", "medium", "high"]
YES_SCORE = {"yes": 1.0, "partly": 0.5, "maybe": 0.5, "no": 0.0}


def _matches(unit: dict, source: tuple) -> bool:
    kind, value = source
    if kind == "type":
        return unit["type"] == value
    return unit["type"] == "lens" and unit.get("lens") == value


def category_coverage(units: list, category: str):
    """Return (coverage fraction, number of tested-or-partial units). Skipped units are excluded."""
    relevant = [u for u in units if any(_matches(u, s) for s in CATEGORY_SOURCES[category]) and u["status"] != "skipped"]
    if not relevant:
        return 0.0, 0
    credit = sum(1.0 if u["status"] == "tested" else 0.5 if u["status"] == "partial" else 0.0 for u in relevant)
    tested = sum(1 for u in relevant if u["status"] in ("tested", "partial"))
    return credit / len(relevant), tested


def not_assessed_reason(category: str, units: list, tier: str):
    """Return a reason string when the category cannot be assessed, else None."""
    if TIER_CAP[category][tier] is None:
        return f"{category} cannot be judged from {tier}-only evidence"
    _, tested = category_coverage(units, category)
    if tested == 0:
        return "no unit that evidences this category was tested"
    done = ("tested", "partial")
    if category == "mobile" and not any(u["type"] == "viewport" and u.get("viewport") == "mobile" and u["status"] in done for u in units):
        return "no mobile viewport unit was tested"
    if category == "accessibility" and not any(u["type"] == "lens" and u.get("lens") == "accessibility" and u["status"] in done for u in units):
        return "the accessibility lens was not run"
    return None


def penalty_total(severities: list) -> float:
    penalties = sorted((PENALTY[s] for s in severities), reverse=True)
    return sum(p * (DECAY ** i) for i, p in enumerate(penalties))


def score_category(category: str, findings: list, units: list, tier: str, isolation: str, weight: float, adjustment: dict | None):
    reason = not_assessed_reason(category, units, tier)
    if reason:
        return {"status": "not_assessed", "weight": weight, "reason": reason}

    confirmed = [f for f in findings if f["verdict"] == "confirmed" and f["category"] == category]
    pending = [f for f in findings if f["verdict"] == "needs_validation" and f["category"] == category]
    severities = [f["severity"]["overall_severity"] for f in confirmed]
    counts = {name: severities.count(name) for name in ("blocker", "major", "moderate", "minor")}
    coverage, _ = category_coverage(units, category)

    idx = CONFIDENCE.index(TIER_CAP[category][tier])
    if coverage < THIN_COVERAGE:
        idx = 0
    elif coverage < GOOD_COVERAGE:
        idx = max(0, idx - 1)
    if isolation == "degraded":
        idx = max(0, idx - 1)
    if pending:
        idx = min(idx, 1)
    confidence = CONFIDENCE[idx]

    raw = max(0.0, 10.0 - penalty_total(severities))
    caps = [(f"{confidence} confidence: capped at {CONFIDENCE_CEILING[confidence]}", CONFIDENCE_CEILING[confidence])]
    if counts["blocker"]:
        caps.append((f"blocker present: capped at {CAP_BLOCKER}", CAP_BLOCKER))
    elif counts["major"]:
        caps.append((f"major problem present: capped at {CAP_MAJOR}", CAP_MAJOR))
    if coverage < THIN_COVERAGE:
        caps.append((f"coverage below {int(THIN_COVERAGE * 100)}%: capped at {CAP_THIN_COVERAGE}", CAP_THIN_COVERAGE))
    ceiling = min(value for _, value in caps)
    computed = round(min(raw, ceiling), 1)
    applied = [label for label, value in caps if value == ceiling and raw > value]

    adj_value = 0.0
    adj_reason = ""
    justification = None
    if adjustment:
        adj_value = round(float(adjustment.get("adjustment", 0.0)), 1)
        adj_reason = adjustment.get("reason", "")
        justification = adjustment.get("justification")
        if abs(adj_value) > 1.0:
            raise ValueError(f"{category}: adjustment {adj_value} exceeds the +/-1.0 limit")
        if adj_value != 0.0 and not adj_reason.strip():
            raise ValueError(f"{category}: a non-zero adjustment needs a reason")
    final = round(max(0.0, min(computed + adj_value, ceiling)), 1)
    if adj_value > 0 and computed + adj_value > ceiling:
        applied.append("adjustment clipped by cap")

    if justification is None:
        parts = [f"{counts[n]} {n}" for n in ("blocker", "major", "moderate", "minor") if counts[n]]
        found = ", ".join(parts) if parts else "no confirmed problems"
        justification = f"{found}; coverage {coverage:.0%}; evidence tier {tier}."

    return {
        "status": "assessed",
        "weight": weight,
        "computed_score": computed,
        "adjustment": adj_value,
        "adjustment_reason": adj_reason,
        "final_score": final,
        "confidence": confidence,
        "coverage": round(coverage, 3),
        "caps_applied": applied,
        "finding_counts": counts,
        "needs_validation_count": len(pending),
        "justification": justification,
    }


def task_metrics(units: list, personas: list) -> dict:
    tasks = [u for u in units if u["type"] == "task" and u["status"] in ("tested", "partial") and "outcome" in u]
    counts = Counter(u["outcome"] for u in tasks)
    attempted = len(tasks)
    scored = attempted - counts["blocked"]  # a blocked attempt is reported separately, not as user failure

    def rate(n: int, denominator: int):
        return round(n / denominator, 3) if denominator else None

    success = counts["completed"] + counts["completed_with_difficulty"]
    efficiencies = [
        min(1.0, u["optimal_steps"] / u["steps_taken"])
        for u in tasks
        if u["outcome"] in ("completed", "completed_with_difficulty") and u.get("optimal_steps") and u.get("steps_taken")
    ]
    first_clicks = [u["first_click_correct"] for u in tasks if u.get("first_click_correct") is not None]

    by_persona = []
    for persona in personas:
        mine = [u for u in tasks if persona["id"] in u.get("personas", [])]
        pc = Counter(u["outcome"] for u in mine)
        by_persona.append({
            "persona": persona["id"],
            "attempted": len(mine),
            "completed": pc["completed"],
            "completed_with_difficulty": pc["completed_with_difficulty"],
            "completed_incorrectly": pc["completed_incorrectly"],
            "abandoned": pc["abandoned"],
            "blocked": pc["blocked"],
        })

    return {
        "attempted": attempted,
        "success_rate": rate(success, scored),
        "difficulty_rate": rate(counts["completed_with_difficulty"], success),
        "abandon_rate": rate(counts["abandoned"], scored),
        "incorrect_rate": rate(counts["completed_incorrectly"], scored),
        "blocked_count": counts["blocked"],
        "mean_efficiency": round(sum(efficiencies) / len(efficiencies), 3) if efficiencies else None,
        "first_click_success_rate": rate(sum(1 for c in first_clicks if c), len(first_clicks)),
        "by_persona": by_persona,
    }


def first_impression_metrics(units: list) -> dict:
    rows = [u["five_second"] for u in units if u["type"] == "first_impression" and u["status"] in ("tested", "partial") and "five_second" in u]
    n = len(rows)

    def mean(values):
        return round(sum(values) / len(values), 3) if values else None

    return {
        "personas_tested": n,
        "understood_what": mean([YES_SCORE[r["understood_what"]] for r in rows]),
        "understood_audience": mean([YES_SCORE[r["understood_audience"]] for r in rows]),
        "understood_action": mean([YES_SCORE[r["understood_action"]] for r in rows]),
        "mean_gut_rating": mean([r["gut_rating"] for r in rows]),
        "would_continue_rate": mean([YES_SCORE[r["would_continue"]] for r in rows]),
    }


def band(score) -> str:
    if score is None:
        return "not_rated"
    if score >= 9.0:
        return "excellent"
    if score >= 7.0:
        return "good"
    if score >= 5.0:
        return "fair"
    if score >= 3.0:
        return "poor"
    return "failing"


def compute(findings_record: dict, ledger: dict, adjustments: dict | None = None) -> dict:
    adjustments = adjustments or {}
    run = ledger["run"]
    site = ledger["site"]
    tier = run["evidence_tier"]
    isolation = run["isolation"]
    units = ledger["units"]
    profile = site.get("weight_profile") or SITE_TYPE_PROFILE[site["type"]]
    weights = WEIGHT_PROFILES[profile]
    per_category_adj = adjustments.get("categories", {})

    categories = {}
    for category in CATEGORIES:
        categories[category] = score_category(
            category, findings_record["findings"], units, tier, isolation, weights[category], per_category_adj.get(category)
        )

    assessed = {c: r for c, r in categories.items() if r["status"] == "assessed"}
    missing = [c for c, r in categories.items() if r["status"] != "assessed"]
    assessed_weight_sum = sum(r["weight"] for r in assessed.values())
    if not assessed:
        global_block = {
            "score": None, "band": "not_rated", "assessed_weight": 0.0, "confidence": "none",
            "provisional": True, "floor_warning": [], "note": "No category could be assessed with the available evidence.",
        }
    else:
        score = round(sum(r["weight"] * r["final_score"] for r in assessed.values()) / assessed_weight_sum, 1)
        idx_mean = sum(r["weight"] * CONFIDENCE.index(r["confidence"]) for r in assessed.values()) / assessed_weight_sum
        confidence = CONFIDENCE[int(idx_mean + 0.5)]
        assessed_share = assessed_weight_sum / sum(weights.values())
        floor = [c for c, r in assessed.items() if r["final_score"] <= FLOOR]
        note_parts = []
        if missing:
            note_parts.append(f"Computed over {len(assessed)} of {len(CATEGORIES)} categories ({assessed_share:.0%} of the weight, weights renormalised); not assessed: {', '.join(missing)}.")
        if floor:
            note_parts.append(f"The average hides weak spots: {', '.join(floor)} scored {FLOOR} or lower.")
        if adjustments.get("global_note"):
            note_parts.append(adjustments["global_note"])
        global_block = {
            "score": score,
            "band": band(score),
            "assessed_weight": round(assessed_share, 3),
            "confidence": confidence,
            "provisional": assessed_share < 0.6 or confidence == "low",
            "floor_warning": floor,
            "note": " ".join(note_parts),
        }

    scorecard = {
        "schema_version": "1.0",
        "site": {"url": site["url"], "slug": site["slug"], "type": site["type"]},
        "run": {
            "number": run["number"], "mode": run["mode"], "date": run["date"],
            "evidence_tier": tier, "isolation": isolation, "weight_profile": profile,
        },
        "categories": categories,
        "global": global_block,
        "task_metrics": task_metrics(units, ledger["personas"]),
        "first_impression_metrics": first_impression_metrics(units),
    }
    if adjustments.get("persona_verdicts"):
        scorecard["persona_verdicts"] = adjustments["persona_verdicts"]

    problems = schema_lite.validate(scorecard, schema_lite.load_schema(SCHEMA_PATH))
    if problems:
        raise ValueError("computed scorecard failed its own schema: " + "; ".join(problems))
    return scorecard


def validate_scorecard(scorecard: dict) -> list:
    """Schema plus arithmetic consistency; returns a list of error strings."""
    errors = schema_lite.validate(scorecard, schema_lite.load_schema(SCHEMA_PATH))
    if errors:
        return errors
    weights = WEIGHT_PROFILES[scorecard["run"]["weight_profile"]]
    assessed = {c: r for c, r in scorecard["categories"].items() if r["status"] == "assessed"}
    for category, result in scorecard["categories"].items():
        if result["weight"] != weights[category]:
            errors.append(f"{category}: weight {result['weight']} does not match profile '{scorecard['run']['weight_profile']}'")
    for category, result in assessed.items():
        if abs(result["adjustment"]) > 1.0:
            errors.append(f"{category}: adjustment exceeds +/-1.0")
        if result["adjustment"] != 0 and not result["adjustment_reason"].strip():
            errors.append(f"{category}: non-zero adjustment without a reason")
        counts = result["finding_counts"]
        if counts["blocker"] and result["final_score"] > CAP_BLOCKER:
            errors.append(f"{category}: final score {result['final_score']} exceeds the blocker cap {CAP_BLOCKER}")
        elif counts["major"] and result["final_score"] > CAP_MAJOR:
            errors.append(f"{category}: final score {result['final_score']} exceeds the major cap {CAP_MAJOR}")
        if result["final_score"] > CONFIDENCE_CEILING[result["confidence"]]:
            errors.append(f"{category}: final score exceeds the ceiling for {result['confidence']} confidence ({CONFIDENCE_CEILING[result['confidence']]})")
        if abs(result["final_score"] - (result["computed_score"] + result["adjustment"])) > 0.15 and "adjustment clipped by cap" not in result["caps_applied"]:
            errors.append(f"{category}: final score is not computed score plus adjustment")
    if assessed:
        total = sum(r["weight"] for r in assessed.values())
        expected = round(sum(r["weight"] * r["final_score"] for r in assessed.values()) / total, 1)
        got = scorecard["global"]["score"]
        if got is None or abs(got - expected) > 0.1:
            errors.append(f"global score {got} does not match the weighted average {expected}")
    elif scorecard["global"]["score"] is not None:
        errors.append("global score must be null when no category was assessed")
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("compute")
    c.add_argument("--findings", required=True)
    c.add_argument("--ledger", required=True)
    c.add_argument("--out", required=True)
    c.add_argument("--adjustments")
    v = sub.add_parser("validate")
    v.add_argument("scorecard")
    args = parser.parse_args(argv)

    try:
        if args.command == "compute":
            with open(args.findings, "r", encoding="utf-8") as h:
                findings_record = json.load(h)
            with open(args.ledger, "r", encoding="utf-8") as h:
                ledger = json.load(h)
            adjustments = None
            if args.adjustments:
                with open(args.adjustments, "r", encoding="utf-8") as h:
                    adjustments = json.load(h)
            scorecard = compute(findings_record, ledger, adjustments)
            with open(args.out, "w", encoding="utf-8") as h:
                json.dump(scorecard, h, indent=2, ensure_ascii=False)
                h.write("\n")
            g = scorecard["global"]
            print(f"wrote {args.out}: global {g['score']} ({g['band']}, confidence {g['confidence']}{', provisional' if g['provisional'] else ''})")
            return 0
        with open(args.scorecard, "r", encoding="utf-8") as h:
            scorecard = json.load(h)
        errors = validate_scorecard(scorecard)
        for error in errors:
            print(f"error: {error}")
        print(f"INVALID ({len(errors)} error(s))" if errors else "OK")
        return 1 if errors else 0
    except (OSError, json.JSONDecodeError, ValueError, KeyError) as exc:
        print(f"error: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
