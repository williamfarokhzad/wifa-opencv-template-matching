"""Run: python main.py examples/shift.json"""
import argparse
import json
from pathlib import Path

import cv2 as cv

from matching import locate
from scenes import scene


def gray(path):
    image = cv.imread(str(path), cv.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"could not decode {path}")
    return image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("example", nargs="?", type=Path, help="synthetic case JSON")
    inputs.add_argument("--image", type=Path, help="grayscale image path")
    parser.add_argument("--template", type=Path, help="template for --image")
    parser.add_argument("--minimum", type=float)
    parser.add_argument("--margin", type=float)
    args = parser.parse_args()
    try:
        if args.example:
            if args.template:
                raise ValueError("--template is only used with --image")
            cfg = json.loads(args.example.read_text(encoding="utf-8"))
            image, template = scene(cfg["case"])
        else:
            if not args.template:
                raise ValueError("--image requires --template")
            cfg = {}
            image, template = gray(args.image), gray(args.template)
        minimum = args.minimum if args.minimum is not None else cfg.get("minimum", .87)
        margin = args.margin if args.margin is not None else cfg.get("margin", .06)
        result = locate(image, template, minimum=minimum, margin=margin)
    except (ValueError, TypeError, KeyError, OSError, cv.error) as error:
        parser.error(str(error))

    print(f"response_rows_cols={result.response_shape[0]}x{result.response_shape[1]}")
    print(f"status={result.status}")
    for name, p in (("best", result.best), ("runner", result.runner)):
        print(f"{name}=none" if p is None else f"{name}=({p.x},{p.y}) score={p.score:.4f}")


if __name__ == "__main__":
    main()
