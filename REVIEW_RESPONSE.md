# Response to the supplied academic review

Version addressed: `1.1.0-candidate`  
Response date: 2026-10-11  
Recommendation received: minor revisions  
Supplied review archive SHA-256:
`77a746b50fbf22f9328d26cbd500f86d099bbc029e2244a16d22a6c4d3bf178d`

The supplied review assessed the frozen six-page manuscript and private
evidence archive. This response records changes in the revised public
derivative. It does not represent the revised version as externally rereviewed.
No fatal issue or major mathematical defect was reported.

## Major comments

### 4.1 Add the minimal-balanced-collection literature

**Disposition: resolved with explicit scope.**

The binary-matrix section now identifies the columns of `B` as coalition
incidence vectors. Full column rank and a positive solution of `B w = 1`
produce a minimal balanced collection, while the cross-polytope normalization
adds the restriction `sum(w) < 2` so the basepoint weight is positive. The
manuscript cites Laplace Mermoud, Grabisch, and Sudhölter (2023) and explicitly
denies a new enumeration-algorithm claim.

The external minimal-balanced catalogue was not obtained or compared. That
comparison was recommended only as future corroboration, and the review agreed
that the independent orbit proof already supplies present completeness. The
public source and citation records preserve this limit.

### 4.2 Make the replay instructions follow the combined proof

**Disposition: resolved.**

The public workflow now separates four routes:

1. `code/verify_supplied.py` checks the shipped graph files, exact
   classification, all 217 certificates, strict schemas, semantic negative
   controls, and the 49-class catalogue without invoking `genbg`;
2. `code/verify_transport_simulators.py` independently reconstructs all 2,604
   exact common-`F` input-column simulations;
3. `code/verify-genbg-orbits.cpp` proves the shipped representative lists have
   disjoint coordinate-permutation orbits covering the independent ambient
   counts; and
4. `code/regenerate_inputs.py` is the optional nauty byte-regeneration route.

Normal and optimized supplied-input and transport runs pass. The orbit audit
passes, and optional `genbg` regeneration is byte-identical. Exact commands,
environment details, hashes, and boundaries are in
[REPLAY_RECEIPT.md](REPLAY_RECEIPT.md) and [ENVIRONMENT.txt](ENVIRONMENT.txt).

### 4.3 Distinguish rooted representatives from full geometric classes

**Disposition: resolved and the optional catalogue supplied.**

The abstract, enumeration discussion, and table now call 39 and 178 the valid
rooted or basepoint-normalized records. The table separately reports 12 and 37
full signed-coordinate classes, and 5 and 23 difficult full classes.

The deterministic public catalogue
`data/full-signed-cube-catalogue.json` maps every one of the 217 rooted records
exactly once, records each re-rooting/coordinate-permutation map, and transports
an exact certificate to canonical vertex order. The public verifier checks the
entire partition and every transport. The manuscript and assurance documents
still assign ambient completeness to the separate orbit audit, not to this
explanatory quotient.

### 4.4 Explain one certificate and the shared distribution

**Disposition: resolved.**

The manuscript now states that one distribution `F` is fixed across all twelve
extremal input columns and explains the supply--demand meaning of the selected
subsets. It gives the requested concrete difficult example: five-column-group
record 5605, support encodings `(0,16,35,15,61,62)`, all weights `1/3`, and
distribution mass `1/3` on masks 14, 25, and 37. Direct exact evaluation checks
84 facet-subset occurrences representing 31 distinct constraints.

The small-facet proof now contains the two missing cases: if a tested subset
meets the fixed small facet its coverage is one; otherwise coverage equals its
demand. A fresh public exact max-flow program independently reconstructs all
217 simulations across 2,604 input columns and verifies that the same `F` is
used for all twelve inputs of each measurement.

## Minor comments

### 1. State the nonnegative domain of the measurement weights

**Resolved.** The first measurement definition now declares
`f : {-1,1}^d -> [0,1]`.

### 2. Make consistency explicit in the rectangular binary system

**Resolved.** The binary-reduction lemma now requires that `B w = 1` be
consistent, have a unique solution, and that the solution and basepoint weight
be strictly positive. It no longer lets “full column rank” imply consistency.

### 3. Clarify the table's “infeasible” row

**Resolved.** The table separately reports 132,913 rejected prefilter records
and labels the zero row “Infeasible valid measurements.” It therefore no longer
suggests that rejected non-measurement supports are failed simulation cases.

### 4. Generalize the small-support lemma

**Resolved.** The lemma is now the general small-facet construction for any
measurement of `diamond_d`: a facet with at most `r-1` support points gives an
`r`-state simulation. The five-outcome/three-state statement is an immediate
specialization. The text credits Bencze--Frenkel and makes clear that affine
independence is unnecessary.

### 5. Improve software and schema provenance

**Resolved.** The generation record identifies nauty `genbg` 2.9.3. The public
environment file separates Python-standard-library verification, C++17 orbit
audit, and optional nauty regeneration. The supplied-input verifier enforces
exact manifest keys and counters, canonical rationals, graph6 length, ASCII
range, padding, bipartition, support structure, and catalogue transports.
Normal and optimized modes and eight semantic negative controls are retained.

### 6. Move hashes and replace draft declarations

**Resolved at the release-document layer.** The long in-paper hash table was
removed. Machine-readable receipts and the final package manifest carry exact
identities; final manifest generation remains correctly sequenced after the
mutable candidate is frozen. The byline is Anonymous. The author-contribution,
conflict-of-interest, funding, and AI statements now report only supplied facts
and explicitly avoid inferring a human mathematical contribution, personal
circumstances, affiliation, or award.

### 7. Add software citations, the published DOI, and a durable archive identifier

**Resolved, with provider state kept explicit.** The manuscript now cites the inspected commits of
`mda/sigdim` and `ChitambarLab/SignalingDimension.jl` and includes the published
Dall'Arno--Tosini--Buscemi DOI `10.26421/QIC24.5-6-2`. Version DOI
`10.5281/zenodo.23296390` is reserved in draft record `23296390`. The public
documents distinguish that reservation from later Zenodo publication,
resolution, asset parity, and canonical readback.

## Bounded structural-extension outcome

The publication-stage scout did not obtain a new uniform proof for the 28
difficult full classes. It proved only the necessary facet-transversal
restriction: every subset with positive simulator mass meets every coordinate
facet intersection. The revised manuscript includes this useful pruning
observation, attributes its basis to the imported criterion, and explains that
it does not replace the proper-subset inequalities or construct a common
distribution.

The attempted two-block construction fails because its hit probability is
`a + b - ab` while the criterion requires `a + b` whenever both sides carry
positive demand. No higher-dimensional bound, new enumeration method,
structural significance uplift, or performance benchmark is claimed.

## Assessment retained

The revisions improve exposition, attribution, and replayability but do not
inflate the contribution assessment. The supplied review's prospective
judgement remains 2-star overall with a credible 2-star/3-star boundary and no
present support for 4-star. This is an internal prospective assessment, not an
official REF result, peer-review acceptance decision, or correctness
probability.

