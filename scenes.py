"""Small synthetic grayscale fixtures. Coordinates are (x, y), arrays [y, x]."""
import numpy as np

CASES = ("shift", "repeat", "absent", "rotated")


def scene(case):
    if case not in CASES:
        raise ValueError(f"unknown case: {case}")
    rng = np.random.default_rng(2816)
    frame = rng.integers(75, 115, size=(52, 78), dtype=np.uint8)
    marker = np.full((9, 9), 32, dtype=np.uint8)
    marker[1:8, 1:3] = 125
    marker[6:8, 1:8] = 125
    marker[2:4, 6:8] = 208
    marker[4, 4] = 178
    if case == "shift":
        frame[11:20, 47:56] = (marker.astype(np.uint16) * 3 // 4 + 30).astype(np.uint8)
    elif case == "repeat":
        frame[11:20, 47:56] = marker
        frame[34:43, 13:22] = marker
    elif case == "rotated":
        frame[11:20, 47:56] = np.rot90(marker)
    return frame, marker
