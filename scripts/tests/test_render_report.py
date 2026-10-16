import copy
import json
import os
import re
import tempfile
import unittest

import helpers
import compare_runs
import render_report as rr


def render_all(labels=None, evolution=None):
    L = dict(rr.LABELS)
    if labels:
        L.update(labels)
    f, s, led = helpers.findings(), helpers.scorecard(), helpers.ledger()
    return (rr.render_tables(f, s, led, evolution, L), rr.render_detail(f, led, L), rr.render_needs_validation(f, L))


class RenderReportTests(unittest.TestCase):
    def test_tables_contain_every_section(self):
        tables, _, _ = render_all()
        for heading in ("## Scorecard", "## Task results", "## First impression (five-second test)", "## Findings",
                        "### Quick wins", "## What works well"):
            self.assertIn(heading, tables)
        self.assertIn("**Overall: 6.9 / 10 · Fair", tables)
        self.assertIn("Not assessed", tables)

    def test_findings_table_is_sorted_by_severity(self):
        tables, _, _ = render_all()
        order = [m.group(1) for m in re.finditer(r"^\| (P[0-9]+) \|", tables, re.MULTILINE)]
        self.assertEqual(order, ["P1", "P2", "P4", "P5", "P3", "P6"])

    def test_quick_wins_listed(self):
        tables, _, _ = render_all()
        quick = tables.split("### Quick wins")[1].split("## What works well")[0]
        self.assertIn("P1", quick)
        self.assertIn("P2", quick)
        self.assertNotIn("P4", quick)

    def test_persona_names_are_used(self):
        tables, _, _ = render_all()
        self.assertIn("First-time visitor", tables)

    def test_detail_has_full_records_and_rejected_table(self):
        _, detail, _ = render_all()
        self.assertIn("## P2 — Menu labels are brand-speak and hide the ordering path", detail)
        self.assertIn("**Verification:** corrected", detail)
        self.assertIn("overall_severity: blocker -> major", detail)
        self.assertIn("## Rejected candidates", detail)
        self.assertIn("| P8 |", detail)
        self.assertIn("Suggested copy changes", detail)
        self.assertIn("S1-E03", detail)
        self.assertIn("source: goal inferred from the site", detail)

    def test_needs_validation_file(self):
        _, _, nv = render_all()
        self.assertIn("## P7", nv)
        self.assertIn("Does the home-page carousel advance automatically", nv)
        self.assertNotIn("## P1", nv)

    def test_empty_needs_validation(self):
        rec = helpers.findings()
        rec["findings"] = [f for f in rec["findings"] if f["verdict"] != "needs_validation"]
        text = rr.render_needs_validation(rec, rr.LABELS)
        self.assertIn("No open questions.", text)

    def test_label_override_falls_back_to_english(self):
        tables, _, _ = render_all({"scorecard": "Score sheet", "overall": "Total"})
        self.assertIn("## Score sheet", tables)
        self.assertIn("**Total: 6.9", tables)
        self.assertIn("## Findings", tables)

    def test_every_label_used_exists(self):
        # Rendering with a dict that raises on unknown keys proves no template key is missing from LABELS.
        class Strict(dict):
            def __missing__(self, key):
                raise AssertionError(f"label '{key}' missing")
        L = Strict(rr.LABELS)
        f, s, led = helpers.findings(), helpers.scorecard(), helpers.ledger()
        rr.render_tables(f, s, led, None, L)
        rr.render_detail(f, led, L)
        rr.render_needs_validation(f, L)

    def test_evolution_section(self):
        pc, pf = helpers.scorecard(), helpers.findings()
        cc, cf = copy.deepcopy(pc), copy.deepcopy(pf)
        cc["run"]["number"] = 2
        cf["run"] = 2
        helpers.finding(cf, "P1")["persists_from"] = "run-1:P1"
        cc["categories"]["clarity"]["final_score"] = 8.0
        evo = compare_runs.compare(pc, pf, cc, cf)

        class Strict(dict):
            def __missing__(self, key):
                raise AssertionError(f"label '{key}' missing")
        tables = rr.render_tables(cf, cc, helpers.ledger(), evo, Strict(rr.LABELS))
        self.assertIn("## Evolution since run 1", tables)
        self.assertIn("+1.5 (improved)", tables)
        self.assertIn("**Resolved** (5)", tables)
        self.assertIn("**Persisting** (1)", tables)

    def test_evolution_section_lists_not_retested(self):
        pc, pf = helpers.scorecard(), helpers.findings()
        cc, cf = copy.deepcopy(pc), copy.deepcopy(pf)
        cc["run"]["number"] = 2
        cf["run"] = 2
        evo = compare_runs.compare(pc, pf, cc, cf, not_retested=["P3"])

        class Strict(dict):
            def __missing__(self, key):
                raise AssertionError(f"label '{key}' missing")
        tables = rr.render_tables(cf, cc, helpers.ledger(), evo, Strict(rr.LABELS))
        self.assertIn("**Not re-examined** (1)", tables)
        self.assertIn("**Resolved** (5)", tables)
        # older evolution files without the key still render
        del evo["findings"]["not_retested"]
        del evo["findings"]["counts"]["not_retested"]
        rr.render_tables(cf, cc, helpers.ledger(), evo, Strict(rr.LABELS))

    def test_cli_writes_three_files_and_dumps_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "out")
            args = ["--findings", os.path.join(helpers.EXAMPLE, "findings.json"),
                    "--scorecard", os.path.join(helpers.EXAMPLE, "scorecard.json"),
                    "--ledger", os.path.join(helpers.EXAMPLE, "coverage-ledger.json"), "--out-dir", out]
            self.assertEqual(rr.main(args), 0)
            self.assertEqual(sorted(os.listdir(out)), ["FINDINGS-DETAIL.md", "NEEDS-VALIDATION.md", "report-tables.md"])
            partial = os.path.join(tmp, "labels.json")
            with open(partial, "w") as h:
                json.dump({"findings": "Achados"}, h)
            self.assertEqual(rr.main(args + ["--labels", partial]), 0)
            with open(os.path.join(out, "report-tables.md")) as h:
                self.assertIn("## Achados", h.read())
        self.assertEqual(rr.main(["--dump-labels"]), 0)


if __name__ == "__main__":
    unittest.main()
