"""Command-line workflows for constructive formulas, not website generation."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from .core import Bitmap, encode, decode, parse_decimal, decimal_string
from .io import read_bitmap, read_text, svg, pbm
from .manifest import write_bundle, read_manifest, verify_manifest


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Exact Tupper encodings and constructive self-images")
    sub = p.add_subparsers(dest="command", required=True)
    en = sub.add_parser("encode", help="encode 0/1 or ./# text, P1 PBM, or an image")
    en.add_argument("input", type=Path)
    en.add_argument("-o", "--output", type=Path, required=True)
    en.add_argument("--image", action="store_true", help="read PNG/JPEG via optional Pillow")
    en.add_argument("--width", type=int)
    en.add_argument("--height", type=int)
    en.add_argument("--threshold", type=int, default=160)
    de = sub.add_parser("derive", help="typeset an inequality, encode it, and construct its k")
    de.add_argument("--height", type=int, default=32)
    de.add_argument("--variant", choices=["tupper", "bit"], default="tupper")
    de.add_argument("--threshold", type=int, default=160)
    de.add_argument("-o", "--output", type=Path, required=True)
    dc = sub.add_parser("decode", help="decode an aligned k into .svg, .pbm, or .txt")
    dc.add_argument("--k-file", type=Path, required=True)
    dc.add_argument("--width", type=int, required=True)
    dc.add_argument("--height", type=int, required=True)
    dc.add_argument("--orientation", choices=["cartesian", "historical"], default="cartesian")
    dc.add_argument("-o", "--output", type=Path, required=True)
    ve = sub.add_parser("verify", help="recompute dimensions, integers, digest, and pixel equality")
    ve.add_argument("manifest", type=Path)
    ve.add_argument("--literal", action="store_true", help="also evaluate the nested floor/mod at every rational midpoint")
    ce = sub.add_parser("cell", help="inspect one mathematical cell (x,j), j counted bottom-up")
    ce.add_argument("manifest", type=Path)
    ce.add_argument("--x", type=int, required=True)
    ce.add_argument("--j", type=int, required=True)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "encode":
            if args.image:
                from .render import load_image
                bitmap = load_image(args.input, args.width, args.height, args.threshold)
            else:
                if args.width is not None or args.height is not None:
                    raise ValueError("width/height resizing is only available with --image")
                bitmap = read_bitmap(args.input)
            data = write_bundle(bitmap, args.output, {"kind": "image" if args.image else "bitmap",
                                "input_name": args.input.name, "threshold": args.threshold if args.image else None})
            print(json.dumps({"output": str(args.output), "width": data["width"], "height": data["height"],
                              "k_digits": len(data["k"]), "verified": True}))
        elif args.command == "derive":
            from .render import rasterize_formula, save_png
            bitmap, source = rasterize_formula(args.height, args.variant, args.threshold)
            data = write_bundle(bitmap, args.output, source, args.variant)
            save_png(bitmap, args.output / "plot.png", scale=4)
            print(json.dumps({"output": str(args.output), "width": data["width"], "height": data["height"],
                              "k_digits": len(data["k"]), "verified": True,
                              "claim": "Tupper-type self-image, with external k"}))
        elif args.command == "decode":
            if args.output.exists():
                raise FileExistsError("output already exists")
            bitmap = decode(parse_decimal(read_text(args.k_file)), args.width, args.height)
            ext = args.output.suffix.lower()
            if ext != ".svg" and args.orientation != "cartesian":
                raise ValueError("historical display is SVG-only; data exports stay canonical")
            if ext == ".svg":
                content = svg(bitmap, args.orientation)
            elif ext == ".pbm":
                content = pbm(bitmap)
            elif ext == ".txt":
                content = "\n".join(bitmap.rows)+"\n"
            else:
                raise ValueError("output extension must be .svg, .pbm, or .txt")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content, encoding="utf-8")
            print(str(args.output))
        elif args.command == "verify":
            result = verify_manifest(read_manifest(args.manifest), args.literal)
            print(json.dumps(result, indent=2))
            return 0 if result["passed"] else 1
        elif args.command == "cell":
            data = read_manifest(args.manifest)
            verify_manifest(data)
            w, h = data["width"], data["height"]
            if not (0 <= args.x < w and 0 <= args.j < h):
                raise ValueError("cell is outside the image")
            n = parse_decimal(data["N"])
            index = h*args.x+args.j
            print(json.dumps({"x": args.x, "j": args.j, "top_row": h-1-args.j,
                              "bit_index": index, "quotient": decimal_string(n >> index),
                              "bit": (n >> index) & 1}, indent=2))
        return 0
    except (OSError, ValueError, TypeError, RuntimeError, KeyError) as exc:
        print(f"tupper: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
