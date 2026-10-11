#!/usr/bin/env python3
"""Run the compiled orbit audit and write a freshly validated JSON receipt."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


class OrbitRunError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise OrbitRunError(message)


def validate(value: Any) -> None:
    require(type(value) is dict, "orbit audit did not emit a JSON object")
    require(value == {
        "schema": "cross-polytope-six-orbit-audit-v1",
        "coordinate_permutations": 720,
        "right_size_5": {
            "records": 14_303,
            "distinct_canonical_keys": 14_303,
            "orbit_size_sum": 6_054_006,
            "expected_labelled_supports": 6_054_006,
        },
        "right_size_6": {
            "records": 118_827,
            "distinct_canonical_keys": 118_827,
            "orbit_size_sum": 63_602_770,
            "expected_labelled_supports": 63_602_770,
        },
        "result": "all_orbits_unique_and_complete",
        "count_formula": "sum_{j=0}^6 (-1)^j binom(6,j) binom(2^(6-j)-1,k)",
    }, "orbit audit output differs from the exact expected coverage receipt")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--input-five", type=Path, required=True)
    parser.add_argument("--input-six", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(args.binary.is_file() and not args.binary.is_symlink(), "orbit binary is not a regular file")
    require(args.input_five.is_file() and args.input_six.is_file(), "orbit input is missing")
    require(not args.output.exists(), f"refusing to overwrite output: {args.output}")
    try:
        completed = subprocess.run(
            [str(args.binary), str(args.input_five), str(args.input_six)],
            env={"LANG": "C", "LC_ALL": "C"},
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as error:
        raise OrbitRunError(f"cannot execute orbit binary: {error}") from error
    require(completed.returncode == 0, f"orbit audit exited {completed.returncode}: {completed.stderr.strip()}")
    require(not completed.stderr, "orbit audit emitted stderr")
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise OrbitRunError(f"orbit audit emitted invalid JSON: {error}") from error
    validate(value)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(value, indent=2))


if __name__ == "__main__":
    try:
        main()
    except OrbitRunError as error:
        raise SystemExit(f"orbit runner error: {error}") from error
