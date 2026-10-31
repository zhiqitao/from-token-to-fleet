"""Geometry regression for the promotion pipeline, without writing assets."""
import contextlib
import io
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch


class FactoryGateLayoutTest(unittest.TestCase):
    def test_decision_seams_and_failure_edges(self):
        generator = Path(__file__).with_name('fig_ch21_pipeline.py')
        with patch('matplotlib.pyplot.savefig'), contextlib.redirect_stdout(io.StringIO()):
            ns = runpy.run_path(str(generator))
        ax = ns['ax']
        # Six gate failure branches need their own labels, plus the FAIL node.
        self.assertEqual(sum(t.get_text() == 'FAIL' for t in ax.texts), 7)
        for left, right in zip(ns['xs'][:-1], ns['xs'][1:]):
            seam = (left + ns['w'] + right) / 2
            ticks = [line for line in ax.lines
                     if len(line.get_xdata()) == 2
                     and all(abs(float(x) - seam) < 1e-8 for x in line.get_xdata())
                     and abs(float(line.get_ydata()[1]) - float(line.get_ydata()[0])) < 0.6]
            self.assertEqual(len(ticks), 1, f'missing decision tick at {seam}')
        self.assertFalse(any('[ILLUSTRATIVE]' in t.get_text() for t in ax.texts))


if __name__ == '__main__':
    unittest.main()
