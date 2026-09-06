"""Plain text/PBM input and self-contained SVG output; no font files required."""
from __future__ import annotations
from html import escape
from pathlib import Path
from .core import Bitmap, dimensions

MAX_INPUT_BYTES = 2_000_000


def read_text(path: Path) -> str:
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("input exceeds 2 MB")
    return path.read_text(encoding="utf-8-sig")


def read_bitmap(path: Path) -> Bitmap:
    text = read_text(path)
    if path.suffix.lower() == ".pbm":
        clean = "\n".join(line.split("#", 1)[0] for line in text.splitlines())
        fields = clean.split()
        if len(fields) < 3 or fields[0] != "P1":
            raise ValueError("only plain PBM (P1) is supported by the core")
        if len(fields[1]) > 5 or len(fields[2]) > 5:
            raise ValueError("PBM dimensions exceed limits")
        w, h = int(fields[1]), int(fields[2])
        dimensions(w, h)
        if len(fields) != 3 + w * h or any(b not in ("0", "1") for b in fields[3:]):
            raise ValueError("PBM pixel count or value is invalid")
        return Bitmap(tuple("".join(fields[3 + j*w:3 + (j+1)*w]) for j in range(h)))
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return Bitmap(tuple(line.translate(str.maketrans({".": "0", "#": "1"})) for line in lines))


def pbm(bitmap: Bitmap) -> str:
    return f"P1\n# Tupper-Formula; rows top-to-bottom; 1=ink\n{bitmap.width} {bitmap.height}\n" + "\n".join(" ".join(r) for r in bitmap.rows) + "\n"


def svg(bitmap: Bitmap, orientation: str = "cartesian", scale: int = 8,
        title: str = "Tupper bitmap") -> str:
    if type(scale) is not int or not 1 <= scale <= 64:
        raise ValueError("scale must be 1..64")
    rows = bitmap.display_rows(orientation)
    w, h = bitmap.width, bitmap.height
    # Unit-cell geometry is stored exactly. White pixel separators are not added.
    commands = []
    for top, row in enumerate(rows):
        for i, bit in enumerate(row):
            if bit == "1":
                commands.append(f"M{i},{top}h1v1h-1z")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w*scale}" height="{h*scale}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">\n'
            f'<title id="title">{escape(title)}</title><desc id="desc">'
            f'{w} by {h} binary cells. Display: {orientation}. Canonical rows are stored separately.</desc><rect width="{w}" height="{h}" fill="white"/>'
            f'<path fill="#192d3f" shape-rendering="crispEdges" d="{"".join(commands)}"/></svg>\n')
