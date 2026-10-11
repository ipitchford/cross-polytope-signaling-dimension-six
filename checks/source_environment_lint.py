#!/usr/bin/env python3
"""Lint the public verification gate for optimization and environment safety.

This is a narrow source-bound check.  It covers the fresh public verifier,
catalogue/transport logic, and package gate scripts.  It intentionally excludes
the byte-preserved original programs and the optional ``genbg`` regeneration
wrapper, whose different dependency boundaries are documented separately.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


GATING_SOURCES = (
    "code/verification_core.py",
    "code/build_full_cube_catalogue.py",
    "code/verify_supplied.py",
    "code/verify_transport_simulators.py",
    "checks/check_manifest.py",
    "checks/check_replay_gate.py",
    "checks/run_orbit_audit.py",
    "checks/source_environment_lint.py",
)
LOCAL_MODULES = {"verification_core"}
FORBIDDEN_MODULES = {
    "ctypes", "http", "importlib", "multiprocessing", "os", "requests",
    "resource", "shutil", "socket", "subprocess", "urllib",
}
FORBIDDEN_CALLS = {"__import__", "compile", "eval", "exec"}
EXPLICIT_PROCESS_WRAPPERS = {"checks/run_orbit_audit.py": {"subprocess"}}
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")


class SourceLintError(ValueError):
    """Raised when a gate source depends on ambient state or assertions."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SourceLintError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def imported_roots(tree: ast.AST) -> set[str]:
    result: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            require(node.level == 0 and node.module is not None, "relative imports are not allowed in gate sources")
            result.add(node.module.split(".", 1)[0])
    return result


def call_name(node: ast.Call) -> str | None:
    return node.func.id if isinstance(node.func, ast.Name) else None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    require(root.is_dir(), f"package root is not a directory: {root}")
    require(not args.output.exists(), f"refusing to overwrite output: {args.output}")
    try:
        args.output.resolve().relative_to(root)
    except ValueError:
        pass
    else:
        raise SourceLintError("output must be outside the source closure")

    rows: list[dict[str, Any]] = []
    total_assertions = 0
    total_dynamic_calls = 0
    total_forbidden_imports = 0
    for relative in GATING_SOURCES:
        path = root / relative
        require(path.is_file() and not path.is_symlink(), f"missing regular gate source: {relative}")
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=relative)
        except (OSError, UnicodeDecodeError, SyntaxError) as error:
            raise SourceLintError(f"cannot parse {relative}: {error}") from error
        assertions = [node for node in ast.walk(tree) if isinstance(node, ast.Assert)]
        dynamic = [node for node in ast.walk(tree)
                   if isinstance(node, ast.Call) and call_name(node) in FORBIDDEN_CALLS]
        imports = imported_roots(tree)
        permitted_process_imports = EXPLICIT_PROCESS_WRAPPERS.get(relative, set())
        forbidden = sorted((imports & FORBIDDEN_MODULES) - permitted_process_imports)
        nonstdlib = sorted(imports - set(sys.stdlib_module_names) - LOCAL_MODULES)
        require(not assertions, f"{relative}: assert is disabled by optimized mode")
        require(not dynamic, f"{relative}: dynamic execution/import call is forbidden")
        require(not forbidden, f"{relative}: ambient/process/network imports forbidden: {forbidden}")
        require(not nonstdlib, f"{relative}: non-standard-library imports found: {nonstdlib}")
        digest = sha256_file(path)
        require(SHA256_RE.fullmatch(digest) is not None, f"{relative}: hash construction failed")
        total_assertions += len(assertions)
        total_dynamic_calls += len(dynamic)
        total_forbidden_imports += len(forbidden) + len(nonstdlib)
        rows.append({
            "path": relative,
            "sha256": digest,
            "imports": sorted(imports),
            "assert_statements": len(assertions),
            "dynamic_execution_calls": len(dynamic),
            "forbidden_or_nonstdlib_imports": len(forbidden) + len(nonstdlib),
        })

    receipt = {
        "schema": "cross-polytope-six-source-environment-lint-v1",
        "verified_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "scope": list(GATING_SOURCES),
        "files_checked": len(rows),
        "assert_statements": total_assertions,
        "dynamic_execution_calls": total_dynamic_calls,
        "forbidden_or_nonstdlib_imports": total_forbidden_imports,
        "declared_execution_contract": {
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
            "PYTHONOPTIMIZE": ["0", "1"],
        },
        "files": rows,
        "result": "gate_sources_are_standard_library_optimization_safe_and_ambient_state_independent",
        "boundary": "This static lint does not audit the preserved original programs or optional genbg regeneration wrapper and is not a correctness proof.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except SourceLintError as error:
        raise SystemExit(f"source-environment lint error: {error}") from error
