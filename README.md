# The six-dimensional cross-polytope has signaling dimension three

This is the public evidence package for the exact computer-assisted theorem

\[
\operatorname{sign.dim}(\diamond_6)=3,
\qquad
\diamond_6=\{v\in\mathbb R^6:\lVert v\rVert_1\le 1\}.
\]

Here signaling dimension means exact simulation of every transition matrix in
the full affine-effect model, with free shared randomness. Three classical
states means a trit, not three bits and not a three-dimensional simplex.

Version: **1.1.0-candidate**. Scholarly creator: **Anonymous**. This is an
unrefereed candidate release, not a proof-assistant formalization or a journal
publication. Version DOI `10.5281/zenodo.23296390` has been reserved; it is not
represented as published, resolving, or canonically read back yet.

## Result and scope

The new upper bound covers every primitive measurement of the
six-dimensional cross-polytope. Combining it with the previously known lower
bound gives equality. With prior exact values and the general lower bound, it
also gives the endpoint classification

\[
\operatorname{sign.dim}(\diamond_d)=3
\quad\Longleftrightarrow\quad
3\le d\le 6
\]

for positive integer dimensions. The exact value at dimension seven remains
between four and five.

The proof is finite but not merely numerical:

1. primitive measurements have support size at most seven;
2. supports of size at most five use the established small-facet construction;
3. after choosing and normalizing one support point, the remaining cases are
   binary matrices modulo coordinate and column permutations;
4. an orbit audit proves complete coverage of the supplied representative
   lists;
5. exact rational filtering finds every valid primitive measurement; and
6. exact rational distributions certify a three-state simulation in every
   retained case.

The general finite criterion, the small-facet construction, symmetry-reduced
enumeration, and generic linear-programming strategy are prior work. The
bounded contribution is the exact dimension-six value, its endpoint
consequence, and the replayable exact evidence for this instance.

## Evidence at a glance

| Object | Six-point support | Seven-point support | Total |
|---|---:|---:|---:|
| Basepoint-normalized representatives | 14,303 | 118,827 | 133,130 |
| Valid primitive-measurement records | 39 | 178 | 217 |
| Small-facet certificates | 24 | 63 | 87 |
| Other rational certificates | 15 | 115 | 130 |
| Labelled normalized supports covered | 6,054,006 | 63,602,770 | 69,656,776 |

The 217 records are not 217 inequivalent measurements under the full cube
symmetry group. A separate, reviewer-derived catalogue merges them into 49
full classes (12 six-point and 37 seven-point), and the 130 difficult records
into 28 full classes (5 and 23). That catalogue is an explanatory diagnostic
of the already verified corpus; completeness is established separately by the
orbit audit.

## Read and replay

- [paper.tex](paper.tex) is the authoritative mathematical source,
  [paper.pdf](paper.pdf) is the seven-page reader edition, and
  [paper.md](paper.md) is the accessible text edition.
- [AI_INDEX.md](AI_INDEX.md) gives a machine-oriented reading order and claim
  dependency graph.
- [CLAIMS.json](CLAIMS.json) records claim scope, evidence, and limitations.
- [ASSURANCE.md](ASSURANCE.md) explains what was proved, computed, reviewed,
  and not established.
- [REPLAY_RECEIPT.md](REPLAY_RECEIPT.md) gives the public commands and observed
  outputs for the final package.
- [ENVIRONMENT.txt](ENVIRONMENT.txt) records the tested execution environments.
- [REVIEW_RESPONSE.md](REVIEW_RESPONSE.md) disposes of all four major and seven
  minor comments in the supplied review.
- [SOURCES.md](SOURCES.md) and [CITATION_AUDIT.md](CITATION_AUDIT.md) map prior
  work to the claims for which it is used.

The economical verification route checks the shipped graph lists and exact
certificates, then runs the independent orbit audit. Regenerating the graph
lists with nauty `genbg` is a distinct reproducibility route and is not
required to trust the orbit coverage argument. Exact commands, hashes, and
results are recorded in the replay receipt rather than inferred from a passing
badge.

## Important limits

- This release proves one exact value and no improved all-dimensional bound.
- It supplies no proof-assistant verification and no human peer review.
- The 49-class catalogue does not independently enumerate the ambient universe.
- The necessary facet-transversal restriction recorded in the release is a
  direct consequence of the imported finite criterion, not a new structural
  simulation theorem; it does not replace the 130 rational certificates.
- The bounded literature search supports a narrow originality statement, not
  universal historical priority.
- Review and execution receipts establish their stated scopes only; running a
  program is not by itself evidence that the mathematical encoding is adequate.

## Licence

Original research prose, structured claims, generated research data, diagrams,
and public release records are dedicated to the public domain under
[CC0-1.0](LICENSE). Original executable code is licensed under the
[MIT License](LICENSE-CODE). [LICENSES.md](LICENSES.md) gives the component map
and exclusions. Cited papers, external software, reviews, and other third-party
materials retain their own terms and are not relicensed here.

