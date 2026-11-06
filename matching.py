"""Locate one fixed-size grayscale marker or explain why the match is uncertain."""
from dataclasses import dataclass
import math

import cv2 as cv
import numpy as np


@dataclass(frozen=True)
class Peak:
    x: int
    y: int
    score: float


@dataclass(frozen=True)
class Match:
    status: str
    best: Peak | None
    runner: Peak | None
    response_shape: tuple[int, int]


def response(image: np.ndarray, template: np.ndarray) -> np.ndarray:
    for name, a in (("image", image), ("template", template)):
        if not isinstance(a, np.ndarray) or a.ndim != 2 or a.dtype != np.uint8:
            raise ValueError(f"{name} must be a two-dimensional uint8 grayscale image")
    h, w = template.shape
    H, W = image.shape
    if h < 2 or w < 2 or h > H or w > W:
        raise ValueError("template must be at least 2 by 2 and fit inside image")
    if int(template.min()) == int(template.max()):
        raise ValueError("constant template has no contrast; crop a distinctive feature")

    scores = cv.matchTemplate(image, template, cv.TM_CCOEFF_NORMED)
    # The denominator is zero for a flat patch. Use exact integer-valued
    # sums in float64 and invalidate such windows explicitly.
    s, q = cv.integral2(image, sdepth=cv.CV_64F, sqdepth=cv.CV_64F)

    def area(a):
        return a[h:, w:] - a[:-h, w:] - a[h:, :-w] + a[:-h, :-w]

    total = area(s)
    varied = (h * w) * area(q) > total * total
    return np.where(varied & np.isfinite(scores), scores, -np.inf)


def _peak(scores):
    if not np.isfinite(scores).any():
        return None
    y, x = np.unravel_index(np.argmax(scores), scores.shape)
    return Peak(int(x), int(y), float(scores[y, x]))


def locate(image, template, *, minimum=0.87, margin=0.06):
    if not math.isfinite(minimum) or not 0 <= minimum <= 1:
        raise ValueError("minimum must be finite and between 0 and 1")
    if not math.isfinite(margin) or not 0 < margin <= 1:
        raise ValueError("margin must be finite and in (0, 1]")
    scores = response(image, template)
    best = _peak(scores)
    if best is None:
        return Match("no_texture", None, None, scores.shape)

    h, w = template.shape
    separate = scores.copy()
    # Remove every origin whose template rectangle shares pixels with the winner.
    separate[max(0, best.y-h+1):best.y+h, max(0, best.x-w+1):best.x+w] = -np.inf
    runner = _peak(separate)
    if best.score < minimum:
        status = "no_match"
    elif runner is not None and best.score - runner.score < margin:
        status = "ambiguous"
    else:
        status = "found"
    return Match(status, best, runner, scores.shape)
