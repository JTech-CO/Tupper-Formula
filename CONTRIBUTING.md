[English](CONTRIBUTING.md) · [한국어](CONTRIBUTING-KR.md)

# Contributing

Start by stating whether a change is a correction, reproduction, new construction, proposed experiment or theorem. Do not call a different bitmap integer a new self-reference theorem.

Keep the canonical top-to-bottom row format and `Hi+j` mathematical indexing stable. A format change needs a schema/version change, migration notes and asymmetric regression tests. Maintain every English Markdown file with its `-KR.md` counterpart; keep UI and scientific content bilingual as well.

Run the Python tests, arithmetic suite, native Node tests and repository validator before a pull request. For UI changes, also run the browser smoke test and inspect desktop/mobile English/Korean views. Record which tests actually ran, including skips and browser test-double limitations. Never edit a `passed` field to conceal a mismatch.

Add primary-source references for mathematical/historical claims, with a precise section or figure when relevant. Keep third-party code, fonts and paper images out of the repository unless rights and licenses have been reviewed. This project currently distributes no font files.

Describe the question, approach, limitations, reproduction commands and changed artifacts in the pull request. Do not include private photos, huge unbounded integers, credentials, machine-specific paths or generated virtual environments.
