[English](PYTHON-GUIDE.md) · [한국어](PYTHON-GUIDE-KR.md)

# Python package, CLI and interchange

## Installation and environments

Use Python 3.11 or later in a virtual environment. `python -m pip install -e .` installs the dependency-free exact core; `python -m pip install -e ".[render]"` adds Pillow and Matplotlib. No system TeX executable, cloud model, image-recognition API or network service is used by the package.

For the recorded renderer versions, install `python -m pip install -r requirements-render.txt`. Dependency installation itself may access package indexes. Pinning versions improves reproducibility but does not guarantee identical antialiasing across operating systems.

## Construct a self-image

```sh
python -m tupper_formula derive --height 32 --variant tupper -o output/self-h32
python -m tupper_formula verify output/self-h32/experiment.json --literal
```

The pipeline is: specialize H in the expression → Mathtext rendering → crop/pad → resize to H → threshold → exact binary mask → encode N → multiply by H → decode → compare. `--variant bit` selects the equivalent quotient-before-mod form. Typography changes the represented string and its bitmap; the fixed-point claim is only the externally positioned self-image.

The constructor accepts H=16…96 and a threshold 0…255 (a value erasing all formula pixels is rejected). Extremely small or thin glyphs may be difficult to read even when arithmetic reproduction is exact. Inspect `plot.png` before describing a generated expression as legible.

## Encode a user-supplied mask or image

```sh
python -m tupper_formula encode examples/input/asymmetric.txt -o output/asymmetric
python -m tupper_formula encode drawing.png --image --width 106 --height 17 --threshold 160 -o output/drawing
```

Without `--image`, inputs are rectangular `0/1` or `./#` text and plain P1 PBM (comments allowed). Binary P4 PBM is intentionally not supported. With `--image`, both width and height must be supplied together to resize; neither means preserving the source dimensions subject to limits. Image import applies EXIF orientation and composites transparency on white. Values below the threshold become 1. Resizing and thresholding can lose information before the exact mask is formed.

## Decode and inspect

```sh
python -m tupper_formula decode --k-file examples/historical/k.txt --width 106 --height 17 --orientation historical -o output/historical.svg
python -m tupper_formula decode --k-file examples/letter-a/k.txt --width 3 --height 5 -o output/a.pbm
python -m tupper_formula cell examples/letter-a/experiment.json --x 1 --j 4
```

`decode` accepts aligned noncanonical offsets, but `--orientation historical` is available only for SVG display. PBM and text exports remain canonical top-to-bottom data. `cell` reports the mathematical cell, its screen row, bit index, quotient and bit. It does not use floating-point approximations of the enormous absolute y coordinate.

Exit codes: 0 success, 1 computed verification failure, 2 malformed input or other handled error. Files and bundle directories are not silently overwritten. Standard streams use JSON where structured output is useful.

## Core API

```python
from fractions import Fraction
from tupper_formula import Bitmap, encode, decode, evaluate, evaluate_literal
from tupper_formula.manifest import make_manifest, verify_manifest

image = Bitmap(("010", "101", "111", "101", "101"))
N, k = encode(image)
assert decode(k, image.width, image.height) == image
assert evaluate(Fraction(3, 2), Fraction(2*(k+4)+1, 2), 5) == 1
assert evaluate_literal(Fraction(3, 2), Fraction(2*(k+4)+1, 2), 5) == 1
report = verify_manifest(make_manifest(image), literal=True)
assert report["passed"]
```

`evaluate` returns the predicate's RHS bit using shifts. `evaluate_literal` computes `floor(mod(q/2**n,2))` with `Fraction`. Coordinates must be nonnegative `int` or `Fraction`; floats and booleans are rejected. These are explicit domain restrictions, not a claim that no extension to negative coordinates exists.

`radix.encode_array(values, shape, base)` and `radix.decode_array(N, shape, base)` handle known-shape flattened arrays. The last axis varies fastest; this differs from the special column-major bitmap convention. The examples/tests make that distinction explicit.

## JSON contract

See [`experiment.schema.json`](../schemas/experiment.schema.json). `N` and `k` are **decimal strings**, never JSON numbers. Required semantic checks include dimensions, binary rows, canonical `k=HN`, orientation, formula variant/H, half-open viewport and bitmap hash. `source` and `generator` are provenance objects, not trusted proof certificates. Unknown top-level fields fail JSON Schema validation; arithmetic validation focuses on required semantic invariants.

The canonical hash payload is ASCII:

```text
tupper-bitmap-v1
W H
first top row
...
last bottom row
```

Every line, including the last row, ends with `\n`. `W H` is replaced by decimal dimensions separated by one space. Orientation and provenance are not part of this bitmap hash; they are separately checked or recorded. A matching hash detects mismatch but does not authenticate who produced the artifact.

Python and the browser exchange the same manifest within the **intersection of their resource limits**. Browser JSON uses Web Crypto SHA-256 and therefore requires an appropriate secure context (HTTPS or localhost). Independently import the exported JSON in Python before using it as research evidence.

## Resource policy

| Layer | Limit |
|---|---|
| Python bitmap | Each side ≤4096; total cells ≤65,536 |
| Python decimal text | ≤25,000 ASCII digits; bounded conversion chunks |
| Python evaluated integer | ≤84,000 bits; bit index <65,536 |
| File input | Text/manifest ≤2 MB; image ≤20 MB and ≤16 million source pixels |
| Browser | W≤512; H≤128; total≤16,384 cells; decimal≤5,500 digits; JSON≤1 MB |

Limits are deliberately conservative, not benchmarked maxima of Python or JavaScript. The core does not call `eval`, execute imported LaTeX, load plugins from manifests or change Python's global integer-string security setting.
