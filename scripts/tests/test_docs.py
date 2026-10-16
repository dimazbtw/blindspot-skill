"""Consistency tests between the documentation, the schemas, the scripts and the worked example.

The documentation is part of the contract: findings cite check IDs that must be defined, the scoring
document states numbers that the calculator uses, the skill text must stay in English and the
frontmatter must be valid. These tests fail when one of them drifts from the others.
"""
import glob
import json
import os
import re
import unittest

import helpers
import compute_scores
import validate_findings

ROOT = helpers.ROOT

CHECK_ID = r"(?:NN-(?:10|[1-9])|(?:NV|DS|CL|CT|TR|FL|MB)-[0-9]{2}|WCAG-[1-4]\.[0-9]+\.[0-9]+)"
ROW = re.compile(r"^\|\s*(" + CHECK_ID + r")\s*\|(.*)\|\s*$")
ANY_ID = re.compile(r"\b" + CHECK_ID + r"\b")

CHECK_FILES = {
    "HEURISTICS.md": ("NN", "NV", "DS"),
    "CONTENT-AND-TRUST.md": ("CL", "CT", "TR"),
    "FLOWS-AND-FORMS.md": ("FL",),
    "MOBILE-AND-PERFORMANCE.md": ("MB",),
    "ACCESSIBILITY.md": ("WCAG",),
}
EXPECTED_COUNTS = {"NN": 10, "NV": 12, "DS": 12, "CL": 12, "CT": 13, "TR": 14, "FL": 26, "MB": 16}
TIERS = {"text", "partial", "rendered"}
# Files the skill creates inside a run folder; documents mention them but they do not ship with the skill.
RUN_OUTPUTS = {"REPORT.md", "FINDINGS-DETAIL.md", "NEEDS-VALIDATION.md"}


def read(name):
    with open(os.path.join(ROOT, name), "r", encoding="utf-8") as handle:
        return handle.read()


def doc_names():
    return sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "*.md")))


def check_rows():
    """Return {file: [(id, tier, cells)]} for every check table row."""
    rows = {}
    for name in CHECK_FILES:
        found = []
        for line in read(name).splitlines():
            match = ROW.match(line)
            if match:
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                found.append((match.group(1), cells[-1], cells))
        rows[name] = found
    return rows


def prefix(check_id):
    return check_id.split("-")[0]


class CheckDefinitionTests(unittest.TestCase):
    def test_every_namespace_is_defined_in_its_file_with_the_expected_count(self):
        rows = check_rows()
        for name, prefixes in CHECK_FILES.items():
            ids = [r[0] for r in rows[name]]
            self.assertTrue(ids, f"{name} defines no checks")
            for check_id in ids:
                self.assertIn(prefix(check_id), prefixes, f"{check_id} is in the wrong file ({name})")
            for p in prefixes:
                if p in EXPECTED_COUNTS:
                    count = sum(1 for i in ids if prefix(i) == p)
                    self.assertEqual(count, EXPECTED_COUNTS[p], f"{p}: expected {EXPECTED_COUNTS[p]} checks, found {count}")

    def test_ids_are_unique_and_match_the_schema_pattern(self):
        with open(os.path.join(ROOT, "schemas", "findings.schema.json"), encoding="utf-8") as handle:
            pattern = re.compile(json.load(handle)["$defs"]["heuristic_ref"]["pattern"])
        seen = set()
        for name, found in check_rows().items():
            for check_id, _, _ in found:
                self.assertNotIn(check_id, seen, f"{check_id} is defined twice")
                seen.add(check_id)
                self.assertRegex(check_id, pattern)

    def test_ids_are_sequential_within_each_namespace(self):
        by_prefix = {}
        for found in check_rows().values():
            for check_id, _, _ in found:
                by_prefix.setdefault(prefix(check_id), []).append(check_id)
        for p, ids in by_prefix.items():
            if p == "WCAG":
                continue
            numbers = [int(i.split("-")[1]) for i in ids]
            self.assertEqual(numbers, list(range(1, len(numbers) + 1)), f"{p} ids are not 1..n in order")

    def test_every_row_has_a_valid_tier_and_five_cells(self):
        for name, found in check_rows().items():
            for check_id, tier, cells in found:
                self.assertEqual(len(cells), 5, f"{check_id}: expected 5 columns")
                self.assertIn(tier, TIERS, f"{check_id}: bad tier '{tier}'")

    def test_visual_design_checks_need_rendering(self):
        for check_id, tier, _ in check_rows()["HEURISTICS.md"]:
            if check_id.startswith("DS-"):
                self.assertEqual(tier, "rendered", check_id)

    def test_rendered_wcag_rows_match_the_validator(self):
        documented = {i.replace("WCAG-", "") for i, tier, _ in check_rows()["ACCESSIBILITY.md"] if tier == "rendered"}
        self.assertEqual(documented, set(validate_findings.RENDERED_ONLY_WCAG))

    def test_wcag_ids_are_real_level_a_and_aa_criteria(self):
        ids = {i.replace("WCAG-", "") for i, _, _ in check_rows()["ACCESSIBILITY.md"]}
        self.assertNotIn("4.1.1", ids)  # removed in WCAG 2.2
        for required in ("1.1.1", "1.4.3", "2.1.1", "2.4.7", "2.5.8", "3.3.2", "3.3.8", "4.1.2"):
            self.assertIn(required, ids)
        self.assertEqual(len(ids), len(check_rows()["ACCESSIBILITY.md"]))

    def test_every_id_used_in_the_example_is_defined(self):
        defined = {i for found in check_rows().values() for i, _, _ in found}
        used = set()
        with open(os.path.join(helpers.EXAMPLE, "findings.json"), encoding="utf-8") as handle:
            record = json.load(handle)
        for finding in record["findings"]:
            used.update(finding.get("heuristic_refs", []))
        for path in glob.glob(os.path.join(helpers.SESSIONS, "*.md")):
            with open(path, encoding="utf-8") as handle:
                used.update(ANY_ID.findall(handle.read()))
        self.assertTrue(used)
        self.assertEqual(sorted(used - defined), [], "the example uses check IDs the docs do not define")

    def test_every_id_mentioned_in_prose_is_defined(self):
        defined = {i for found in check_rows().values() for i, _, _ in found}
        for name in doc_names():
            for line in read(name).splitlines():
                if ROW.match(line):
                    continue
                for check_id in ANY_ID.findall(line):
                    if check_id in ("WCAG-1.0.0",):
                        continue
                    self.assertIn(check_id, defined, f"{name} mentions undefined check {check_id}: {line.strip()[:80]}")


class ScoringDocTests(unittest.TestCase):
    def test_tier_limits_table_matches_the_calculator(self):
        table = {}
        in_section = False
        for line in read("SCORING.md").splitlines():
            if line.startswith("## 6."):
                in_section = True
            elif line.startswith("## 7."):
                break
            elif in_section and line.startswith("| ") and not line.startswith("| Category") and not line.startswith("|---"):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if cells[0] in compute_scores.CATEGORIES:
                    table[cells[0]] = {t: (None if v == "not assessable" else v) for t, v in zip(("rendered", "provided", "text"), cells[1:4])}
        self.assertEqual(table, compute_scores.TIER_CAP)

    def test_penalties_caps_and_ceilings_are_stated_as_coded(self):
        text = read("SCORING.md")
        for severity, value in compute_scores.PENALTY.items():
            self.assertIn(f"{severity} {value}", text)
        self.assertIn(f"{compute_scores.CAP_BLOCKER}", text)
        self.assertIn(f"{compute_scores.CAP_MAJOR}", text)
        self.assertIn(f"{compute_scores.CAP_THIN_COVERAGE}", text)
        self.assertIn("0.8 raised to its position", text)
        for level, value in compute_scores.CONFIDENCE_CEILING.items():
            self.assertIn(f"{level} {value}", text)

    def test_coverage_sources_table_matches_the_calculator(self):
        text = read("SCORING.md")
        section = text.split("## 7. Coverage rule")[1].split("## 8.")[0]
        for category, sources in compute_scores.CATEGORY_SOURCES.items():
            row = next((l for l in section.splitlines() if l.startswith(f"| {category} |")), None)
            self.assertIsNotNone(row, f"{category} missing from the coverage table")
            for kind, value in sources:
                label = value.replace("_", "_") if kind == "type" else value
                self.assertIn(label, row, f"{category}: source {value} not listed")

    def test_weight_profiles_in_site_types_match_the_calculator(self):
        text = read("SITE-TYPES.md")
        section = text.split("## 4. Weight profile mapping")[1].split("## 5.")[0]
        header = next(l for l in section.splitlines() if l.startswith("| Category |"))
        profiles = [c.strip() for c in header.strip().strip("|").split("|")][1:]
        for line in section.splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells and cells[0] in compute_scores.CATEGORIES:
                for profile, value in zip(profiles, cells[1:]):
                    self.assertEqual(int(value), compute_scores.WEIGHT_PROFILES[profile][cells[0]], f"{profile}/{cells[0]}")

    def test_site_types_agree_across_schema_calculator_and_doc(self):
        with open(os.path.join(ROOT, "schemas", "ledger.schema.json"), encoding="utf-8") as handle:
            schema_types = set(json.load(handle)["$defs"]["site"]["properties"]["type"]["enum"])
        self.assertEqual(schema_types, set(compute_scores.SITE_TYPE_PROFILE))
        text = read("SITE-TYPES.md")
        headings = set(re.findall(r"^### ([a-z-]+)$", text, re.M))
        self.assertEqual(headings, schema_types)
        listed = set(re.findall(r"^- `([a-z-]+)`: ", text.split("## 3.")[0], re.M))
        self.assertEqual(listed, schema_types)
        # each type's section names the profile the calculator uses
        for site_type in schema_types:
            section = re.split(rf"^### {re.escape(site_type)}$", text, flags=re.M)[1]
            section = re.split(r"^##+ ", section, flags=re.M)[0]
            match = re.search(r"\*\*Weight profile\*\*: `([a-z]+)`", section)
            self.assertIsNotNone(match, f"{site_type}: no weight profile line")
            self.assertEqual(match.group(1), compute_scores.SITE_TYPE_PROFILE[site_type], site_type)

    def test_bands_and_noise_thresholds_are_documented(self):
        text = read("SCORING.md")
        for fragment in ("9.0 and up", "7.0 to 8.9", "5.0 to 6.9", "3.0 to 4.9", "below 3.0"):
            self.assertIn(fragment, text)
        self.assertIn("0.7", text)
        self.assertIn("0.5", text)


class PersonaDocTests(unittest.TestCase):
    def test_personas_used_in_the_site_type_file_are_defined(self):
        defined = set(re.findall(r"^### ([a-z-]+): ", read("PERSONAS.md"), re.M))
        self.assertEqual(len(defined), 10)
        for name in ("SITE-TYPES.md", "PERSONAS.md"):
            for line in read(name).splitlines():
                if line.startswith("- **Personas**:") or (line.startswith("| ") and "first-timer" in line):
                    for token in re.findall(r"[a-z]+(?:-[a-z]+)+", line):
                        if token in ("first-timer", "low-literacy", "mobile-rusher", "screen-reader", "keyboard-low-vision",
                                     "non-native", "comparison-shopper", "returning-customer", "cognitive-load"):
                            self.assertIn(token, defined)
        for site_type_line in re.findall(r"^\| ([a-z-]+) \| (.*) \| (.*) \|$", read("PERSONAS.md"), re.M):
            for cell in site_type_line[1:]:
                for persona in [p.strip() for p in cell.split(",")]:
                    if re.fullmatch(r"[a-z]+(?:-[a-z]+)*", persona) and "persona" not in persona:
                        self.assertIn(persona, defined, f"unknown persona '{persona}' in the selection matrix")


class SkillFileTests(unittest.TestCase):
    def test_frontmatter_is_valid(self):
        text = read("SKILL.md")
        match = re.match(r"---\n(.*?)\n---\n", text, re.S)
        self.assertIsNotNone(match)
        name = re.search(r"^name: (.+)$", match.group(1), re.M).group(1).strip()
        description = re.search(r"^description: (.+)$", match.group(1), re.M).group(1).strip()
        self.assertEqual(name, "blindspot")
        self.assertRegex(name, r"^[a-z0-9-]{1,64}$")
        self.assertLessEqual(len(description), 1024)
        self.assertGreater(len(description), 200)
        self.assertNotIn("<", description)
        self.assertNotIn(">", description)

    def test_file_index_lists_real_files_and_every_doc_is_indexed(self):
        text = read("SKILL.md")
        section = text.split("## File index")[1]
        indexed = re.findall(r"^\| `([^`]+)` \|", section, re.M)
        self.assertTrue(indexed)
        for entry in indexed:
            self.assertTrue(os.path.exists(os.path.join(ROOT, entry)), f"file index lists missing path {entry}")
        for name in doc_names():
            if name != "SKILL.md":
                self.assertIn(name, indexed, f"{name} is not in the file index")

    def test_referenced_documents_exist(self):
        known = set(doc_names()) | RUN_OUTPUTS
        for name in doc_names():
            for ref in re.findall(r"`([A-Z][A-Z-]+\.md)`", read(name)):
                self.assertIn(ref, known, f"{name} references missing document {ref}")

    def test_referenced_scripts_exist(self):
        for name in doc_names():
            for ref in re.findall(r"scripts/([a-z_]+\.py)", read(name)):
                self.assertTrue(os.path.exists(os.path.join(ROOT, "scripts", ref)), f"{name} references missing script {ref}")
        for ref in re.findall(r"schemas/([a-z.]+\.json)", "".join(read(n) for n in doc_names())):
            self.assertTrue(os.path.exists(os.path.join(ROOT, "schemas", ref)), f"missing schema {ref}")

    def test_every_workflow_phase_document_exists_and_has_contents(self):
        for name in doc_names():
            if name == "SKILL.md":
                continue
            text = read(name)
            if len(text.splitlines()) >= 60:
                self.assertIn("## Contents", text, f"{name} has no contents list")

    def test_documented_commands_use_real_options(self):
        text = "".join(read(n) for n in doc_names())
        for option in ("--stage", "--sessions-dir", "--ledger", "--adjustments", "--not-retested", "--dump-labels",
                       "--labels", "--evolution", "--out-dir"):
            self.assertIn(option, text)
        # every long option written next to a script call exists in that script's source
        for script in ("validate_ledger", "validate_findings", "compute_scores", "compare_runs", "render_report"):
            with open(os.path.join(ROOT, "scripts", script + ".py"), encoding="utf-8") as handle:
                source = handle.read()
            for match in re.finditer(rf"scripts/{script}\.py([^\n`]*)", text):
                for option in re.findall(r"(--[a-z][a-z-]*)", match.group(1)):
                    self.assertIn(option, source, f"{script}: documented option {option} not found in the script")


class LanguageTests(unittest.TestCase):
    PORTUGUESE_WORDS = re.compile(
        r"\b(não|você|também|então|porque|são|está|pelo|pela|isso|muito|quando|onde|uma|para o|para a|com o|com a)\b",
        re.IGNORECASE,
    )
    ACCENTED = re.compile(r"[ãõçáéíóúâêôàÃÕÇÁÉÍÓÚÂÊÔÀ]")

    def test_skill_text_is_english(self):
        patterns = ["*.md", "*.py", os.path.join("schemas", "*.json"), os.path.join("examples", "**", "*.*"),
                    os.path.join("scripts", "tests", "*.py")]
        files = set()
        for pattern in patterns:
            files.update(glob.glob(os.path.join(ROOT, pattern), recursive=True))
        files = sorted(f for f in files if os.path.isfile(f) and not f.endswith(("test_docs.py",)) and "__pycache__" not in f)
        self.assertGreater(len(files), 30)
        for path in files:
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            rel = os.path.relpath(path, ROOT)
            self.assertIsNone(self.ACCENTED.search(text), f"{rel}: accented characters found; the skill must be in English")
            self.assertIsNone(self.PORTUGUESE_WORDS.search(text), f"{rel}: Portuguese words found")

    def test_no_unfinished_markers(self):
        for name in doc_names():
            text = read(name)
            for marker in ("TBD", "FIXME", "XXX"):
                self.assertNotIn(marker, text, f"{name} contains {marker}")


if __name__ == "__main__":
    unittest.main()
