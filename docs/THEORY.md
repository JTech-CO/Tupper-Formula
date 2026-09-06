[English](THEORY.md) · [한국어](THEORY-KR.md)

# The mathematical contract and its derivation

## 1. Object being represented

The graph is a **region satisfying an inequality**, not necessarily a single-valued curve `y=f(x)`. Fix positive integers W,H and binary pixels b(i,j). Mathematical coordinates increase rightward and upward. Stored text rows run top-to-bottom, so screen row `r` corresponds to `j=H-1-r`.

Set

$$
N=\sum_{i=0}^{W-1}\sum_{j=0}^{H-1}b_{i,j}2^{Hi+j},\quad k=HN.
$$

The map `(i,j) → Hi+j` is a bijection onto `0,...,WH-1`. Binary positional notation therefore makes the encoding injective **when W and H are fixed**. Zero padding requires dimensions; an integer alone does not encode all the metadata of an image.

## 2. Reading a bit

For integers N,n≥0,

$$
\operatorname{bit}(N,n)=\lfloor N/2^n\rfloor\bmod2.
$$

Write `N=a·2^(n+1)+b·2^n+c`, with b∈{0,1} and `0≤c<2^n`. Division and flooring produce `2a+b`, whose residue modulo 2 is b. This establishes the extraction identity without image recognition or approximation.

For a real z, use the mathematical convention `mod(z,2)=z-2 floor(z/2)`. Write `z=m+δ`, where m is an integer and `0≤δ<1`. The residue is either δ or 1+δ, so

$$
\lfloor\operatorname{mod}(z,2)\rfloor=\lfloor z\rfloor\bmod2.
$$

This is why the original arrangement of floor and mod is equivalent to an integer bit test.

## 3. Generalized Tupper predicate

For nonnegative x,y and positive integer H, define

$$
B_H(x,y)=\left\lfloor\operatorname{mod}\left(
\left\lfloor\frac yH\right\rfloor
2^{-H\lfloor x\rfloor-\operatorname{mod}(\lfloor y\rfloor,H)},2\right)\right\rfloor.
$$

Put `q=floor(y/H)`, `r=mod(floor(y),H)`, and `n=H floor(x)+r`. Then

$$
B_H(x,y)=\left\lfloor q/2^n\right\rfloor\bmod2\in\{0,1\}.
$$

The visible region is `1/2 < B_H(x,y)`. The threshold separates exactly 0 and 1; it is not a numerical tolerance.

## 4. Exactness over whole cells

For `0≤i<W`, `0≤j<H`, choose `0≤u,v<1` and set

$$
x=i+u,\qquad y=HN+j+v.
$$

Then `floor(y/H)=N`, `floor(x)=i` and `mod(floor(y),H)=j`. Consequently

$$
B_H(i+u,HN+j+v)=\operatorname{bit}(N,Hi+j)=b_{i,j}.
$$

The graph in `0≤x<W`, `k≤y<k+H` is exactly the union of half-open unit squares assigned 1. The right/top edge belongs to the next cell or lies outside the viewport. It is not an assertion of equality only at integer sample points. Pixel screenshots may draw shared edges differently; the data-level set convention remains explicit.

The proof motivates two executable checks: shifts for fast decoding, and `Fraction` evaluation of the displayed nested floor/mod for an independent extraction oracle. Both use the same documented coordinate convention; they are not independent formal proofs.

## 5. Every finite binary picture, and repeated occurrences

There are `2^(WH)` different W×H masks. The canonical integers `0≤N<2^(WH)` enumerate them. The 106×17 viewport thus stores 1,802 bits, not an unlimited-resolution photograph. A bit-packed buffer needs 226 bytes for those bits; a long decimal number is another representation, not a compression miracle.

For any integer t≥0,

$$
N'=N+t2^{WH},\qquad k'=H(N+t2^{WH})
$$

has the same low WH bits. The same finite image therefore reappears. `decode` accepts these offsets; canonical manifests re-encode only the visible mask and discard invisible high bits. The first H-strip after an unaligned offset may cross image indices: the simple single-mask decoder consequently requires `k % H == 0`.

## 6. Worked 3×5 example

The top-to-bottom rows `010 / 101 / 111 / 101 / 101` have column values 15,20,15 when read bottom-up:

$$
N=15+20\cdot2^5+15\cdot2^{10}=16015,\qquad k=5N=80075.
$$

At `(i,j)=(1,4)`, the bit index is 9 and `floor(16015/512) mod 2 = 1`. At `(1,3)`, the index is 8 and `floor(16015/256) mod 2 = 0`. The supplied asymmetric fixture detects orientation errors that symmetric letters can hide.

## 7. A constructive self-image, not a semantic fixed point

`derive` first fixes H and a predicate variant, typesets that **same H** in the inequality, resizes to a height-H binary mask, and encodes it. Its own displayed formula is therefore found at the constructed external k. The bitmap does not include that k's digits. This is a constructive instance of the universal decoder, not a claim that the equation recognizes itself or that a new theorem was discovered.

Font choice, antialiasing, resizing and thresholding belong to the presentation pipeline. Exact equality begins at the finalized binary mask. Re-running typography need not reproduce identical pixels across systems; decoding the saved mask does.

## 8. Beyond binary masks

For color indices `0≤c_l<C`, define `N_C = Σ c_l C^l`; recover `c_l=floor(N_C/C^l) mod C`. Our `radix.py` flattens a known shape with the last axis varying fastest. A palette and shape remain external. This is a simple positional-number exercise, **not an implementation of the entire multidimensional graphing construction in Somu–Mishra**.

Stronger self-graphing problems seek `Gr(s)=Gl(s)` for an expression string s, with a fixed language, glyph renderer and equality convention. Kleene-style semantic fixed points concern equality of program behavior, not the numeric identity `e=f(e)` or convergence of iterative bitmap replacement. These distinctions and primary sources are documented in [LITERATURE](LITERATURE.md).
