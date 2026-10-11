#!/usr/bin/env python3
"""Independent exact verifier for the diamond_6 exhaustive evidence.

This verifier deliberately imports neither NumPy, SymPy nor Z3.  It regenerates
the nauty class files, solves every measurement system using a local Fraction
RREF implementation, and checks every saved Proposition 2.1 distribution or
separator by direct rational arithmetic.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path


DIMENSION = 6
R = 3
EXPECTED_CLASSES = {5: 14_303, 6: 118_827}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_graph6(record: str, right_size: int) -> list[int]:
    order = DIMENSION + right_size
    if not record or ord(record[0]) - 63 != order:
        raise AssertionError("wrong graph6 order")
    payload: list[int] = []
    for character in record[1:]:
        value = ord(character) - 63
        if value < 0 or value > 63:
            raise AssertionError("invalid graph6 character")
        payload.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    columns = [0] * right_size
    cursor = 0
    for high in range(1, order):
        for low in range(high):
            edge = payload[cursor]
            cursor += 1
            if edge:
                if low >= DIMENSION or high < DIMENSION:
                    raise AssertionError("within-colour edge")
                columns[high - DIMENSION] |= 1 << low
    if any(value == 0 for value in columns) or len(columns) != len(set(columns)):
        raise AssertionError("zero or duplicate support column")
    return columns


def graph_records(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text().splitlines() if line.strip() and not line.startswith(">>")]


def solve_measurement(columns: list[int]) -> list[Fraction] | None:
    width = len(columns)
    augmented = [
        [Fraction(1 if column & (1 << row) else 0) for column in columns] + [Fraction(1)]
        for row in range(DIMENSION)
    ]
    pivot_row_for_column: list[int] = []
    next_row = 0
    for column in range(width):
        pivot = next((row for row in range(next_row, DIMENSION) if augmented[row][column]), None)
        if pivot is None:
            return None
        augmented[next_row], augmented[pivot] = augmented[pivot], augmented[next_row]
        divisor = augmented[next_row][column]
        augmented[next_row] = [value / divisor for value in augmented[next_row]]
        for row in range(DIMENSION):
            if row == next_row or not augmented[row][column]:
                continue
            multiplier = augmented[row][column]
            augmented[row] = [
                augmented[row][j] - multiplier * augmented[next_row][j] for j in range(width + 1)
            ]
        pivot_row_for_column.append(next_row)
        next_row += 1
    for row in range(DIMENSION):
        if all(augmented[row][column] == 0 for column in range(width)) and augmented[row][-1] != 0:
            return None
    other = [augmented[pivot_row_for_column[column]][-1] for column in range(width)]
    weights = [Fraction(2) - sum(other, Fraction(0)), *other]
    if any(value <= 0 for value in weights):
        return None
    if sum(weights, Fraction(0)) != 2:
        raise AssertionError("weight sum")
    for coordinate in range(DIMENSION):
        plus = sum(
            (weights[j + 1] for j, column in enumerate(columns) if column & (1 << coordinate)),
            Fraction(0),
        )
        if plus != 1:
            raise AssertionError("facet weight")
    return weights


def family_masks(size: int) -> list[int]:
    return [
        sum(1 << member for member in members)
        for cardinality in range(1, R + 1)
        for members in itertools.combinations(range(size), cardinality)
    ]


def facet_rows(vertices: list[int]) -> list[int]:
    rows: set[int] = set()
    for coordinate in range(DIMENSION):
        for bit in (0, 1):
            members = [j for j, point in enumerate(vertices) if ((point >> coordinate) & 1) == bit]
            for cardinality in range(1, len(members) + 1):
                for subset in itertools.combinations(members, cardinality):
                    rows.add(sum(1 << member for member in subset))
    return sorted(rows, key=lambda value: (value.bit_count(), value))


def demand(mask: int, weights: list[Fraction]) -> Fraction:
    return sum((weights[j] for j in range(len(weights)) if mask & (1 << j)), Fraction(0))


def parse_distribution(items: list[dict[str, object]]) -> dict[int, Fraction]:
    result: dict[int, Fraction] = {}
    for item in items:
        mask = int(item["support_subset_mask"])
        if mask in result:
            raise AssertionError("duplicate distribution mask")
        result[mask] = Fraction(str(item["mass"]))
    return result


def check_distribution(
    distribution: dict[int, Fraction], rows: list[int], columns: list[int], weights: list[Fraction]
) -> None:
    if any(mask not in columns or value < 0 for mask, value in distribution.items()):
        raise AssertionError("invalid distribution")
    if sum(distribution.values(), Fraction(0)) != 1:
        raise AssertionError("distribution does not sum to one")
    for row in rows:
        coverage = sum((value for mask, value in distribution.items() if mask & row), Fraction(0))
        if coverage < demand(row, weights):
            raise AssertionError("failed Proposition 2.1 inequality")


def check_separator(
    separator: dict[str, object], rows: list[int], columns: list[int], weights: list[Fraction]
) -> None:
    allowed_rows = set(rows)
    multipliers: dict[int, Fraction] = {}
    for item in separator["multipliers"]:
        row = int(item["facet_subset_mask"])
        value = Fraction(str(item["mass"]))
        if row not in allowed_rows or row in multipliers or value < 0:
            raise AssertionError("invalid separator multiplier")
        multipliers[row] = value
    if sum(multipliers.values(), Fraction(0)) != 1:
        raise AssertionError("separator normalization")
    weighted_demand = sum((value * demand(row, weights) for row, value in multipliers.items()), Fraction(0))
    maximum = max(
        sum((value for row, value in multipliers.items() if row & column), Fraction(0)) for column in columns
    )
    if not weighted_demand > maximum:
        raise AssertionError("separator has no strict gap")
    if Fraction(str(separator["weighted_demand"])) != weighted_demand:
        raise AssertionError("separator demand receipt")
    if Fraction(str(separator["maximum_column_score"])) != maximum:
        raise AssertionError("separator maximum receipt")
    if Fraction(str(separator["strict_gap"])) != weighted_demand - maximum:
        raise AssertionError("separator gap receipt")


def verify_valid_record(record: dict[str, object], columns: list[int], weights: list[Fraction]) -> str:
    if record["columns"] != columns:
        raise AssertionError("saved columns mismatch")
    if [Fraction(value) for value in record["weights"]] != weights:
        raise AssertionError("saved weights mismatch")
    vertices = [0, *columns]
    rows = facet_rows(vertices)
    distribution_columns = family_masks(len(vertices))
    if record["facet_subset_constraints"] != len(rows) or record["distribution_columns"] != len(distribution_columns):
        raise AssertionError("saved constraint counts mismatch")
    method = str(record["method"])
    if method in {"seed_small_facet_construction", "proposition_2_1_exact_feasible"}:
        distribution = parse_distribution(record["distribution"])
        check_distribution(distribution, rows, distribution_columns, weights)
        if method == "seed_small_facet_construction":
            construction = record["construction"]
            coordinate = int(construction["coordinate"])
            bit = int(construction["bit"])
            facet = [j for j, point in enumerate(vertices) if ((point >> coordinate) & 1) == bit]
            if len(facet) > 2 or int(construction["facet_mask"]) != sum(1 << member for member in facet):
                raise AssertionError("invalid small-facet construction receipt")
    elif method == "exact_rational_separator":
        check_separator(record["separator"], rows, distribution_columns, weights)
    else:
        raise AssertionError(f"unknown method {method}")
    return method


def regenerate_and_compare(evidence: Path, right_size: int) -> bool:
    with tempfile.TemporaryDirectory(prefix="verify-cross-polytope-") as temporary:
        generated = Path(temporary) / f"genbg-6-{right_size}.g6"
        subprocess.run(
            ["genbg", "-q", "-z", "-d1", "-l", str(DIMENSION), str(right_size), str(generated)],
            check=True,
            capture_output=True,
            text=True,
        )
        return generated.read_bytes() == (evidence / f"genbg-6-{right_size}.g6").read_bytes()


def verify_file(
    evidence: Path, manifest: dict[str, object], right_size: int
) -> tuple[dict[str, int | bool], dict[str, int]]:
    path = evidence / f"genbg-6-{right_size}.g6"
    records = graph_records(path)
    generated = manifest["generated_classes"][str(right_size)]
    if len(records) != EXPECTED_CLASSES[right_size] or generated["records"] != len(records):
        raise AssertionError("class count mismatch")
    if generated["sha256"] != sha256(path):
        raise AssertionError("class file hash mismatch")
    saved_list = manifest["valid_measurements"][str(right_size)]
    saved = {int(record["ordinal"]): record for record in saved_list}
    if len(saved) != len(saved_list):
        raise AssertionError("duplicate saved ordinal")
    valid = 0
    methods: dict[str, int] = {}
    for ordinal, graph6 in enumerate(records):
        columns = parse_graph6(graph6, right_size)
        weights = solve_measurement(columns)
        if weights is None:
            if ordinal in saved:
                raise AssertionError("invalid class saved as a measurement")
            continue
        valid += 1
        record = saved.pop(ordinal, None)
        if record is None:
            raise AssertionError(f"valid class omitted at 6+{right_size} ordinal {ordinal}")
        if record["graph6"] != graph6:
            raise AssertionError("graph6 receipt mismatch")
        method = verify_valid_record(record, columns, weights)
        methods[method] = methods.get(method, 0) + 1
    if saved:
        raise AssertionError("saved measurements outside regenerated class list")
    summary = manifest["summaries"][str(right_size)]
    if summary["classes"] != len(records) or summary["valid_measurements"] != valid or not summary["complete"]:
        raise AssertionError("summary mismatch")
    return {
        "classes": len(records),
        "valid_measurements": valid,
        "regenerated_byte_identical": regenerate_and_compare(evidence, right_size),
    }, methods


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--producer-script", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("refusing to overwrite verification receipt")
    evidence = args.evidence_dir
    manifest_path = evidence / "manifest.json"
    manifest_hash = sha256(manifest_path)
    receipt_line = (evidence / "MANIFEST.sha256").read_text().strip()
    if receipt_line != f"{manifest_hash}  manifest.json":
        raise AssertionError("manifest hash receipt mismatch")
    manifest = json.loads(manifest_path.read_text())
    if manifest["script_sha256"] != sha256(args.producer_script):
        raise AssertionError("producer script hash mismatch")
    if manifest["branch"] != "all_enumerated_classes_simulable_by_three" or manifest["witness"] is not None:
        raise AssertionError("this completion verifier expected the all-feasible branch")

    files: dict[str, object] = {}
    total_methods: dict[str, int] = {}
    for right_size in (5, 6):
        result, methods = verify_file(evidence, manifest, right_size)
        if not result["regenerated_byte_identical"]:
            raise AssertionError("regenerated nauty output differs")
        files[str(right_size)] = result
        for method, count in methods.items():
            total_methods[method] = total_methods.get(method, 0) + count

    if sum(int(files[key]["classes"]) for key in files) != 133_130:
        raise AssertionError("combined class coverage")
    if sum(int(files[key]["valid_measurements"]) for key in files) != 217:
        raise AssertionError("combined valid measurement count")
    if total_methods.get("exact_rational_separator", 0):
        raise AssertionError("unexpected infeasible class in all-feasible branch")
    if 5 // 2 + 1 > R:
        raise AssertionError("small-support reduction arithmetic")

    receipt = {
        "schema": "cross-polytope-six-independent-verification-v1",
        "verified_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "manifest_sha256": manifest_hash,
        "producer_script_sha256": sha256(args.producer_script),
        "verifier_sha256": sha256(Path(__file__)),
        "files": files,
        "certificate_methods": total_methods,
        "small_support_proof": "For m<=5, one member of any complementary coordinate-facet pair contains at most floor(m/2)<=2 support points, so the seed construction uses sets of size at most 3.",
        "result": "verified_signaling_dimension_at_most_three",
        "combined_with_seed_lower_bound": "Theorem 2.3 of arXiv:2610.05924v1 gives sign.dim(diamond_6)>=ceil(log2(8))=3; therefore the verified exact value is 3.",
        "trust_boundary": "The verifier trusts nauty genbg 2.9.3 for non-isomorphic bicoloured graph generation, then independently regenerates byte-identical output and checks all subsequent mathematics with Python Fraction arithmetic.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    temporary.replace(args.output)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
