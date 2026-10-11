#!/usr/bin/env python3
"""Build the deterministic 49-class full signed-cube certificate catalogue."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from verification_core import (
    EXPECTED_VALID, VerificationError, canonical_transport, decode_graph6, fraction_text,
    load_json, parse_distribution, parse_rational, permutation_maps, read_graph6_records,
    remap_mask, require, sha256_file, validate_manifest_schema, verify_distribution,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parents[1] / "data")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "full-signed-cube-catalogue.json")
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"refusing to overwrite {args.output}")

    manifest_path = args.data_dir / "manifest.json"
    manifest = load_json(manifest_path)
    validate_manifest_schema(manifest)
    maps = permutation_maps()
    grouped: dict[tuple[int, ...], list[dict[str, object]]] = defaultdict(list)

    for right_size in (5, 6):
        records = read_graph6_records(args.data_dir / f"genbg-6-{right_size}.g6", right_size)
        for saved in manifest["valid_measurements"][str(right_size)]:
            ordinal = saved["ordinal"]
            require(type(ordinal) is int and 0 <= ordinal < len(records), "catalogue: saved ordinal outside graph file")
            graph6 = records[ordinal]
            require(saved["graph6"] == graph6, "catalogue: saved graph6 mismatch")
            columns = decode_graph6(graph6, right_size)
            require(saved["columns"] == columns, "catalogue: saved columns mismatch")
            vertices = [0, *columns]
            canonical, transport = canonical_transport(vertices, maps)
            grouped[canonical].append({
                "right_size": right_size,
                "ordinal": ordinal,
                "graph6": graph6,
                "vertices": vertices,
                "transport": transport,
                "record": saved,
            })

    classes = []
    for canonical, members in sorted(grouped.items(), key=lambda item: (len(item[0]), item[0])):
        members.sort(key=lambda member: (member["right_size"], member["ordinal"]))
        methods = {member["record"]["method"] for member in members}
        require(len(methods) == 1, "catalogue: one full-cube orbit has mixed certificate methods")
        method = next(iter(methods))
        source = members[0]
        record = source["record"]
        index_map = source["transport"]["source_to_canonical_index"]
        source_weights = [parse_rational(value, "catalogue.source.weight") for value in record["weights"]]
        canonical_weights = [None] * len(source_weights)
        for source_index, target_index in enumerate(index_map):
            canonical_weights[target_index] = source_weights[source_index]
        require(all(weight is not None for weight in canonical_weights), "catalogue: incomplete weight transport")
        source_distribution = parse_distribution(record["distribution"], len(source_weights), "catalogue.source.distribution")
        canonical_distribution = {
            remap_mask(mask, index_map): mass for mask, mass in source_distribution.items()
        }
        require(len(canonical_distribution) == len(source_distribution), "catalogue: distribution transport collided")
        verify_distribution(list(canonical), canonical_weights, canonical_distribution)
        identity = hashlib.sha256((",".join(map(str, canonical))).encode("ascii")).hexdigest()[:16]
        classes.append({
            "id": f"signed-cube-6-{len(canonical)}-{identity}",
            "support_size": len(canonical),
            "canonical_vertices": list(canonical),
            "certificate_method": method,
            "difficult": method == "proposition_2_1_exact_feasible",
            "rooted_representative_count": len(members),
            "members": [
                {
                    "right_size": member["right_size"],
                    "ordinal": member["ordinal"],
                    "graph6": member["graph6"],
                    "source_vertices": member["vertices"],
                    **member["transport"],
                }
                for member in members
            ],
            "canonical_certificate": {
                "source": {"right_size": source["right_size"], "ordinal": source["ordinal"], "graph6": source["graph6"]},
                "weights": [fraction_text(weight) for weight in canonical_weights],
                "distribution": [
                    {"support_subset_mask": mask, "mass": fraction_text(mass)}
                    for mask, mass in sorted(canonical_distribution.items())
                ],
                "transport": source["transport"],
            },
        })

    total_members = sum(item["rooted_representative_count"] for item in classes)
    difficult = sum(item["difficult"] for item in classes)
    require(len(classes) == 49 and difficult == 28 and total_members == sum(EXPECTED_VALID.values()),
            "catalogue: expected 49 classes, 28 difficult classes and 217 rooted records")
    document = {
        "schema": "cross-polytope-six-full-signed-cube-catalogue-v1",
        "scope": "Full signed-cube orbits of the 217 exactly retained rooted measurement records; exhaustive graph-list coverage is checked separately.",
        "input_manifest_sha256": sha256_file(manifest_path),
        "canonical_action": "Choose a support vertex as XOR origin, then permute the six coordinates; sort the transformed vertices.",
        "certificate_transport": "Each class carries one exact supplied distribution transported to canonical vertex order and a source-to-canonical map for every rooted record.",
        "counts": {
            "classes": 49,
            "difficult_classes": 28,
            "small_facet_classes": 21,
            "rooted_records": 217,
            "support_size_6_classes": sum(item["support_size"] == 6 for item in classes),
            "support_size_7_classes": sum(item["support_size"] == 7 for item in classes),
        },
        "provenance": {
            "original_producer_sha256": manifest["script_sha256"],
            "original_exact_verifier_sha256": "15431091e6f88adda304193fbc543d5174e7c8abcfa3e780c3b3fd4191c0f512",
            "review_method_credit": "The full signed-cube grouping follows the method recorded in the internal independent-structure review; this builder is a fresh implementation and does not include that private review code.",
        },
        "classes": classes,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print(json.dumps(document["counts"], sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except VerificationError as error:
        raise SystemExit(f"verification error: {error}") from error
