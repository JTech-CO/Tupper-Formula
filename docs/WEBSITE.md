[English](WEBSITE.md) · [한국어](WEBSITE-KR.md)

# Website architecture, editing and deployment

## Architecture

The checked-in `index.html` is ready to serve. `css/style.css` and `css/print.css` provide a light-only paper layout. `js/core.js` performs independent BigInt arithmetic, `js/math.js` constructs native MathML from trusted local data, and `js/app.js` manages the lab and language state. There is no React/Vite build, SPA router, remote font, math CDN or analytics service.

English/Korean article fragments live in `data/content.json`; UI strings in `data/ui.json`; paired MathML and LaTeX in `data/formulas.json`; citations and examples in their respective JSON files. HTML insertion is limited to trusted, checked-in article/formula data. Imported user JSON is never evaluated as HTML or code.

## Editing the article

Edit both language records. Update the matching Markdown documents when the scientific contract changes. Then rebuild:

```sh
python scripts/build_site.py
python scripts/validate_repo.py
```

`build_site.py` creates pre-rendered English equations and article text from `scripts/templates/index.html` and the JSON sources. It also refreshes the canonical sitemap. Do not maintain divergent edits only in the generated HTML. The active language is selected by `?lang=ko|en`, then localStorage, then English. This is one bilingual application, not two independent server-rendered language routes. No claim of complete bilingual SEO indexing is made.

Every displayed equation has a copy button and a LaTeX source disclosure; the live cell inspector also copies its current equation. Browser and system settings can deny automatic copying, so a selectable-text dialog is provided. The test harness can verify requested clipboard text, not bypass a user's clipboard policy.

## Local preview

```sh
python -m http.server 8000
```

Use `http://localhost:8000/`, not `file://`. JSON SHA-256 imports/exports require Web Crypto in a suitable secure context. External-network HTTP may render the article while disabling these functions. Use HTTPS for public hosting.

## GitHub Pages: choose one method

**Branch publication:** push the repository, open Settings → Pages, choose **Deploy from a branch**, then `main` and `/(root)`. The checked-in HTML and `.nojekyll` are sufficient. No Python runtime exists on GitHub Pages; Python experiments run locally or in CI.

**Actions publication:** select **GitHub Actions** as the Pages source and use `.github/workflows/pages.yml`. The workflow stages only public site content into `_site`, uploads the Pages artifact and deploys it. It runs on main-branch pushes and manual dispatch. CI is separate. Review Actions permissions in the repository before enabling it; the ZIP does not change them.

All local assets use relative paths, so repository subpaths work without rewriting `/css` or `/js` roots. There is no client-side route fallback or arbitrary deep-link route to configure; section links use fragments.

## Owner, repository and OG configuration

Before first publication or when moving the repository:

```sh
python scripts/configure_site.py --owner YOUR_ACCOUNT --repo Tupper-Formula
# Optional custom canonical URL:
python scripts/configure_site.py --owner YOUR_ACCOUNT --repo Tupper-Formula --base-url https://example.org/research/tupper/
```

This updates site metadata, canonical URL, social image URL, schema identifier and citation repository links; it does not contact GitHub or create anything. The default account/repository is a prepared destination, not an independently verified deployment.

`assets/og-image.png` is a real 1200×630 PNG. `og-image.svg` records a vector equivalent. The card uses the recomputed historical binary mask, not a copied figure. Regenerate with `python scripts/build_assets.py` after installing the render extra. No fonts are copied into the repository. Font availability can change text metrics when rebuilding; the committed PNG is the publication reference.

Social cards use absolute HTTPS URLs in HTML. A local preview cannot make a public crawler fetch a localhost image. Publish first; a social service may cache old metadata. Test with the target service after deployment rather than treating the presence of tags as proof of successful scraping.

## Accessibility and browser scope

The site includes landmarks, a skip link, semantic equation markup with LaTeX annotation, keyboard pixel navigation, explicit labels, visible focus states, live status and a text-grid alternative. These measures are not a full WCAG conformance audit. Use the canonical editor for large masks whose on-screen cells are small.

Native MathML appearance depends on the browser's math-font support. Chromium rendering was inspected in the recorded environment. Firefox/WebKit and assistive technologies remain explicit follow-up tests. Print styling is included; printer pagination and every browser's print output are not certified.
