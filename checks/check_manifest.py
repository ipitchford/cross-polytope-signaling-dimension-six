#!/usr/bin/env python3
"""Verify the frozen package manifest, checksum list, and file closure.

The checker is deliberately read-only.  It accepts no exclusions beyond the
two control files that describe the closure: ``MANIFEST.json`` and
``SHA256SUMS``.  Build artefacts therefore have to be removed before a package
is frozen rather than silently ignored during later verification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
CONTROL_FILES = {"MANIFEST.json", "SHA256SUMS"}
EXPECTED_PACKAGE = "cross-polytope-signaling-dimension-six"
EXPECTED_VERSION = "1.1.0-candidate"


class ManifestError(ValueError):
    """Raised when the frozen package is not the declared byte closure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ManifestError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def exact_keys(value: Any, expected: set[str], where: str) -> None:
    require(type(value) is dict, f"{where}: expected object")
    actual = set(value)
    require(actual == expected,
            f"{where}: keys differ; missing={sorted(expected-actual)}, extra={sorted(actual-expected)}")


def safe_relative_path(value: Any, where: str) -> str:
    require(type(value) is str and value and "\\" not in value, f"{where}: invalid path text")
    path = PurePosixPath(value)
    require(not path.is_absolute() and value == path.as_posix(), f"{where}: path is not canonical POSIX-relative")
    require(all(part not in ("", ".", "..") for part in path.parts), f"{where}: unsafe path component")
    require(value not in CONTROL_FILES, f"{where}: control file must not list itself")
    return value


def parse_manifest(path: Path) -> list[dict[str, Any]]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ManifestError(f"cannot read strict JSON manifest: {error}") from error
    exact_keys(manifest, {"schemaVersion", "package", "version", "scope", "files"}, "MANIFEST.json")
    require(manifest["schemaVersion"] == "1.0", "MANIFEST.json: unsupported schemaVersion")
    require(manifest["package"] == EXPECTED_PACKAGE, "MANIFEST.json: package identity mismatch")
    require(manifest["version"] == EXPECTED_VERSION, "MANIFEST.json: version mismatch")
    require(manifest["scope"] == "Every shipped payload except MANIFEST.json and SHA256SUMS.",
            "MANIFEST.json: scope text mismatch")
    require(type(manifest["files"]) is list and manifest["files"], "MANIFEST.json: files must be nonempty")
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, row in enumerate(manifest["files"]):
        where = f"MANIFEST.json.files[{index}]"
        exact_keys(row, {"path", "size_bytes", "sha256"}, where)
        relative = safe_relative_path(row["path"], f"{where}.path")
        require(relative not in seen, f"{where}: duplicate path")
        seen.add(relative)
        require(type(row["size_bytes"]) is int and row["size_bytes"] >= 0, f"{where}: invalid size")
        require(type(row["sha256"]) is str and SHA256_RE.fullmatch(row["sha256"]) is not None,
                f"{where}: invalid SHA-256")
        rows.append(row)
    require([row["path"] for row in rows] == sorted(seen), "MANIFEST.json: rows are not path-sorted")
    return rows


def parse_checksum_list(path: Path) -> list[tuple[str, str]]:
    try:
        text = path.read_text(encoding="ascii")
    except (OSError, UnicodeDecodeError) as error:
        raise ManifestError(f"cannot read ASCII SHA256SUMS: {error}") from error
    require(text.endswith("\n"), "SHA256SUMS: missing terminal newline")
    parsed: list[tuple[str, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        require(len(line) >= 67 and line[64:66] == "  ", f"SHA256SUMS:{line_number}: invalid format")
        digest, relative = line[:64], line[66:]
        require(SHA256_RE.fullmatch(digest) is not None, f"SHA256SUMS:{line_number}: invalid SHA-256")
        parsed.append((digest, safe_relative_path(relative, f"SHA256SUMS:{line_number}")))
    require(bool(parsed), "SHA256SUMS: empty")
    return parsed


def actual_files(root: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        require(not path.is_symlink(), f"package contains symlink: {relative}")
        if path.is_dir():
            continue
        require(path.is_file(), f"package contains unsupported filesystem object: {relative}")
        if relative not in CONTROL_FILES:
            result[relative] = path
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    require(root.is_dir(), f"package root is not a directory: {root}")
    require((root / "MANIFEST.json").is_file(), "package root lacks MANIFEST.json")
    require((root / "SHA256SUMS").is_file(), "package root lacks SHA256SUMS")
    if args.output is not None:
        require(not args.output.exists(), f"refusing to overwrite output: {args.output}")
        try:
            args.output.resolve().relative_to(root)
        except ValueError:
            pass
        else:
            raise ManifestError("output must be outside the frozen package root")

    rows = parse_manifest(root / "MANIFEST.json")
    expected = {row["path"]: row for row in rows}
    listed = parse_checksum_list(root / "SHA256SUMS")
    require(listed == [(row["sha256"], row["path"]) for row in rows],
            "SHA256SUMS does not exactly reproduce the manifest rows")
    actual = actual_files(root)
    require(set(actual) == set(expected),
            f"package closure differs; missing={sorted(set(expected)-set(actual))}, "
            f"unexpected={sorted(set(actual)-set(expected))}")
    total_bytes = 0
    for relative, row in expected.items():
        path = actual[relative]
        require(path.stat().st_size == row["size_bytes"], f"{relative}: size mismatch")
        require(sha256_file(path) == row["sha256"], f"{relative}: SHA-256 mismatch")
        total_bytes += row["size_bytes"]

    receipt = {
        "schema": "cross-polytope-six-package-manifest-check-v1",
        "verified_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "package": EXPECTED_PACKAGE,
        "version": EXPECTED_VERSION,
        "files": len(rows),
        "payload_bytes": total_bytes,
        "manifest_sha256": sha256_file(root / "MANIFEST.json"),
        "sha256sums_sha256": sha256_file(root / "SHA256SUMS"),
        "symlinks": 0,
        "unexpected_files": 0,
        "result": "complete_file_closure_matches_manifest_and_checksum_list",
    }
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except ManifestError as error:
        raise SystemExit(f"manifest error: {error}") from error
