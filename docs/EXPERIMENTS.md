[English](EXPERIMENTS.md) · [한국어](EXPERIMENTS-KR.md)

# Reproduction and verification protocol

## Evidence levels

1. The algebra in [THEORY](THEORY.md) establishes the extraction identity and constant-on-cell property.
2. Unit tests check invariants and regression cases in each implementation.
3. Exhaustive/seeded experiments check finite enumerations and independent arithmetic paths.
4. Saved masks and cross-language manifests check interchange.
5. UI/HTTP checks address delivery and interaction, not mathematical proof.

These levels must not be collapsed into a claim of formal verification, complete browser certification or a newly proved self-reference theorem.

## Reproduce the arithmetic suite

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
python experiments/run_suite.py
npm test
python scripts/validate_repo.py
```

The experiment runner writes `reports/arithmetic.json`. Its fixed seed is **20260906**. Exhaustive dimensions are `(1,1), (2,2), (3,2), (2,3), (3,3)`; their image counts sum to 658. Every exhaustive mask is decoded, and every cell midpoint is evaluated with exact rational floor/mod arithmetic. There are 5,442 such midpoint checks. A further 300 seeded masks test larger dimensions and repeated offsets. The recorded run checked 65,856 binary cells in aggregate and eight base-C shape cases, with zero mismatches.

The literal oracle avoids shift extraction but shares the coordinate helper. A coordinated indexing defect could evade both paths; the known A, asymmetric image, historical reference and separately written JavaScript core reduce this risk. None is a machine-checked formal proof.

## Bundled construction experiments

| Fixture | Purpose |
|---|---|
| `letter-a` | Transparent manual reference: 3×5, N=16015, k=80075 |
| `asymmetric` | Makes accidental rotations/mirroring visible |
| `historical` | Integer transcribed from original Figure 13; 106×17, 543-digit k |
| `formula-h32` | This program's typeset original-style inequality; 353×32, 3,380-digit k |
| `bit-h32` | Equivalent quotient-based inequality; 193×32, 1,838-digit k |

The two typography fixtures are constructive examples, not discoveries of previously unknown principles. `source` stores the LaTeX, renderer settings and versions. Preserve the PBM/JSON and their hash when reproducing an experiment; a generated PNG alone is weaker evidence.

To run the heavier literal check on the larger generated mask:

```sh
python -m tupper_formula verify examples/formula-h32/experiment.json --literal
```

This checks 11,296 cell midpoints. A successful result establishes exact agreement for this saved mask. It is separate from the 5,442 checks in the exhaustive experiment report and should not be silently substituted for that count.

## Browser and static-site checks

```sh
python -m pip install -e ".[qa]"
python -m playwright install chromium
python scripts/browser_smoke.py --mode http --output reports/browser-local.json
```

The normal `http` mode serves the site from a temporary local server and uses the real ES module loader and local JSON requests. `--chromium PATH` can select an installed browser. `--mode memory` is an explicit fallback for environments whose browser policies block all navigation: it injects authored code/CSS/data into an in-memory document, stubs local fetch and URL-history updates, and tests the UI there. It does **not** validate browser navigation or the native ES module graph. Any in-memory SHA bridge and clipboard test double are documented in its output; they must not be presented as an actual OS clipboard integration test.

This release's recorded browser mode and limitations are in `reports/validation.json`. Static HTTP resource checks and Node ESM tests are separate, complementary checks. Actual GitHub Pages deployment, social crawler previews, Firefox and WebKit are not asserted as tested.

## Cross-language interchange

Native Node tests load every Python-produced preset and recompute N, k, the mask and SHA-256. `scripts/crosscheck.py` additionally creates a browser-format manifest using the JavaScript core and verifies it in Python with the literal oracle. Large integer fields stay strings in JSON. Changing a stored `passed` flag cannot make a malformed experiment valid; the verifier recomputes invariants.

## Reporting a new experiment

Record input provenance, rights, W/H, threshold/resizing, renderer/library versions, formula variant, coordinate convention, N/k as strings, mask hash, output files, verification method and mismatches. Separate scientific claims from presentation quality. For a strong self-contained construction, additionally declare the expression language, every allowed primitive, glyph rules, representation of constants, and exact notion of equality.

The standard test runner overwrites its own report file intentionally; the experiment constructor refuses to overwrite existing experiment bundles. Keep earlier reports under new filenames when comparing revisions.
