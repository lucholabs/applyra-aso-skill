#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "validate_metadata.py"
SPEC = importlib.util.spec_from_file_location("validate_metadata", MODULE_PATH)
assert SPEC and SPEC.loader
vm = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = vm
SPEC.loader.exec_module(vm)


class MetadataValidatorTests(unittest.TestCase):
    def result(self):
        return vm.ValidationResult(issues=[], sources=[])

    def write_manifest(self, root: Path, payload: dict) -> Path:
        path = root / "metadata.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def valid_locale(self) -> dict:
        return {
            "ios": {
                "name": "GapRelay",
                "subtitle": "Offline QR toolkit",
                "keywords": "airgap,qrcode,offline,scanner",
                "promotional_text": "Useful offline tools for QR workflows.",
                "description": "A clear and truthful description.",
                "whats_new": "Improved reliability.",
            },
            "android": {
                "title": "GapRelay: QR Toolkit",
                "short_description": "Offline QR tools for careful data transfer.",
                "full_description": "GapRelay provides offline QR tools for supported workflows.",
                "release_notes": "Improved reliability.",
            },
        }

    def test_valid_manifest_has_no_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_manifest(
                Path(tmp),
                {"schema_version": "1.0", "locales": {"en-US": self.valid_locale()}},
            )
            result = self.result()
            vm.validate_manifest(result, path, [])
            self.assertEqual([], result.errors)

    def test_manifest_requires_supported_schema_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_manifest(Path(tmp), {"locales": {"en-US": self.valid_locale()}})
            result = self.result()
            vm.validate_manifest(result, path, [])
            self.assertTrue(any(i.code == "unsupported_schema_version" for i in result.errors))

    def test_manifest_rejects_empty_locales(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_manifest(Path(tmp), {"schema_version": "1.0", "locales": {}})
            result = self.result()
            vm.validate_manifest(result, path, [])
            self.assertTrue(any(i.code == "empty_locales" for i in result.errors))

    def test_manifest_requires_complete_platform_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_manifest(
                Path(tmp),
                {
                    "schema_version": "1.0",
                    "locales": {
                        "en-US": {
                            "ios": {"name": "GapRelay"},
                            "android": {"title": "GapRelay"},
                        }
                    },
                },
            )
            result = self.result()
            vm.validate_manifest(result, path, [])
            missing = {i.field for i in result.errors if i.code == "required_missing"}
            self.assertTrue({"keywords", "description", "short_description", "full_description"} <= missing)

    def test_non_string_metadata_is_an_error(self):
        result = self.result()
        vm.validate_android_locale(
            result,
            "en-US",
            {"title": 123},
            source="unit",
            forbidden_terms=[],
        )
        self.assertTrue(any(i.code == "invalid_field_type" for i in result.errors))

    def test_apple_keywords_use_utf8_bytes(self):
        result = self.result()
        vm.validate_ios_locale(
            result,
            "ja",
            {"name": "テスト", "keywords": "検索語" * 12},
            source="unit",
            forbidden_terms=[],
        )
        self.assertTrue(any(i.code == "bytes_limit" for i in result.errors))

    def test_apple_keyword_tokens_must_exceed_two_characters(self):
        result = self.result()
        vm.validate_ios_locale(
            result,
            "en-US",
            {"keywords": "ai,qr,scanner"},
            source="unit",
            forbidden_terms=[],
        )
        short_tokens = {i.actual for i in result.errors if i.code == "keyword_too_short"}
        self.assertEqual({"ai", "qr"}, short_tokens)

    def test_limits_are_errors(self):
        result = self.result()
        vm.validate_ios_locale(
            result,
            "en-US",
            {"name": "A" * 31, "subtitle": "B" * 31},
            source="unit",
            forbidden_terms=[],
        )
        vm.validate_android_locale(
            result,
            "en-US",
            {"title": "C" * 31, "short_description": "D" * 81},
            source="unit",
            forbidden_terms=[],
        )
        self.assertGreaterEqual(len(result.errors), 4)

    def test_duplicate_and_overlap_are_warnings(self):
        result = self.result()
        vm.validate_ios_locale(
            result,
            "en-US",
            {
                "name": "QR Scanner",
                "subtitle": "Offline tools",
                "keywords": "qrcode,scanner,qrcode,offline",
            },
            source="unit",
            forbidden_terms=[],
        )
        codes = {i.code for i in result.warnings}
        self.assertIn("duplicate_keyword_token", codes)
        self.assertIn("indexed_field_overlap", codes)

    def test_unknown_field_is_reported_and_ignored(self):
        result = self.result()
        vm.validate_ios_locale(
            result,
            "en-US",
            {"name": "GapRelay", "typo_field": "value"},
            source="unit",
            forbidden_terms=[],
        )
        self.assertTrue(any(i.code == "unknown_field" for i in result.warnings))

    def test_forbidden_term_is_error(self):
        result = self.result()
        vm.validate_android_locale(
            result,
            "en-US",
            {"title": "CompetitorBrand Helper"},
            source="unit",
            forbidden_terms=["CompetitorBrand"],
        )
        self.assertTrue(any(i.code == "forbidden_term" for i in result.errors))

    def test_google_promotional_claims_warn(self):
        result = self.result()
        vm.validate_android_locale(
            result,
            "en-US",
            {
                "title": "Best Tracker",
                "short_description": "Download now for free.",
            },
            source="unit",
            forbidden_terms=[],
        )
        codes = {i.code for i in result.warnings}
        self.assertIn("google_ranking_claim", codes)
        self.assertIn("google_install_cta", codes)
        self.assertIn("google_price_promo", codes)

    def test_google_release_notes_have_no_unverified_hard_limit_by_default(self):
        result = self.result()
        vm.validate_android_locale(
            result,
            "en-US",
            {"release_notes": "A" * 600},
            source="unit",
            forbidden_terms=[],
        )
        self.assertFalse(any(i.code == "chars_limit" for i in result.errors))
        self.assertTrue(any(i.code == "release_notes_limit_not_enforced" for i in result.infos))

    def test_google_release_notes_optional_limit_is_enforced(self):
        result = self.result()
        vm.validate_android_locale(
            result,
            "en-US",
            {"release_notes": "A" * 501},
            source="unit",
            forbidden_terms=[],
            release_notes_limit=500,
        )
        self.assertTrue(any(i.code == "chars_limit" for i in result.errors))

    def test_fastlane_directories_require_complete_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ios = root / "ios" / "en-US"
            android = root / "android" / "en-US"
            ios.mkdir(parents=True)
            android.mkdir(parents=True)
            (ios / "name.txt").write_text("GapRelay\n", encoding="utf-8")
            (ios / "keywords.txt").write_text("offline,qrcode\n", encoding="utf-8")
            (ios / "description.txt").write_text("Truthful description.\n", encoding="utf-8")
            (android / "title.txt").write_text("GapRelay\n", encoding="utf-8")
            (android / "short_description.txt").write_text("Offline QR toolkit.\n", encoding="utf-8")
            (android / "full_description.txt").write_text("Truthful full description.\n", encoding="utf-8")
            result = self.result()
            vm.validate_ios_dir(result, root / "ios", [])
            vm.validate_android_dir(result, root / "android", [])
            self.assertEqual([], result.errors)

    def test_changelog_only_directory_does_not_require_listing_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "android"
            changelogs = root / "en-US" / "changelogs"
            changelogs.mkdir(parents=True)
            (changelogs / "100.txt").write_text("Reliability improvements.\n", encoding="utf-8")
            result = self.result()
            vm.validate_android_dir(result, root, [])
            self.assertFalse(any(i.code.startswith("required_") for i in result.errors))


if __name__ == "__main__":
    unittest.main()
