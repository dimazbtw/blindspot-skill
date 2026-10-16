import copy
import unittest

import helpers
import validate_findings


def check(record, ledger=None, sessions=None, stage="structured"):
    return validate_findings.check(record, ledger, sessions, stage)


class ValidateFindingsTests(unittest.TestCase):
    def test_example_passes_at_verified_stage(self):
        errors, _, summary = check(helpers.findings(), helpers.ledger(), helpers.SESSIONS, "verified")
        self.assertEqual(errors, [])
        self.assertEqual(summary["verdicts"], {"confirmed": 6, "needs_validation": 1, "rejected": 1})
        self.assertEqual(summary["quick_wins"], ["P1", "P2"])

    def test_verified_stage_requires_verification(self):
        rec = helpers.findings()
        del helpers.finding(rec, "P1")["verification"]
        self.assertEqual(check(rec)[0], [])
        errors = check(rec, stage="verified")[0]
        self.assertTrue(any("P1" in e and "verification" in e for e in errors))

    def test_corrected_verification_lists_corrections(self):
        rec = helpers.findings()
        del helpers.finding(rec, "P2")["verification"]["corrections"]
        errors = check(rec)[0]
        self.assertTrue(any("must list its corrections" in e for e in errors))

    def test_confirmed_needs_observed_evidence(self):
        rec = helpers.findings()
        for item in helpers.finding(rec, "P3")["evidence"]:
            item["kind"] = "inferred"
        errors = check(rec)[0]
        self.assertTrue(any("P3" in e and "observed evidence" in e for e in errors))

    def test_design_finding_needs_rendered_or_provided_evidence(self):
        rec = helpers.findings()
        helpers.finding(rec, "P6")["category"] = "design"
        errors = check(rec)[0]
        self.assertTrue(any("P6" in e and "'rendered' or 'provided'" in e for e in errors))

    def test_rendering_dependent_wcag_needs_rendered_evidence(self):
        rec = helpers.findings()
        helpers.finding(rec, "P6")["heuristic_refs"].append("WCAG-1.4.3")
        errors = check(rec)[0]
        self.assertTrue(any("P6" in e and "rendering-dependent" in e for e in errors))

    def test_text_checkable_wcag_is_fine_with_text_evidence(self):
        rec = helpers.findings()
        helpers.finding(rec, "P6")["heuristic_refs"].append("WCAG-3.3.2")
        self.assertEqual(check(rec)[0], [])

    def test_rendered_evidence_satisfies_design_rule_when_run_allows(self):
        led = helpers.ledger()
        led["run"]["evidence_tier"] = "rendered"
        rec = helpers.findings()
        p = helpers.finding(rec, "P6")
        p["category"] = "design"
        p["evidence"][0]["tier"] = "rendered"
        self.assertEqual(check(rec, led)[0], [])

    def test_evidence_tier_cannot_exceed_run_tier(self):
        rec = helpers.findings()
        helpers.finding(rec, "P1")["evidence"][0]["tier"] = "rendered"
        errors = check(rec, helpers.ledger())[0]
        self.assertTrue(any("higher than the run's evidence tier" in e for e in errors))

    def test_severity_must_be_coherent_with_impact(self):
        rec = helpers.findings()
        helpers.finding(rec, "P1")["severity"]["overall_severity"] = "blocker"
        errors = check(rec)[0]
        self.assertTrue(any("P1" in e and "not coherent" in e for e in errors))
        rec = helpers.findings()
        p = helpers.finding(rec, "P6")
        p["severity"]["impact"]["score"] = "cosmetic"
        p["severity"]["overall_severity"] = "moderate"
        self.assertTrue(any("not coherent" in e for e in check(rec)[0]))

    def test_blocker_requires_blocking_impact(self):
        rec = helpers.findings()
        p = helpers.finding(rec, "P2")
        p["severity"]["overall_severity"] = "blocker"
        self.assertEqual([e for e in check(rec)[0] if "not coherent" in e], [])
        p["severity"]["impact"]["score"] = "major"
        self.assertTrue(any("not coherent" in e for e in check(rec)[0]))

    def test_quick_win_is_derived(self):
        rec = helpers.findings()
        helpers.finding(rec, "P1")["quick_win"] = False
        errors = check(rec)[0]
        self.assertTrue(any("P1" in e and "quick_win should be True" in e for e in errors))
        rec = helpers.findings()
        helpers.finding(rec, "P3")["quick_win"] = True
        errors = check(rec)[0]
        self.assertTrue(any("P3" in e and "quick_win should be False" in e for e in errors))

    def test_moderate_common_low_effort_is_a_quick_win(self):
        rec = helpers.findings()
        p = helpers.finding(rec, "P3")
        p["severity"]["frequency"]["score"] = "common"
        p["quick_win"] = True
        self.assertEqual([e for e in check(rec)[0] if "quick_win" in e], [])

    def test_confirmed_needs_at_least_medium_confidence(self):
        rec = helpers.findings()
        helpers.finding(rec, "P3")["confidence"]["score"] = "low"
        errors = check(rec)[0]
        self.assertTrue(any("at least medium confidence" in e for e in errors))

    def test_high_confidence_needs_two_sessions(self):
        rec = helpers.findings()
        p = helpers.finding(rec, "P6")
        p["evidence"] = p["evidence"][:1]
        p["confidence"]["score"] = "high"
        errors = check(rec)[0]
        self.assertTrue(any("two independent sessions" in e for e in errors))

    def test_high_confidence_not_allowed_when_isolation_degraded(self):
        led = helpers.ledger()
        led["run"]["isolation"] = "degraded"
        errors = check(helpers.findings(), led)[0]
        self.assertTrue(any("isolation is degraded" in e for e in errors))

    def test_log_ref_must_exist_in_sessions(self):
        rec = helpers.findings()
        helpers.finding(rec, "P1")["evidence"][0]["log_ref"] = "S1-E99"
        errors = check(rec, sessions=helpers.SESSIONS)[0]
        self.assertTrue(any("S1-E99" in e and "not found" in e for e in errors))

    def test_log_ref_must_belong_to_its_session(self):
        rec = helpers.findings()
        helpers.finding(rec, "P1")["evidence"][0]["log_ref"] = "S2-E01"
        errors = check(rec)[0]
        self.assertTrue(any("does not belong to session" in e for e in errors))

    def test_unknown_persona_in_affected_personas(self):
        rec = helpers.findings()
        helpers.finding(rec, "P1")["affected_personas"].append("ghost")
        errors = check(rec, helpers.ledger())[0]
        self.assertTrue(any("unknown persona 'ghost'" in e for e in errors))

    def test_needs_validation_cannot_carry_severity(self):
        rec = helpers.findings()
        helpers.finding(rec, "P7")["severity"] = helpers.finding(rec, "P1")["severity"]
        errors = check(rec)[0]
        self.assertTrue(any("unexpected field 'severity'" in e for e in errors))

    def test_rejected_needs_class_and_reason(self):
        rec = helpers.findings()
        p = helpers.finding(rec, "P8")
        del p["rejection_class"]
        errors = check(rec)[0]
        self.assertTrue(any("rejection_class" in e for e in errors))

    def test_duplicate_ids(self):
        rec = helpers.findings()
        rec["findings"].append(copy.deepcopy(helpers.finding(rec, "P6")))
        errors = check(rec)[0]
        self.assertTrue(any("duplicate finding id" in e for e in errors))
        rec = helpers.findings()
        rec["strengths"].append(copy.deepcopy(rec["strengths"][0]))
        self.assertTrue(any("duplicate strength id" in e for e in check(rec)[0]))

    def test_persists_from_not_allowed_in_run_one(self):
        rec = helpers.findings()
        helpers.finding(rec, "P1")["persists_from"] = "run-1:P1"
        errors = check(rec)[0]
        self.assertTrue(any("persists_from is not allowed in run 1" in e for e in errors))

    def test_persists_from_pattern(self):
        rec = helpers.findings()
        rec["run"] = 2
        helpers.finding(rec, "P1")["persists_from"] = "P1"
        errors = check(rec)[0]
        self.assertTrue(any("persists_from" in e for e in errors))

    def test_heuristic_ref_pattern(self):
        rec = helpers.findings()
        helpers.finding(rec, "P1")["heuristic_refs"] = ["XX-99"]
        self.assertTrue(check(rec)[0])
        for good in ("NN-10", "WCAG-2.4.4", "CL-01", "MB-12"):
            rec = helpers.findings()
            helpers.finding(rec, "P1")["heuristic_refs"] = [good]
            self.assertEqual(check(rec)[0], [], good)

    def test_expected_quick_win_function(self):
        rec = helpers.findings()
        self.assertTrue(validate_findings.expected_quick_win(helpers.finding(rec, "P1")))
        self.assertFalse(validate_findings.expected_quick_win(helpers.finding(rec, "P4")))

    def test_cli_exit_codes(self):
        import json
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            good = os.path.join(tmp, "f.json")
            with open(good, "w") as h:
                json.dump(helpers.findings(), h)
            self.assertEqual(validate_findings.main([good, "--stage", "verified"]), 0)
            rec = helpers.findings()
            rec["findings"] = "nope"
            bad = os.path.join(tmp, "bad.json")
            with open(bad, "w") as h:
                json.dump(rec, h)
            self.assertEqual(validate_findings.main([bad]), 1)
            self.assertEqual(validate_findings.main([os.path.join(tmp, "none.json")]), 2)


if __name__ == "__main__":
    unittest.main()
