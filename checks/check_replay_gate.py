#!/usr/bin/env python3
"""Gate normal/optimized exact replays and independent orbit coverage."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
NEGATIVE_CONTROLS = [
    "graph6-truncated",
    "graph6-nonzero-padding",
    "graph6-within-colour-edge",
    "manifest-missing-key",
    "manifest-extra-key",
    "noncanonical-rational",
    "certificate-mass-total",
    "certificate-semantic-inequality",
]
METHOD_COUNTS = {
    "proposition_2_1_exact_feasible": 130,
    "seed_small_facet_construction": 87,
}
ALLOCATION_STREAM_SHA256 = "b3c0ff9b7bafb08c144f16938b8c9ed9a8b01fe15f6019de4359334ad1fe56c0"


class GateError(ValueError):
    """Raised when one of the frozen scientific replay gates fails."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise GateError(message)


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise GateError(f"{path}: cannot read strict JSON: {error}") from error
    require(type(value) is dict, f"{path}: expected JSON object")
    return value


def payload_without_time(value: dict[str, Any], where: str) -> dict[str, Any]:
    copy = dict(value)
    timestamp = copy.pop("verified_at", None)
    require(type(timestamp) is str and timestamp.endswith("Z"), f"{where}: invalid verified_at")
    return copy


def digest(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def check_supplied(value: dict[str, Any]) -> None:
    require(value.get("schema") == "cross-polytope-six-supplied-input-verification-v1",
            "supplied-input receipt: schema mismatch")
    require(value.get("mode") == "supplied-input-exact-replay-without-graph-regeneration",
            "supplied-input receipt: mode mismatch")
    classification = value.get("classification")
    require(type(classification) is dict, "supplied-input receipt: missing classification")
    require(classification.get("combined_graph_classes") == 133_130,
            "supplied-input receipt: graph-class count mismatch")
    require(classification.get("combined_valid_measurements") == 217,
            "supplied-input receipt: valid-measurement count mismatch")
    require(classification.get("combined_exact_rejections") == 132_913,
            "supplied-input receipt: rejection count mismatch")
    require(classification.get("certificate_methods") == METHOD_COUNTS,
            "supplied-input receipt: certificate-method count mismatch")
    require(classification.get("facet_subset_inequalities_checked") == 12_091,
            "supplied-input receipt: inequality count mismatch")
    require(classification.get("zero_slack_inequalities") == 7_245,
            "supplied-input receipt: zero-slack count mismatch")
    require(classification.get("minimum_positive_slack") == "1/12",
            "supplied-input receipt: positive-slack minimum mismatch")
    require(value.get("full_signed_cube_catalogue") == {
        "classes": 49,
        "difficult_classes": 28,
        "small_facet_classes": 21,
        "rooted_records": 217,
        "support_size_6_classes": 12,
        "support_size_7_classes": 37,
    }, "supplied-input receipt: full signed-cube catalogue counts mismatch")
    require(value.get("semantic_negative_controls") == NEGATIVE_CONTROLS,
            "supplied-input receipt: the eight semantic negative controls did not all reject")
    strict = value.get("strict_checks")
    require(type(strict) is dict and strict and all(flag is True for flag in strict.values()),
            "supplied-input receipt: strict structural checks are incomplete")
    require(value.get("result") ==
            "all_133130_supplied_classes_classified_217_certificates_verified_and_49_full_cube_classes_mapped",
            "supplied-input receipt: result mismatch")


def check_transport(value: dict[str, Any]) -> None:
    require(value.get("schema") == "cross-polytope-six-exact-transport-reconstruction-v1",
            "transport receipt: schema mismatch")
    require(value.get("measurement_count") == 217, "transport receipt: measurement count mismatch")
    require(value.get("exact_input_column_transports") == 2_604,
            "transport receipt: input-column transport count mismatch")
    require(value.get("method_counts") == METHOD_COUNTS, "transport receipt: method counts mismatch")
    require(value.get("common_distribution_fixed_across_twelve_inputs") is True,
            "transport receipt: common distribution was not fixed")
    require(value.get("simulator_components_use_at_most_three_output_rows") is True,
            "transport receipt: simulator support bound failed")
    require(value.get("allocation_stream_sha256") == ALLOCATION_STREAM_SHA256,
            "transport receipt: allocation stream mismatch")
    require(value.get("result") == "all_2604_input_column_simulations_reconstructed_exactly",
            "transport receipt: result mismatch")


def check_orbit(value: dict[str, Any]) -> None:
    require(set(value) == {"schema", "coordinate_permutations", "right_size_5", "right_size_6",
                           "result", "count_formula"}, "orbit receipt: keys mismatch")
    require(value["schema"] == "cross-polytope-six-orbit-audit-v1", "orbit receipt: schema mismatch")
    require(value["coordinate_permutations"] == 720, "orbit receipt: permutation count mismatch")
    expected = {
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
    }
    for key, fields in expected.items():
        require(value[key] == fields, f"orbit receipt: {key} mismatch")
    require(value["result"] == "all_orbits_unique_and_complete", "orbit receipt: result mismatch")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verification-normal", type=Path, required=True)
    parser.add_argument("--verification-optimized", type=Path, required=True)
    parser.add_argument("--transport-normal", type=Path, required=True)
    parser.add_argument("--transport-optimized", type=Path, required=True)
    parser.add_argument("--orbit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), f"refusing to overwrite output: {args.output}")

    verification_normal = load(args.verification_normal)
    verification_optimized = load(args.verification_optimized)
    transport_normal = load(args.transport_normal)
    transport_optimized = load(args.transport_optimized)
    orbit = load(args.orbit)
    check_supplied(verification_normal)
    check_supplied(verification_optimized)
    check_transport(transport_normal)
    check_transport(transport_optimized)
    check_orbit(orbit)

    verification_payload = payload_without_time(verification_normal, "normal supplied-input receipt")
    require(payload_without_time(verification_optimized, "optimized supplied-input receipt") == verification_payload,
            "normal and optimized supplied-input receipts differ beyond verified_at")
    transport_payload = payload_without_time(transport_normal, "normal transport receipt")
    require(payload_without_time(transport_optimized, "optimized transport receipt") == transport_payload,
            "normal and optimized transport receipts differ beyond verified_at")
    for value, where in ((digest(verification_payload), "supplied-input payload"),
                         (digest(transport_payload), "transport payload")):
        require(SHA256_RE.fullmatch(value) is not None, f"{where}: digest construction failed")

    receipt = {
        "schema": "cross-polytope-six-replay-gate-v1",
        "verified_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "supplied_input_payload_sha256": digest(verification_payload),
        "transport_payload_sha256": digest(transport_payload),
        "allocation_stream_sha256": ALLOCATION_STREAM_SHA256,
        "semantic_negative_controls_rejected": len(NEGATIVE_CONTROLS),
        "graph_classes": 133_130,
        "retained_measurements": 217,
        "full_signed_cube_classes": 49,
        "difficult_full_signed_cube_classes": 28,
        "exact_input_column_transports": 2_604,
        "coordinate_permutations": 720,
        "labelled_supports_covered": 6_054_006 + 63_602_770,
        "result": "normal_optimized_exact_replays_match_and_independent_orbit_gate_passes",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except GateError as error:
        raise SystemExit(f"replay gate error: {error}") from error
