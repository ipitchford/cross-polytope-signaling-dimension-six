#!/usr/bin/env python3
"""Exact public replay using the supplied graph files; never invokes genbg.

The original producer and verifier are preserved separately.  This fresh
standard-library verifier adds strict manifest and graph6 validation, checks
every one of 133,130 supplied representatives with rational arithmetic, checks
all 217 certificates, and verifies the deterministic 49-class catalogue.
Completeness of the supplied graph lists is established by the separate C++
orbit audit, not by this command.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

from verification_core import (
    DIMENSION, EXPECTED_CLASSES, EXPECTED_METHODS, EXPECTED_VALID, SHA256_RE,
    VerificationError, canonical_transport, decode_graph6, exact_keys,
    family_masks, fraction_text, load_json, parse_distribution, parse_rational,
    permutation_maps, read_graph6_records, remap_mask, require, sha256_file,
    solve_measurement, validate_manifest_schema, verify_distribution,
    verify_saved_record,
)


ORIGINAL_EXACT_VERIFIER_SHA256 = "15431091e6f88adda304193fbc543d5174e7c8abcfa3e780c3b3fd4191c0f512"
ORIGINAL_ORBIT_AUDIT_SHA256 = "d7f06eee42f6aa46f53780e2685e9042462b368e84889c6aee8488e413255c1d"


def process_inputs(data_dir: Path, manifest: dict[str, Any]) -> tuple[dict[str, Any], dict[tuple[int, int], dict[str, Any]]]:
    file_results: dict[str, Any] = {}
    record_index: dict[tuple[int, int], dict[str, Any]] = {}
    methods: Counter[str] = Counter()
    inequalities = 0
    zero_slacks = 0
    minimum_positive: Fraction | None = None

    for right_size in (5, 6):
        key = str(right_size)
        path = data_dir / f"genbg-6-{right_size}.g6"
        require(sha256_file(path) == manifest["generated_classes"][key]["sha256"], f"{path}: hash mismatch")
        graphs = read_graph6_records(path, right_size)
        saved_list = manifest["valid_measurements"][key]
        saved: dict[int, dict[str, Any]] = {}
        for index, record in enumerate(saved_list):
            require(type(record) is dict and type(record.get("ordinal")) is int, f"saved {key}[{index}]: invalid ordinal")
            ordinal = record["ordinal"]
            require(0 <= ordinal < len(graphs) and ordinal not in saved, f"saved {key}[{index}]: duplicate or out-of-range ordinal")
            saved[ordinal] = record

        valid = 0
        rejected = 0
        local_methods: Counter[str] = Counter()
        for ordinal, graph6 in enumerate(graphs):
            columns = decode_graph6(graph6, right_size)
            weights = solve_measurement(columns)
            record = saved.pop(ordinal, None)
            if weights is None:
                require(record is None, f"{key}:{ordinal}: invalid class has a saved certificate")
                rejected += 1
                continue
            require(record is not None, f"{key}:{ordinal}: valid class omitted from manifest")
            require(record["graph6"] == graph6, f"{key}:{ordinal}: saved graph6 mismatch")
            statistics = verify_saved_record(record, columns, weights, f"valid_measurements.{key}[ordinal={ordinal}]")
            method = statistics["method"]
            methods[method] += 1
            local_methods[method] += 1
            inequalities += statistics["constraints"]
            zero_slacks += statistics["zero_slacks"]
            positive = statistics["minimum_positive_slack"]
            if positive is not None and (minimum_positive is None or positive < minimum_positive):
                minimum_positive = positive
            valid += 1
            record_index[(right_size, ordinal)] = {
                "record": record,
                "vertices": statistics["vertices"],
                "weights": statistics["weights"],
                "distribution": statistics["distribution"],
            }
        require(not saved, f"{key}: saved records were not consumed")
        summary = manifest["summaries"][key]
        require(valid == EXPECTED_VALID[right_size] == summary["valid_measurements"], f"{key}: valid count mismatch")
        require(rejected + valid == EXPECTED_CLASSES[right_size], f"{key}: classification total mismatch")
        require(local_methods["seed_small_facet_construction"] == summary["seed_facet_certificates"],
                f"{key}: small-facet count mismatch")
        require(local_methods["proposition_2_1_exact_feasible"] == summary["lp_feasible_certificates"],
                f"{key}: exact-feasible count mismatch")
        file_results[key] = {
            "graph_classes": len(graphs),
            "valid_measurements": valid,
            "exact_rejections": rejected,
            "all_saved_records_matched_once": True,
            "methods": dict(sorted(local_methods.items())),
            "sha256": sha256_file(path),
        }

    require(sum(item["graph_classes"] for item in file_results.values()) == 133_130, "combined class count mismatch")
    require(len(record_index) == 217, "combined valid-measurement count mismatch")
    require(dict(methods) == EXPECTED_METHODS, "combined certificate-method counts mismatch")
    require(inequalities == 12_091, "combined inequality count mismatch")
    require(minimum_positive == Fraction(1, 12), "minimum positive slack mismatch")
    return {
        "files": file_results,
        "combined_graph_classes": 133_130,
        "combined_valid_measurements": 217,
        "combined_exact_rejections": 132_913,
        "certificate_methods": dict(sorted(methods.items())),
        "facet_subset_inequalities_checked": inequalities,
        "zero_slack_inequalities": zero_slacks,
        "minimum_positive_slack": fraction_text(minimum_positive),
    }, record_index


def transformed_vertices(source_vertices: list[int], origin_index: int, permutation: list[int]) -> list[int]:
    require(type(origin_index) is int and 0 <= origin_index < len(source_vertices), "catalogue member: invalid XOR origin")
    require(type(permutation) is list and sorted(permutation) == list(range(DIMENSION)),
            "catalogue member: invalid coordinate permutation")
    origin = source_vertices[origin_index]
    result = []
    for vertex in source_vertices:
        shifted = vertex ^ origin
        result.append(sum(((shifted >> source) & 1) << permutation[source] for source in range(DIMENSION)))
    return result


def validate_catalogue(catalogue: Any, manifest_hash: str,
                       record_index: dict[tuple[int, int], dict[str, Any]]) -> dict[str, int]:
    exact_keys(catalogue, {"schema", "scope", "input_manifest_sha256", "canonical_action",
                           "certificate_transport", "counts", "provenance", "classes"}, "catalogue")
    require(catalogue["schema"] == "cross-polytope-six-full-signed-cube-catalogue-v1", "catalogue: wrong schema")
    require(catalogue["input_manifest_sha256"] == manifest_hash, "catalogue: manifest binding mismatch")
    exact_keys(catalogue["counts"], {"classes", "difficult_classes", "small_facet_classes", "rooted_records",
                                     "support_size_6_classes", "support_size_7_classes"}, "catalogue.counts")
    exact_keys(catalogue["provenance"], {"original_producer_sha256", "original_exact_verifier_sha256",
                                         "review_method_credit"}, "catalogue.provenance")
    require(catalogue["provenance"]["original_exact_verifier_sha256"] == ORIGINAL_EXACT_VERIFIER_SHA256,
            "catalogue: original verifier attribution changed")
    require(type(catalogue["classes"]) is list, "catalogue.classes: expected array")
    maps = permutation_maps()
    seen_ids: set[str] = set()
    seen_records: set[tuple[int, int]] = set()
    difficult = 0
    support_counts: Counter[int] = Counter()

    for class_index, item in enumerate(catalogue["classes"]):
        where = f"catalogue.classes[{class_index}]"
        exact_keys(item, {"id", "support_size", "canonical_vertices", "certificate_method", "difficult",
                          "rooted_representative_count", "members", "canonical_certificate"}, where)
        canonical = item["canonical_vertices"]
        require(type(canonical) is list and len(canonical) in (6, 7) and canonical == sorted(set(canonical)) and canonical[0] == 0,
                f"{where}: invalid canonical support")
        require(all(type(vertex) is int and 0 <= vertex < 64 for vertex in canonical), f"{where}: invalid vertex")
        recomputed, _ = canonical_transport(canonical, maps)
        require(list(recomputed) == canonical, f"{where}: support is not canonical")
        expected_id = f"signed-cube-6-{len(canonical)}-{hashlib.sha256((','.join(map(str, canonical))).encode('ascii')).hexdigest()[:16]}"
        require(item["id"] == expected_id and item["id"] not in seen_ids, f"{where}: invalid or duplicate identity")
        seen_ids.add(item["id"])
        require(item["support_size"] == len(canonical), f"{where}: support-size mismatch")
        require(item["certificate_method"] in EXPECTED_METHODS, f"{where}: unknown method")
        expected_difficult = item["certificate_method"] == "proposition_2_1_exact_feasible"
        require(type(item["difficult"]) is bool and item["difficult"] == expected_difficult, f"{where}: difficulty mismatch")
        difficult += int(expected_difficult)
        support_counts[len(canonical)] += 1
        require(type(item["members"]) is list and item["rooted_representative_count"] == len(item["members"]) > 0,
                f"{where}: member count mismatch")

        member_lookup: dict[tuple[int, int], dict[str, Any]] = {}
        for member_index, member in enumerate(item["members"]):
            member_where = f"{where}.members[{member_index}]"
            exact_keys(member, {"right_size", "ordinal", "graph6", "source_vertices", "xor_origin_source_index",
                                "coordinate_permutation", "source_to_canonical_index"}, member_where)
            key = (member["right_size"], member["ordinal"])
            require(key in record_index and key not in seen_records, f"{member_where}: unknown or repeated source record")
            seen_records.add(key)
            member_lookup[key] = member
            source = record_index[key]
            require(member["graph6"] == source["record"]["graph6"], f"{member_where}: graph6 mismatch")
            require(member["source_vertices"] == source["vertices"], f"{member_where}: source vertices mismatch")
            transformed = transformed_vertices(source["vertices"], member["xor_origin_source_index"], member["coordinate_permutation"])
            require(sorted(transformed) == canonical, f"{member_where}: transform misses canonical support")
            index_map = member["source_to_canonical_index"]
            require(type(index_map) is list and sorted(index_map) == list(range(len(canonical))),
                    f"{member_where}: invalid vertex-index map")
            require([canonical[target] for target in index_map] == transformed, f"{member_where}: vertex-index map mismatch")
            require(source["record"]["method"] == item["certificate_method"], f"{member_where}: method mismatch")

        certificate = item["canonical_certificate"]
        exact_keys(certificate, {"source", "weights", "distribution", "transport"}, f"{where}.canonical_certificate")
        exact_keys(certificate["source"], {"right_size", "ordinal", "graph6"}, f"{where}.canonical_certificate.source")
        source_key = (certificate["source"]["right_size"], certificate["source"]["ordinal"])
        require(source_key in member_lookup and certificate["source"]["graph6"] == record_index[source_key]["record"]["graph6"],
                f"{where}: certificate source is not a member")
        member = member_lookup[source_key]
        exact_keys(certificate["transport"], {"xor_origin_source_index", "coordinate_permutation", "source_to_canonical_index"},
                   f"{where}.canonical_certificate.transport")
        require(certificate["transport"] == {field: member[field] for field in certificate["transport"]},
                f"{where}: certificate transport differs from member transport")
        weights = [parse_rational(value, f"{where}.weights") for value in certificate["weights"]]
        require(len(weights) == len(canonical) and sum(weights, Fraction(0)) == 2 and all(weight > 0 for weight in weights),
                f"{where}: invalid canonical weights")
        for coordinate in range(DIMENSION):
            require(sum((weight for vertex, weight in zip(canonical, weights) if vertex & (1 << coordinate)), Fraction(0)) == 1,
                    f"{where}: canonical facet weight mismatch")
        distribution = parse_distribution(certificate["distribution"], len(canonical), f"{where}.distribution")
        verify_distribution(canonical, weights, distribution)

        source = record_index[source_key]
        index_map = member["source_to_canonical_index"]
        transported_weights: list[Fraction | None] = [None] * len(canonical)
        for source_index, target_index in enumerate(index_map):
            transported_weights[target_index] = source["weights"][source_index]
        require(transported_weights == weights, f"{where}: canonical weights do not transport from source")
        transported_distribution = {remap_mask(mask, index_map): mass for mask, mass in source["distribution"].items()}
        require(transported_distribution == distribution, f"{where}: canonical distribution does not transport from source")

    require(seen_records == set(record_index), "catalogue: rooted record coverage is not exact")
    observed = {
        "classes": len(catalogue["classes"]),
        "difficult_classes": difficult,
        "small_facet_classes": len(catalogue["classes"]) - difficult,
        "rooted_records": len(seen_records),
        "support_size_6_classes": support_counts[6],
        "support_size_7_classes": support_counts[7],
    }
    require(observed == catalogue["counts"] == {
        "classes": 49, "difficult_classes": 28, "small_facet_classes": 21,
        "rooted_records": 217, "support_size_6_classes": 12, "support_size_7_classes": 37,
    }, "catalogue: aggregate counts mismatch")
    return observed


def mutate_graph_bit(record: str, bit_index: int) -> str:
    values = [ord(character) - 63 for character in record[1:]]
    character_index, within = divmod(bit_index, 6)
    values[character_index] |= 1 << (5 - within)
    return record[0] + "".join(chr(value + 63) for value in values)


def negative_controls(manifest: dict[str, Any], first_graph: str, first_record: dict[str, Any],
                      first_columns: list[int], first_weights: list[Fraction]) -> list[str]:
    passed: list[str] = []

    def rejects(name: str, action: Callable[[], Any]) -> None:
        try:
            action()
        except (VerificationError, KeyError, TypeError, IndexError):
            passed.append(name)
            return
        raise VerificationError(f"negative control was accepted: {name}")

    rejects("graph6-truncated", lambda: decode_graph6(first_graph[:-1], 5))
    edge_bits = 11 * 10 // 2
    rejects("graph6-nonzero-padding", lambda: decode_graph6(mutate_graph_bit(first_graph, edge_bits), 5))
    rejects("graph6-within-colour-edge", lambda: decode_graph6(mutate_graph_bit(first_graph, 0), 5))
    missing = copy.deepcopy(manifest)
    del missing["schema"]
    rejects("manifest-missing-key", lambda: validate_manifest_schema(missing))
    extra = copy.deepcopy(manifest)
    extra["unexpected"] = True
    rejects("manifest-extra-key", lambda: validate_manifest_schema(extra))
    rejects("noncanonical-rational", lambda: parse_rational("2/6", "negative-control"))
    wrong_total = copy.deepcopy(first_record)
    wrong_total["distribution"][0]["mass"] = "0"
    rejects("certificate-mass-total", lambda: verify_saved_record(wrong_total, first_columns, first_weights, "negative-control"))
    wrong_semantics = copy.deepcopy(first_record)
    wrong_semantics["distribution"] = [{"support_subset_mask": 1, "mass": "1"}]
    rejects("certificate-semantic-inequality", lambda: verify_saved_record(wrong_semantics, first_columns, first_weights, "negative-control"))
    require(len(passed) == 8, "negative-control count mismatch")
    return passed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[1]
    parser.add_argument("--data-dir", type=Path, default=root / "data")
    parser.add_argument("--producer-script", type=Path, default=root / "code" / "exhaustive-cross-polytope-six.py")
    parser.add_argument("--original-verifier", type=Path, default=root / "code" / "verify-cross-polytope-six-original.py")
    parser.add_argument("--orbit-source", type=Path, default=root / "code" / "verify-genbg-orbits.cpp")
    parser.add_argument("--catalogue", type=Path, default=root / "data" / "full-signed-cube-catalogue.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"refusing to overwrite {args.output}")

    manifest_path = args.data_dir / "manifest.json"
    manifest = load_json(manifest_path)
    validate_manifest_schema(manifest)
    manifest_hash = sha256_file(manifest_path)
    receipt_line = (args.data_dir / "MANIFEST.sha256").read_text().strip()
    require(receipt_line == f"{manifest_hash}  manifest.json", "manifest hash receipt mismatch")
    require(sha256_file(args.producer_script) == manifest["script_sha256"], "preserved original producer hash mismatch")
    require(sha256_file(args.original_verifier) == ORIGINAL_EXACT_VERIFIER_SHA256, "preserved original verifier hash mismatch")
    require(sha256_file(args.orbit_source) == ORIGINAL_ORBIT_AUDIT_SHA256, "preserved original orbit-audit hash mismatch")

    classification, record_index = process_inputs(args.data_dir, manifest)
    catalogue = load_json(args.catalogue)
    catalogue_counts = validate_catalogue(catalogue, manifest_hash, record_index)
    first_graph = read_graph6_records(args.data_dir / "genbg-6-5.g6", 5)[0]
    first_saved = manifest["valid_measurements"]["5"][0]
    first_columns = first_saved["columns"]
    first_weights = solve_measurement(first_columns)
    require(first_weights is not None, "negative-control fixture unexpectedly invalid")
    controls = negative_controls(manifest, first_graph, first_saved, first_columns, first_weights)

    receipt = {
        "schema": "cross-polytope-six-supplied-input-verification-v1",
        "verified_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "mode": "supplied-input-exact-replay-without-graph-regeneration",
        "input_hashes": {
            "manifest.json": manifest_hash,
            "genbg-6-5.g6": sha256_file(args.data_dir / "genbg-6-5.g6"),
            "genbg-6-6.g6": sha256_file(args.data_dir / "genbg-6-6.g6"),
            "full-signed-cube-catalogue.json": sha256_file(args.catalogue),
        },
        "preserved_original_attribution": {
            "producer": {"role": "original search and certificate production", "sha256": manifest["script_sha256"]},
            "exact_verifier": {"role": "original rational reclassification and certificate verification", "sha256": ORIGINAL_EXACT_VERIFIER_SHA256},
            "orbit_audit": {"role": "original independent coordinate-permutation orbit coverage", "sha256": ORIGINAL_ORBIT_AUDIT_SHA256},
            "research_workflow": "The supplied manuscript records OpenAI Codex as performing the searches, computation, verification and drafting under a human-directed workflow.",
        },
        "classification": classification,
        "full_signed_cube_catalogue": catalogue_counts,
        "strict_checks": {
            "manifest_exact_keys_and_counters": True,
            "graph6_exact_length_ascii_padding_bipartite_and_support_checks": True,
            "saved_record_schema_and_exact_rational_checks": True,
            "catalogue_transport_and_record_partition_checks": True,
        },
        "semantic_negative_controls": controls,
        "result": "all_133130_supplied_classes_classified_217_certificates_verified_and_49_full_cube_classes_mapped",
        "trust_boundary": "This command verifies the supplied bytes and mathematics after graph enumeration. Run the preserved C++ orbit audit for independent supplied-list completeness, and run regenerate_inputs.py only when byte-for-byte genbg reproduction is desired.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except VerificationError as error:
        raise SystemExit(f"verification error: {error}") from error
