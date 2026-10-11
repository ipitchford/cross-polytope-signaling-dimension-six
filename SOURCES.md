# Sources and claim map

This is a source-to-claim map, not a bibliography dump. The publication intake
read the load-bearing parts of the closest primary sources and used the
remaining references for definitions, context, or software provenance. A
bounded negative search is not a universal novelty certificate.

## Load-bearing mathematical sources

### Bencze and Frenkel (2026)

T. Bencze and P. E. Frenkel, “On the signaling dimension of the
cross-polytope,” arXiv:2610.05924v1 (2026),
<https://arxiv.org/abs/2610.05924v1>.

The full v1 text was inspected, including Proposition 2.1 and Theorems 2.2 and
2.3 with their proofs. This source supplies:

- the finite simulability criterion used for every certificate;
- the general lower and upper bounds;
- the lower bound three at dimension six;
- the small-facet construction; and
- the fact that the prior bounds leave dimension six at either three or four.

It does not prove equality at dimension six. The facet-transversal restriction
in this package is explicitly treated as a direct consequence of its
Proposition 2.1, not as a new external theorem.

### Kai and Dall'Arno (2024)

S. Kai and M. Dall'Arno, “The signaling dimension of two-dimensional and
polytopic systems,” *Quantum Information and Computation* 24 (11--12),
932--944 (2024), <https://doi.org/10.26421/QIC24.11-12-3>;
arXiv:2407.17725.

Sections 4--6, Table 2, and the conclusion were inspected. This source supplies
the exact cross-polytope values through affine dimension five and the earlier
symmetry-reduced computational strategy. It also establishes that the generic
enumeration/decomposition approach is not new here.

### Dall'Arno, Tosini, and Buscemi (2024)

M. Dall'Arno, A. Tosini, and F. Buscemi, “The signaling dimension in
generalized probabilistic theories,” *Quantum Information and Computation* 24
(5--6), 411--424 (2024), <https://doi.org/10.26421/QIC24.5-6-2>;
arXiv:2311.13103.

This source supplies the general definitions, extremal-measurement reduction,
and linear-programming framework. Publisher pagination is 411--424; an
inconsistent arXiv metadata page value was not used to overwrite it.

## Balanced-collection connection

D. Laplace Mermoud, M. Grabisch, and P. Sudhölter, “Minimal balanced
collections and their application to core stability and other topics of game
theory,” *Discrete Applied Mathematics* 341, 60--81 (2023),
<https://doi.org/10.1016/j.dam.2023.07.025>; accessible manuscript
arXiv:2507.05898v1.

Sections 2.3 and 4, together with the balanced-collection/hypergraph
correspondence, were inspected. Writing binary columns as coalition indicators
turns `B w = 1` with positive unique `w` into a restricted minimal balanced
collection. The cross-polytope problem additionally requires
`sum(w) < 2` so the normalized basepoint has positive weight.

This is prior art for the enumeration object. It does not establish the
three-state simulation inequalities. The external enumerated catalogue was not
obtained or compared, so no catalogue-parity claim is made.

## Foundational and contextual sources

- P. E. Frenkel, “Classical simulations of communication channels,” *Quantum*
  6, 751 (2022), <https://doi.org/10.22331/q-2022-06-29-751>. Used for earlier
  channel-simulation results and the dimension-three context; no dimension-six
  shortcut was found in the inspected material.
- P. E. Frenkel and M. Weiner, “Classical information storage in an n-level
  quantum system,” *Communications in Mathematical Physics* 340, 563--574
  (2015), <https://doi.org/10.1007/s00220-015-2463-0>. Foundational context for
  classical simulation with shared randomness.
- M. Dall'Arno, S. Brandsen, A. Tosini, F. Buscemi, and V. Vedral,
  “No-hypersignaling principle,” *Physical Review Letters* 119, 020401 (2017),
  <https://doi.org/10.1103/PhysRevLett.119.020401>. Foundational physical
  motivation.
- B. Doolittle and E. Chitambar, “Certifying the classical simulation cost of a
  quantum channel,” *Physical Review Research* 3, 043073 (2021),
  <https://doi.org/10.1103/PhysRevResearch.3.043073>. Separate channel-family
  certification tools; no theorem there was found to settle every primitive
  measurement in this cross-polytope model.
- B. D. McKay and A. Piperno, “Practical graph isomorphism, II,” *Journal of
  Symbolic Computation* 60, 94--112 (2014),
  <https://doi.org/10.1016/j.jsc.2013.09.003>. Provenance for nauty/`genbg`.

## Inspected software

- M. Dall'Arno, `sigdim`, Codeberg commit
  `24f7eb387703fadb0c4d79c831b9def2314fe198`,
  <https://codeberg.org/mda/sigdim>. The inspected files support the account of
  prior extremal-measurement and LP software; no dimension-six cross-polytope
  result appeared in that inspected scope.
- Chitambar Lab, `SignalingDimension.jl`, GitHub commit
  `5ec10bda0b480e0f811595210d33aad99eba4e0a`,
  <https://github.com/ChitambarLab/SignalingDimension.jl>. The inspected package
  concerns channel certification and signaling-polytope inequalities, not this
  exhaustive cross-polytope computation.
- The separately cited `syu-shu/sigdim` GitHub repository returned HTTP 404
  during review. Its contents were not inspected, and that missing access is not
  evidence about what it may previously have contained.

## Search boundary

The review used exact-title, identifier, terminology-variant, author,
repository, and code searches on 11 October 2026. No inspected source proved the
new dimension-six equality. The search cannot exclude private or unpublished
work, deleted or inaccessible repositories, indexing gaps, contemporaneous
work, or an equivalent theorem expressed in different language. No
unsolicited outreach or paid/subscription account change was performed.

