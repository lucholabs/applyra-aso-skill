"""Offline package checks. Behavioral scenario execution is a separate evaluation."""
from __future__ import annotations

import csv
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

SKILL_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = SKILL_ROOT.parent
SPEC = importlib.util.spec_from_file_location(
    "integrity_metadata", SKILL_ROOT / "scripts" / "validate_metadata.py"
)
assert SPEC and SPEC.loader
vm = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = vm
SPEC.loader.exec_module(vm)


class SkillIntegrityTests(unittest.TestCase):
    def test_release_versions_agree(self):
        version = (SKILL_ROOT / "VERSION").read_text().strip()
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")
        skill = (SKILL_ROOT / "SKILL.md").read_text()
        self.assertIn(f'version: "{version}"', skill.split("---", 2)[1])
        self.assertEqual(version, vm.VERSION)
        for name in ("README.md", "README.es.md"):
            with self.subTest(name=name):
                self.assertIn(f"**{version}**", (REPO_ROOT / name).read_text())

    def test_local_markdown_links_resolve(self):
        documents = list(SKILL_ROOT.rglob("*.md")) + [
            REPO_ROOT / "README.md", REPO_ROOT / "README.es.md"
        ]
        for document in documents:
            for target in re.findall(r"\]\(([^)]+)\)", document.read_text()):
                target = target.strip("<>")
                url = urlsplit(target)
                if url.scheme or url.netloc or not url.path:
                    continue
                with self.subTest(document=document, target=target):
                    resolved = (document.parent / unquote(url.path)).resolve()
                    self.assertTrue(resolved.is_relative_to(REPO_ROOT))
                    self.assertTrue(resolved.exists(), f"Missing link: {target}")

    def test_entrypoint_routes_to_every_reference(self):
        entrypoint = (SKILL_ROOT / "SKILL.md").read_text()
        for reference in (SKILL_ROOT / "references").glob("*.md"):
            with self.subTest(reference=reference.name):
                self.assertIn(f"references/{reference.name}", entrypoint)
        paths = re.findall(
            r"(?:references|assets|scripts)/[\w./-]+\.(?:md|json|yaml|csv|py|sh)",
            entrypoint,
        )
        for path in paths:
            with self.subTest(path=path):
                self.assertTrue((SKILL_ROOT / path).is_file())

    def test_json_assets_are_readable(self):
        for path in (SKILL_ROOT / "assets").glob("*.json"):
            with self.subTest(path=path.name):
                payload = json.loads(path.read_text())
                self.assertIsInstance(payload, dict)
                self.assertEqual("1.0", payload["schema_version"])

    def test_csv_templates_have_unique_headers(self):
        for path in (SKILL_ROOT / "assets").glob("*.csv"):
            with self.subTest(path=path.name):
                with path.open(newline="") as stream:
                    rows = list(csv.reader(stream))
                header = rows[0]
                self.assertTrue(all(header))
                self.assertEqual(len(header), len(set(header)))
                for row in rows[1:]:
                    self.assertEqual(len(header), len(row))

    def test_behavior_cases_have_inputs_and_evaluation_criteria(self):
        evaluation = SKILL_ROOT / "evals"
        suite = json.loads((evaluation / "scenarios.json").read_text())
        self.assertEqual("1.0", suite["schema_version"])
        common = json.loads((evaluation / suite["common_fixture"]).read_text())
        self.assertTrue(common["synthetic"])
        cases = suite["cases"]
        self.assertTrue(cases)
        self.assertEqual(len(cases), len({case["id"] for case in cases}))
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertTrue(case["prompt"])
                self.assertIsInstance(case["fixture"], dict)
                for criterion in ("expected", "forbidden"):
                    self.assertTrue(case[criterion])
                    self.assertTrue(all(isinstance(item, str) and item for item in case[criterion]))
                for reference in case["references"]:
                    self.assertTrue((SKILL_ROOT / reference).is_file())
                for candidate in case["fixture"].get("candidates_from_common_fixture", []):
                    self.assertIn(candidate, common["manifests"])

    def test_complete_candidate_fixtures_validate(self):
        fixture = json.loads((SKILL_ROOT / "evals" / "fixtures" / "app.json").read_text())
        for name, manifest in fixture["manifests"].items():
            with self.subTest(candidate=name):
                for locale, fields in manifest["locales"].items():
                    result = vm.ValidationResult(issues=[], sources=[])
                    vm.validate_ios_locale(
                        result, locale, fields["ios"], source="synthetic-fixture",
                        forbidden_terms=[], require_complete=True,
                    )
                    self.assertEqual([], result.errors)

    def test_focused_title_validates_without_other_fields(self):
        result = vm.ValidationResult(issues=[], sources=[])
        title = "PocketTrail: Rutas a pie"
        self.assertEqual(24, vm.char_count(title))
        vm.validate_ios_locale(
            result, "es-ES", {"name": title}, source="synthetic-fixture",
            forbidden_terms=[],
        )
        self.assertEqual([], result.errors)
        result = vm.ValidationResult(issues=[], sources=[])
        vm.validate_ios_locale(
            result, "es-ES", {"name": "a" * 31}, source="synthetic-fixture",
            forbidden_terms=[],
        )
        self.assertTrue(any(issue.code == "chars_limit" for issue in result.errors))


if __name__ == "__main__":
    unittest.main()
