# Replay receipt

Package: `cross-polytope-signaling-dimension-six`  
Version: `1.1.0-candidate`  
Replay date: 2026-10-11  
Current result: supplied-input exact verification, optimized-mode replay,
independent orbit coverage, full-symmetry catalogue verification, independent
common-`F` transport reconstruction, and optional graph regeneration passed.

This receipt records the public-package replay. It does not turn command
execution into scientific adequacy, peer review, or formal proof.

## Route 1: supplied-input exact verification

Commands, from the repository root:

```sh
python3 code/verify_supplied.py --output checks/verification-normal.json
python3 -O code/verify_supplied.py --output checks/verification-optimized.json
```

Dependencies: Python 3 standard library only. Observed Python: 3.14.7.
Neither command invokes `genbg`.

Both modes reported:

- 133,130 shipped graph representatives classified;
- 132,913 exact rejections as non-measurement candidates;
- 217 exact valid primitive-measurement records;
- all 217 saved certificates matched exactly once;
- 87 small-facet and 130 general rational certificates;
- 12,091 distinct facet-subset inequalities checked;
- 7,245 zero-slack inequalities;
- minimum positive slack `1/12`;
- 49 full signed-cube classes, including 28 difficult classes;
- all catalogue record partitions, symmetry transports, certificate
  transports, canonical weights, and canonical distributions checked; and
- eight semantic negative controls rejected.

The normal and optimized outputs differ only in `verified_at`. Their canonical
payload SHA-256 after removing that field is:

`68cbdb8cf2987039dfeca54b08f6746383f85313b39df4edcfac3e8235b3502f`

Retained output identities:

| File | SHA-256 |
|---|---|
| `checks/verification-normal.json` | `7d068ba13602990cad545c8b7ae57d70a31c8c09f9c424fc26bb0bd8d55a3c5d` |
| `checks/verification-optimized.json` | `8670f66792ddf4a2d17d32c09e5ddf2d36e833ddc6e62131f8dd5a60799900b1` |

Semantic negative controls:

1. truncated graph6 record;
2. nonzero graph6 padding;
3. within-colour graph edge;
4. missing manifest key;
5. extra manifest key;
6. noncanonical rational value;
7. certificate mass not summing to one; and
8. a certificate violating a required inequality.

These controls show that the public verifier rejects representative structural
and semantic corruption. They do not prove that every conceivable defect is
detected.

## Route 2: independent orbit coverage

Commands:

```sh
c++ -std=c++17 -O2 code/verify-genbg-orbits.cpp -o checks/verify-genbg-orbits
checks/verify-genbg-orbits data/genbg-6-5.g6 data/genbg-6-6.g6
```

Observed compiler: Apple clang 21.0.0. Both commands exited zero; stderr was
empty.

The audit applied all 720 coordinate permutations to every representative,
found no duplicate canonical orbit, and recovered the independent
inclusion--exclusion totals:

| File family | Representatives | Sum of orbit sizes | Expected labelled supports |
|---|---:|---:|---:|
| Five binary columns / six-point support | 14,303 | 6,054,006 | 6,054,006 |
| Six binary columns / seven-point support | 118,827 | 63,602,770 | 63,602,770 |

Retained identities:

| File | SHA-256 |
|---|---|
| `checks/orbit-compile.log` | `13a00a5c2c53c17dd07da4c5671110c74c699fd1cd6ed5f8347b4b8de7a069f7` |
| `checks/orbit-audit.json` | `18b7df052a0eb5878de244f2dcfc9df16415f8b878b4402adac9155d7054fbdc` |
| `code/verify-genbg-orbits.cpp` | `d7f06eee42f6aa46f53780e2685e9042462b368e84889c6aee8488e413255c1d` |

The compiled binary is environment-specific and need not be treated as a
portable scientific input; the source, command, compiler identity, and JSON
result are the durable record.

## Route 3: optional graph-list regeneration

Command:

```sh
python3 code/regenerate_inputs.py --output checks/regeneration.json
```

This route requires nauty `genbg` on `PATH`. The observed executable was
`/opt/homebrew/bin/genbg`; the frozen scientific manifest identifies version
2.9.3. Both generated files were byte-identical to the shipped inputs:

| File | Records | SHA-256 |
|---|---:|---|
| `data/genbg-6-5.g6` | 14,303 | `577bdda1746350f0644b793d2a1cd8d416f2f16c3a10a0180aaf6b812783c0a3` |
| `data/genbg-6-6.g6` | 118,827 | `32a669ac020071965b16e55f299bfb50cbf58fa1c2d360e3dd2242589044f43c` |

Receipt: `checks/regeneration.json`, SHA-256
`b13fc08de818632e3188f515962db3d1c5ac68cbdeb34904cf74fba936f7d838`.

Regeneration checks byte reproducibility. The supplied-input verifier and orbit
audit separately establish classification, exact certificate validity, and
coverage, so an environment without nauty can still run the complete economical
verification route.

## Full-symmetry catalogue

The deterministic catalogue uses the action: choose any support vertex as the
XOR origin, permute all six coordinates, and sort the transformed vertices.
It maps every one of the 217 rooted records exactly once, transports one exact
certificate to each canonical class, and reports:

- 12 six-point classes;
- 37 seven-point classes;
- 49 total classes;
- 21 small-facet classes; and
- 28 difficult classes, split 5 six-point and 23 seven-point.

Catalogue SHA-256:

`data/full-signed-cube-catalogue.json`  
`5fe2c2c860dbd1b55b89f63caf845423b2cfa89bbec8d3585f6d78ff20321ed7`

This catalogue is an explanatory quotient of the verified 217-record corpus.
It is not the independent proof that the original representative files cover
the full ambient universe; that role belongs to Route 2.

## Independent common-distribution simulation

Commands:

```sh
python3 code/verify_transport_simulators.py --output checks/transport-normal.json
python3 -O code/verify_transport_simulators.py --output checks/transport-optimized.json
```

The fresh public standard-library implementation uses exact integer max-flow
to reconstruct the operational simulator independently of the original
facet-inequality loop. Both modes passed and reported:

- 217 measurement systems;
- 2,604 exact transports, one for each of twelve extremal input states;
- the same fixed subset distribution `F` across all twelve inputs of a
  measurement;
- simulator components supported on at most three output rows;
- 87 small-facet and 130 general exact-certificate measurements; and
- identical allocation-stream SHA-256
  `b3c0ff9b7bafb08c144f16938b8c9ed9a8b01fe15f6019de4359334ad1fe56c0`.

Retained identities:

| File | SHA-256 |
|---|---|
| `code/verify_transport_simulators.py` | `78a2a09640ea2b85d6a41080259625bcf86abbd03fc3fa8d183743093aaedd8f` |
| `checks/transport-normal.json` | `0b805a3327c0bfeacc9e64f53ded4a328e48aac2fe672cbea77208ade0b01154` |
| `checks/transport-optimized.json` | `0f635673b010b43c7e628b68d4b634c916f7434cc7104060ec23ed6bb47fe4f5` |

The implementation follows the operational method described in the supplied
proof audit but contains no private review code. It checks exact supplies,
demands, support restrictions, saturation, and allocation identities without
an optimizer or floating-point arithmetic.

## Selected input and implementation identities

| File | SHA-256 |
|---|---|
| `data/manifest.json` | `bee562da971e9bd8c25513407438158dadd3a88d423dee21ffc3674528e55036` |
| `code/verification_core.py` | `f13d91542b465833eaca9186a4b4b999da1ceb49918cf6bd341acd09bd7e1123` |
| `code/verify_supplied.py` | `64947c7b4d9cb0cbad157f42f5f78e09d3fde19b2573319ccc43ba7fe31244f4` |
| `code/regenerate_inputs.py` | `0ac5dd8139627a233c606acc8a5be1413648c506be80649c0717c4bd8d4c7abf` |
| `code/build_full_cube_catalogue.py` | `22e750fe7502f425a0c800bb9084d5446e9df1ba121ffb7b7956f3cf8da44558` |
| `code/verify_transport_simulators.py` | `78a2a09640ea2b85d6a41080259625bcf86abbd03fc3fa8d183743093aaedd8f` |
| `data/ORIGINAL_ATTRIBUTION.json` | `6cebac0fc826b1c02856e4ddecba56dc5be2632973b39c9155c914537186525a` |
| `data/ORIGINAL_INPUTS.sha256` | `ca13072813bb08a949b1b380a45a964c9dfe9f51126bdbcc225ae8ca0453dd69` |
| `checks/replay-summary.json` | `18d142b8e3a1a3d479e0ce63c54b15367cbc4cec3d9011197fd0c0e96ce5e6f1` |
| `checks/FILE_SHA256SUMS` | `40602ff72377787b92c0d20749f13de2d63466b32662cdc2106d28bd6d44e0e5` |
| `checks/check_manifest.py` | `9792460471a06b52b9fe25423f79917460364a9767fbb31e31f499dbf82b7d01` |
| `checks/check_replay_gate.py` | `0123ec4228d931dfeaa14f5e6c4455057f0cc5ec39723774dbae0c14dd3be13c` |
| `checks/run_orbit_audit.py` | `51e566d8d2cafaa960dd9cad5ff3cc7b5dbc4aa38f73ebe1825e64608a76ea65` |
| `checks/source_environment_lint.py` | `9a0f8ef504a0674e7c4f1b83136655eb390775a495a2de6f97d3ef61a509b8e7` |

The original producer, exact verifier, orbit-audit source, graph files, and
certificate manifest are preserved byte-for-byte and attributed by
`data/ORIGINAL_ATTRIBUTION.json` and `data/ORIGINAL_INPUTS.sha256`.

The final public checksum ledger was verified from the repository root with
`shasum -a 256 -c checks/FILE_SHA256SUMS`; every listed file matched. The
manifest, replay-gate, and source-environment checks are release-integrity
checks rather than additional mathematical evidence.

## What this replay establishes

Together with the manuscript's finite reduction, Routes 1 and 2 supply exact
evidence for every remaining primitive measurement. Route 3 is optional
generation reproducibility. The catalogue makes full cube symmetry explicit.
The independent common-distribution route is a redundant operational check of
the criterion's meaning.

None of these commands proves the imported criterion or lower bound, checks
the entire argument in a proof assistant, supplies human peer review, or
establishes public-provider byte identity. Final manifest coverage, PDF QA, CI,
tag, release, archive publication, and canonical readback are distinct
publication gates.

