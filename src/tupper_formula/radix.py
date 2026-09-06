"""A separate positional-notation extension, not a port of Somu--Mishra's formula.

values use coordinate order with the last axis fastest, e.g. index=H*i+j in 2D.
Color values are palette indices; the palette is external, not inferred here.
"""
from math import prod
from .core import MAX_CELLS, MAX_INTEGER_BITS, require_int


def _size(shape: tuple[int, ...], base: int) -> int:
    if not isinstance(shape, (tuple, list)) or not 1 <= len(shape) <= 8:
        raise ValueError("shape must contain 1..8 dimensions")
    for side in shape:
        require_int(side, "dimension", 1)
    require_int(base, "base", 2)
    size = prod(shape)
    if size > MAX_CELLS or base > 256 or size * (base - 1).bit_length() > MAX_INTEGER_BITS:
        raise ValueError("array exceeds resource limits (base <=256)")
    return size


def encode_array(values: list[int], shape: tuple[int, ...], base: int = 2) -> int:
    size = _size(shape, base)
    if len(values) != size:
        raise ValueError("number of values must equal product(shape)")
    n = 0
    for digit in reversed(values):
        require_int(digit, "digit")
        if digit >= base:
            raise ValueError("digit outside the palette")
        n = base * n + digit
    return n


def decode_array(n: int, shape: tuple[int, ...], base: int = 2) -> list[int]:
    require_int(n, "n")
    size = _size(shape, base)
    if n.bit_length() > MAX_INTEGER_BITS:
        raise ValueError("n exceeds resource limit")
    values = []
    for _ in range(size):
        n, digit = divmod(n, base)
        values.append(digit)
    return values
