import copy
import json
import os
import tempfile
import unittest

import helpers
import compare_runs


def pair():
    prior_card = helpers.scorecard()
    prior_findings = helpers.findings()
    current_card = copy.deepcopy(prior_card)
    current_card["run"]["number"] = 2
    current_findings = copy.deepcopy(prior_findings)
    current_findings["run"] = 2
    return prior_card, prior_findings, current_card, current_findings


class CompareRunsTests(unittest.TestCase):
    def test_identical_runs_have_no_movement(self):
        evo = compare_runs.compare(*pair())
        self.assertTrue(evo["comparable"])
        self.assertEqual(evo["global"]["delta"], 0.0)
        self.assertEqual(evo["global"]["verdict"], "within_noise")
        for name, result in evo["categories"].items():
            self.assertIn(result["verdict"], ("within_noise", "not_comparable"), name)

    def test_category_movement_uses_noise_threshold(self):
        pc, pf, cc, cf = pair()
        cc["categories"]["clarity"]["final_score"] = 8.0
        cc["categories"]["navigation"]["final_score"] = 6.8
        cc["categories"]["trust"]["final_score"] = 7.0
        evo = compare_runs.compare(pc, pf, cc, cf)
        self.assertEqual(evo["categories"]["clarity"]["verdict"], "improved")
        self.assertEqual(evo["categories"]["navigation"]["verdict"], "within_noise")
        self.assertEqual(evo["categories"]["trust"]["verdict"], "regressed")
        self.assertEqual(evo["categories"]["clarity"]["delta"], 1.5)

    def test_not_assessed_categories_are_not_comparable(self):
        pc, pf, cc, cf = pair()
        evo = compare_runs.compare(pc, pf, cc, cf)
        self.assertEqual(evo["categories"]["design"]["verdict"], "not_comparable")
        self.assertIsNone(evo["categories"]["design"]["delta"])

    def test_findings_are_classified(self):
        pc, pf, cc, cf = pair()
        helpers.finding(cf, "P1")["persists_from"] = "run-1:P1"
        helpers.finding(cf, "P2")["persists_from"] = "run-1:P2"
        helpers.finding(cf, "P2")["severity"]["overall_severity"] = "moderate"
        for fid in ("P3", "P4", "P5"):
            cf["findings"] = [f for f in cf["findings"] if f["id"] != fid]
        new = copy.deepcopy(helpers.finding(cf, "P6"))
        new["id"] = "P9"
        cf["findings"] = [f for f in cf["findings"] if f["id"] != "P6"] + [new]
        evo = compare_runs.compare(pc, pf, cc, cf)
        counts = evo["findings"]["counts"]
        self.assertEqual(counts, {"resolved": 4, "persisting": 2, "not_retested": 0, "new": 1})
        persisting = {p["prior_id"]: p for p in evo["findings"]["persisting"]}
        self.assertEqual(persisting["P1"]["severity_change"], "same")
        self.assertEqual(persisting["P2"]["severity_change"], "improved")
        self.assertEqual(evo["findings"]["new"][0]["id"], "P9")
        self.assertEqual({r["prior_id"] for r in evo["findings"]["resolved"]}, {"P3", "P4", "P5", "P6"})

    def test_not_retested_findings_are_never_reported_as_resolved(self):
        pc, pf, cc, cf = pair()
        for fid in ("P3", "P4"):
            cf["findings"] = [f for f in cf["findings"] if f["id"] != fid]
        evo = compare_runs.compare(pc, pf, cc, cf, not_retested=["P3"])
        resolved = {r["prior_id"] for r in evo["findings"]["resolved"]}
        self.assertIn("P4", resolved)
        self.assertNotIn("P3", resolved)
        self.assertEqual([r["prior_id"] for r in evo["findings"]["not_retested"]], ["P3"])
        self.assertEqual(evo["findings"]["counts"]["not_retested"], 1)

    def test_not_retested_warnings(self):
        pc, pf, cc, cf = pair()
        helpers.finding(cf, "P1")["persists_from"] = "run-1:P1"
        evo = compare_runs.compare(pc, pf, cc, cf, not_retested=["P1", "P99"])
        self.assertTrue(any("P99" in w and "ignored" in w for w in evo["warnings"]))
        self.assertTrue(any("P1" in w and "treated as persisting" in w for w in evo["warnings"]))
        self.assertEqual(evo["findings"]["counts"]["not_retested"], 0)
        self.assertTrue(any(p["prior_id"] == "P1" for p in evo["findings"]["persisting"]))

    def test_worsened_severity(self):
        pc, pf, cc, cf = pair()
        p = helpers.finding(cf, "P3")
        p["persists_from"] = "run-1:P3"
        p["severity"]["impact"]["score"] = "blocking"
        p["severity"]["overall_severity"] = "major"
        evo = compare_runs.compare(pc, pf, cc, cf)
        item = next(x for x in evo["findings"]["persisting"] if x["prior_id"] == "P3")
        self.assertEqual(item["severity_change"], "worsened")

    def test_bad_persists_from_is_a_warning_and_counts_as_new(self):
        pc, pf, cc, cf = pair()
        helpers.finding(cf, "P1")["persists_from"] = "run-1:P99"
        helpers.finding(cf, "P2")["persists_from"] = "run-7:P2"
        evo = compare_runs.compare(pc, pf, cc, cf)
        self.assertEqual(sum("treated as new" in w for w in evo["warnings"]), 2)
        self.assertEqual(evo["findings"]["counts"]["persisting"], 0)

    def test_tier_change_makes_the_comparison_non_strict(self):
        pc, pf, cc, cf = pair()
        cc["run"]["evidence_tier"] = "rendered"
        evo = compare_runs.compare(pc, pf, cc, cf)
        self.assertFalse(evo["comparable"])
        self.assertEqual(evo["global"]["verdict"], "not_comparable")
        self.assertTrue(any("evidence tier changed" in w for w in evo["warnings"]))

    def test_profile_change_makes_the_comparison_non_strict(self):
        pc, pf, cc, cf = pair()
        cc["run"]["weight_profile"] = "transactional"
        evo = compare_runs.compare(pc, pf, cc, cf)
        self.assertFalse(evo["comparable"])
        self.assertTrue(any("weight profile changed" in w for w in evo["warnings"]))

    def test_run_order_and_site_warnings(self):
        pc, pf, cc, cf = pair()
        cc["run"]["number"] = 1
        cc["site"]["slug"] = "other.example"
        warnings = compare_runs.compare(pc, pf, cc, cf)["warnings"]
        self.assertTrue(any("not later than" in w for w in warnings))
        self.assertTrue(any("different sites" in w for w in warnings))

    def test_metric_deltas(self):
        pc, pf, cc, cf = pair()
        cc["task_metrics"]["success_rate"] = 0.9
        cc["first_impression_metrics"]["understood_what"] = 0.667
        evo = compare_runs.compare(pc, pf, cc, cf)
        self.assertEqual(evo["task_metrics"]["success_rate"]["delta"], round(0.9 - 0.667, 3))
        self.assertEqual(evo["first_impression_metrics"]["understood_what"]["delta"], round(0.667 - 0.167, 3))

    def test_cli_writes_evolution_file(self):
        pc, pf, cc, cf = pair()
        with tempfile.TemporaryDirectory() as tmp:
            paths = {}
            for name, data in (("pc", pc), ("pf", pf), ("cc", cc), ("cf", cf)):
                paths[name] = os.path.join(tmp, f"{name}.json")
                with open(paths[name], "w") as h:
                    json.dump(data, h)
            out = os.path.join(tmp, "evolution.json")
            code = compare_runs.main(["--prior-scorecard", paths["pc"], "--prior-findings", paths["pf"],
                                      "--current-scorecard", paths["cc"], "--current-findings", paths["cf"], "--out", out])
            self.assertEqual(code, 0)
            with open(out) as h:
                self.assertEqual(json.load(h)["prior_run"], 1)
            code = compare_runs.main(["--prior-scorecard", paths["pc"], "--prior-findings", paths["pf"],
                                      "--current-scorecard", paths["cc"], "--current-findings", paths["cf"], "--out", out,
                                      "--not-retested", "P3, P4"])
            self.assertEqual(code, 0)
            with open(out) as h:
                self.assertEqual(json.load(h)["findings"]["counts"]["not_retested"], 2)
            self.assertEqual(compare_runs.main(["--prior-scorecard", "x", "--prior-findings", "x", "--current-scorecard", "x",
                                                "--current-findings", "x", "--out", out]), 2)


if __name__ == "__main__":
    unittest.main()
