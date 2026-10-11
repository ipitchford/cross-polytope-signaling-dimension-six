**Keywords:** signaling dimension; cross-polytope; generalized probabilistic theories; exact computation; symmetry reduction; rational certificate.

# Introduction

The signaling dimension of a physical state space is its exact classical simulation cost: the smallest classical alphabet that reproduces every transition matrix obtainable from the state space when shared randomness is free. The notion originates in the study of hypersignaling and classical simulation of quantum systems . It depends on the whole correlation set rather than on one discrimination or coding task.

Exact values outside classical and quantum state spaces are scarce. Kai and Dall’Arno developed an algorithm for rational polytopes and computed the cross-polytope through affine dimension five, obtaining the value three in dimensions three, four and five . Their general-purpose calculation stopped there. Dall’Arno, Tosini and Buscemi gave the underlying extremal-measurement and linear-programming framework together with a public implementation ; Doolittle and Chitambar developed separate signaling-polytope tools for certifying channel simulation costs . No dimension-six cross-polytope result was found in the inspected versions of these implementations ; this is not an exhaustive absence claim. Bencze and Frenkel subsequently proved that the $`d`$-dimensional cross-polytope $`\diamond_d`$ satisfies
``` math
\begin{equation}
\label{eq:seed-bounds}
 \left\lceil\log_2(d+2)\right\rceil
 \leq \operatorname{sign.dim}(\diamond_d)
 \leq \left\lfloor\frac{d+3}{2}\right\rfloor
\end{equation}
```
and gave a finite criterion tailored to its primitive measurements . At $`d=6`$, the two bounds are three and four.

<div id="thm:main" class="theorem">

**Theorem 1**. *The signaling dimension of the six-dimensional cross-polytope is
``` math
\operatorname{sign.dim}(\diamond_6)=3.
```*

</div>

Together with the known values in dimensions three through five and the lower bound in <a href="#eq:seed-bounds" data-reference-type="eqref" data-reference="eq:seed-bounds">[eq:seed-bounds]</a>, Theorem <a href="#thm:main" data-reference-type="ref" data-reference="thm:main">1</a> identifies the complete three-state range:

<div id="cor:boundary" class="corollary">

**Corollary 2**. *For positive integers $`d`$,
``` math
\operatorname{sign.dim}(\diamond_d)=3 \quad\Longleftrightarrow\quad 3\leq d\leq6.
```*

</div>

<div class="proof">

*Proof.* The values for $`3\leq d\leq5`$ are known, and Theorem <a href="#thm:main" data-reference-type="ref" data-reference="thm:main">1</a> supplies $`d=6`$. The one- and two-dimensional cross-polytopes have signaling dimension at most two . For $`d\geq7`$, the lower bound in <a href="#eq:seed-bounds" data-reference-type="eqref" data-reference="eq:seed-bounds">[eq:seed-bounds]</a> is at least four. ◻

</div>

The upper bound in Theorem <a href="#thm:main" data-reference-type="ref" data-reference="thm:main">1</a> is computer-assisted. The reduction to a finite set is proved below. Every surviving linear feasibility instance has a saved rational solution, so the scientific certificate does not depend on floating-point optimization. Two replay programs check different possible failure modes. One reclassifies all supports and verifies every inequality using exact fractions. The other avoids the graph-generation software and proves by orbit sizes that the supplied representatives are unique and complete.

# Measurements and the finite criterion

Write
``` math
\diamond_d=\left\{v\in\mathbb R^d:\sum_{i=1}^d|v_i|\leq1\right\}.
```
An extremal effect of $`\diamond_d`$ is indexed by a hypercube vertex $`x\in\{-1,1\}^d`$ and has the form
``` math
e_x(v)=\frac{1+x\cdot v}{2}.
```
Thus a nonzero weight function $`f:\{-1,1\}^d\to[0,1]`$ represents a measurement precisely when
``` math
\begin{equation}
\label{eq:measurement}
 \sum_{x:x_i=1} f(x)=\sum_{x:x_i=-1}f(x)=1
 \qquad(1\leq i\leq d).
\end{equation}
```
Equivalently, $`\sum_x f(x)=2`$ and $`\sum_x f(x)x=0`$. The measurement is primitive precisely when $`\operatorname{supp}f`$ is affinely independent . It therefore has at most $`d+1`$ support points.

We use the following specialization of the finite simulability criterion in . For a finite set $`U`$, let $`\binom{U}{\leq r}`$ denote its subsets of size at most $`r`$.

<div id="prop:criterion" class="proposition">

**Proposition 3** (Bencze–Frenkel criterion). *Let $`f:\{-1,1\}^d\to[0,1]`$ satisfy <a href="#eq:measurement" data-reference-type="eqref" data-reference="eq:measurement">[eq:measurement]</a>, and set $`U=\operatorname{supp}f`$. Its transition matrix is simulable by an $`r`$-vertex simplex if and only if there is a probability distribution $`F`$ on $`\binom{U}{\leq r}`$ such that
``` math
\begin{equation}
\label{eq:criterion}
 \sum_{x\in S}f(x)
 \leq \sum_{X:X\cap S\ne\varnothing}F(X)
\end{equation}
```
whenever $`S\subseteq U`$ lies in a coordinate facet of the hypercube.*

</div>

The same distribution $`F`$ must work for all $`2d`$ input vertices, not a separate distribution for each input. The supply–demand argument underlying the criterion then supplies an input-dependent coupling with this common marginal. Shared randomness draws a set $`X`$; the sender communicates one of its at most $`r`$ outcomes. Thus three states mean a three-symbol alphabet, not three bits. The empty subset may be omitted: moving its mass to a singleton only increases the right-hand sides of <a href="#eq:criterion" data-reference-type="eqref" data-reference="eq:criterion">[eq:criterion]</a>.

Taking $`S`$ to be an entire coordinate-facet intersection gives demand one. Consequently every $`X`$ with $`F(X)>0`$ must meet both sides of every coordinate. This necessary transversal condition can prune candidate variables, but does not replace the inequalities for proper subsets of facets.

<div id="lem:small" class="lemma">

**Lemma 4** (Small-facet construction). *Let $`f`$ be any measurement of $`\diamond_d`$. If a coordinate facet contains at most $`r-1`$ points of its support, it is simulable by an $`r`$-vertex simplex. In particular every measurement with at most five outcomes is three-state simulable.*

</div>

<div class="proof">

*Proof.* Choose such a facet $`H`$ and put $`L=H\cap U`$. The construction in the proof of assigns
``` math
F(L\cup\{x\})=f(x)\qquad(x\in U\setminus H)
```
and zero elsewhere. The opposite facet has total weight one, so $`F`$ is a probability distribution supported on sets of size at most $`r`$. If $`S\cap L\ne\varnothing`$, its coverage probability is one, which bounds its facet demand. Otherwise its coverage probability is exactly $`\sum_{x\in S}f(x)`$. These two cases prove <a href="#eq:criterion" data-reference-type="eqref" data-reference="eq:criterion">[eq:criterion]</a>. For at most five outcomes, either side of some coordinate contains at most two support points. This is the existing Bencze–Frenkel construction, restated here; neither affine independence nor a new structural theorem is required. ◻

</div>

# Binary-matrix reduction

It remains to consider primitive supports of size six or seven. The next lemma turns their enumeration into a small bicoloured-graph problem.

<div id="lem:binary" class="lemma">

**Lemma 5**. *Choose $`x_0\in U`$ and apply coordinate sign changes so that $`x_0=(-1,\ldots,-1)`$. For the other points write
``` math
x_j=-\boldsymbol 1+2b_j,
 \qquad b_j\in\{0,1\}^6\setminus\{0\},
```
and let $`B`$ be the matrix with columns $`b_j`$. Then $`U`$ is affinely independent if and only if $`B`$ has full column rank. It supports a primitive measurement if and only if the system
``` math
\begin{equation}
\label{eq:Bweights}
 Bw=\boldsymbol 1
\end{equation}
```
is consistent, has a unique solution, and that solution satisfies
``` math
w_j>0\quad\text{for all }j,
 \qquad w_0:=2-\boldsymbol 1^{\mathsf T}w>0.
```
The measurement weights are $`(w_0,w_1,\ldots)`$.*

</div>

<div class="proof">

*Proof.* Represent the affine function $`e_x`$ by the column $`(1,x)`$. Subtracting the $`x_0`$ column from each other column replaces it by $`(0,2b_j)`$, proving the rank assertion. If $`w_0`$ is the weight at $`x_0`$, the constant part of the measurement equation gives $`w_0+\sum_jw_j=2`$. Its six linear parts become
``` math
-\left(w_0+\sum_jw_j\right)\boldsymbol 1+2Bw=0,
```
which is exactly <a href="#eq:Bweights" data-reference-type="eqref" data-reference="eq:Bweights">[eq:Bweights]</a>. Full column rank makes a consistent solution unique. Strict positivity is precisely the condition that all listed points belong to the support. ◻

</div>

Permuting coordinates permutes the rows of $`B`$, while relabeling $`U\setminus\{x_0\}`$ permutes its columns. A matrix with distinct nonzero columns is the incidence matrix of a bicoloured graph. No valid matrix has a zero row, because <a href="#eq:Bweights" data-reference-type="eqref" data-reference="eq:Bweights">[eq:Bweights]</a> has right-hand side $`\boldsymbol1`$. Consequently, bicoloured graph isomorphism gives a lossless prefilter for the remaining supports. Choosing a different $`x_0`$ can duplicate an orbit, but cannot omit one. Accordingly the 217 retained records below are rooted records, not full signed-coordinate symmetry classes.

There is also a standard cooperative-game interpretation. The columns of $`B`$ are incidence vectors of coalitions on six players. Full column rank and a positive solution of $`Bw=\boldsymbol1`$ characterize a minimal balanced collection. Our additional condition $`\sum_jw_j<2`$ ensures positive weight at the normalized vertex. Enumeration of minimal balanced collections is established prior work ; our calculation does not claim a new enumeration algorithm. The external catalogue is available on request, and no direct catalogue-to-catalogue comparison is claimed here.

The program `genbg` from nauty 2.9.3 generated the prefilter classes. Its output was audited independently. For $`k\in\{5,6\}`$, the number of unordered $`k`$-subsets of distinct nonzero binary columns that meet every row is
``` math
\begin{equation}
\label{eq:labelled-count}
 N_k=\sum_{j=0}^6(-1)^j\binom6j
              \binom{2^{6-j}-1}{k}.
\end{equation}
```
An independent C++ program applies every one of the $`6!=720`$ row permutations to each representative and sorts its columns. It found distinct canonical keys and summed the resulting orbit sizes to $`N_k`$ in both cases. Thus the supplied class lists are complete without assuming that `genbg` itself returned a complete list.

<div id="tab:counts">

|                                     | six-point support | seven-point support |
|:------------------------------------|------------------:|--------------------:|
| Binary columns $`k`$                |                 5 |                   6 |
| Labelled supports $`N_k`$           |         6,054,006 |          63,602,770 |
| Coordinate-permutation classes      |            14,303 |             118,827 |
| Rejected prefilter records          |            14,264 |             118,649 |
| Valid rooted primitive measurements |                39 |                 178 |
| Small-facet certificates            |                24 |                  63 |
| Exact criterion certificates        |                15 |                 115 |
| Infeasible valid measurements       |                 0 |                   0 |
| Full cube-symmetry classes          |                12 |                  37 |
| Difficult full classes              |                 5 |                  23 |

Exact rooted support enumeration and certificates. Rejected prefilter records are not valid measurements.

</div>

# Exact certificate computation

Each graph representative was decoded into $`B`$. Equation <a href="#eq:Bweights" data-reference-type="eqref" data-reference="eq:Bweights">[eq:Bweights]</a>, its consistency, rank and positivity were first used as a floating-point producer prefilter. This left the 217 candidate valid classes in Table <a href="#tab:counts" data-reference-type="ref" data-reference="tab:counts">1</a>. The independent verifier then reclassified every one of the 133,130 representatives using rational arithmetic, detected no omitted valid class and obtained the same 217 classes. Thus completeness does not depend on the producer’s numerical gate. For 87 retained classes, some coordinate facet contains at most two support points, and the distribution in Lemma <a href="#lem:small" data-reference-type="ref" data-reference="lem:small">4</a> supplies a three-state simulation.

For each of the other 130 classes, all nonempty subsets $`X\subseteq U`$ with $`|X|\leq3`$ were used as distribution variables. The constraints comprise $`F(X)\geq0`$, $`\sum_XF(X)=1`$, and <a href="#eq:criterion" data-reference-type="eqref" data-reference="eq:criterion">[eq:criterion]</a> for every nonempty subset of each of the twelve coordinate-facet intersections. Duplicate subsets were removed. Exact linear rational arithmetic found every instance feasible. The evidence manifest stores the nonzero values of one rational $`F`$ for each class.

For a concrete example, record 5605 in the five-column group uses the binary support encodings $`(0,16,35,15,61,62)`$ in that order: bit $`i`$ is coordinate $`i+1`$, and a zero bit denotes sign $`-1`$. Every outcome has weight $`1/3`$. The distribution gives mass $`1/3`$ to each of
``` math
\{1,2,3\},\qquad\{0,3,4\},\qquad\{0,2,5\}.
```
These are subset masks $`14,25,37`$. Direct rational evaluation checks all 84 nonempty facet-subset occurrences (31 distinct constraints). The geometry is essential: this distribution is not asserted to work on arbitrary supports. The same shared draw is used for all twelve input columns.

Re-rooting every valid support at each of its vertices and minimizing over all coordinate permutations gives 12 and 37 full signed-coordinate classes. Of these, 5 and 23 are difficult. The catalogue maps every rooted record to its full class and transports a rational simulator to canonical vertex order. This reduces the explanatory catalogue to 28 difficult classes, without replacing the exhaustive rooted coverage argument.

The independent verifier does not invoke the feasibility solver. Its default mode reads the supplied class files, decodes every record separately, and uses a local rational row-reduction implementation to recompute <a href="#eq:Bweights" data-reference-type="eqref" data-reference="eq:Bweights">[eq:Bweights]</a>. It fails if any valid class is absent from the manifest. For every saved distribution it checks nonnegativity, total mass one, and every inequality <a href="#eq:criterion" data-reference-type="eqref" data-reference="eq:criterion">[eq:criterion]</a> by integer and rational arithmetic. This replay found the same 39 and 178 valid classes and verified all 217 certificates. Regeneration with nauty is a separate optional provenance check; it is not a prerequisite for this supplied-input replay. Completeness of the supplied files is established separately by the orbit-size audit.

<div class="proof">

*Proof of Theorem <a href="#thm:main" data-reference-type="ref" data-reference="thm:main">1</a>.* It suffices to simulate every primitive measurement . Such a measurement has at most seven outcomes. Lemma <a href="#lem:small" data-reference-type="ref" data-reference="lem:small">4</a> handles supports of size at most five. For sizes six and seven, Lemma <a href="#lem:binary" data-reference-type="ref" data-reference="lem:binary">5</a> and the orbit audit show that the class lists in Table <a href="#tab:counts" data-reference-type="ref" data-reference="tab:counts">1</a> contain a representative of every possible support. Exact filtering retains every possible primitive measurement, and the rational certificates verify Proposition <a href="#prop:criterion" data-reference-type="ref" data-reference="prop:criterion">3</a> with $`r=3`$ for each retained class. Therefore $`\operatorname{sign.dim}(\diamond_6)\leq3`$.

The lower bound in <a href="#eq:seed-bounds" data-reference-type="eqref" data-reference="eq:seed-bounds">[eq:seed-bounds]</a> gives $`\operatorname{sign.dim}(\diamond_6)\geq\lceil\log_2 8\rceil=3`$. Hence equality holds. ◻

</div>

# Reproducibility and limitations

The evidence archive contains the two graph-class files, the 217 rational certificates, the producer, the exact verifier, the independent orbit audit, and hashes for every scientific input. The package’s `MANIFEST.json` binds final file sizes and SHA-256 digests; the AI index and verification receipt identify the replay commands and their scope. Historical receipts remain distinct from checks of the revised publication package.

The result is exact but computer-assisted. Its trust base includes the stated source theorem, ordinary compiler and interpreter correctness, and inspection of short replay programs. The orbit audit removes nauty completeness from the trust base, although nauty remains the source of the candidate representatives. The rational replay removes Z3, NumPy and SymPy from the certificate trust base. A future structural proof could explain uniformly why the 28 difficult full classes (130 rooted records) are feasible and would be preferable to a class-by-class certificate. Different internal implementations remain producer-side checking, not unaffiliated reproduction or formal verification.

The generic strategy of enumerating extremal measurements and solving finite classical-simulation linear programs is prior work . The contribution here is the exact dimension-six value, its three-state boundary consequence, and an assurance chain that separately audits orbit coverage and rational feasibility. The certificate instances themselves are small; the main computational burden is complete support coverage. No new general signaling-dimension algorithm is claimed.

The theorem resolves only $`d=6`$. It does not improve the general bounds in <a href="#eq:seed-bounds" data-reference-type="eqref" data-reference="eq:seed-bounds">[eq:seed-bounds]</a>, nor does the computation determine the next open dimensions.

## Data and code availability

All source, class lists, exact certificates, verification receipts and replay instructions are included in the accompanying evidence archive. No external dataset is used. The versioned archive identifier is <https://doi.org/10.5281/zenodo.23296390>. The source repository is <https://github.com/ipitchford/cross-polytope-signaling-dimension-six>.

## Ethics declaration

The work uses no human participants, animals, personal data or sensitive data. No ethics approval was required.

## Author contributions

The scholarly attribution is Anonymous. OpenAI Codex assisted with recorded searches, computation, checking and drafting. Publication authority and account ownership do not establish a human mathematical contribution; none is inferred.

## Conflict of interest

No competing interests were reported in the supplied materials. This is not independent verification of an anonymous creator’s personal circumstances.

## Funding

No external funding was reported in the supplied materials. No institutional affiliation or funding award is asserted.

## AI disclosure

OpenAI Codex assisted with literature screening, program construction, computer-assisted proof search, exact replay and manuscript drafting. All mathematical claims are intended to be assessed from the cited sources and the archived certificates rather than from model authority.

<div class="thebibliography">

99

D. Laplace Mermoud, M. Grabisch and P. Sudhölter, “Minimal balanced collections and their application to core stability and other topics of game theory,” *Discrete Applied Mathematics* **341** (2023), 60–81. <https://doi.org/10.1016/j.dam.2023.07.025>. Accepted text: arXiv:2507.05898v1.

M. Dall’Arno, *sigdim*, software, inspected commit:\
. <https://codeberg.org/mda/sigdim>.

Chitambar Lab, *SignalingDimension.jl*, software, inspected commit:\
. <https://github.com/ChitambarLab/SignalingDimension.jl>.

T. Bencze and P. E. Frenkel, “On the signaling dimension of the cross-polytope,” arXiv:2610.05924v1 (2026). <https://arxiv.org/abs/2610.05924v1>.

S. Kai and M. Dall’Arno, “The signaling dimension of two-dimensional and polytopic systems,” *Quantum Information and Computation* **24** (2024), 932–944. <https://doi.org/10.26421/QIC24.11-12-3>.

M. Dall’Arno, A. Tosini and F. Buscemi, “The signaling dimension in generalized probabilistic theories,” *Quantum Information and Computation* **24** (2024), 411–424. <https://doi.org/10.26421/QIC24.5-6-2>. <https://arxiv.org/abs/2311.13103>.

P. E. Frenkel, “Classical simulations of communication channels,” *Quantum* **6** (2022), 751. <https://doi.org/10.22331/q-2022-06-29-751>.

P. E. Frenkel and M. Weiner, “Classical information storage in an $`n`$-level quantum system,” *Communications in Mathematical Physics* **340** (2015), 563–574. <https://doi.org/10.1007/s00220-015-2463-0>.

M. Dall’Arno, S. Brandsen, A. Tosini, F. Buscemi and V. Vedral, “No-hypersignaling principle,” *Physical Review Letters* **119** (2017), 020401. <https://doi.org/10.1103/PhysRevLett.119.020401>.

B. Doolittle and E. Chitambar, “Certifying the classical simulation cost of a quantum channel,” *Physical Review Research* **3** (2021), 043073.\
<https://doi.org/10.1103/PhysRevResearch.3.043073>.

B. D. McKay and A. Piperno, “Practical graph isomorphism, II,” *Journal of Symbolic Computation* **60** (2014), 94–112. <https://doi.org/10.1016/j.jsc.2013.09.003>.

</div>
