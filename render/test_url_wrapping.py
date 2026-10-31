#!/usr/bin/env python3
"""Regression: URL wrapping must not corrupt a hyperref target."""
import ast
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'render/latex/md_to_latex.py'
module = ast.parse(source.read_text())
function = next(n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == 'fix_urls')
namespace = {}
exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), 'exec'), namespace)
fix_urls = namespace['fix_urls']

class URLTests(unittest.TestCase):
    def test_href_target_is_not_wrapped(self):
        text = (r'\begin{longtable}x\end{longtable}' + '\n' +
                r'\href{https://github.com/NVIDIA/nccl-tests/blob/master/doc/PERFORMANCE.md}{NCCL}')
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as tmp:
            path = Path(tmp) / 'probe.tex'
            path.write_text(text)
            fix_urls(path)
            self.assertEqual(path.read_text(), text)

if __name__ == '__main__':
    unittest.main()
