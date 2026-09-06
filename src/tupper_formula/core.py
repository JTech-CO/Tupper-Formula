"""Exact arithmetic and explicit coordinate conventions.

Rows are stored top-to-bottom. Column i and bottom-up row j have index H*i+j.
Domain: x,y >= 0, H positive. A canonical image slice starts at k=H*N.
Floats are rejected so that enormous offsets cannot silently lose precision.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from math import floor
from typing import Sequence

MAX_CELLS = 65_536
MAX_SIDE = 4096
MAX_DECIMAL_DIGITS = 25_000
MAX_INTEGER_BITS = 84_000


def require_int(value: int, name: str, minimum: int = 0) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer (not bool or float)")
    if value < minimum:
        raise ValueError(f"{name} must be >= {minimum}")
    return value


def dimensions(width: int, height: int) -> tuple[int, int]:
    require_int(width, "width", 1)
    require_int(height, "height", 1)
    if max(width, height) > MAX_SIDE or width * height > MAX_CELLS:
        raise ValueError(f"Maximum {MAX_SIDE} per side and {MAX_CELLS} cells")
    return width, height


@dataclass(frozen=True)
class Bitmap:
    """Immutable, nonempty rectangular binary image, stored in screen row order."""
    rows: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.rows, (list, tuple)) or not self.rows:
            raise ValueError("rows must be a nonempty list or tuple")
        if not all(isinstance(row, str) for row in self.rows):
            raise TypeError("each row must be a 0/1 string")
        object.__setattr__(self, "rows", tuple(self.rows))
        width = len(self.rows[0])
        dimensions(width, len(self.rows))
        if any(len(row) != width or set(row) - {"0", "1"} for row in self.rows):
            raise ValueError("rows must have equal width and contain only 0 and 1")

    @property
    def width(self) -> int:
        return len(self.rows[0])

    @property
    def height(self) -> int:
        return len(self.rows)

    @property
    def population(self) -> int:
        return sum(row.count("1") for row in self.rows)

    def digest(self) -> str:
        """Hash a versioned, unambiguous canonical ASCII payload."""
        data = f"tupper-bitmap-v1\n{self.width} {self.height}\n" + "\n".join(self.rows) + "\n"
        return sha256(data.encode("ascii")).hexdigest()

    def display_rows(self, orientation: str = "cartesian") -> tuple[str, ...]:
        if orientation == "cartesian":
            return self.rows
        if orientation == "historical":
            return tuple(row[::-1] for row in reversed(self.rows))
        raise ValueError("orientation must be cartesian or historical")


def encode(bitmap: Bitmap) -> tuple[int, int]:
    """Return (N, k), where k=H*N. Never infer the image width from N."""
    n = 0
    h = bitmap.height
    for top, row in enumerate(bitmap.rows):
        j = h - 1 - top
        for i, bit in enumerate(row):
            if bit == "1":
                n |= 1 << (h * i + j)
    return n, h * n


def decode(k: int, width: int, height: int) -> Bitmap:
    """Decode one aligned slice. High bits outside the requested width are allowed."""
    require_int(k, "k")
    dimensions(width, height)
    if k.bit_length() > MAX_INTEGER_BITS:
        raise ValueError("k exceeds the resource limit")
    if k % height:
        raise ValueError("k must be divisible by height for a single-image slice")
    n = k // height
    return Bitmap(tuple("".join(str((n >> (height * i + j)) & 1) for i in range(width))
                        for j in range(height - 1, -1, -1)))


def _coordinates(x: int | Fraction, y: int | Fraction, height: int) -> tuple[int, int, int]:
    require_int(height, "height", 1)
    if height > MAX_SIDE:
        raise ValueError("height exceeds resource limit")
    if any(type(v) not in (int, Fraction) for v in (x, y)):
        raise TypeError("coordinates must be int or Fraction; floats are not exact")
    if x < 0 or y < 0:
        raise ValueError("this implementation restricts x,y to nonnegative values")
    q, r = floor(y / height) if isinstance(y, Fraction) else y // height, floor(y) % height
    n = height * floor(x) + r
    if n >= MAX_CELLS or q.bit_length() > MAX_INTEGER_BITS:
        raise ValueError("coordinate exceeds the evaluation resource limit")
    return q, r, n


def evaluate(x: int | Fraction, y: int | Fraction, height: int = 17) -> int:
    """Exact right-hand side, 0 or 1, via the proved bit identity."""
    q, _, n = _coordinates(x, y, height)
    return (q >> n) & 1


def evaluate_literal(x: int | Fraction, y: int | Fraction, height: int = 17) -> int:
    """Independent oracle: floor(mod(q * 2**(-n), 2)) using Fraction.

    This deliberately avoids bit shifts in the extraction itself. Fractional
    midpoints test the displayed inequality rather than only integer vertices.
    """
    q, _, n = _coordinates(x, y, height)
    z = Fraction(q, 2 ** n)
    return floor(z - 2 * floor(z / 2))


def repeat_k(k: int, width: int, height: int, repetition: int = 1) -> int:
    """Another offset with the same W*H low bits; not another unique image."""
    decode(k, width, height)  # validate first
    require_int(repetition, "repetition")
    result = k + height * repetition * (1 << (width * height))
    if result.bit_length() > MAX_INTEGER_BITS:
        raise ValueError("repetition exceeds resource limit")
    return result


def parse_decimal(text: str) -> int:
    """Bounded decimal input without changing Python's global int digit limit."""
    if not isinstance(text, str):
        raise TypeError("a decimal string is required")
    text = text.strip()
    if not text or len(text) > MAX_DECIMAL_DIGITS or any(c < "0" or c > "9" for c in text):
        raise ValueError(f"expected 1..{MAX_DECIMAL_DIGITS} ASCII decimal digits")
    n = 0
    for start in range(0, len(text), 9):
        chunk = text[start:start + 9]
        n = n * (10 ** len(chunk)) + int(chunk)
    return n


def decimal_string(n: int) -> str:
    """Exact, bounded formatting in nine-digit chunks; no sys.set_int_max_str_digits."""
    require_int(n, "n")
    if n.bit_length() > MAX_INTEGER_BITS:
        raise ValueError("integer exceeds resource limit")
    if n == 0:
        return "0"
    parts: list[int] = []
    while n:
        n, part = divmod(n, 1_000_000_000)
        parts.append(part)
    result = str(parts.pop()) + "".join(f"{part:09d}" for part in reversed(parts))
    if len(result) > MAX_DECIMAL_DIGITS:
        raise ValueError("decimal string exceeds resource limit")
    return result


def formula_latex(height: int, variant: str = "tupper") -> str:
    """The displayed, specialized predicate. Its k is deliberately external."""
    require_int(height, "height", 1)
    if height > MAX_SIDE:
        raise ValueError("height exceeds resource limit")
    h = str(height)
    q = r"\left\lfloor\frac{y}{" + h + r"}\right\rfloor"
    exponent = h + r"\lfloor x\rfloor+\operatorname{mod}(\lfloor y\rfloor," + h + ")"
    if variant == "tupper":
        return (r"\frac{1}{2}<\left\lfloor\operatorname{mod}\left(" + q +
                "2^{-" + h + r"\lfloor x\rfloor-\operatorname{mod}(\lfloor y\rfloor," + h +
                r")},2\right)\right\rfloor")
    if variant == "bit":
        return (r"\frac{1}{2}<\operatorname{mod}\left(\left\lfloor\frac{" + q +
                "}{2^{" + exponent + r"}}\right\rfloor,2\right)")
    raise ValueError("variant must be tupper or bit")
