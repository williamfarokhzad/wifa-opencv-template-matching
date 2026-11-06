# OpenCV Template Matching: Find a Marker and Reject Ambiguous Matches

This lab uses `cv2.matchTemplate` to locate a small grayscale marker in a larger frame. It reports when the best match is weak, when a second location is nearly as plausible, and when no window contains texture. The four included scenes are generated in Python. No camera or robot is required.

Full lesson: [OpenCV template matching at WIFA Robotics](https://wifarobotics.com/learn/opencv-template-matching/).

## Start here

1. Install Python 3.12 from [python.org](https://www.python.org/downloads/). Use a 64-bit build on a platform supported by the NumPy and OpenCV wheels.
2. On GitHub select **Code → Download ZIP**, extract the folder, and open a terminal in the folder containing `main.py`. If you already have Git, run:

   ```sh
   git clone https://github.com/williamfarokhzad/wifa-opencv-template-matching.git
   cd wifa-opencv-template-matching
   ```

3. Create an isolated environment. You can run its Python directly, with no activation.

   macOS and Linux:

   ```sh
   python3.12 -m venv .venv
   .venv/bin/python -m pip install -r requirements.txt
   .venv/bin/python main.py examples/shift.json
   ```

   Windows PowerShell:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe main.py examples/shift.json
   ```

## Compare the cases

Use the same environment Python for these commands.

| File after `python main.py` | Expected status | What to check |
| --- | --- | --- |
| `examples/shift.json` | `found` | Best origin `(47,11)`, score near 1, second score near 0.341. |
| `examples/repeat.json` | `ambiguous` | Two separate score peaks near 1 at `(47,11)` and `(13,34)`. Tiny backend differences may change their order. |
| `examples/absent.json` | `no_match` | A numerical maximum still exists, about 0.341, but is too weak. |
| `examples/rotated.json` | `no_match` | A 90 degree turn lowers the best score to about 0.524. |

Each case prints a grid of 44 rows by 70 columns. Coordinates are zero based `(x,y)`. Arrays use `[y,x]`. A score is a similarity measure, not a probability.

To try a pair of your own files offline, crop a distinctive marker from a reference image at its expected pixel size, then run:

```sh
python main.py --image frame.png --template marker.png
python -m unittest discover -s tests -v
```

On the repeat case, try `--margin 0.10`: the two peaks are still ambiguous. Use `--minimum 0.99` on the shift case and compare the result. These example settings are teaching values; do not transfer them to a production line.

## What's where

- `matching.py`: score map, flat window rejection, and best versus separate runner decision.
- `scenes.py`: four deterministic scenes and one 9 × 9 marker.
- `main.py`: commands for generated or local grayscale images.
- `tests/`: hand-calculated correlation, exact grid boundaries, ambiguity, and input checks.
- `diagrams/`: original SVGs, WebPs, and the renderer. To regenerate, install Inkscape and Pillow in addition to the lab dependencies, then run `python diagrams/render.py`.

If the template is rejected as constant, crop an asymmetric feature with visible contrast. If a clean-looking match is ambiguous, inspect both candidate positions and reduce the search area only if the fixture rules out the excluded region. If the part changes size or angle, normalize the geometry or choose a different detector. If `import cv2` fails, check that pip and the lab use the same environment; keep only one OpenCV wheel variant installed.

This is offline synthetic image testing. It does not measure lens distortion, latency, motion blur, false accept rates on hardware, or whether a robot may move. Before a machine pilot, collect and label images across lighting, shifts, part variation and empty frames. Calibrate thresholds on one labeled set and measure errors on a separate set. Keep the vision result outside the machine safety chain.

Primary references: [OpenCV Python template matching](https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html), [OpenCV score formulas](https://docs.opencv.org/4.x/df/dfb/group__imgproc__object.html), and [OpenCV headless wheel](https://pypi.org/project/opencv-python-headless/).
