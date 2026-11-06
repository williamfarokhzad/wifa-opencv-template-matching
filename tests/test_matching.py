import math
import unittest

import numpy as np

from matching import locate, response
from scenes import scene


class MatchingTests(unittest.TestCase):
    def test_manual_scores_have_right_sign_and_top_left_coordinates(self):
        image = np.array([[1, 2, 8, 7], [3, 4, 6, 5]], dtype=np.uint8)
        template = np.array([[1, 2], [3, 4]], dtype=np.uint8)
        actual = response(image, template)
        self.assertEqual(actual.shape, (1, 3))
        self.assertAlmostEqual(float(actual[0, 0]), 1, places=6)
        self.assertAlmostEqual(float(actual[0, 2]), -1, places=6)
        # Independent centered vectors for the center patch:
        # T'=(-1.5,-.5,.5,1.5); I'=(-3,3,-1,1). Dot=4, energies=5 and 20.
        self.assertAlmostEqual(float(actual[0, 1]), .4, places=6)

    def test_last_valid_window_is_included(self):
        image = np.zeros((5, 7), dtype=np.uint8)
        template = np.array([[9, 3], [4, 7]], dtype=np.uint8)
        image[-2:, -2:] = template
        result = locate(image, template, minimum=.99)
        self.assertEqual((result.best.x, result.best.y), (5, 3))

    def test_gain_offset_and_location(self):
        r = locate(*scene("shift"))
        self.assertEqual(r.status, "found")
        self.assertEqual(r.response_shape, (44, 70))
        self.assertEqual((r.best.x, r.best.y), (47, 11))
        self.assertGreater(r.best.score, .9999)
        self.assertGreater(r.best.score-r.runner.score, .2)

    def test_distinct_equal_peaks_are_ambiguous(self):
        r = locate(*scene("repeat"))
        self.assertEqual(r.status, "ambiguous")
        self.assertEqual({(r.best.x, r.best.y), (r.runner.x, r.runner.y)}, {(47, 11), (13, 34)})
        self.assertAlmostEqual(r.best.score, r.runner.score, places=5)

    def test_touching_rectangles_are_not_overlapping(self):
        t = np.array([[2, 8], [4, 3]], dtype=np.uint8)
        r = locate(np.tile(t, (1, 2)), t)
        self.assertEqual(r.status, "ambiguous")
        self.assertEqual({r.best.x, r.runner.x}, {0, 2})

    def test_absent_and_rotated_examples_fail_the_minimum(self):
        for case in ("absent", "rotated"):
            with self.subTest(case=case):
                r = locate(*scene(case))
                self.assertEqual(r.status, "no_match")
                self.assertLess(r.best.score, .87)

    def test_constant_template_and_flat_windows_are_not_matches(self):
        image = np.full((5, 6), 20, dtype=np.uint8)
        with self.assertRaisesRegex(ValueError, "constant template"):
            locate(image, image[:2, :2])
        marker = np.array([[12, 33], [45, 10]], dtype=np.uint8)
        r = locate(image, marker, minimum=0)
        self.assertEqual(r.status, "no_texture")
        self.assertIsNone(r.best)

    def test_disjoint_runner_may_not_exist_in_small_roi(self):
        marker = np.array([[12, 33], [45, 10]], dtype=np.uint8)
        r = locate(marker, marker)
        self.assertEqual(r.status, "found")
        self.assertIsNone(r.runner)

    def test_invalid_inputs_and_thresholds_fail_explicitly(self):
        f, t = scene("shift")
        for image, template in ((f.astype(float), t), (f[..., None], t), (t, f), (f, t[:1])):
            with self.assertRaises(ValueError):
                locate(image, template)
        for opts in ({"minimum": math.nan}, {"minimum": -1}, {"margin": 0}, {"margin": math.inf}):
            with self.assertRaises(ValueError):
                locate(f, t, **opts)


if __name__ == "__main__":
    unittest.main()
