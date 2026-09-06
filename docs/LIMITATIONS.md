[English](LIMITATIONS.md) · [한국어](LIMITATIONS-KR.md)

# Limitations and non-goals

## Scientific limitations

The implemented self-image is selected by an **external k**. It does not include every digit of that k in its own graph, and does not solve unrestricted self-description. SVG output consists of square cells, not Trávník's smooth curves. Base-C packing is not a complete n-variable generalized graphing system. No automated theorem prover, novelty detector, general shortest-formula solver or neural image recognizer is included.

Exactness refers to the saved binary mask and the specified half-open viewport. It does not mean lossless recovery of an arbitrary source photograph, semantic understanding of the formula, truth of text drawn in the image, or equality of the entire unbounded graph with the finite typeset expression. Larger k values can repeat the same visible mask.

## Numerical and implementation limits

Python and JavaScript have different resource policies; not every Python-sized artifact is importable in the browser. Huge decimal conversions and exact fractions can become expensive. Limits are intentional and must not be removed merely to process untrusted files. Coordinates use nonnegative integers/Fractions in Python; the UI edits discrete cells. Floating-point absolute coordinates near a 543-digit k are not meaningful here.

Encoding plus decoding can share a defect. Known examples, asymmetric fixtures, rational extraction and cross-language checks reduce but do not eliminate that possibility. JSON Schema alone cannot establish `k=HN` or the hash. Hash equality does not establish provenance, scientific validity or collision impossibility.

## Rendering and presentation

Mathtext and image thresholding create a binary target; their output can vary with software/font/platform changes. Identical input LaTeX is not a guarantee of identical pixels. Font files are intentionally not included. Native MathML may differ across browsers; screen-reader compatibility and full WCAG conformance are not certified. Article Korean translation is client-side, not a separate fully pre-rendered search-index route.

Clipboard permissions, Web Crypto secure-context requirements and local file restrictions are real platform constraints. The app provides errors/fallbacks but cannot override those policies. Browser test doubles only check the application's requested behavior, not operating-system clipboard access. Public social-card scraping and live Pages deployment must be tested after publication.

## Operational boundaries

This is research software, not an isolated hostile-file analysis service. Run unknown images in an appropriately restricted environment and keep optional image libraries patched. There is no server-side account system, cloud persistence or public upload endpoint. The ZIP does not create a GitHub repository. No maintenance schedule, service-level guarantee or future dependency availability is promised.

Sources are attributed but not republished in full. Follow their own licenses when reusing a third-party implementation. The project MIT license does not relicense papers or authors' source code outside this repository.
