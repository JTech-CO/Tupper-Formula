"""Optional typesetting/image bridge. No external TeX engine or network calls.

Exactness begins AFTER thresholding; an antialiased input is not losslessly
represented by the binary mask. Typography changes can change the resulting k.
"""
from __future__ import annotations
from io import BytesIO
from pathlib import Path
from .core import Bitmap, dimensions, formula_latex


def _pillow():
    try:
        from PIL import Image, ImageChops
    except ImportError as exc:
        raise RuntimeError('Install rendering extras: pip install -e ".[render]"') from exc
    return Image, ImageChops


def load_image(path: Path, width: int | None = None, height: int | None = None,
               threshold: int = 160) -> Bitmap:
    Image, _ = _pillow()
    if type(threshold) is not int or not 0 <= threshold <= 255:
        raise ValueError("threshold must be 0..255")
    if (width is None) != (height is None):
        raise ValueError("set both width and height, or neither")
    if path.stat().st_size > 20_000_000:
        raise ValueError("image file exceeds 20 MB")
    with Image.open(path) as src:
        if src.width * src.height > 16_000_000:
            raise ValueError("source image exceeds 16 million pixels")
        # Composite alpha on white, not black; enforce EXIF orientation.
        from PIL import ImageOps
        src = ImageOps.exif_transpose(src).convert("RGBA")
        image = Image.new("RGBA", src.size, "white")
        image.alpha_composite(src)
        image = image.convert("L")
        if width is not None:
            dimensions(width, height)
            image = image.resize((width, height), Image.Resampling.LANCZOS)
        dimensions(image.width, image.height)
        return _bitmap(image, threshold)


def _bitmap(image, threshold: int) -> Bitmap:
    pixels = list(image.getdata())
    w, h = image.size
    return Bitmap(tuple("".join("1" if pixels[r*w+c] < threshold else "0"
                                for c in range(w)) for r in range(h)))


def rasterize_formula(height: int = 32, variant: str = "tupper", threshold: int = 160
                      ) -> tuple[Bitmap, dict]:
    Image, ImageChops = _pillow()
    if type(height) is not int or not 16 <= height <= 96:
        raise ValueError("formula raster height must be 16..96")
    if type(threshold) is not int or not 0 <= threshold <= 255:
        raise ValueError("threshold must be 0..255")
    try:
        import matplotlib
        from matplotlib.mathtext import math_to_image
        import PIL
    except ImportError as exc:
        raise RuntimeError('Install rendering extras: pip install -e ".[render]"') from exc
    tex = formula_latex(height, variant)
    buffer = BytesIO()
    with matplotlib.rc_context({"mathtext.fontset": "dejavuserif", "text.usetex": False}):
        math_to_image("$" + tex + "$", buffer, dpi=240, format="png", color="black")
    buffer.seek(0)
    with Image.open(buffer) as original:
        original = original.convert("RGBA")
        white = Image.new("RGBA", original.size, "white")
        white.alpha_composite(original)
        gray = white.convert("L")
    bbox = ImageChops.invert(gray).getbbox()
    if bbox is None:
        raise ValueError("renderer produced an empty formula")
    gray = gray.crop(bbox)
    padding = 2
    inner_height = height - 2*padding
    width = max(1, round(gray.width * inner_height / gray.height)) + 2*padding
    dimensions(width, height)
    canvas = Image.new("L", (width, height), "white")
    canvas.paste(gray.resize((width-2*padding, inner_height), Image.Resampling.LANCZOS),
                 (padding, padding))
    bitmap = _bitmap(canvas, threshold)
    if bitmap.population == 0:
        raise ValueError("threshold erased all formula pixels")
    return bitmap, {
        "kind": "typeset-formula", "variant": variant,
        "claim": "Tupper-type self-image; external k and viewport; not a self-contained quine",
        "latex": tex, "matplotlib": matplotlib.__version__, "pillow": PIL.__version__,
        "fontset": "dejavuserif", "threshold": threshold, "padding": padding,
        "raster_height": height, "resampling": "LANCZOS", "initial_dpi": 240,
    }


def save_png(bitmap: Bitmap, path: Path, scale: int = 8,
             orientation: str = "cartesian") -> None:
    Image, _ = _pillow()
    if type(scale) is not int or not 1 <= scale <= 64:
        raise ValueError("scale must be 1..64")
    if bitmap.width * bitmap.height * scale * scale > 32_000_000:
        raise ValueError("scaled image exceeds 32 million pixels")
    rows = bitmap.display_rows(orientation)
    image = Image.new("L", (bitmap.width, bitmap.height))
    image.putdata([0 if b == "1" else 255 for row in rows for b in row])
    image.resize((image.width*scale, image.height*scale), Image.Resampling.NEAREST).save(path)
