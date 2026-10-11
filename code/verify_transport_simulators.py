#!/usr/bin/env python3
"""Reconstruct all 2,604 exact common-F stochastic simulations.

This fresh standard-library implementation is independent of the original
facet-inequality loop.  For each saved distribution F it solves twelve exact
integer transportation networks, verifies their allocations, and hashes the
complete allocation stream.  It follows the operational check described by
the internal proof audit without copying that private implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, deque
from datetime import datetime, timezone
from fractions import Fraction
from math import lcm
from pathlib import Path

from verification_core import (
    VerificationError, decode_graph6, load_json, parse_distribution, parse_rational,
    read_graph6_records, require, sha256_file, solve_measurement, validate_manifest_schema,
)


class FlowNetwork:
    def __init__(self, size: int) -> None:
        self.adjacency: list[list[int]] = [[] for _ in range(size)]
        self.capacity: dict[tuple[int, int], int] = {}
        self.original: dict[tuple[int, int], int] = {}

    def add(self, source: int, target: int, capacity: int) -> None:
        require(type(capacity) is int and capacity >= 0, "flow: invalid capacity")
        require((source, target) not in self.capacity, "flow: duplicate directed edge")
        self.adjacency[source].append(target)
        self.adjacency[target].append(source)
        self.capacity[source, target] = capacity
        self.capacity[target, source] = 0
        self.original[source, target] = capacity

    def maximum_flow(self, source: int, sink: int) -> int:
        total = 0
        while True:
            parent = {source: source}
            queue = deque([source])
            while queue and sink not in parent:
                current = queue.popleft()
                for target in self.adjacency[current]:
                    if target not in parent and self.capacity[current, target] > 0:
                        parent[target] = current
                        queue.append(target)
            if sink not in parent:
                return total
            amount: int | None = None
            current = sink
            while current != source:
                previous = parent[current]
                residual = self.capacity[previous, current]
                amount = residual if amount is None else min(amount, residual)
                current = previous
            require(amount is not None and amount > 0, "flow: nonpositive augmentation")
            current = sink
            while current != source:
                previous = parent[current]
                self.capacity[previous, current] -= amount
                self.capacity[current, previous] += amount
                current = previous
            total += amount

    def sent(self, source: int, target: int) -> int:
        return self.original[source, target] - self.capacity[source, target]


def transport(support_masks: list[int], supplies: list[int], demands: list[int], scale: int) -> list[list[int]]:
    subset_count = len(support_masks)
    outcome_count = len(demands)
    source = 0
    subset_start = 1
    outcome_start = subset_start + subset_count
    sink = outcome_start + outcome_count
    network = FlowNetwork(sink + 1)
    for subset_index, (mask, supply) in enumerate(zip(support_masks, supplies)):
        subset_node = subset_start + subset_index
        network.add(source, subset_node, supply)
        for outcome in range(outcome_count):
            if mask & (1 << outcome):
                network.add(subset_node, outcome_start + outcome, scale)
    for outcome, demand in enumerate(demands):
        network.add(outcome_start + outcome, sink, demand)
    require(network.maximum_flow(source, sink) == scale, "transport: common-F network does not saturate")
    allocation = []
    for subset_index, mask in enumerate(support_masks):
        subset_node = subset_start + subset_index
        row = []
        for outcome in range(outcome_count):
            value = network.sent(subset_node, outcome_start + outcome) if mask & (1 << outcome) else 0
            row.append(value)
        allocation.append(row)
    require([sum(row) for row in allocation] == supplies, "transport: supply mismatch")
    require([sum(row[outcome] for row in allocation) for outcome in range(outcome_count)] == demands,
            "transport: demand mismatch")
    require(all(value == 0 for mask, row in zip(support_masks, allocation)
                for outcome, value in enumerate(row) if not (mask & (1 << outcome))),
            "transport: allocation escaped subset support")
    return allocation


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[1]
    parser.add_argument("--data-dir", type=Path, default=root / "data")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"refusing to overwrite {args.output}")
    manifest_path = args.data_dir / "manifest.json"
    manifest = load_json(manifest_path)
    validate_manifest_schema(manifest)
    allocation_hash = hashlib.sha256()
    method_counts: Counter[str] = Counter()
    measurement_count = 0
    transport_count = 0

    for right_size in (5, 6):
        graphs = read_graph6_records(args.data_dir / f"genbg-6-{right_size}.g6", right_size)
        for record in manifest["valid_measurements"][str(right_size)]:
            graph6 = graphs[record["ordinal"]]
            require(graph6 == record["graph6"], "transport replay: graph6 mismatch")
            columns = decode_graph6(graph6, right_size)
            vertices = [0, *columns]
            weights = solve_measurement(columns)
            require(weights is not None, "transport replay: saved measurement is invalid")
            require(weights == [parse_rational(value, "transport replay weight") for value in record["weights"]],
                    "transport replay: saved weights mismatch")
            distribution = parse_distribution(record["distribution"], len(vertices), "transport replay distribution")
            positive = [(mask, mass) for mask, mass in sorted(distribution.items()) if mass > 0]
            require(positive and sum((mass for _, mass in positive), Fraction(0)) == 1,
                    "transport replay: positive common distribution is not normalized")
            support_masks = [mask for mask, _ in positive]
            masses = [mass for _, mass in positive]
            scale = lcm(*(value.denominator for value in [*weights, *masses]))
            supplies = [int(mass * scale) for mass in masses]
            require(sum(supplies) == scale, "transport replay: scaled supplies do not sum")

            for coordinate in range(6):
                for bit in (0, 1):
                    demands = [int(weight * scale) if ((vertex >> coordinate) & 1) == bit else 0
                               for vertex, weight in zip(vertices, weights)]
                    require(sum(demands) == scale, "transport replay: scaled demands do not sum")
                    allocation = transport(support_masks, supplies, demands, scale)
                    payload = {
                        "right_size": right_size,
                        "ordinal": record["ordinal"],
                        "coordinate": coordinate,
                        "bit": bit,
                        "scale": scale,
                        "support_masks": support_masks,
                        "allocation": allocation,
                    }
                    allocation_hash.update(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("ascii"))
                    allocation_hash.update(b"\n")
                    transport_count += 1
            method_counts[record["method"]] += 1
            measurement_count += 1

    require(measurement_count == 217 and transport_count == 2_604, "transport replay: aggregate count mismatch")
    require(dict(method_counts) == {
        "seed_small_facet_construction": 87,
        "proposition_2_1_exact_feasible": 130,
    }, "transport replay: method counts mismatch")
    receipt = {
        "schema": "cross-polytope-six-exact-transport-reconstruction-v1",
        "verified_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_manifest_sha256": sha256_file(manifest_path),
        "measurement_count": measurement_count,
        "exact_input_column_transports": transport_count,
        "method_counts": dict(sorted(method_counts.items())),
        "common_distribution_fixed_across_twelve_inputs": True,
        "simulator_components_use_at_most_three_output_rows": True,
        "allocation_stream_sha256": allocation_hash.hexdigest(),
        "method": "Exact integer max-flow reconstruction with explicit supply, demand and support checks; no optimizer or floating-point arithmetic.",
        "provenance_boundary": "Fresh public implementation based on the operational method described by the internal proof audit; no private review code is included.",
        "result": "all_2604_input_column_simulations_reconstructed_exactly",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except VerificationError as error:
        raise SystemExit(f"verification error: {error}") from error
