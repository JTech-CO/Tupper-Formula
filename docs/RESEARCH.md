[English](RESEARCH.md) · [한국어](RESEARCH-KR.md)

# Research agenda: constructions before novelty claims

## What this version contributes

This repository combines an explicit coordinate contract, exact independent arithmetic paths, a constructive formula rasterizer, reproducible fixtures, bilingual exposition and a small interactive laboratory. This is an educational/reproducibility contribution. It does not establish that the mathematical identities or generated k values are new to the literature.

## Experiment A — Typography as controlled input

Hold H and the formula variant fixed. Vary only threshold, resolution or font selection. Measure binary disagreement, ink population, width, k digit count and human-readable symbol retention. A smaller integer is not necessarily a better or more self-referential formula. Preserve exact masks so renderer noise can be distinguished from decoding bugs.

The current renderer fixes its internal math font and offers H/threshold/variant controls. Font sweeps require a deliberate renderer change with provenance; they are not a current CLI flag.

## Experiment B — Restrict a formula language

Define a grammar before optimizing expression length: permitted constants, operators, recursion, summation, primitives and glyph renderer. Count the entire necessary representation, including a helper's definition and constants. Treat a longer decoder plus a shorter data integer as a tradeoff, not automatic compression.

A bounded enumerator or constraint solver could search short equivalent decoders. This version does not ship such a search engine. Proposed results should include the exact search space and proof/checker; a failed bounded search does not prove nonexistence outside the bound.

## Experiment C — Strong self-contained construction

A meaningful extension would implement both the expression body and a digit-printing mechanism, including every necessary constant and helper definition in the visible expression under an agreed language. The conceptual split `N = 2^L A + D` separates body data A from a digit dictionary D; it is an architectural sketch, not a completed universal solution.

Printing decimal digit r uses `floor(N/10^r) mod 10`, but choosing termination, layout, quoting/substitution rules and full self-description remains part of the construction. Citing a semantic recursion theorem does not make repeated numerical replacement converge. Compare against the primary constructions in [LITERATURE](LITERATURE.md) before claiming a first example.

## Experiment D — Exact sets rather than sampled pictures

For pixel predicates, constant-on-cell algebra makes one interior sample per cell sufficient after the algebra is established. For curves, a finite grid of matching samples is generally insufficient to prove equal planar regions. Any Bézier/glyph extension needs a boundary convention and a justification for the inside/outside computation. Distinguish set equality, equality except boundaries, raster equality and visual similarity.

## Result acceptance checklist

A research change should specify the question, baseline, assumptions, implemented versus proposed components, all external information, reproducible environment, exact artifacts, negative results and test limitations. Claims of novelty need a focused literature comparison. A successful generator run alone supports only its stated constructive output.
