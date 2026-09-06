[English](LITERATURE.md) · [한국어](LITERATURE-KR.md)

# Literature, attribution and claim boundaries

This is a focused source map, not an exhaustive historical-priority survey. Sources were checked for the repository on **2026-09-06**. The research note does not claim that every self-referential formula is known or that the listed authors are necessarily the first for every variation.

## R1 — Tupper (2001)

Jeff Tupper, *Reliable Two-Dimensional Graphing Methods for Mathematical Formulae with Two Free Variables*, SIGGRAPH 2001, pp. 77–86. [Author-hosted paper](https://www.dgp.toronto.edu/~mooncake/papers/SIGGRAPH2001_Tupper.pdf). DOI: `10.1145/383259.383267`.

The relevant example is Figure 13 (PDF page 7, printed p.83), within a broader paper about reliable graphing. Its inequality enumerates binary grid images; the paper also notes possible changes to the grid size. The famous image occupies a 106×17 window and uses the printed 543-digit k. `examples/historical/k.txt` records that integer; the reconstructed mask has 334 ink cells. The population is our recomputation, not an additional claim quoted from the paper.

**Boundary:** the display window carries information through k. Plotting the finite window is not the same as a globally self-contained equation that prints every necessary constant.

## R2 — Trávník (2011, later updates)

Jakub Trávník, [*Self Referential Formula in Math*](https://jtra.cz/stuff/essays/math-self-reference/index.html). Author's notes and implementation.

This construction separates fixed expression graphics from the digits of the large integer and prints both. The author gives a 12,876-digit constant and a reproduction program. The page's later notes also credit an earlier self-plotting construction by Tupper; this repository therefore does **not** claim that Trávník introduced the first fully self-contained example.

**Boundary:** the implementation is discussed, not copied or executed here. A user's newly chosen Tupper k is not automatically an equivalent self-contained construction.

## R3 / R11 — Trávník (2019)

[Overview](https://jtra.cz/stuff/essays/math-self-reference-smooth/index.html) and [detailed explanation](https://jtra.cz/stuff/essays/math-self-reference-smooth/detailed-explanation.html).

The later construction uses Bézier-based glyph outlines and inside/outside evaluation rather than a fixed binary pixel grid. Separating the expression body from a digit-printing mechanism remains central. "Smooth" concerns the glyph representation; it does not remove every boundary/limit issue in the membership predicate.

**Boundary:** the repository's SVG is a vector container for exact **square pixels**. It is not a recreation of this smooth-curve equation. No 50,000-digit self-contained example is claimed as implemented.

## R4 — Somu and Mishra (2021 / 2023)

Sai Teja Somu and Vidyanshu Mishra, [*On a Generalization of Tupper's Formula for m Colours and n Dimensions*](https://arxiv.org/abs/2109.11013), arXiv:2109.11013; *Discrete Mathematics*, article 113600 (2023). DOI: `10.1016/j.disc.2023.113600`.

The paper constructs extensions for colored and multidimensional arrays. It supports treating Tupper's mechanism as an array-representation method beyond monochrome 2D.

**Boundary:** `radix.py` implements our elementary base-C packing exercise with an explicit shape. It is not a port, validation or full reproduction of the paper's n-variable predicates.

## R5 — Alexander (2025)

Samuel Allen Alexander, [*Self-graphing equations*](https://arxiv.org/html/2504.00006v1), arXiv:2504.00006, version consulted dated 18 March 2025.

The framework distinguishes mathematical graphing from glyph rendering and studies sufficient conditions for their fixed-point equality. Expression language and permitted graphing operations matter. Sufficient existence results in an expressive formalism do not promise a short elementary formula under arbitrary operator restrictions.

**Boundary:** no proof assistant formalization, implementation of that theorem's complete construction, or unrestricted shortest-formula search is included here.

## Engineering documentation

[R6: Python integer conversion limits](https://docs.python.org/3/library/stdtypes.html#integer-string-conversion-length-limitation) explains why large decimal formatting needs care. The package uses bounded nine-digit chunks and does not disable the interpreter's global protection.

[R7: MathML](https://developer.mozilla.org/en-US/docs/Web/MathML) and [R8: BigInt](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/BigInt) document the browser technologies. [R9: Matplotlib Mathtext](https://matplotlib.org/stable/users/explain/text/mathtext.html) documents the optional mathematical typesetter. [R10: GitHub Pages publishing sources](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) covers deployment.

References are also available in [`data/references.json`](../data/references.json) and [`references.bib`](../references.bib). Internet sources are not vendored; their continued availability is not guaranteed. All theoretical extensions are attributed, and numerical experiment counts are explicitly repository measurements.
