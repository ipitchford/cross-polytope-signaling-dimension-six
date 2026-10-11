#!/usr/bin/env python3
"""Strict standard-library primitives for the public cross-polytope replay.

This is a fresh public implementation.  It follows the mathematical data model
of the original OpenAI Codex producer and exact verifier, and the full-cube
canonicalisation idea recorded by the later internal review.  It does not
import either implementation and contains no solver or floating-point path.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import re
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


DIMENSION = 6
R = 3
EXPECTED_CLASSES = {5: 14_303, 6: 118_827}
EXPECTED_VALID = {5: 39, 6: 178}
EXPECTED_METHODS = {
    "seed_small_facet_construction": 87,
    "proposition_2_1_exact_feasible": 130,
}
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
RATIONAL_RE = re.compile(r"(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?\Z")


class VerificationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def exact_keys(value: Any, expected: Iterable[str], where: str) -> None:
    require(type(value) is dict, f"{where}: expected object")
    wanted = set(expected)
    actual = set(value)
    require(actual == wanted, f"{where}: keys differ; missing={sorted(wanted-actual)}, extra={sorted(actual-wanted)}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_rational(value: Any, where: str) -> Fraction:
    require(type(value) is str and RATIONAL_RE.fullmatch(value) is not None, f"{where}: noncanonical rational")
    result = Fraction(value)
    canonical = str(result.numerator) if result.denominator == 1 else f"{result.numerator}/{result.denominator}"
    require(value == canonical, f"{where}: rational is not reduced")
    return result


def validate_manifest_schema(manifest: Any) -> None:
    exact_keys(manifest, {
        "branch", "claim_boundary", "dimension", "generated_at", "generated_classes",
        "known_case_regression", "nauty_version", "schema", "script_sha256", "summaries",
        "support_reduction", "tested_simplex_vertices", "valid_measurements", "witness",
        "witness_right_size",
    }, "manifest")
    require(manifest["schema"] == "cross-polytope-six-exhaustive-v1", "manifest: wrong schema")
    require(manifest["dimension"] == DIMENSION, "manifest: wrong dimension")
    require(manifest["tested_simplex_vertices"] == R, "manifest: wrong simulation size")
    require(manifest["branch"] == "all_enumerated_classes_simulable_by_three", "manifest: wrong result branch")
    require(manifest["witness"] is None and manifest["witness_right_size"] is None, "manifest: unexpected witness")
    require(type(manifest["generated_at"]) is str and manifest["generated_at"], "manifest: missing generation time")
    require(type(manifest["claim_boundary"]) is str and manifest["claim_boundary"], "manifest: missing claim boundary")
    require(type(manifest["nauty_version"]) is str and manifest["nauty_version"], "manifest: missing nauty version")
    require(type(manifest["script_sha256"]) is str and SHA256_RE.fullmatch(manifest["script_sha256"]) is not None,
            "manifest: invalid producer hash")
    exact_keys(manifest["generated_classes"], {"5", "6"}, "manifest.generated_classes")
    exact_keys(manifest["summaries"], {"5", "6"}, "manifest.summaries")
    exact_keys(manifest["valid_measurements"], {"5", "6"}, "manifest.valid_measurements")
    exact_keys(manifest["support_reduction"], {"normalization", "sizes_at_most_five", "sizes_six_and_seven"},
               "manifest.support_reduction")
    exact_keys(manifest["known_case_regression"], {"dimension", "r2", "r3", "support", "weights"},
               "manifest.known_case_regression")
    require(manifest["known_case_regression"] == {
        "dimension": 3, "r2": "unsat", "r3": "sat", "support": [0, 3, 5, 6],
        "weights": ["1/2", "1/2", "1/2", "1/2"],
    }, "manifest: known-case regression changed")

    generated_keys = {"command", "records", "sha256", "stderr"}
    summary_keys = {
        "classes", "complete", "exact_rejects_after_numeric_gate", "lp_feasible_certificates",
        "lp_infeasible_certificates", "numeric_rejects", "processed_classes", "right_size",
        "seed_facet_certificates", "support_size", "valid_measurements",
    }
    for right_size in (5, 6):
        key = str(right_size)
        generated = manifest["generated_classes"][key]
        exact_keys(generated, generated_keys, f"manifest.generated_classes.{key}")
        require(type(generated["command"]) is list and all(type(x) is str for x in generated["command"]),
                f"generated {key}: invalid command")
        require(generated["command"][:7] == ["genbg", "-q", "-z", "-d1", "-l", "6", key],
                f"generated {key}: unexpected command prefix")
        require(type(generated["records"]) is int and generated["records"] == EXPECTED_CLASSES[right_size],
                f"generated {key}: wrong count")
        require(type(generated["sha256"]) is str and SHA256_RE.fullmatch(generated["sha256"]) is not None,
                f"generated {key}: invalid hash")
        require(type(generated["stderr"]) is str, f"generated {key}: stderr must be text")

        summary = manifest["summaries"][key]
        exact_keys(summary, summary_keys, f"manifest.summaries.{key}")
        for field in summary_keys - {"complete"}:
            require(type(summary[field]) is int and summary[field] >= 0, f"summary {key}.{field}: invalid integer")
        require(summary["complete"] is True, f"summary {key}: incomplete")
        require(summary["right_size"] == right_size and summary["support_size"] == right_size + 1,
                f"summary {key}: size mismatch")
        require(summary["classes"] == EXPECTED_CLASSES[right_size] == summary["processed_classes"],
                f"summary {key}: coverage mismatch")
        require(summary["valid_measurements"] == EXPECTED_VALID[right_size], f"summary {key}: valid count mismatch")
        require(summary["lp_infeasible_certificates"] == 0 and summary["exact_rejects_after_numeric_gate"] == 0,
                f"summary {key}: unexpected branch counters")
        require(summary["numeric_rejects"] + summary["valid_measurements"] == summary["classes"],
                f"summary {key}: classification counters do not add")
        require(summary["seed_facet_certificates"] + summary["lp_feasible_certificates"] == summary["valid_measurements"],
                f"summary {key}: certificate counters do not add")
        require(type(manifest["valid_measurements"][key]) is list and
                len(manifest["valid_measurements"][key]) == EXPECTED_VALID[right_size],
                f"manifest.valid_measurements.{key}: wrong length")


def read_graph6_records(path: Path, right_size: int) -> list[str]:
    raw = path.read_bytes()
    require(b"\r" not in raw, f"{path}: CR bytes are not accepted")
    require(raw.endswith(b"\n"), f"{path}: missing terminal newline")
    lines = raw.splitlines()
    require(bool(lines), f"{path}: empty graph file")
    result: list[str] = []
    for index, line in enumerate(lines):
        require(line and not line.startswith(b">>"), f"{path}:{index+1}: headers and blanks are not accepted")
        try:
            record = line.decode("ascii")
        except UnicodeDecodeError as error:
            raise VerificationError(f"{path}:{index+1}: non-ASCII graph6") from error
        decode_graph6(record, right_size)
        result.append(record)
    require(len(result) == EXPECTED_CLASSES[right_size], f"{path}: unexpected record count")
    return result


def decode_graph6(record: str, right_size: int) -> list[int]:
    require(type(record) is str and record, "graph6: empty record")
    order = DIMENSION + right_size
    require(order <= 62 and ord(record[0]) - 63 == order, "graph6: wrong short-form order")
    edge_bits = order * (order - 1) // 2
    payload_chars = (edge_bits + 5) // 6
    require(len(record) == 1 + payload_chars, "graph6: payload length is not exact")
    values: list[int] = []
    for character in record[1:]:
        value = ord(character) - 63
        require(0 <= value <= 63, "graph6: byte outside printable graph6 range")
        values.append(value)
    bits = [(value >> shift) & 1 for value in values for shift in range(5, -1, -1)]
    require(all(bit == 0 for bit in bits[edge_bits:]), "graph6: nonzero padding bit")
    columns = [0] * right_size
    cursor = 0
    for high in range(1, order):
        for low in range(high):
            edge = bits[cursor]
            cursor += 1
            if edge:
                require(low < DIMENSION <= high, "graph6: edge inside a colour class")
                columns[high - DIMENSION] |= 1 << low
    require(all(1 <= value < 1 << DIMENSION for value in columns), "graph6: zero or oversized support column")
    require(len(columns) == len(set(columns)), "graph6: duplicate support column")
    require(sum(columns, 0) >= 0, "graph6: unreachable guard")
    row_union = 0
    for column in columns:
        row_union |= column
    require(row_union == (1 << DIMENSION) - 1, "graph6: isolated left vertex")
    return columns


def solve_measurement(columns: list[int]) -> list[Fraction] | None:
    width = len(columns)
    matrix = [[Fraction((column >> row) & 1) for column in columns] + [Fraction(1)]
              for row in range(DIMENSION)]
    pivots: list[int] = []
    next_row = 0
    for column in range(width):
        pivot = next((row for row in range(next_row, DIMENSION) if matrix[row][column] != 0), None)
        if pivot is None:
            return None
        matrix[next_row], matrix[pivot] = matrix[pivot], matrix[next_row]
        divisor = matrix[next_row][column]
        matrix[next_row] = [value / divisor for value in matrix[next_row]]
        for row in range(DIMENSION):
            if row == next_row:
                continue
            factor = matrix[row][column]
            if factor:
                matrix[row] = [matrix[row][j] - factor * matrix[next_row][j] for j in range(width + 1)]
        pivots.append(next_row)
        next_row += 1
    if any(all(matrix[row][column] == 0 for column in range(width)) and matrix[row][-1] != 0
           for row in range(DIMENSION)):
        return None
    tail = [matrix[pivots[column]][-1] for column in range(width)]
    weights = [Fraction(2) - sum(tail, Fraction(0)), *tail]
    if any(weight <= 0 for weight in weights):
        return None
    require(sum(weights, Fraction(0)) == 2, "measurement: weights do not sum to two")
    for row in range(DIMENSION):
        require(sum((weights[j + 1] for j, column in enumerate(columns) if column & (1 << row)), Fraction(0)) == 1,
                "measurement: facet weight is not one")
    return weights


def family_masks(size: int) -> list[int]:
    return [sum(1 << member for member in members)
            for cardinality in range(1, R + 1)
            for members in itertools.combinations(range(size), cardinality)]


def facet_masks(vertices: list[int]) -> list[int]:
    masks: set[int] = set()
    for coordinate in range(DIMENSION):
        for bit in (0, 1):
            members = [index for index, vertex in enumerate(vertices) if ((vertex >> coordinate) & 1) == bit]
            for cardinality in range(1, len(members) + 1):
                for subset in itertools.combinations(members, cardinality):
                    masks.add(sum(1 << member for member in subset))
    return sorted(masks, key=lambda mask: (mask.bit_count(), mask))


def demand(mask: int, weights: list[Fraction]) -> Fraction:
    return sum((weight for index, weight in enumerate(weights) if mask & (1 << index)), Fraction(0))


def parse_distribution(items: Any, size: int, where: str) -> dict[int, Fraction]:
    require(type(items) is list and items, f"{where}: distribution must be a nonempty array")
    allowed = set(family_masks(size))
    result: dict[int, Fraction] = {}
    for index, item in enumerate(items):
        exact_keys(item, {"mass", "support_subset_mask"}, f"{where}[{index}]")
        mask = item["support_subset_mask"]
        require(type(mask) is int and mask in allowed and mask not in result, f"{where}[{index}]: invalid or duplicate mask")
        mass = parse_rational(item["mass"], f"{where}[{index}].mass")
        require(mass >= 0, f"{where}[{index}]: negative mass")
        result[mask] = mass
    require(sum(result.values(), Fraction(0)) == 1, f"{where}: masses do not sum to one")
    return result


def verify_distribution(vertices: list[int], weights: list[Fraction], distribution: dict[int, Fraction]) -> dict[str, Any]:
    rows = facet_masks(vertices)
    zero = 0
    minimum: Fraction | None = None
    for row in rows:
        coverage = sum((mass for mask, mass in distribution.items() if mask & row), Fraction(0))
        slack = coverage - demand(row, weights)
        require(slack >= 0, "certificate: Proposition 2.1 inequality fails")
        if slack == 0:
            zero += 1
        elif minimum is None or slack < minimum:
            minimum = slack
    return {"constraints": len(rows), "zero_slacks": zero, "minimum_positive_slack": minimum}


def verify_saved_record(record: Any, columns: list[int], weights: list[Fraction], where: str) -> dict[str, Any]:
    base_keys = {"columns", "distribution", "distribution_columns", "facet_subset_constraints",
                 "graph6", "method", "ordinal", "weights"}
    method = record.get("method") if type(record) is dict else None
    expected_keys = base_keys | ({"construction"} if method == "seed_small_facet_construction" else set())
    exact_keys(record, expected_keys, where)
    require(method in EXPECTED_METHODS, f"{where}: unknown method")
    require(type(record["ordinal"]) is int and record["ordinal"] >= 0, f"{where}: invalid ordinal")
    require(type(record["graph6"]) is str, f"{where}: graph6 must be text")
    require(type(record["columns"]) is list and record["columns"] == columns, f"{where}: columns mismatch")
    require(type(record["weights"]) is list and len(record["weights"]) == len(weights), f"{where}: weight length mismatch")
    parsed_weights = [parse_rational(value, f"{where}.weights[{index}]") for index, value in enumerate(record["weights"])]
    require(parsed_weights == weights, f"{where}: saved weights mismatch")
    vertices = [0, *columns]
    rows = facet_masks(vertices)
    families = family_masks(len(vertices))
    require(record["facet_subset_constraints"] == len(rows), f"{where}: constraint count mismatch")
    require(record["distribution_columns"] == len(families), f"{where}: distribution-column count mismatch")
    distribution = parse_distribution(record["distribution"], len(vertices), f"{where}.distribution")
    statistics = verify_distribution(vertices, weights, distribution)
    if method == "seed_small_facet_construction":
        exact_keys(record["construction"], {"bit", "coordinate", "facet_mask"}, f"{where}.construction")
        coordinate = record["construction"]["coordinate"]
        bit = record["construction"]["bit"]
        require(type(coordinate) is int and 0 <= coordinate < DIMENSION, f"{where}: invalid construction coordinate")
        require(type(bit) is int and bit in (0, 1), f"{where}: invalid construction bit")
        facet = [index for index, vertex in enumerate(vertices) if ((vertex >> coordinate) & 1) == bit]
        facet_mask = sum(1 << index for index in facet)
        require(len(facet) <= 2 and record["construction"]["facet_mask"] == facet_mask,
                f"{where}: invalid small-facet receipt")
    return {**statistics, "distribution": distribution, "vertices": vertices, "weights": weights, "method": method}


def permutation_maps() -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    result = []
    for permutation in itertools.permutations(range(DIMENSION)):
        mapping = tuple(sum(((value >> source) & 1) << permutation[source] for source in range(DIMENSION))
                        for value in range(1 << DIMENSION))
        result.append((permutation, mapping))
    require(len(result) == 720, "canonicalisation: permutation count")
    return result


def canonical_transport(vertices: list[int], maps: list[tuple[tuple[int, ...], tuple[int, ...]]]) -> tuple[tuple[int, ...], dict[str, Any]]:
    best_vertices: tuple[int, ...] | None = None
    best_receipt: tuple[Any, ...] | None = None
    best_data: dict[str, Any] | None = None
    for origin_index, origin in enumerate(vertices):
        for permutation, mapping in maps:
            transformed = [mapping[vertex ^ origin] for vertex in vertices]
            canonical = tuple(sorted(transformed))
            index_map = tuple(canonical.index(value) for value in transformed)
            receipt_key = (origin_index, permutation, index_map)
            if best_vertices is None or canonical < best_vertices or (canonical == best_vertices and receipt_key < best_receipt):
                best_vertices = canonical
                best_receipt = receipt_key
                best_data = {
                    "xor_origin_source_index": origin_index,
                    "coordinate_permutation": list(permutation),
                    "source_to_canonical_index": list(index_map),
                }
    require(best_vertices is not None and best_data is not None, "canonicalisation: no image")
    return best_vertices, best_data


def remap_mask(mask: int, source_to_target: list[int]) -> int:
    result = 0
    for source, target in enumerate(source_to_target):
        if mask & (1 << source):
            result |= 1 << target
    return result


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise VerificationError(f"cannot read strict JSON {path}: {error}") from error
