import copy
import json
import os
import tempfile
import unittest

import helpers
import compute_scores as cs


def compute(led=None, rec=None, adj="example"):
    led = led or helpers.ledger()
    rec = rec or helpers.findings()
    adjustments = helpers.adjustments() if adj == "example" else adj
    return cs.compute(rec, led, adjustments)


class ComputeScoresTests(unittest.TestCase):
    def test_example_scorecard_values(self):
        card = compute()
        cats = card["categories"]
        self.assertEqual(cats["clarity"]["final_score"], 6.5)
        self.assertEqual(cats["clarity"]["confidence"], "medium")
        self.assertEqual(cats["trust"]["computed_score"], 9.0)
        self.assertEqual(cats["trust"]["adjustment"], -1.0)
        self.assertEqual(cats["trust"]["final_score"], 8.0)
        self.assertEqual(cats["content"]["confidence"], "high")
        self.assertEqual(cats["flows"]["confidence"], "low")
        self.assertEqual(cats["accessibility"]["final_score"], 7.5)
        self.assertEqual(cats["accessibility"]["coverage"], 0.5)
        self.assertEqual(cats["design"]["status"], "not_assessed")
        self.assertEqual(cats["mobile"]["status"], "not_assessed")
        self.assertEqual(card["global"]["score"], 6.9)
        self.assertEqual(card["global"]["band"], "fair")
        self.assertEqual(card["global"]["assessed_weight"], 0.8)
        self.assertFalse(card["global"]["provisional"])
        self.assertEqual(card["run"]["weight_profile"], "default")

    def test_example_scorecard_file_matches_computation(self):
        self.assertEqual(compute(), helpers.scorecard())

    def test_penalty_decay(self):
        self.assertAlmostEqual(cs.penalty_total(["major", "major"]), 1.5 + 1.5 * 0.8)
        self.assertAlmostEqual(cs.penalty_total(["minor", "major"]), 1.5 + 0.2 * 0.8)
        self.assertEqual(cs.penalty_total([]), 0)

    def test_blocker_cap(self):
        rec = helpers.findings()
        helpers.finding(rec, "P1")["severity"]["overall_severity"] = "blocker"
        card = compute(rec=rec)
        self.assertEqual(card["categories"]["clarity"]["final_score"], 4.0)
        self.assertTrue(any("blocker" in c for c in card["categories"]["clarity"]["caps_applied"]))

    def test_major_cap(self):
        card = compute()
        self.assertTrue(any("major" in c for c in card["categories"]["clarity"]["caps_applied"]))

    def test_confidence_ceiling_limits_a_clean_category(self):
        card = compute()
        acc = card["categories"]["accessibility"]
        self.assertEqual(acc["finding_counts"], {"blocker": 0, "major": 0, "moderate": 0, "minor": 0})
        self.assertEqual(acc["confidence"], "low")
        self.assertEqual(acc["computed_score"], 7.5)

    def test_adjustment_is_bounded_and_needs_a_reason(self):
        with self.assertRaises(ValueError):
            compute(adj={"categories": {"clarity": {"adjustment": 1.5, "reason": "x"}}})
        with self.assertRaises(ValueError):
            compute(adj={"categories": {"clarity": {"adjustment": -0.5}}})

    def test_adjustment_cannot_break_the_ceiling(self):
        card = compute(adj={"categories": {"clarity": {"adjustment": 1.0, "reason": "strong strengths"}}})
        clarity = card["categories"]["clarity"]
        self.assertEqual(clarity["final_score"], 6.5)
        self.assertIn("adjustment clipped by cap", clarity["caps_applied"])

    def test_rendered_tier_with_mobile_viewport_assesses_mobile_and_design(self):
        led = helpers.ledger()
        led["run"]["evidence_tier"] = "rendered"
        u = helpers.unit(led, "U-022")
        u["status"] = "tested"
        u["sessions"] = ["S1"]
        card = compute(led=led)
        self.assertEqual(card["categories"]["mobile"]["status"], "assessed")
        self.assertEqual(card["categories"]["design"]["status"], "assessed")

    def test_mobile_needs_a_tested_mobile_viewport_unit(self):
        led = helpers.ledger()
        led["run"]["evidence_tier"] = "rendered"
        card = compute(led=led)
        self.assertEqual(card["categories"]["mobile"]["status"], "not_assessed")
        self.assertIn("mobile viewport", card["categories"]["mobile"]["reason"])

    def test_accessibility_needs_the_lens(self):
        led = helpers.ledger()
        led["units"] = [u for u in led["units"] if u["id"] != "U-017"]
        card = compute(led=led)
        self.assertEqual(card["categories"]["accessibility"]["status"], "not_assessed")

    def test_degraded_isolation_lowers_confidence(self):
        led = helpers.ledger()
        led["run"]["isolation"] = "degraded"
        cats = compute(led=led)["categories"]
        self.assertEqual(cats["content"]["confidence"], "medium")
        self.assertEqual(cats["clarity"]["confidence"], "low")

    def test_pending_findings_cap_confidence_at_medium(self):
        rec = helpers.findings()
        extra = copy.deepcopy(helpers.finding(rec, "P7"))
        extra["id"] = "P9"
        extra["category"] = "content"
        rec["findings"].append(extra)
        card = compute(rec=rec)
        self.assertEqual(card["categories"]["content"]["confidence"], "medium")
        self.assertEqual(card["categories"]["content"]["needs_validation_count"], 1)

    def test_thin_coverage_caps_and_lowers_confidence(self):
        led = helpers.ledger()
        for uid in ("U-001", "U-002"):
            helpers.unit(led, uid)["status"] = "untested"
        # clarity sources: 3 first impressions + content_trust lens; 2 untested of 4 -> coverage 0.5, not thin.
        helpers.unit(led, "U-003")["status"] = "untested"
        card = compute(led=led)
        clarity = card["categories"]["clarity"]
        self.assertEqual(clarity["coverage"], 0.25)
        self.assertEqual(clarity["confidence"], "low")
        self.assertTrue(clarity["final_score"] <= 6.5)

    def test_all_profiles_sum_to_one_hundred(self):
        for name, weights in cs.WEIGHT_PROFILES.items():
            self.assertEqual(sum(weights.values()), 100, name)
            self.assertEqual(set(weights), set(cs.CATEGORIES), name)

    def test_site_types_map_to_profiles(self):
        led = helpers.ledger()
        led["site"]["type"] = "ecommerce"
        self.assertEqual(compute(led=led)["run"]["weight_profile"], "transactional")
        led["site"]["type"] = "saas"
        self.assertEqual(compute(led=led)["run"]["weight_profile"], "app")
        led["site"]["type"] = "documentation"
        self.assertEqual(compute(led=led)["run"]["weight_profile"], "content")
        led["site"]["weight_profile"] = "transactional"
        self.assertEqual(compute(led=led)["run"]["weight_profile"], "transactional")

    def test_task_metrics(self):
        tm = compute()["task_metrics"]
        self.assertEqual(tm["attempted"], 9)
        self.assertEqual(tm["success_rate"], 0.667)
        self.assertEqual(tm["difficulty_rate"], 0.5)
        self.assertEqual(tm["abandon_rate"], 0.222)
        self.assertEqual(tm["incorrect_rate"], 0.111)
        self.assertEqual(tm["first_click_success_rate"], 0.333)
        self.assertAlmostEqual(tm["mean_efficiency"], 0.615, places=3)
        lows = next(r for r in tm["by_persona"] if r["persona"] == "low-literacy")
        self.assertEqual((lows["completed_incorrectly"], lows["abandoned"], lows["completed"]), (1, 1, 1))

    def test_blocked_attempts_are_excluded_from_rates(self):
        led = helpers.ledger()
        helpers.unit(led, "U-005")["outcome"] = "blocked"
        tm = compute(led=led)["task_metrics"]
        self.assertEqual(tm["blocked_count"], 1)
        self.assertEqual(tm["attempted"], 9)
        self.assertEqual(tm["abandon_rate"], round(1 / 8, 3))

    def test_first_impression_metrics(self):
        fm = compute()["first_impression_metrics"]
        self.assertEqual(fm["personas_tested"], 3)
        self.assertEqual(fm["understood_what"], 0.167)
        self.assertEqual(fm["mean_gut_rating"], 2.667)
        self.assertEqual(fm["would_continue_rate"], 0.333)

    def test_no_assessed_categories_gives_not_rated(self):
        led = helpers.ledger()
        for u in led["units"]:
            u["status"] = "skipped"
            u["reason"] = "test"
        card = compute(led=led)
        self.assertIsNone(card["global"]["score"])
        self.assertEqual(card["global"]["band"], "not_rated")
        self.assertEqual(card["global"]["confidence"], "none")
        self.assertTrue(card["global"]["provisional"])
        self.assertEqual(cs.validate_scorecard(card), [])

    def test_floor_warning_lists_weak_categories(self):
        rec = helpers.findings()
        helpers.finding(rec, "P1")["severity"]["overall_severity"] = "blocker"
        card = compute(rec=rec)
        self.assertIn("clarity", card["global"]["floor_warning"])
        self.assertIn("hides weak spots", card["global"]["note"])

    def test_persona_verdicts_pass_through(self):
        card = compute()
        self.assertEqual(len(card["persona_verdicts"]), 3)

    def test_validate_scorecard_accepts_computed(self):
        self.assertEqual(cs.validate_scorecard(compute()), [])

    def test_validate_scorecard_catches_tampering(self):
        card = compute()
        card["categories"]["clarity"]["final_score"] = 9.0
        errors = cs.validate_scorecard(card)
        self.assertTrue(any("major cap" in e for e in errors))
        self.assertTrue(any("not computed score plus adjustment" in e for e in errors))
        card = compute()
        card["global"]["score"] = 9.9
        self.assertTrue(any("weighted average" in e for e in cs.validate_scorecard(card)))
        card = compute()
        card["categories"]["clarity"]["weight"] = 50
        self.assertTrue(any("does not match profile" in e for e in cs.validate_scorecard(card)))

    def test_cli_compute_and_validate(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "scorecard.json")
            code = cs.main(["compute", "--findings", os.path.join(helpers.EXAMPLE, "findings.json"),
                            "--ledger", os.path.join(helpers.EXAMPLE, "coverage-ledger.json"),
                            "--adjustments", os.path.join(helpers.EXAMPLE, "adjustments.json"), "--out", out])
            self.assertEqual(code, 0)
            with open(out) as h:
                self.assertEqual(json.load(h)["global"]["score"], 6.9)
            self.assertEqual(cs.main(["validate", out]), 0)
            self.assertEqual(cs.main(["validate", os.path.join(tmp, "missing.json")]), 2)


if __name__ == "__main__":
    unittest.main()
