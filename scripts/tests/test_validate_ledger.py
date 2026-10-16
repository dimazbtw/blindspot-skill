import copy
import unittest

import helpers
import validate_ledger


def errors_for(led, stage="final", sessions_dir=None):
    errors, warnings, _ = validate_ledger.check(led, stage, sessions_dir)
    return errors, warnings


class ValidateLedgerTests(unittest.TestCase):
    def test_example_passes_every_stage(self):
        for stage in ("recon", "hunt", "final"):
            errors, _ = errors_for(helpers.ledger(), stage, helpers.SESSIONS)
            self.assertEqual(errors, [], stage)

    def test_schema_errors_stop_early(self):
        led = helpers.ledger()
        del led["site"]
        errors, _ = errors_for(led)
        self.assertTrue(any("site" in e for e in errors))

    def test_duplicate_unit_id(self):
        led = helpers.ledger()
        led["units"].append(copy.deepcopy(led["units"][0]))
        errors, _ = errors_for(led)
        self.assertTrue(any("duplicate unit id" in e for e in errors))

    def test_unknown_persona_reference(self):
        led = helpers.ledger()
        helpers.unit(led, "U-004")["personas"] = ["ghost"]
        errors, _ = errors_for(led)
        self.assertTrue(any("unknown persona 'ghost'" in e for e in errors))

    def test_persona_without_first_impression(self):
        led = helpers.ledger()
        led["units"] = [u for u in led["units"] if u["id"] != "U-003"]
        errors, _ = errors_for(led)
        self.assertTrue(any("skeptic" in e and "no first_impression" in e for e in errors))

    def test_persona_with_too_few_tasks(self):
        led = helpers.ledger()
        led["units"] = [u for u in led["units"] if u["id"] != "U-012"]
        errors, _ = errors_for(led)
        self.assertTrue(any("skeptic" in e and "at least 3 task units" in e for e in errors))

    def test_quick_mode_needs_fewer_tasks_and_lenses(self):
        led = helpers.ledger()
        led["run"]["mode"] = "quick"
        led["units"] = [u for u in led["units"] if u["id"] not in ("U-012", "U-009", "U-006", "U-016", "U-017", "U-018")]
        errors, _ = errors_for(led)
        self.assertEqual(errors, [])

    def test_missing_lens_is_an_error(self):
        led = helpers.ledger()
        led["units"] = [u for u in led["units"] if u["id"] != "U-016"]
        errors, _ = errors_for(led)
        self.assertTrue(any("lens 'flows_forms'" in e for e in errors))

    def test_partial_blocked_skipped_need_reason(self):
        led = helpers.ledger()
        del helpers.unit(led, "U-017")["reason"]
        errors, _ = errors_for(led)
        self.assertTrue(any("U-017" in e and "reason" in e for e in errors))

    def test_tested_unit_needs_sessions_from_hunt_stage(self):
        led = helpers.ledger()
        helpers.unit(led, "U-014")["sessions"] = []
        self.assertEqual(errors_for(led, "recon")[0], [])
        errors, _ = errors_for(led, "hunt")
        self.assertTrue(any("U-014" in e and "session" in e for e in errors))

    def test_tested_task_needs_outcome_and_steps(self):
        led = helpers.ledger()
        u = helpers.unit(led, "U-004")
        del u["outcome"]
        u["steps_taken"] = None
        errors, _ = errors_for(led, "hunt")
        self.assertTrue(any("missing 'outcome'" in e for e in errors))
        self.assertTrue(any("missing 'steps_taken'" in e for e in errors))

    def test_tested_first_impression_needs_five_second(self):
        led = helpers.ledger()
        del helpers.unit(led, "U-001")["five_second"]
        errors, _ = errors_for(led, "hunt")
        self.assertTrue(any("five_second" in e for e in errors))

    def test_outcome_only_on_task_units(self):
        led = helpers.ledger()
        helpers.unit(led, "U-014")["outcome"] = "completed"
        errors, _ = errors_for(led)
        self.assertTrue(any("only valid on task units" in e for e in errors))

    def test_hunt_stage_blocks_untested_high_priority(self):
        led = helpers.ledger()
        helpers.unit(led, "U-014")["status"] = "untested"
        errors, _ = errors_for(led, "hunt")
        self.assertTrue(any("high-priority unit is still untested" in e for e in errors))

    def test_low_priority_untested_ok_at_hunt_but_not_final(self):
        led = helpers.ledger()
        u = helpers.unit(led, "U-019")
        u["status"] = "untested"
        del u["reason"]
        self.assertEqual(errors_for(led, "hunt")[0], [])
        errors, _ = errors_for(led, "final")
        self.assertTrue(any("U-019" in e and "untested" in e for e in errors))

    def test_text_tier_cannot_test_viewports(self):
        led = helpers.ledger()
        u = helpers.unit(led, "U-022")
        u["status"] = "tested"
        u["sessions"] = ["S1"]
        errors, _ = errors_for(led, "hunt")
        self.assertTrue(any("text-only evidence" in e for e in errors))

    def test_rendered_tier_without_mobile_unit_warns(self):
        led = helpers.ledger()
        led["run"]["evidence_tier"] = "rendered"
        led["units"] = [u for u in led["units"] if u["id"] != "U-022"]
        errors, warnings = errors_for(led)
        self.assertEqual(errors, [])
        self.assertTrue(any("mobile viewport" in w for w in warnings))

    def test_brief_must_be_opened_before_final(self):
        led = helpers.ledger()
        led["run"]["brief_present"] = True
        led["run"]["brief_opened"] = False
        errors, _ = errors_for(led, "final")
        self.assertTrue(any("brief_opened" in e for e in errors))
        self.assertEqual(errors_for(led, "hunt")[0], [])

    def test_leniency_warning_when_everything_succeeds(self):
        led = helpers.ledger()
        for u in led["units"]:
            if u["type"] == "task":
                u["outcome"] = "completed"
        _, warnings = errors_for(led)
        self.assertTrue(any("leniency" in w for w in warnings))

    def test_task_text_with_quotes_warns(self):
        led = helpers.ledger()
        helpers.unit(led, "U-004")["target"] = 'Click "Atelier" to order a cake'
        _, warnings = errors_for(led)
        self.assertTrue(any("U-004" in w and "UI label" in w for w in warnings))

    def test_missing_session_log_file(self):
        led = helpers.ledger()
        helpers.unit(led, "U-004")["sessions"] = ["S9"]
        errors, _ = errors_for(led, "final", helpers.SESSIONS)
        self.assertTrue(any("S9" in e and "no log file" in e for e in errors))

    def test_cli_exit_codes(self):
        import json
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            good = os.path.join(tmp, "ok.json")
            with open(good, "w") as h:
                json.dump(helpers.ledger(), h)
            self.assertEqual(validate_ledger.main([good, "--stage", "final"]), 0)
            bad = helpers.ledger()
            del bad["units"]
            badpath = os.path.join(tmp, "bad.json")
            with open(badpath, "w") as h:
                json.dump(bad, h)
            self.assertEqual(validate_ledger.main([badpath]), 1)
            self.assertEqual(validate_ledger.main([os.path.join(tmp, "missing.json")]), 2)


if __name__ == "__main__":
    unittest.main()
