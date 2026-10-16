#!/usr/bin/env python3
"""Derive report files from the verified records.

Usage:
  python render_report.py --findings findings.json --scorecard scorecard.json --ledger coverage-ledger.json \
         --out-dir DIR [--evolution evolution.json] [--labels labels.json]
  python render_report.py --dump-labels > labels.json

Writes into DIR:
  report-tables.md       scorecard, task results, first impressions, findings, quick wins, strengths, evolution
  FINDINGS-DETAIL.md     every confirmed finding in full, plus a table of rejected candidates
  NEEDS-VALIDATION.md    every finding that still has an open question

Why a script: tables and per-finding detail must say exactly what the validated JSON says. The
orchestrator writes REPORT.md itself (summary, narrative, pros and cons) and pastes the tables in.

Language: all fixed text comes from a label dictionary. English is built in; to produce a report in
another language, run --dump-labels, translate the values, and pass the file with --labels. Missing keys
fall back to English. Free text inside the records is rendered as written.

Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

LABELS = {
    "scorecard": "Scorecard",
    "category": "Category", "weight": "Weight", "score": "Score", "confidence": "Confidence",
    "coverage": "Coverage", "justification": "Justification", "not_assessed": "Not assessed",
    "overall": "Overall", "band": "Band", "provisional": "Provisional result",
    "evidence_tier": "Evidence tier", "isolation": "Isolation",
    "cat_clarity": "Clarity", "cat_navigation": "Navigation", "cat_trust": "Trust", "cat_content": "Content",
    "cat_design": "Design", "cat_flows": "Flows and forms", "cat_mobile": "Mobile", "cat_accessibility": "Accessibility",
    "band_excellent": "Excellent", "band_good": "Good", "band_fair": "Fair", "band_poor": "Poor",
    "band_failing": "Failing", "band_not_rated": "Not rated",
    "conf_none": "none", "conf_low": "low", "conf_medium": "medium", "conf_high": "high",
    "sev_blocker": "Blocker", "sev_major": "Major", "sev_moderate": "Moderate", "sev_minor": "Minor",
    "effort_low": "Low", "effort_medium": "Medium", "effort_high": "High",
    "task_results": "Task results", "persona": "Persona", "attempted": "Attempted", "completed": "Completed",
    "with_difficulty": "With difficulty", "incorrectly": "Incorrectly", "abandoned": "Abandoned", "blocked": "Blocked",
    "success_rate": "Success rate", "abandon_rate": "Abandon rate", "mean_efficiency": "Path efficiency",
    "first_click": "First-click success",
    "first_impression": "First impression (five-second test)", "understood_what": "Understood what the site is",
    "understood_audience": "Understood who it is for", "understood_action": "Understood the main action",
    "gut_rating": "Gut rating (1-5)", "would_continue": "Would continue",
    "findings": "Findings", "id": "ID", "title": "Title", "severity": "Severity", "effort": "Effort", "personas": "Personas",
    "quick_wins": "Quick wins", "none": "None",
    "strengths": "What works well", "preserve": "Keep",
    "evolution": "Evolution since run {prior}", "before": "Before", "after": "After", "change": "Change",
    "resolved": "Resolved", "persisting": "Persisting", "not_retested": "Not re-examined", "new": "New",
    "verdict_improved": "improved", "verdict_regressed": "regressed", "verdict_within_noise": "within noise",
    "verdict_not_comparable": "not comparable",
    "sev_worsened": "worsened", "sev_improved": "improved", "sev_same": "unchanged",
    "detail_title": "Findings in detail", "needs_validation_title": "Needs validation",
    "description": "What happens", "user_impact": "Impact on the user", "root_cause": "Root cause",
    "intended_behavior": "What the site seems to intend", "evidence": "Evidence", "reproduction": "How to reproduce",
    "expected": "Expected", "actual": "Actual", "baseline": "How comparable sites handle it",
    "remediation": "Recommended fix", "copy_changes": "Suggested copy changes", "verification": "Verification",
    "open_question": "Open question", "resolution_path": "How to resolve it", "found_by": "Found by",
    "references": "Checks referenced", "rejected_title": "Rejected candidates", "reason": "Reason", "class": "Class",
    "impact_label": "Impact", "frequency_label": "Frequency", "persistence_label": "Persistence",
    "gap": "Gap between intent and perception", "gap_intended": "Intended", "gap_perceived": "Perceived",
    "gap_source_brief": "source: the developer's brief", "gap_source_inferred_goal": "source: goal inferred from the site",
    "persists_from": "Persists from", "no_findings": "No findings in this category.",
    "observed": "observed", "inferred": "inferred", "excerpt": "Excerpt", "steps": "Steps",
    "none_open": "No open questions.",
}

SEVERITY_ORDER = {"blocker": 0, "major": 1, "moderate": 2, "minor": 3}
CATEGORIES = ["clarity", "navigation", "trust", "content", "design", "flows", "mobile", "accessibility"]


def _pct(value):
    return "n/a" if value is None else f"{round(value * 100)}%"


def _num(value, digits=1):
    return "n/a" if value is None else f"{value:.{digits}f}"


def _sort_key(finding: dict):
    sev = finding.get("severity", {}).get("overall_severity")
    return (SEVERITY_ORDER.get(sev, 9), int(finding["id"][1:]))


def _persona_names(ledger: dict) -> dict:
    return {p["id"]: p.get("name") or p["id"] for p in ledger["personas"]}


def _evidence_line(item: dict, L: dict) -> str:
    text = f"- [{L[item['kind']]} · {item['tier']}] {item['url']} — {item['location']} ({item['log_ref']}): {item['description']}"
    if item.get("excerpt"):
        text += f" {L['excerpt']}: \"{item['excerpt']}\""
    return text


def render_tables(findings: dict, scorecard: dict, ledger: dict, evolution: dict | None, L: dict) -> str:
    out: list[str] = []
    names = _persona_names(ledger)
    run = scorecard["run"]

    out.append(f"## {L['scorecard']}\n")
    out.append(f"{L['evidence_tier']}: {run['evidence_tier']} · {L['isolation']}: {run['isolation']}\n")
    out.append(f"| {L['category']} | {L['weight']} | {L['score']} | {L['confidence']} | {L['coverage']} | {L['justification']} |")
    out.append("|---|---|---|---|---|---|")
    for category in CATEGORIES:
        r = scorecard["categories"][category]
        label = L[f"cat_{category}"]
        if r["status"] == "assessed":
            out.append(f"| {label} | {r['weight']:g} | {_num(r['final_score'])} | {L['conf_' + r['confidence']]} | {_pct(r['coverage'])} | {r['justification']} |")
        else:
            out.append(f"| {label} | {r['weight']:g} | {L['not_assessed']} | – | – | {r['reason']} |")
    g = scorecard["global"]
    provisional = f" ({L['provisional']})" if g["provisional"] else ""
    out.append(f"\n**{L['overall']}: {_num(g['score'])} / 10 · {L['band_' + g['band']]} · {L['confidence']}: {L['conf_' + g['confidence']]}{provisional}**")
    if g["note"]:
        out.append(f"\n{g['note']}")

    tm = scorecard["task_metrics"]
    out.append(f"\n## {L['task_results']}\n")
    out.append(f"| {L['persona']} | {L['attempted']} | {L['completed']} | {L['with_difficulty']} | {L['incorrectly']} | {L['abandoned']} | {L['blocked']} |")
    out.append("|---|---|---|---|---|---|---|")
    for row in tm["by_persona"]:
        out.append(f"| {names.get(row['persona'], row['persona'])} | {row['attempted']} | {row['completed']} | {row['completed_with_difficulty']} | {row['completed_incorrectly']} | {row['abandoned']} | {row['blocked']} |")
    out.append(f"\n{L['success_rate']}: {_pct(tm['success_rate'])} · {L['abandon_rate']}: {_pct(tm['abandon_rate'])} · "
               f"{L['mean_efficiency']}: {_pct(tm['mean_efficiency'])} · {L['first_click']}: {_pct(tm['first_click_success_rate'])}")

    out.append(f"\n## {L['first_impression']}\n")
    out.append(f"| {L['persona']} | {L['understood_what']} | {L['understood_audience']} | {L['understood_action']} | {L['gut_rating']} | {L['would_continue']} |")
    out.append("|---|---|---|---|---|---|")
    for unit in ledger["units"]:
        if unit["type"] == "first_impression" and "five_second" in unit and unit["status"] in ("tested", "partial"):
            fs = unit["five_second"]
            who = ", ".join(names.get(p, p) for p in unit.get("personas", []))
            out.append(f"| {who} | {fs['understood_what']} | {fs['understood_audience']} | {fs['understood_action']} | {fs['gut_rating']} | {fs['would_continue']} |")
    fm = scorecard["first_impression_metrics"]
    out.append(f"\n{L['understood_what']}: {_pct(fm['understood_what'])} · {L['understood_audience']}: {_pct(fm['understood_audience'])} · "
               f"{L['understood_action']}: {_pct(fm['understood_action'])}")

    confirmed = sorted((f for f in findings["findings"] if f["verdict"] == "confirmed"), key=_sort_key)
    out.append(f"\n## {L['findings']}\n")
    if confirmed:
        out.append(f"| {L['id']} | {L['title']} | {L['category']} | {L['severity']} | {L['effort']} | {L['personas']} |")
        out.append("|---|---|---|---|---|---|")
        for f in confirmed:
            who = ", ".join(names.get(p, p) for p in f["affected_personas"])
            out.append(f"| {f['id']} | {f['title']} | {L['cat_' + f['category']]} | {L['sev_' + f['severity']['overall_severity']]} | {L['effort_' + f['remediation']['effort']]} | {who} |")
    else:
        out.append(L["none"])

    out.append(f"\n### {L['quick_wins']}\n")
    quick = [f for f in confirmed if f["quick_win"]]
    if quick:
        for f in quick:
            out.append(f"- **{f['id']}** {f['title']} — {f['remediation']['strategy']}")
    else:
        out.append(L["none"])

    out.append(f"\n## {L['strengths']}\n")
    if findings["strengths"]:
        out.append(f"| {L['id']} | {L['title']} | {L['category']} | {L['preserve']} |")
        out.append("|---|---|---|---|")
        for s in findings["strengths"]:
            out.append(f"| {s['id']} | {s['title']} | {L['cat_' + s['category']]} | {s['preserve_note']} |")
    else:
        out.append(L["none"])

    if evolution:
        out.append(f"\n## {L['evolution'].format(prior=evolution['prior_run'])}\n")
        for warning in evolution["warnings"]:
            out.append(f"> {warning}")
        if evolution["warnings"]:
            out.append("")
        out.append(f"| {L['category']} | {L['before']} | {L['after']} | {L['change']} |")
        out.append("|---|---|---|---|")
        for category in CATEGORIES:
            c = evolution["categories"][category]
            delta = "–" if c["delta"] is None else f"{c['delta']:+.1f}"
            out.append(f"| {L['cat_' + category]} | {_num(c['before'])} | {_num(c['after'])} | {delta} ({L['verdict_' + c['verdict']]}) |")
        eg = evolution["global"]
        delta = "–" if eg["delta"] is None else f"{eg['delta']:+.1f}"
        out.append(f"| **{L['overall']}** | {_num(eg['before'])} | {_num(eg['after'])} | {delta} ({L['verdict_' + eg['verdict']]}) |")
        for key, heading in (("resolved", L["resolved"]), ("persisting", L["persisting"]), ("not_retested", L["not_retested"]), ("new", L["new"])):
            items = evolution["findings"].get(key, [])
            if key == "not_retested" and not items:
                continue
            out.append(f"\n**{heading}** ({evolution['findings'].get('counts', {}).get(key, len(items))})")
            for item in items:
                if key in ("resolved", "not_retested"):
                    out.append(f"- {item['prior_id']} {item['title']} ({L['sev_' + item['severity']]})")
                elif key == "persisting":
                    out.append(f"- {item['id']} ← {item['prior_id']} {item['title']} ({L['sev_' + item['severity_after']]}, {L['sev_' + item['severity_change']]})")
                else:
                    out.append(f"- {item['id']} {item['title']} ({L['sev_' + item['severity']]})")

    return "\n".join(out) + "\n"


def render_detail(findings: dict, ledger: dict, L: dict) -> str:
    names = _persona_names(ledger)
    out = [f"# {L['detail_title']}\n"]
    confirmed = sorted((f for f in findings["findings"] if f["verdict"] == "confirmed"), key=_sort_key)
    if not confirmed:
        out.append(L["no_findings"])
    for f in confirmed:
        sev = f["severity"]
        out.append(f"## {f['id']} — {f['title']}\n")
        out.append(f"**{L['severity']}:** {L['sev_' + sev['overall_severity']]} · **{L['category']}:** {L['cat_' + f['category']]} · "
                   f"**{L['confidence']}:** {L['conf_' + f['confidence']['score']]} · **{L['effort']}:** {L['effort_' + f['remediation']['effort']]}"
                   + (f" · **{L['quick_wins']}**" if f["quick_win"] else ""))
        out.append(f"\n**{L['personas']}:** {', '.join(names.get(p, p) for p in f['affected_personas'])} · **{L['found_by']}:** {', '.join(f['found_by'])}")
        if f.get("persists_from"):
            out.append(f"\n**{L['persists_from']}:** {f['persists_from']}")
        out.append(f"\n**{L['description']}.** {f['description']}")
        out.append(f"\n**{L['user_impact']}.** {f['user_impact']}")
        out.append(f"\n**{L['root_cause']}.** {f['root_cause']}")
        out.append(f"\n**{L['intended_behavior']}.** {f['intended_behavior']}")
        out.append(f"\n**{L['severity']}:** {L['impact_label']} {sev['impact']['score']} ({sev['impact']['reason']}); "
                   f"{L['frequency_label']} {sev['frequency']['score']} ({sev['frequency']['reason']}); "
                   f"{L['persistence_label']} {sev['persistence']['score']} ({sev['persistence']['reason']}).")
        if f.get("gap"):
            gap = f["gap"]
            out.append(f"\n**{L['gap']}** ({L['gap_source_' + gap['source']]}). {L['gap_intended']}: {gap['intended']} {L['gap_perceived']}: {gap['perceived']}")
        out.append(f"\n**{L['evidence']}**\n")
        out.extend(_evidence_line(e, L) for e in f["evidence"])
        repro = f["reproduction"]
        out.append(f"\n**{L['reproduction']}**\n")
        out.extend(f"{i}. {step}" for i, step in enumerate(repro["steps"], 1))
        out.append(f"\n{L['expected']}: {repro['expected']}\n{L['actual']}: {repro['actual']}")
        out.append(f"\n**{L['baseline']}.** {f['baseline_comparison']}")
        rem = f["remediation"]
        out.append(f"\n**{L['remediation']}.** {rem['strategy']}")
        if rem.get("copy_changes"):
            out.append(f"\n{L['copy_changes']}:")
            for c in rem["copy_changes"]:
                before = f" \"{c['before']}\" →" if c.get("before") else ""
                out.append(f"- {c['location']}:{before} \"{c['after']}\"")
        if rem.get("notes"):
            out.append(f"\n{rem['notes']}")
        if f.get("heuristic_refs"):
            out.append(f"\n**{L['references']}:** {', '.join(f['heuristic_refs'])}")
        if f.get("verification"):
            v = f["verification"]
            out.append(f"\n**{L['verification']}:** {v['status']} — {v['notes']}")
            for correction in v.get("corrections", []):
                out.append(f"- {correction}")
        out.append("")

    rejected = [f for f in findings["findings"] if f["verdict"] == "rejected"]
    if rejected:
        out.append(f"## {L['rejected_title']}\n")
        out.append(f"| {L['id']} | {L['title']} | {L['class']} | {L['reason']} |")
        out.append("|---|---|---|---|")
        for f in rejected:
            out.append(f"| {f['id']} | {f['title']} | {f['rejection_class']} | {f['reason']} |")
    return "\n".join(out) + "\n"


def render_needs_validation(findings: dict, L: dict) -> str:
    out = [f"# {L['needs_validation_title']}\n"]
    pending = [f for f in findings["findings"] if f["verdict"] == "needs_validation"]
    if not pending:
        out.append(L["none_open"])
    for f in pending:
        out.append(f"## {f['id']} — {f['title']}\n")
        out.append(f"**{L['category']}:** {L['cat_' + f['category']]} · **{L['found_by']}:** {', '.join(f['found_by'])}")
        out.append(f"\n{f['description']}")
        out.append(f"\n**{L['open_question']}.** {f['open_question']}")
        out.append(f"\n**{L['resolution_path']}.** {f['resolution_path']}")
        if f.get("gap"):
            gap = f["gap"]
            out.append(f"\n**{L['gap']}** ({L['gap_source_' + gap['source']]}). {L['gap_intended']}: {gap['intended']} {L['gap_perceived']}: {gap['perceived']}")
        out.append(f"\n**{L['evidence']}**\n")
        out.extend(_evidence_line(e, L) for e in f["evidence"])
        out.append("")
    return "\n".join(out) + "\n"


def load_labels(path: str | None) -> dict:
    labels = dict(LABELS)
    if path:
        with open(path, "r", encoding="utf-8") as handle:
            labels.update(json.load(handle))
    return labels


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--findings")
    parser.add_argument("--scorecard")
    parser.add_argument("--ledger")
    parser.add_argument("--out-dir")
    parser.add_argument("--evolution")
    parser.add_argument("--labels")
    parser.add_argument("--dump-labels", action="store_true")
    args = parser.parse_args(argv)

    if args.dump_labels:
        print(json.dumps(LABELS, indent=2, ensure_ascii=False))
        return 0
    if not (args.findings and args.scorecard and args.ledger and args.out_dir):
        parser.error("--findings, --scorecard, --ledger and --out-dir are required")

    try:
        data = {}
        for name in ("findings", "scorecard", "ledger"):
            with open(getattr(args, name), "r", encoding="utf-8") as handle:
                data[name] = json.load(handle)
        evolution = None
        if args.evolution:
            with open(args.evolution, "r", encoding="utf-8") as handle:
                evolution = json.load(handle)
        labels = load_labels(args.labels)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}")
        return 2

    os.makedirs(args.out_dir, exist_ok=True)
    files = {
        "report-tables.md": render_tables(data["findings"], data["scorecard"], data["ledger"], evolution, labels),
        "FINDINGS-DETAIL.md": render_detail(data["findings"], data["ledger"], labels),
        "NEEDS-VALIDATION.md": render_needs_validation(data["findings"], labels),
    }
    for name, content in files.items():
        with open(os.path.join(args.out_dir, name), "w", encoding="utf-8") as handle:
            handle.write(content)
        print(f"wrote {os.path.join(args.out_dir, name)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
