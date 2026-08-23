#!/usr/bin/env python3
"""Validate App Store and Google Play metadata.

No external dependencies.

Supported inputs:
  --manifest metadata-manifest.json
  --ios-dir fastlane/metadata
  --android-dir fastlane/metadata/android
  --forbidden-terms terms.txt
  --output validation.json
  --strict
  --self-test

Exit codes:
  0 = no errors (warnings allowed unless --strict)
  1 = one or more validation errors
  2 = warnings present with --strict
  64 = invalid CLI/input
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import unicodedata
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

VERSION = "1.2.0"

IOS_LIMITS = {
    "name": ("chars", 30),
    "subtitle": ("chars", 30),
    "keywords": ("bytes", 100),
    "promotional_text": ("chars", 170),
    "description": ("chars", 4000),
    "whats_new": ("chars", 4000),
}

IOS_REQUIRED_FIELDS = ("name", "keywords", "description")

ANDROID_LIMITS = {
    "title": ("chars", 30),
    "short_description": ("chars", 80),
    "full_description": ("chars", 4000),
}

IOS_FILE_MAP = {
    "name.txt": "name",
    "subtitle.txt": "subtitle",
    "keywords.txt": "keywords",
    "promotional_text.txt": "promotional_text",
    "description.txt": "description",
    "release_notes.txt": "whats_new",
}

ANDROID_REQUIRED_FIELDS = ("title", "short_description", "full_description")

ANDROID_FILE_MAP = {
    "title.txt": "title",
    "short_description.txt": "short_description",
    "full_description.txt": "full_description",
}

GOOGLE_PROMOTIONAL_PATTERNS = {
    "ranking_claim": re.compile(r"(?i)(?:^|\W)(?:#\s*1|number\s+one|best|top[-\s]?\d*)(?:$|\W)"),
    "install_cta": re.compile(r"(?i)\b(?:download|install|update)\s+(?:now|today)\b"),
    "price_promo": re.compile(r"(?i)(?:^|\W)(?:free|sale|discount|limited[-\s]time)(?:$|\W)"),
}

CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
REPEATED_PUNCT_RE = re.compile(r"([!?.,:_\-])\1{2,}")
WORD_RE = re.compile(r"[^\W_]+(?:['’\-][^\W_]+)*", re.UNICODE)
LOCALE_RE = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "de", "del", "der", "die",
    "das", "el", "en", "for", "from", "für", "in", "is", "it", "la", "las", "le",
    "les", "los", "of", "on", "or", "para", "the", "to", "un", "una", "und", "y",
    "your", "you", "with",
}


@dataclass(frozen=True)
class Issue:
    severity: str
    platform: str
    locale: str
    field: str
    code: str
    message: str
    actual: int | str | None = None
    limit: int | None = None
    source: str | None = None


@dataclass
class ValidationResult:
    issues: list[Issue]
    sources: list[str]

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def infos(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "info"]


def normalize_space(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).split())


def normalized_term(value: str) -> str:
    return normalize_space(value).casefold()


def char_count(value: str) -> int:
    return len(value)


def utf8_bytes(value: str) -> int:
    return len(value.encode("utf-8"))


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path} is not valid UTF-8: {exc}") from exc


def load_forbidden_terms(path: Path | None) -> list[str]:
    if path is None:
        return []
    if not path.is_file():
        raise ValueError(f"Forbidden terms file not found: {path}")
    terms = []
    for raw in read_text(path).splitlines():
        value = raw.strip()
        if not value or value.startswith("#"):
            continue
        terms.append(value)
    return terms


def add_issue(
    result: ValidationResult,
    *,
    severity: str,
    platform: str,
    locale: str,
    field: str,
    code: str,
    message: str,
    actual: int | str | None = None,
    limit: int | None = None,
    source: str | None = None,
) -> None:
    result.issues.append(
        Issue(
            severity=severity,
            platform=platform,
            locale=locale,
            field=field,
            code=code,
            message=message,
            actual=actual,
            limit=limit,
            source=source,
        )
    )


def validate_common(
    result: ValidationResult,
    *,
    platform: str,
    locale: str,
    field: str,
    value: str,
    source: str,
    forbidden_terms: Sequence[str],
) -> None:
    if value != value.strip():
        add_issue(
            result,
            severity="warning",
            platform=platform,
            locale=locale,
            field=field,
            code="outer_whitespace",
            message="Field has leading or trailing whitespace.",
            source=source,
        )

    if "\r" in value:
        add_issue(
            result,
            severity="info",
            platform=platform,
            locale=locale,
            field=field,
            code="carriage_return",
            message="Field contains CR line endings; normalize if the repository expects LF.",
            source=source,
        )

    if CONTROL_RE.search(value):
        add_issue(
            result,
            severity="error",
            platform=platform,
            locale=locale,
            field=field,
            code="control_character",
            message="Field contains an unsupported control character.",
            source=source,
        )

    if REPEATED_PUNCT_RE.search(value):
        add_issue(
            result,
            severity="warning",
            platform=platform,
            locale=locale,
            field=field,
            code="repeated_punctuation",
            message="Field contains excessive repeated punctuation.",
            source=source,
        )

    folded = unicodedata.normalize("NFKC", value).casefold()
    for term in forbidden_terms:
        needle = unicodedata.normalize("NFKC", term).casefold()
        if needle and needle in folded:
            add_issue(
                result,
                severity="error",
                platform=platform,
                locale=locale,
                field=field,
                code="forbidden_term",
                message=f"Field contains forbidden or trademark-sensitive term: {term!r}.",
                actual=term,
                source=source,
            )


def validate_limit(
    result: ValidationResult,
    *,
    platform: str,
    locale: str,
    field: str,
    value: str,
    unit: str,
    limit: int,
    source: str,
) -> None:
    actual = utf8_bytes(value) if unit == "bytes" else char_count(value)
    if actual > limit:
        add_issue(
            result,
            severity="error",
            platform=platform,
            locale=locale,
            field=field,
            code=f"{unit}_limit",
            message=f"Field exceeds the {limit}-{unit} limit.",
            actual=actual,
            limit=limit,
            source=source,
        )


def token_words(value: str) -> list[str]:
    return [normalized_term(m.group(0)) for m in WORD_RE.finditer(value)]


def validate_extreme_repetition(
    result: ValidationResult,
    *,
    platform: str,
    locale: str,
    field: str,
    value: str,
    source: str,
) -> None:
    words = [w for w in token_words(value) if len(w) > 2 and w not in STOPWORDS]
    if len(words) < 20:
        return
    counts = Counter(words)
    total = len(words)
    for word, count in counts.most_common(5):
        ratio = count / total
        if count >= 8 and ratio >= 0.04:
            add_issue(
                result,
                severity="warning",
                platform=platform,
                locale=locale,
                field=field,
                code="extreme_repetition_heuristic",
                message=(
                    f"Term {word!r} appears {count} times ({ratio:.1%}). "
                    "This is a heuristic warning for possible keyword stuffing, not a store rule."
                ),
                actual=count,
                source=source,
            )



def normalize_metadata_fields(
    result: ValidationResult,
    *,
    platform: str,
    locale: str,
    fields: Mapping[str, Any],
    known_fields: set[str],
    source: str,
) -> dict[str, str]:
    """Return known string fields while reporting schema/type problems."""

    normalized: dict[str, str] = {}
    for key, value in fields.items():
        field = str(key)
        if field not in known_fields:
            add_issue(
                result,
                severity="warning",
                platform=platform,
                locale=locale,
                field=field,
                code="unknown_field",
                message="Field is not recognized by this metadata schema and was ignored.",
                source=source,
            )
            continue
        if value is None:
            normalized[field] = ""
            continue
        if not isinstance(value, str):
            add_issue(
                result,
                severity="error",
                platform=platform,
                locale=locale,
                field=field,
                code="invalid_field_type",
                message="Metadata field must be a string or null.",
                actual=type(value).__name__,
                source=source,
            )
            normalized[field] = ""
            continue
        normalized[field] = value
    return normalized


def validate_required_fields(
    result: ValidationResult,
    *,
    platform: str,
    locale: str,
    fields: Mapping[str, str],
    required_fields: Sequence[str],
    source: str,
) -> None:
    for field in required_fields:
        if field not in fields:
            add_issue(
                result,
                severity="error",
                platform=platform,
                locale=locale,
                field=field,
                code="required_missing",
                message="Required metadata field is missing.",
                source=source,
            )
        elif not fields[field].strip():
            add_issue(
                result,
                severity="error",
                platform=platform,
                locale=locale,
                field=field,
                code="required_empty",
                message="Required metadata field is empty.",
                source=source,
            )

def validate_ios_locale(
    result: ValidationResult,
    locale: str,
    fields: Mapping[str, Any],
    *,
    source: str,
    forbidden_terms: Sequence[str],
    require_complete: bool = False,
) -> None:
    normalized_fields = normalize_metadata_fields(
        result,
        platform="ios",
        locale=locale,
        fields=fields,
        known_fields=set(IOS_LIMITS),
        source=source,
    )

    for field, (unit, limit) in IOS_LIMITS.items():
        if field not in normalized_fields:
            continue
        value = normalized_fields[field]
        validate_common(
            result,
            platform="ios",
            locale=locale,
            field=field,
            value=value,
            source=source,
            forbidden_terms=forbidden_terms,
        )
        validate_limit(
            result,
            platform="ios",
            locale=locale,
            field=field,
            value=value,
            unit=unit,
            limit=limit,
            source=source,
        )

    if require_complete:
        validate_required_fields(
            result,
            platform="ios",
            locale=locale,
            fields=normalized_fields,
            required_fields=IOS_REQUIRED_FIELDS,
            source=source,
        )

    name = normalized_fields.get("name", "")
    if name and char_count(name) < 2:
        add_issue(
            result,
            severity="error",
            platform="ios",
            locale=locale,
            field="name",
            code="minimum_length",
            message="Apple app name must contain at least 2 characters.",
            actual=char_count(name),
            limit=2,
            source=source,
        )

    keywords = normalized_fields.get("keywords", "")
    if keywords:
        if ", " in keywords:
            add_issue(
                result,
                severity="warning",
                platform="ios",
                locale=locale,
                field="keywords",
                code="comma_space",
                message="Keyword field contains spaces after commas, which consume the byte budget.",
                source=source,
            )
        raw_tokens = [part.strip() for part in keywords.split(",")]
        for token in raw_tokens:
            if token and char_count(token) <= 2:
                add_issue(
                    result,
                    severity="error",
                    platform="ios",
                    locale=locale,
                    field="keywords",
                    code="keyword_too_short",
                    message="Each Apple keyword token must contain more than 2 characters.",
                    actual=token,
                    limit=3,
                    source=source,
                )
        if any(not token for token in raw_tokens):
            add_issue(
                result,
                severity="warning",
                platform="ios",
                locale=locale,
                field="keywords",
                code="empty_keyword_token",
                message="Keyword field contains an empty comma-separated token.",
                source=source,
            )
        normalized_tokens = [normalized_term(token) for token in raw_tokens if token]
        duplicate_tokens = sorted(
            token for token, count in Counter(normalized_tokens).items() if count > 1
        )
        for token in duplicate_tokens:
            add_issue(
                result,
                severity="warning",
                platform="ios",
                locale=locale,
                field="keywords",
                code="duplicate_keyword_token",
                message=f"Keyword token is duplicated: {token!r}.",
                actual=token,
                source=source,
            )

        indexed_text = " ".join(
            [
                normalized_fields.get("name", ""),
                normalized_fields.get("subtitle", ""),
            ]
        )
        indexed_words = set(token_words(indexed_text))
        keyword_words = set()
        for token in raw_tokens:
            keyword_words.update(token_words(token))
        overlaps = sorted(
            word for word in keyword_words & indexed_words if len(word) > 1 and word not in STOPWORDS
        )
        if overlaps:
            add_issue(
                result,
                severity="warning",
                platform="ios",
                locale=locale,
                field="keywords",
                code="indexed_field_overlap",
                message=(
                    "Keyword field repeats terms already present in name/subtitle: "
                    + ", ".join(overlaps)
                    + ". Review whether the duplication is intentional."
                ),
                actual=", ".join(overlaps),
                source=source,
            )

    for field in ("name", "subtitle", "promotional_text"):
        value = normalized_fields.get(field, "")
        if value and len(value) >= 4:
            alpha = [c for c in value if c.isalpha()]
            if len(alpha) >= 4 and sum(c.isupper() for c in alpha) / len(alpha) > 0.75:
                add_issue(
                    result,
                    severity="warning",
                    platform="ios",
                    locale=locale,
                    field=field,
                    code="excessive_caps",
                    message="Field is predominantly uppercase; verify readability and policy fit.",
                    source=source,
                )


def validate_android_locale(
    result: ValidationResult,
    locale: str,
    fields: Mapping[str, Any],
    *,
    source: str,
    forbidden_terms: Sequence[str],
    release_notes_limit: int | None = None,
    require_complete: bool = False,
) -> None:
    normalized_fields = normalize_metadata_fields(
        result,
        platform="android",
        locale=locale,
        fields=fields,
        known_fields=set(ANDROID_LIMITS) | {"release_notes"},
        source=source,
    )

    for field, (unit, limit) in ANDROID_LIMITS.items():
        if field not in normalized_fields:
            continue
        value = normalized_fields[field]
        validate_common(
            result,
            platform="android",
            locale=locale,
            field=field,
            value=value,
            source=source,
            forbidden_terms=forbidden_terms,
        )
        validate_limit(
            result,
            platform="android",
            locale=locale,
            field=field,
            value=value,
            unit=unit,
            limit=limit,
            source=source,
        )
        if field == "full_description":
            validate_extreme_repetition(
                result,
                platform="android",
                locale=locale,
                field=field,
                value=value,
                source=source,
            )

    if "release_notes" in normalized_fields:
        release_notes = normalized_fields["release_notes"]
        validate_common(
            result,
            platform="android",
            locale=locale,
            field="release_notes",
            value=release_notes,
            source=source,
            forbidden_terms=forbidden_terms,
        )
        if release_notes_limit is not None:
            validate_limit(
                result,
                platform="android",
                locale=locale,
                field="release_notes",
                value=release_notes,
                unit="chars",
                limit=release_notes_limit,
                source=source,
            )
        else:
            add_issue(
                result,
                severity="info",
                platform="android",
                locale=locale,
                field="release_notes",
                code="release_notes_limit_not_enforced",
                message=(
                    "No universal Google Play release-notes limit is enforced by default. "
                    "Pass --android-release-notes-limit when a verified workflow-specific limit applies."
                ),
                actual=char_count(release_notes),
                source=source,
            )

    if require_complete:
        validate_required_fields(
            result,
            platform="android",
            locale=locale,
            fields=normalized_fields,
            required_fields=ANDROID_REQUIRED_FIELDS,
            source=source,
        )

    for field in ("title", "short_description"):
        value = normalized_fields.get(field, "")
        for code, pattern in GOOGLE_PROMOTIONAL_PATTERNS.items():
            if pattern.search(value):
                add_issue(
                    result,
                    severity="warning",
                    platform="android",
                    locale=locale,
                    field=field,
                    code=f"google_{code}",
                    message=(
                        "Field contains wording that may imply ranking, promotion, price, "
                        "or an install call-to-action. Verify current Google Play metadata policy."
                    ),
                    source=source,
                )

    title = normalized_fields.get("title", "")
    if title:
        alpha = [c for c in title if c.isalpha()]
        if len(alpha) >= 4 and sum(c.isupper() for c in alpha) / len(alpha) > 0.75:
            add_issue(
                result,
                severity="warning",
                platform="android",
                locale=locale,
                field="title",
                code="excessive_caps",
                message="Title is predominantly uppercase; verify brand styling and policy fit.",
                source=source,
            )


def load_manifest(path: Path) -> Mapping[str, Any]:
    if not path.is_file():
        raise ValueError(f"Manifest not found: {path}")
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON manifest {path}: {exc}") from exc
    if not isinstance(data, Mapping):
        raise ValueError("Manifest root must be a JSON object.")
    return data


def validate_manifest(
    result: ValidationResult,
    path: Path,
    forbidden_terms: Sequence[str],
    android_release_notes_limit: int | None = None,
) -> None:
    data = load_manifest(path)
    result.sources.append(str(path))

    schema_version = data.get("schema_version")
    if schema_version != "1.0":
        add_issue(
            result,
            severity="error",
            platform="manifest",
            locale="*",
            field="schema_version",
            code="unsupported_schema_version",
            message="Manifest schema_version must be the string '1.0'.",
            actual=None if schema_version is None else str(schema_version),
            source=str(path),
        )

    locales = data.get("locales")
    if not isinstance(locales, Mapping):
        raise ValueError("Manifest must contain an object at `locales`.")
    if not locales:
        add_issue(
            result,
            severity="error",
            platform="manifest",
            locale="*",
            field="locales",
            code="empty_locales",
            message="Manifest must contain at least one locale.",
            source=str(path),
        )

    for locale, locale_data in locales.items():
        locale_name = str(locale)
        if not isinstance(locale, str) or not LOCALE_RE.fullmatch(locale):
            add_issue(
                result,
                severity="warning",
                platform="manifest",
                locale=locale_name,
                field="locale",
                code="locale_format",
                message="Locale key is not a conventional BCP-47 language or language-region tag.",
                source=str(path),
            )
        if not isinstance(locale_data, Mapping):
            add_issue(
                result,
                severity="error",
                platform="manifest",
                locale=locale_name,
                field="locales",
                code="invalid_locale_object",
                message="Locale entry must be an object.",
                source=str(path),
            )
            continue

        ios = locale_data.get("ios")
        android = locale_data.get("android")
        if ios is not None and not isinstance(ios, Mapping):
            add_issue(
                result,
                severity="error",
                platform="manifest",
                locale=locale_name,
                field="ios",
                code="invalid_platform_object",
                message="`ios` metadata must be an object.",
                actual=type(ios).__name__,
                source=str(path),
            )
        if android is not None and not isinstance(android, Mapping):
            add_issue(
                result,
                severity="error",
                platform="manifest",
                locale=locale_name,
                field="android",
                code="invalid_platform_object",
                message="`android` metadata must be an object.",
                actual=type(android).__name__,
                source=str(path),
            )

        if isinstance(ios, Mapping):
            validate_ios_locale(
                result,
                locale_name,
                ios,
                source=str(path),
                forbidden_terms=forbidden_terms,
                require_complete=True,
            )
        if isinstance(android, Mapping):
            validate_android_locale(
                result,
                locale_name,
                android,
                source=str(path),
                forbidden_terms=forbidden_terms,
                release_notes_limit=android_release_notes_limit,
                require_complete=True,
            )
        if ios is None and android is None:
            add_issue(
                result,
                severity="warning",
                platform="manifest",
                locale=locale_name,
                field="locale",
                code="no_platform_metadata",
                message="Locale has neither `ios` nor `android` metadata.",
                source=str(path),
            )


def list_locale_dirs(root: Path, *, exclude: set[str] | None = None) -> list[Path]:
    if not root.is_dir():
        raise ValueError(f"Metadata directory not found: {root}")
    exclude = exclude or set()
    return sorted(
        path for path in root.iterdir()
        if path.is_dir() and not path.name.startswith(".") and path.name not in exclude
    )


def validate_ios_dir(
    result: ValidationResult,
    root: Path,
    forbidden_terms: Sequence[str],
) -> None:
    result.sources.append(str(root))
    for locale_dir in list_locale_dirs(root, exclude={"android", "screenshots", "review_information"}):
        fields: dict[str, str] = {}
        for filename, field in IOS_FILE_MAP.items():
            path = locale_dir / filename
            if path.is_file():
                fields[field] = read_text(path).rstrip("\n")
        if fields:
            validate_ios_locale(
                result,
                locale_dir.name,
                fields,
                source=str(locale_dir),
                forbidden_terms=forbidden_terms,
                require_complete=True,
            )


def validate_android_dir(
    result: ValidationResult,
    root: Path,
    forbidden_terms: Sequence[str],
    android_release_notes_limit: int | None = None,
) -> None:
    result.sources.append(str(root))
    for locale_dir in list_locale_dirs(root):
        fields: dict[str, str] = {}
        for filename, field in ANDROID_FILE_MAP.items():
            path = locale_dir / filename
            if path.is_file():
                fields[field] = read_text(path).rstrip("\n")

        if fields:
            validate_android_locale(
                result,
                locale_dir.name,
                fields,
                source=str(locale_dir),
                forbidden_terms=forbidden_terms,
                release_notes_limit=android_release_notes_limit,
                require_complete=True,
            )

        changelogs = locale_dir / "changelogs"
        if changelogs.is_dir():
            for path in sorted(changelogs.glob("*.txt")):
                validate_android_locale(
                    result,
                    locale_dir.name,
                    {"release_notes": read_text(path).rstrip("\n")},
                    source=str(path),
                    forbidden_terms=forbidden_terms,
                    release_notes_limit=android_release_notes_limit,
                )


def result_payload(result: ValidationResult, strict: bool) -> dict[str, Any]:
    status = "pass"
    if result.errors:
        status = "fail"
    elif strict and result.warnings:
        status = "warn-fail"
    elif result.warnings:
        status = "pass-with-warnings"

    return {
        "validator": "applyra-aso-metadata",
        "version": VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "strict": strict,
        "sources": result.sources,
        "summary": {
            "errors": len(result.errors),
            "warnings": len(result.warnings),
            "infos": len(result.infos),
            "total": len(result.issues),
        },
        "issues": [asdict(issue) for issue in result.issues],
    }


def print_human(payload: Mapping[str, Any]) -> None:
    summary = payload["summary"]
    print(
        f"Validation: {payload['status']} — "
        f"{summary['errors']} error(s), {summary['warnings']} warning(s), "
        f"{summary['infos']} info"
    )
    for issue in payload["issues"]:
        location = f"{issue['platform']}:{issue['locale']}:{issue['field']}"
        suffix = ""
        if issue.get("actual") is not None:
            suffix += f" actual={issue['actual']}"
        if issue.get("limit") is not None:
            suffix += f" limit={issue['limit']}"
        print(f"[{issue['severity'].upper()}] {location} {issue['code']}: {issue['message']}{suffix}")


def run_self_test() -> int:
    result = ValidationResult(issues=[], sources=["self-test"])
    forbidden = ["CompetitorBrand"]
    validate_ios_locale(
        result,
        "en-US",
        {
            "name": "Demo Tracker",
            "subtitle": "Private offline records",
            "keywords": "tracker,offline,CompetitorBrand",
            "promotional_text": "A clear product message.",
            "description": "A truthful description.",
            "whats_new": "Improved import reliability.",
        },
        source="self-test",
        forbidden_terms=forbidden,
    )
    validate_android_locale(
        result,
        "en-US",
        {
            "title": "BEST Demo Tracker",
            "short_description": "Download now and track records.",
            "full_description": ("track " * 12) + ("useful details " * 20),
            "release_notes": "Improved import reliability.",
        },
        source="self-test",
        forbidden_terms=[],
    )
    codes = {issue.code for issue in result.issues}
    required = {
        "forbidden_term",
        "indexed_field_overlap",
        "google_ranking_claim",
        "google_install_cta",
        "extreme_repetition_heuristic",
    }
    missing = required - codes
    if missing:
        print(f"Self-test failed; missing issue codes: {sorted(missing)}", file=sys.stderr)
        return 1

    byte_result = ValidationResult(issues=[], sources=["self-test"])
    validate_ios_locale(
        byte_result,
        "ja",
        {"name": "テスト", "keywords": "語" * 34},
        source="self-test",
        forbidden_terms=[],
    )
    if not any(issue.code == "bytes_limit" for issue in byte_result.errors):
        print("Self-test failed; UTF-8 byte limit was not detected.", file=sys.stderr)
        return 1

    print("Self-test passed.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, help="Metadata manifest JSON")
    parser.add_argument("--ios-dir", type=Path, help="Fastlane-style iOS metadata root")
    parser.add_argument("--android-dir", type=Path, help="Fastlane Supply Android metadata root")
    parser.add_argument("--forbidden-terms", type=Path, help="UTF-8 file, one forbidden term per line")
    parser.add_argument("--output", type=Path, help="Write JSON validation report")
    parser.add_argument(
        "--android-release-notes-limit",
        type=int,
        default=None,
        metavar="N",
        help=(
            "Optional verified character limit for Google Play release notes. "
            "No universal hard limit is enforced when omitted."
        ),
    )
    parser.add_argument("--strict", action="store_true", help="Exit 2 when warnings are present")
    parser.add_argument("--self-test", action="store_true", help="Run built-in validator tests")
    parser.add_argument("--version", action="version", version=VERSION)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    if args.android_release_notes_limit is not None and args.android_release_notes_limit < 1:
        parser.error("--android-release-notes-limit must be a positive integer.")

    if not any((args.manifest, args.ios_dir, args.android_dir)):
        parser.error("Provide --manifest, --ios-dir, or --android-dir.")

    try:
        forbidden_terms = load_forbidden_terms(args.forbidden_terms)
        result = ValidationResult(issues=[], sources=[])

        if args.manifest:
            validate_manifest(
                result,
                args.manifest,
                forbidden_terms,
                android_release_notes_limit=args.android_release_notes_limit,
            )
        if args.ios_dir:
            validate_ios_dir(result, args.ios_dir, forbidden_terms)
        if args.android_dir:
            validate_android_dir(
                result,
                args.android_dir,
                forbidden_terms,
                android_release_notes_limit=args.android_release_notes_limit,
            )

        payload = result_payload(result, args.strict)
        print_human(payload)

        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

        if result.errors:
            return 1
        if args.strict and result.warnings:
            return 2
        return 0
    except (OSError, ValueError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 64


if __name__ == "__main__":
    raise SystemExit(main())
