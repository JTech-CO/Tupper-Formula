"""Constructive bitmap encodings; not a solver for semantic self-reference."""
from .core import (Bitmap, encode, decode, evaluate, evaluate_literal,
                   repeat_k, decimal_string, parse_decimal, formula_latex)
__version__ = "1.0.0"
__all__ = ["Bitmap", "encode", "decode", "evaluate", "evaluate_literal", "repeat_k",
           "decimal_string", "parse_decimal", "formula_latex"]
