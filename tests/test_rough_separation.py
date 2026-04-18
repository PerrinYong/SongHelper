from __future__ import annotations

import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from songhelper.rough_separation import center_extract


def test_center_extract_returns_center_and_side() -> None:
    stereo = np.array([[1.0, 2.0, 3.0], [1.0, 0.0, -1.0]])
    center, side = center_extract(stereo)
    assert np.allclose(center, np.array([1.0, 1.0, 1.0]))
    assert np.allclose(side, np.array([0.0, 1.0, 2.0]))
