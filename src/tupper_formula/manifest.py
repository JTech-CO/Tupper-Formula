"""Interchange schema and recomputed verification, never trusting a stored pass flag."""
from __future__ import annotations
import json
import platform
from fractions import Fraction
from pathlib import Path
from .core import (Bitmap, encode, decode, evaluate_literal, parse_decimal,
                   decimal_string, formula_latex)
from .io import pbm, svg, read_text

SCHEMA_VERSION = "tupper-experiment/v1"
ENCODING = "column-major-bottom-up"


def make_manifest(bitmap: Bitmap, source: dict | None = None,
                  variant: str = "tupper", orientation: str = "cartesian") -> dict:
    bitmap.display_rows(orientation)
    n, k = encode(bitmap)
    return {
        "schema": SCHEMA_VERSION,
        "width": bitmap.width, "height": bitmap.height,
        "encoding": ENCODING, "rows": list(bitmap.rows),
        "N": decimal_string(n), "k": decimal_string(k),
        "canonical": True, "display_orientation": orientation,
        "formula_variant": variant, "formula_latex": formula_latex(bitmap.height, variant),
        "domain": {"x": [0, bitmap.width], "y_relative_to_k": [0, bitmap.height],
                   "endpoints": "left-closed-right-open"},
        "bitmap_sha256": bitmap.digest(),
        "source": source or {"kind": "bitmap"},
        "generator": {"name": "tupper-formula", "version": "1.0.0",
                      "python": platform.python_version()},
    }


def validate_manifest(data: dict) -> Bitmap:
    if not isinstance(data, dict) or data.get("schema") != SCHEMA_VERSION:
        raise ValueError("unsupported manifest schema")
    if data.get("encoding") != ENCODING:
        raise ValueError("unsupported coordinate encoding")
    bitmap = Bitmap(data.get("rows"))
    if type(data.get("width")) is not int or type(data.get("height")) is not int:
        raise ValueError("width and height must be JSON integers")
    if (data["width"], data["height"]) != (bitmap.width, bitmap.height):
        raise ValueError("dimensions disagree with rows")
    bitmap.display_rows(data.get("display_orientation"))
    if data.get("formula_latex") != formula_latex(bitmap.height, data.get("formula_variant")):
        raise ValueError("formula does not match the selected variant and height")
    if data.get("domain") != {"x": [0, bitmap.width], "y_relative_to_k": [0, bitmap.height],
                              "endpoints": "left-closed-right-open"}:
        raise ValueError("invalid or ambiguous viewport")
    if data.get("canonical") is not True:
        raise ValueError("interchange manifests require canonical N and k")
    n, k = encode(bitmap)
    if parse_decimal(data.get("N")) != n or parse_decimal(data.get("k")) != k:
        raise ValueError("N or k disagrees with the bitmap")
    if data.get("bitmap_sha256") != bitmap.digest():
        raise ValueError("bitmap digest mismatch")
    return bitmap


def verify_manifest(data: dict, literal: bool = False) -> dict:
    bitmap = validate_manifest(data)
    k = parse_decimal(data["k"])
    recovered = decode(k, bitmap.width, bitmap.height)
    mismatch = sum(a != b for r1, r2 in zip(bitmap.rows, recovered.rows)
                   for a, b in zip(r1, r2))
    count = 0
    if literal:
        for top, row in enumerate(bitmap.rows):
            j = bitmap.height - 1 - top
            for i, bit in enumerate(row):
                actual = evaluate_literal(Fraction(2*i+1, 2), Fraction(2*(k+j)+1, 2), bitmap.height)
                mismatch += actual != int(bit)
                count += 1
    return {"passed": mismatch == 0, "mismatches": mismatch,
            "cells": bitmap.width*bitmap.height, "literal_midpoints": count,
            "bitmap_sha256": bitmap.digest(),
            "scope": "encoded binary mask and arithmetic; not semantic or typographic self-reference"}


def read_manifest(path: Path) -> dict:
    return json.loads(read_text(path))


def write_bundle(bitmap: Bitmap, destination: Path, source: dict | None = None,
                 variant: str = "tupper", orientation: str = "cartesian") -> dict:
    """Only write into a new directory, preventing accidental overwrites."""
    if destination.exists():
        raise FileExistsError(f"output already exists: {destination}; choose a new directory")
    data = make_manifest(bitmap, source, variant, orientation)
    verification = verify_manifest(data)
    destination.mkdir(parents=True, exist_ok=False)
    n, k = encode(bitmap)
    (destination / "experiment.json").write_text(json.dumps(data, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    (destination / "verification.json").write_text(json.dumps(verification, indent=2)+"\n", encoding="utf-8")
    (destination / "target.pbm").write_text(pbm(bitmap), encoding="ascii")
    (destination / "decoded.pbm").write_text(pbm(decode(k, bitmap.width, bitmap.height)), encoding="ascii")
    (destination / "plot.svg").write_text(svg(bitmap, orientation), encoding="utf-8")
    (destination / "N.txt").write_text(decimal_string(n)+"\n", encoding="ascii")
    (destination / "k.txt").write_text(decimal_string(k)+"\n", encoding="ascii")
    (destination / "formula.tex").write_text(data["formula_latex"]+"\n", encoding="ascii")
    return data
