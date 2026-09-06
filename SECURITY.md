[English](SECURITY.md) · [한국어](SECURITY-KR.md)

# Security notes

The site has no backend or public upload service. Pixels and imported manifests are processed locally; only the language preference is stored in localStorage. JSON imports are bounded and validated. Imported formula text is compared with a trusted template rather than executed. Native integer and image libraries still have resource costs and may have independent vulnerabilities.

Use a virtual environment, retain resource limits and update optional Pillow/Matplotlib dependencies as needed. Do not process hostile files with the privileges of a production service. SHA-256 is an integrity check, not a signature or an authenticity claim.

For a sensitive defect, use the repository's private vulnerability-reporting channel **if the maintainer has enabled it**. Otherwise contact the maintainer through an established private channel; do not publish exploit details or private input files in a public issue. This repository does not invent a security email address or promise a response SLA.
