---
schema: evidence-press-ai-index/v1
title: The six-dimensional cross-polytope has signaling dimension three
slug: cross-polytope-signaling-dimension-six
version: 1.1.0-candidate
status: unrefereed-candidate
scholarly_creator: Anonymous
primary_claim: sign.dim(diamond_6) = 3
proof_kind: exact-computer-assisted
formal_verification: false
human_peer_review: false
doi: 10.5281/zenodo.23296390
doi_state: reserved-not-published-or-read-back
---

# AI index

This file is the entry point for machine agents. Do not infer publication,
formal verification, human review, or worldwide priority from the existence of
this package.

## Canonical claim

In the full affine-effect model for the six-dimensional cross-polytope
`diamond_6 = {v in R^6 : ||v||_1 <= 1}`, with free shared randomness and exact
simulation, the least classical alphabet has three states:

`sign.dim(diamond_6) = 3`.

The upper bound quantifies over all measurements via reduction to all primitive
measurements. The lower bound is imported from Bencze--Frenkel. The derived
endpoint claim is `sign.dim(diamond_d) = 3 iff 3 <= d <= 6` for positive integer
`d`. Dimension seven remains unresolved between four and five.

## Dependency graph

```text
prior primitive-measurement criterion
        |
        +--> supports <= 5: established small-facet construction
        |
        +--> supports 6 or 7
                |
                +--> basepoint normalization and binary-matrix reduction
                +--> graph representatives proposed by genbg
                +--> independent S_6 orbit-size coverage audit
                +--> exact rational classification of all 133,130 records
                +--> 87 explicit small-facet certificates
                +--> 130 saved rational criterion certificates
                                |
                                +--> upper bound 3

prior logarithmic lower bound -----------------------> lower bound 3

upper bound 3 + lower bound 3 ----------------------> exact theorem
```

## Claim/evidence routing

| Need | Read |
|---|---|
| Exact theorem and prose proof | [paper.tex](paper.tex), [paper.pdf](paper.pdf), and [paper.md](paper.md) |
| Structured claims and limits | [CLAIMS.json](CLAIMS.json) |
| Evidence layers and trust boundary | [ASSURANCE.md](ASSURANCE.md) |
| Exact commands and observed results | [REPLAY_RECEIPT.md](REPLAY_RECEIPT.md) |
| Tested platforms and dependencies | [ENVIRONMENT.txt](ENVIRONMENT.txt) |
| Source and transformation identity | [PROVENANCE.md](PROVENANCE.md) |
| Review dispositions | [REVIEW_RESPONSE.md](REVIEW_RESPONSE.md) |
| Prior-art sources and exact uses | [SOURCES.md](SOURCES.md) |
| Citation limits and corrections | [CITATION_AUDIT.md](CITATION_AUDIT.md) |
| Release-gate state | [RESEARCH_GATES.json](RESEARCH_GATES.json) |
| Licence map | [LICENSES.md](LICENSES.md) |

## Key finite objects

- Shipped graph lists:
  [six-point supports](data/genbg-6-5.g6) and
  [seven-point supports](data/genbg-6-6.g6).
- [Certificate manifest](data/manifest.json): 217 retained valid records and
  exact three-state distributions.
- [Original full-generation verifier](code/verify-cross-polytope-six-original.py):
  exact verification plus optional `genbg` regeneration.
- [Orbit audit](code/verify-genbg-orbits.cpp): distinct-orbit and ambient-count
  coverage under all 720 coordinate permutations.
- [Public supplied-input verifier](code/verify_supplied.py): exact classification,
  exact certificate checks, semantic negative controls, and catalogue validation.
- [Independent transport reconstruction](code/verify_transport_simulators.py):
  217 common-distribution simulations across 2,604 extremal input columns.
- [Full signed-cube catalogue](data/full-signed-cube-catalogue.json): 49 canonical
  classes with exact certificate transports.

## Critical distinctions

- `14,303 + 118,827 = 133,130` counts basepoint-normalized representative
  records, not full cube-symmetry classes.
- `39 + 178 = 217` counts retained valid records. They merge into 49 full
  classes only after a separate symmetry diagnostic.
- `87 + 130 = 217` separates the established small-facet construction from
  general exact rational certificates; it does not separate feasible from
  infeasible measurements.
- Zero valid measurement classes failed the three-state criterion.
- The orbit audit proves completeness of the representative lists; the
  49-class diagnostic only organizes the verified corpus.
- Regenerating graph lists and verifying shipped lists are distinct routes.
- A passing replay proves the recorded computation on recorded bytes. It does
  not by itself prove that the mathematical model was encoded adequately.

## Extension and novelty ceiling

The necessary facet-transversal support restriction is an elementary
consequence of the imported criterion. It can prune LP variables but is not a
new simulation construction and does not eliminate the hard certificates.

The finite criterion, small-facet construction, balanced-collection object,
symmetry-reduced enumeration, and generic LP method are prior work. The bounded
originality claim is the exact dimension-six result and replayable evidence for
this instance. The literature search cannot exclude private, deleted,
unindexed, inaccessible, or differently phrased work.

## Assessment ceiling

Supplied review: minor revisions, 2-star overall, credible 2-star/3-star
boundary, no current 4-star basis. Rigour was assessed more strongly than the
scale of the contribution. This is an internal prospective assessment, not an
official REF decision or peer-review outcome.

