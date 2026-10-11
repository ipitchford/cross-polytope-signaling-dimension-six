#!/usr/bin/env python3
"""Exhaustive symmetry-class test for sign.dim(diamond_6) <= 3.

This is the primary search implementation.  It delegates only the generation
of non-isomorphic bicoloured support graphs to nauty ``genbg``.  Measurement
weights and every saved feasibility model use exact rational arithmetic.
An independent verifier, intentionally implemented separately, replays the
graph coverage and all certificates without invoking Z3.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import shutil
import subprocess
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

import numpy as np
import sympy as sp
import z3


DIMENSION = 6
R = 3
EXPECTED_CLASSES = {5: 14_303, 6: 118_827}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def z3_fraction(value: Fraction) -> z3.RatNumRef:
    return z3.Q(value.numerator, value.denominator)


def from_z3(value: z3.RatNumRef) -> Fraction:
    return Fraction(value.numerator_as_long(), value.denominator_as_long())


def decode_graph6(line: str, left_size: int, right_size: int) -> list[int]:
    """Return right-part neighbourhoods as binary column integers."""
    if not line or line.startswith(">>"):
        raise ValueError("expected one ordinary graph6 record")
    order = ord(line[0]) - 63
    if order != left_size + right_size or not 0 <= order <= 62:
        raise ValueError("unexpected graph order")
    bits = "".join(f"{ord(character) - 63:06b}" for character in line[1:])
    needed = order * (order - 1) // 2
    if len(bits) < needed:
        raise ValueError("truncated graph6 record")
    columns = [0] * right_size
    offset = 0
    for upper in range(1, order):
        for lower in range(upper):
            adjacent = bits[offset] == "1"
            offset += 1
            if not adjacent:
                continue
            if lower < left_size <= upper:
                columns[upper - left_size] |= 1 << lower
            else:
                raise ValueError("genbg record contains an edge inside one colour class")
    if any(column == 0 for column in columns) or len(set(columns)) != len(columns):
        raise ValueError("genbg -z -d1 invariant failed")
    return columns


def graph6_records(path: Path) -> list[str]:
    records = [line.strip() for line in path.read_text().splitlines() if line.strip() and not line.startswith(">>")]
    if not records:
        raise ValueError(f"no graph6 records in {path}")
    return records


def generate_classes(destination: Path, right_size: int) -> dict[str, object]:
    command = ["genbg", "-q", "-z", "-d1", "-l", str(DIMENSION), str(right_size), str(destination)]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    records = graph6_records(destination)
    if len(records) != EXPECTED_CLASSES[right_size]:
        raise AssertionError(f"unexpected genbg class count for 6+{right_size}: {len(records)}")
    return {
        "command": command,
        "stderr": completed.stderr,
        "records": len(records),
        "sha256": sha256(destination),
    }


def numeric_candidate(columns: list[int]) -> bool:
    matrix = np.array(
        [[1.0 if column & (1 << row) else 0.0 for column in columns] for row in range(DIMENSION)]
    )
    target = np.ones(DIMENSION)
    solution, _, rank, _ = np.linalg.lstsq(matrix, target, rcond=None)
    if rank != len(columns) or np.max(np.abs(matrix @ solution - target)) > 1e-9:
        return False
    return bool(np.min(solution) > 1e-8 and 2.0 - np.sum(solution) > 1e-8)


def exact_weights(columns: list[int]) -> list[Fraction] | None:
    matrix = sp.Matrix(
        [[1 if column & (1 << row) else 0 for column in columns] for row in range(DIMENSION)]
    )
    target = sp.ones(DIMENSION, 1)
    if matrix.rank() != len(columns):
        return None
    try:
        solution, parameters = matrix.gauss_jordan_solve(target)
    except ValueError:
        return None
    if parameters.rows:
        return None
    other = [Fraction(int(value.p), int(value.q)) for value in solution]
    weights = [Fraction(2) - sum(other, Fraction(0)), *other]
    if any(value <= 0 for value in weights):
        return None
    if sum(weights, Fraction(0)) != 2:
        raise AssertionError("measurement weights do not sum to two")
    for coordinate in range(DIMENSION):
        plus = sum(
            (weights[j + 1] for j, column in enumerate(columns) if column & (1 << coordinate)),
            Fraction(0),
        )
        if plus != 1:
            raise AssertionError("measurement facet weight is not one")
    return weights


def support_vertices(columns: list[int]) -> list[int]:
    return [0, *columns]


def family_masks(size: int) -> list[int]:
    return [
        sum(1 << member for member in members)
        for cardinality in range(1, R + 1)
        for members in itertools.combinations(range(size), cardinality)
    ]


def facet_subset_masks(vertices: list[int]) -> list[int]:
    masks: set[int] = set()
    for coordinate in range(DIMENSION):
        for bit in (0, 1):
            members = [j for j, point in enumerate(vertices) if bool(point & (1 << coordinate)) == bool(bit)]
            for cardinality in range(1, len(members) + 1):
                for subset in itertools.combinations(members, cardinality):
                    masks.add(sum(1 << member for member in subset))
    return sorted(masks, key=lambda mask: (mask.bit_count(), mask))


def subset_demand(mask: int, weights: list[Fraction]) -> Fraction:
    return sum((weights[j] for j in range(len(weights)) if mask & (1 << j)), Fraction(0))


def verify_distribution(
    distribution: dict[int, Fraction], rows: list[int], columns: list[int], weights: list[Fraction]
) -> None:
    if any(mask not in columns or value < 0 for mask, value in distribution.items()):
        raise AssertionError("invalid distribution support or mass")
    if sum(distribution.values(), Fraction(0)) != 1:
        raise AssertionError("distribution mass is not one")
    for row in rows:
        coverage = sum((value for mask, value in distribution.items() if mask & row), Fraction(0))
        if coverage < subset_demand(row, weights):
            raise AssertionError("saved distribution violates Proposition 2.1")


def seed_facet_distribution(vertices: list[int], weights: list[Fraction]) -> tuple[dict[int, Fraction], dict[str, int]] | None:
    for coordinate in range(DIMENSION):
        for bit in (0, 1):
            facet = [j for j, point in enumerate(vertices) if bool(point & (1 << coordinate)) == bool(bit)]
            if len(facet) > 2:
                continue
            facet_mask = sum(1 << member for member in facet)
            outside = [j for j in range(len(vertices)) if j not in facet]
            distribution: dict[int, Fraction] = {}
            for member in outside:
                mask = facet_mask | (1 << member)
                distribution[mask] = distribution.get(mask, Fraction(0)) + weights[member]
            return distribution, {"coordinate": coordinate, "bit": bit, "facet_mask": facet_mask}
    return None


def proposition_distribution(
    vertices: list[int], weights: list[Fraction]
) -> tuple[str, dict[int, Fraction] | None, list[int], list[int]]:
    distribution_masks = family_masks(len(vertices))
    rows = facet_subset_masks(vertices)
    variables = [z3.Real(f"F_{mask}") for mask in distribution_masks]
    solver = z3.Solver()
    solver.set(timeout=30_000)
    solver.add(*(variable >= 0 for variable in variables))
    solver.add(z3.Sum(variables) == 1)
    for row in rows:
        solver.add(
            z3.Sum([variables[j] for j, mask in enumerate(distribution_masks) if mask & row])
            >= z3_fraction(subset_demand(row, weights))
        )
    result = solver.check()
    if result == z3.unknown:
        raise RuntimeError(f"Z3 returned unknown: {solver.reason_unknown()}")
    if result == z3.unsat:
        return "unsat", None, rows, distribution_masks
    model = solver.model()
    distribution = {
        mask: value
        for mask, variable in zip(distribution_masks, variables)
        if (value := from_z3(model.eval(variable, model_completion=True)))
    }
    verify_distribution(distribution, rows, distribution_masks, weights)
    return "sat", distribution, rows, distribution_masks


def separating_certificate(rows: list[int], columns: list[int], weights: list[Fraction]) -> dict[str, object]:
    multipliers = [z3.Real(f"y_{row}") for row in rows]
    solver = z3.Solver()
    solver.add(*(value >= 0 for value in multipliers))
    solver.add(z3.Sum(multipliers) == 1)
    weighted_demand = z3.Sum(
        [multipliers[j] * z3_fraction(subset_demand(row, weights)) for j, row in enumerate(rows)]
    )
    for column in columns:
        solver.add(weighted_demand > z3.Sum([multipliers[j] for j, row in enumerate(rows) if row & column]))
    if solver.check() != z3.sat:
        raise AssertionError("no rational separator for infeasible primal")
    model = solver.model()
    values = [from_z3(model.eval(value, model_completion=True)) for value in multipliers]
    sparse = {row: value for row, value in zip(rows, values) if value}
    demand_score = sum((value * subset_demand(row, weights) for row, value in sparse.items()), Fraction(0))
    column_scores = {
        column: sum((value for row, value in sparse.items() if row & column), Fraction(0)) for column in columns
    }
    maximum = max(column_scores.values(), default=Fraction(0))
    if sum(sparse.values(), Fraction(0)) != 1 or not demand_score > maximum:
        raise AssertionError("invalid rational separator")
    return {
        "multipliers": [
            {"facet_subset_mask": row, "mass": fraction_text(value)} for row, value in sorted(sparse.items())
        ],
        "weighted_demand": fraction_text(demand_score),
        "maximum_column_score": fraction_text(maximum),
        "strict_gap": fraction_text(demand_score - maximum),
        "checked_columns": len(columns),
    }


def saved_distribution(distribution: dict[int, Fraction]) -> list[dict[str, object]]:
    return [
        {"support_subset_mask": mask, "mass": fraction_text(value)}
        for mask, value in sorted(distribution.items())
    ]


def known_case_regression() -> dict[str, object]:
    # The four even-parity vertices in {-1,1}^3 are the shortened-Hadamard
    # witness: not simulable with r=2, but simulable with r=3.
    vertices = [0b000, 0b011, 0b101, 0b110]
    weights = [Fraction(1, 2)] * 4

    def status(r: int) -> str:
        masks = [
            sum(1 << member for member in members)
            for cardinality in range(1, r + 1)
            for members in itertools.combinations(range(4), cardinality)
        ]
        rows: set[int] = set()
        for coordinate in range(3):
            for bit in (0, 1):
                members = [j for j, point in enumerate(vertices) if bool(point & (1 << coordinate)) == bool(bit)]
                for cardinality in range(1, len(members) + 1):
                    for subset in itertools.combinations(members, cardinality):
                        rows.add(sum(1 << member for member in subset))
        variables = [z3.Real(f"reg_{r}_{mask}") for mask in masks]
        solver = z3.Solver()
        solver.add(*(variable >= 0 for variable in variables), z3.Sum(variables) == 1)
        for row in rows:
            solver.add(
                z3.Sum([variables[j] for j, mask in enumerate(masks) if mask & row])
                >= z3_fraction(subset_demand(row, weights))
            )
        return str(solver.check())

    result = {"dimension": 3, "support": vertices, "weights": ["1/2"] * 4, "r2": status(2), "r3": status(3)}
    if result["r2"] != "unsat" or result["r3"] != "sat":
        raise AssertionError("known d=3 regression failed")
    return result


def process_classes(path: Path, right_size: int) -> tuple[dict[str, object], list[dict[str, object]], dict[str, object] | None]:
    records = graph6_records(path)
    summary = {
        "right_size": right_size,
        "support_size": right_size + 1,
        "classes": len(records),
        "numeric_rejects": 0,
        "exact_rejects_after_numeric_gate": 0,
        "valid_measurements": 0,
        "seed_facet_certificates": 0,
        "lp_feasible_certificates": 0,
        "lp_infeasible_certificates": 0,
    }
    valid_records: list[dict[str, object]] = []
    witness = None
    for ordinal, graph6 in enumerate(records):
        columns = decode_graph6(graph6, DIMENSION, right_size)
        if not numeric_candidate(columns):
            summary["numeric_rejects"] += 1
            continue
        weights = exact_weights(columns)
        if weights is None:
            summary["exact_rejects_after_numeric_gate"] += 1
            continue
        summary["valid_measurements"] += 1
        vertices = support_vertices(columns)
        rows = facet_subset_masks(vertices)
        distribution_columns = family_masks(len(vertices))
        easy = seed_facet_distribution(vertices, weights)
        record: dict[str, object] = {
            "ordinal": ordinal,
            "graph6": graph6,
            "columns": columns,
            "weights": [fraction_text(value) for value in weights],
            "facet_subset_constraints": len(rows),
            "distribution_columns": len(distribution_columns),
        }
        if easy is not None:
            distribution, construction = easy
            verify_distribution(distribution, rows, distribution_columns, weights)
            record.update(
                {
                    "method": "seed_small_facet_construction",
                    "construction": construction,
                    "distribution": saved_distribution(distribution),
                }
            )
            summary["seed_facet_certificates"] += 1
        else:
            status, distribution, rows, distribution_columns = proposition_distribution(vertices, weights)
            if status == "unsat":
                certificate = separating_certificate(rows, distribution_columns, weights)
                record.update({"method": "exact_rational_separator", "separator": certificate})
                summary["lp_infeasible_certificates"] += 1
                valid_records.append(record)
                witness = record
                break
            assert distribution is not None
            record.update(
                {
                    "method": "proposition_2_1_exact_feasible",
                    "distribution": saved_distribution(distribution),
                }
            )
            summary["lp_feasible_certificates"] += 1
        valid_records.append(record)
    summary["processed_classes"] = witness["ordinal"] + 1 if witness else len(records)
    summary["complete"] = witness is None
    return summary, valid_records, witness


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir
    partial = output.with_name(output.name + ".partial")
    if output.exists() or partial.exists():
        raise SystemExit("refusing to overwrite an existing output or partial directory")
    if shutil.which("genbg") is None:
        raise SystemExit("nauty genbg is required")
    partial.mkdir(parents=True)

    generated: dict[str, object] = {}
    for right_size in (5, 6):
        path = partial / f"genbg-6-{right_size}.g6"
        generated[str(right_size)] = generate_classes(path, right_size)

    all_valid: dict[str, list[dict[str, object]]] = {}
    summaries: dict[str, dict[str, object]] = {}
    witness: dict[str, object] | None = None
    witness_right_size: int | None = None
    for right_size in (5, 6):
        summary, valid_records, found = process_classes(partial / f"genbg-6-{right_size}.g6", right_size)
        summaries[str(right_size)] = summary
        all_valid[str(right_size)] = valid_records
        if found is not None:
            witness = found
            witness_right_size = right_size
            break

    branch = "signaling_dimension_four_witness" if witness else "all_enumerated_classes_simulable_by_three"
    manifest = {
        "schema": "cross-polytope-six-exhaustive-v1",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "dimension": DIMENSION,
        "tested_simplex_vertices": R,
        "script_sha256": sha256(Path(__file__)),
        "nauty_version": "2.9.3",
        "known_case_regression": known_case_regression(),
        "support_reduction": {
            "normalization": "Choose one support vertex and flip coordinates so it is the all-minus vertex; row permutations are coordinate permutations and right-part permutations relabel the other support vertices.",
            "sizes_at_most_five": "The seed Theorem 2.2 construction uses a coordinate facet containing at most floor(m/2)<=2 support points, hence subsets of size at most three.",
            "sizes_six_and_seven": "All color-preserving genbg classes with distinct nonzero right neighbourhoods are processed; duplicates from different choices of normalized base vertex are harmless.",
        },
        "generated_classes": generated,
        "summaries": summaries,
        "branch": branch,
        "witness_right_size": witness_right_size,
        "witness": witness,
        "valid_measurements": all_valid,
        "claim_boundary": (
            "A signaling-dimension-four branch is proved by the saved exact rational separator. "
            "A signaling-dimension-three branch additionally requires the independent verifier to "
            "confirm every generated class, exact filter and saved feasible distribution."
        ),
    }
    manifest_path = partial / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (partial / "MANIFEST.sha256").write_text(f"{sha256(manifest_path)}  manifest.json\n")
    partial.replace(output)
    print(
        json.dumps(
            {
                "branch": branch,
                "summaries": summaries,
                "manifest_sha256": sha256(output / "manifest.json"),
                "output_dir": str(output),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
