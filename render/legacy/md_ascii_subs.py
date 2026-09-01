import sys
# Apply ASCII-safe symbol substitutions for tectonic (Latin Modern lacks some
# glyphs). Philosophy: OUTSIDE fenced ```math blocks we wrap symbols in inline
# $...$ math; INSIDE math blocks we emit bare LaTeX commands (no $, already in
# math mode). Also escape any stray $ that would break math mode.
text = sys.stdin.read()
lines = text.split('\n')
out = []
in_math = False

# (char, outside_math_repl, inside_math_repl)
subs = [
    ('≈', r'$\\approx$', r'\\approx '),
    ('≠', r'$\\neq$', r'\\neq '),
    ('×', r'$\\times$', r'\\times '),
    ('·', r'$\\cdot$', r'\\cdot '),
    ('÷', r'$\\div$', r'\\div '),
    ('→', r'$\\rightarrow$', r'\\rightarrow '),
    ('§', 'S', 'S'),
]

def apply_outside(s):
    for a, b, _ in subs:
        s = s.replace(a, b)
    s = s.replace('−', '-').replace('…', '...').replace('—', '---')
    return s

def fix_hrule(l):
    # standalone '---' horizontal rules confuse pandoc's markdown parser
    # (em-dash ambiguity in the surrounding line context) and cause it to
    # swallow the following chapter heading; rewrite as an unambiguous '***'.
    if l.strip() == '---':
        return '***'
    return l

def apply_inside(s):
    for a, _, b in subs:
        s = s.replace(a, b)
    # inside math: remove any surrounding $ that a previous pass might have left
    s = s.replace('$', '')
    return s

for l in lines:
    if l.strip().startswith('```'):
        in_math = not in_math
        out.append(l)
        continue
    l = fix_hrule(l)
    out.append(apply_inside(l) if in_math else apply_outside(l))

sys.stdout.write('\n'.join(out))
