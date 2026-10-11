# Assurance statement

This package separates the mathematical argument, executable evidence,
assessment, and publication state. No one layer is promoted into another.

## Claim under assurance

For the six-dimensional cross-polytope in the full affine-effect model with
free shared randomness, every transition matrix is exactly simulable with
three classical states, while two do not suffice. Therefore

\[
\operatorname{sign.dim}(\diamond_6)=3.
\]

The quantifiers range over all measurements in the model, not a selected
family. The proof reduces arbitrary measurements to primitive measurements and
then exhausts every remaining finite support class.

## Proof-obligation map

1. **Primitive reduction and support bound.** Affine independence of augmented
   effect columns bounds primitive supports by seven. Convexity and classical
   outcome processing return the unrestricted measurement claim.
2. **Small supports.** A complementary coordinate-facet pair leaves one side
   with at most two support points. The established construction gives a
   distribution on subsets of size at most three; the candidate manuscript
   includes the direct two-case inequality check.
3. **Binary reduction.** After a cube sign symmetry sends a selected support
   point to the all-minus vertex, affine independence and the measurement
   equations become full column rank, consistency of `B w = 1`, and strictly
   positive weights including `w_0 = 2 - 1^T w`.
4. **Complete support coverage.** The shipped graph lists represent unordered
   nonzero binary-column sets meeting every row. The C++ audit applies all 720
   coordinate permutations, rejects duplicate orbits, and proves that orbit
   sizes sum to independent inclusion--exclusion counts.
5. **Exact classification.** Rational row reduction reclassifies all 133,130
   representatives and retains 39 six-point and 178 seven-point valid records.
6. **Exact feasibility.** Eighty-seven records use the explicit small-facet
   construction. The other 130 contain exact rational distributions. The
   verifier checks nonnegativity, unit mass, and every required facet-subset
   inequality.
7. **Lower bound.** The cited logarithmic lower bound gives three at dimension
   six. A four-outcome direct obstruction also supplies an instance-specific
   sanity check.

## Independent and complementary checks

The assurance chain deliberately addresses different failure modes:

- graph generation proposes the representative lists;
- the orbit audit proves list coverage without trusting generator completeness;
- the exact verifier removes the floating-point producer filter from the
  accepted theorem;
- the supplied review's separately written Cramer/max-flow checker reconstructed
  217 weight systems and 2,604 input-column transports without importing the
  submission verifier;
- a fresh public standard-library max-flow implementation independently
  reconstructs the same 2,604 common-`F` input-column simulations; and
- a separate full-symmetry diagnostic merges the verified records into 49
  explanatory classes.

These are not multiple independent end-to-end formal proofs. They share the
mathematical definitions and ordinary execution environment. Their scopes and
commands are recorded in [REPLAY_RECEIPT.md](REPLAY_RECEIPT.md).

## Numerical versus exact evidence

The original producer used floating-point screening to find candidate cases,
but the theorem does not trust those accept/reject decisions. The public exact
route reclassifies every supplied representative with rational arithmetic and
fails on a missing or extraneous valid record. Certificate masses and all
inequalities are checked exactly.

Timing figures are local reproducibility observations, not algorithmic
complexity results or comparative benchmarks.

## Extension boundary

A bounded structural scout derived one necessary restriction: every subset
given positive simulator mass must meet every coordinate-facet intersection.
It follows immediately by applying the imported criterion to a full facet,
whose demand and total available mass are both one. This permits a lossless
variable prefilter.

The restriction is insufficient: it checks full facets but not their proper
subsets, does not construct a common distribution, and does not replace the
130 difficult rational certificates. No uniform construction for the 28 hard
full-symmetry classes, new enumeration algorithm, higher-dimensional bound, or
speedup benchmark is claimed.

## Review and assessment boundary

The supplied review recommends minor revisions and reports no fatal concern or
major mathematical defect. It reproduced the finite proof on shipped inputs,
audited orbit coverage, and independently reconstructed the simulations. It
did not regenerate graph files because `genbg` was absent in that environment;
the frozen-source clean replay did regenerate them in a separate environment.

The prospective quality assessment is 2-star overall, with a credible
2-star/3-star boundary and no current support for 4-star. Review scores are
judgements about originality, significance, and rigour, not probabilities that
the theorem is correct.

No human peer review, journal acceptance, official REF assessment, or
proof-assistant verification is claimed.

## Publication boundary

Local files and passing checks do not establish a public release. Git commit,
immutable tag, CI, GitHub release, repository visibility, Zenodo publication,
asset parity, Evidence Press deployment, and canonical readback are distinct
facts to be recorded after they occur. DOI `10.5281/zenodo.23296390` is a real
reservation, but reservation alone is not Zenodo publication, DOI resolution,
asset parity, or canonical readback.

