# Citation audit

Date: 2026-10-11. Scope: the v1.1.0-candidate manuscript and the sources that
carry its definitions, reductions, finite criterion, prior values, enumeration
context, and software provenance.

## Outcome

No inspected source was found to prove `sign.dim(diamond_6) = 3`. The evidence
supports a bounded statement that the exact value appears new within the
recorded search. It does not support worldwide or timeless priority language.

The main attribution boundary is clear:

- prior work owns the signaling-dimension framework, extremal-measurement
  reduction, finite criterion, small-facet construction, exact values through
  dimension five, symmetry-reduced computational strategy, and
  minimal-balanced-collection object;
- this release contributes the dimension-six upper bound over every primitive
  measurement, the resulting equality and endpoint classification, and an
  inspectable exact evidence chain for this instance.

## Record-level checks

| Citation | Checked use | Audit result |
|---|---|---|
| Bencze--Frenkel, arXiv:2610.05924v1 | Proposition 2.1; Theorems 2.2--2.3; interval at `d=6` | Full v1 read; supports criterion and bounds, not equality |
| Kai--Dall'Arno, arXiv:2407.17725 / QIC 24, 932--944 | Sections 4--6, Table 2, conclusion | Supports values through `d=5` and prior computational method |
| Dall'Arno--Tosini--Buscemi, QIC 24, 411--424 | Definitions and general LP framework | Published DOI and pagination checked; use 411--424, not inconsistent metadata value 441 |
| Laplace Mermoud--Grabisch--Sudhölter, DAM 341, 60--81 | Minimal balanced collections and enumeration | Supports the established object connection; does not prove simulation feasibility |
| Frenkel (2022) and foundational signaling papers | Historical/physical context | Context only; not used as a dimension-six proof |
| Doolittle--Chitambar (2021) | Separate channel-simulation certification methods | No inspected result immediately resolves the unrestricted cross-polytope model |
| McKay--Piperno (2014) | nauty/graph-isomorphism software provenance | Appropriate software-method citation |

## Corrections and publication treatment

- The Dall'Arno--Tosini--Buscemi published DOI is
  `10.26421/QIC24.5-6-2`, with pages 411--424.
- Kai--Dall'Arno is cited both by its published DOI
  `10.26421/QIC24.11-12-3` and its arXiv identifier where versioned access is
  useful.
- The restricted minimal-balanced-collection connection is cited in the
  manuscript. The additional cross-polytope condition `sum(w) < 2` is stated.
- Software references use inspected commits where available. The inaccessible
  `syu-shu/sigdim` repository is described as inaccessible, not as empty or
  irrelevant.
- Graph generation and verification dependencies are separated. Nauty is an
  optional regeneration dependency; it is not silently made a dependency of
  the economical supplied-input verification route.
- Version DOI `10.5281/zenodo.23296390` has been reserved in Zenodo draft record
  `23296390`. The reservation is recorded accurately and is not represented as
  a published or resolving DOI until provider publication and readback pass.

## Evidence not published as source material

The private supplied review, its raw search payloads, and private intake
archives are not copied into this public repository. Public documentation
summarizes their findings and binds the immutable archive identities in
[PROVENANCE.md](PROVENANCE.md). This avoids presenting review prose or search
results as CC0-covered original research content.

## Limits

The literature work was bounded and recent. Bencze--Frenkel appeared only days
before the review, so contemporaneous unindexed work is a live possibility. An
external minimal-balanced catalogue was available only on request and was not
obtained or compared. Search absence is therefore evidence about the inspected
record, not proof of historical absence.

