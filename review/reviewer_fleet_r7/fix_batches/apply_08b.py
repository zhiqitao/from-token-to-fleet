import io, sys
p = "/home/ubuntu/hermes-work/from-token-to-fleet/design/manuscript/chapter-07/chapter-07.md"
s = io.open(p, encoding="utf-8").read()

edits = [
# label scoping: put the [DERIVED] block in its own paragraph
('([QLoRA](https://arxiv.org/abs/2305.14314v1)). Read every \u201c8-bit\u201d KV figure',
 '([QLoRA](https://arxiv.org/abs/2305.14314v1)).\n\nRead every \u201c8-bit\u201d KV figure'),

# P1-048: Fig 7.7 panel label, stated in the caption + pointer to the figure source
('**Naming note:** the arithmetic panel reads "in-flight"; that quantity is the **KV-resident slot count** (concurrent sequences holding a KV slot), not the Little\'s-Law in-flight request count.',
 '**Naming note \u2014 the panel label is the quantity\u2019s old name.** The panel\u2019s \u201cin-flight\u201d label denotes the **KV-resident slot count** (concurrent sequences holding a KV slot) \u2014 the intended panel label is \u201cKV-resident slots\u201d \u2014 and not the Little\u2019s-Law in-flight request count.'),

# P1-050: Fig 7.8 rounding, stated honestly
('The totals are 228.9 GB at 9.5K (shown as 229), 287.9 GB at 32K (shown as 288) and 539.5 GB at 128K (the figure\'s scale label reads 539); that 0.5 GB is a label-rounding artifact against a 640 GB axis, not a capacity claim.',
 'The totals are 228.9 GB at 9.5K (figure tag 229), 287.9 GB at 32K (tag 288) and 539.5 GB at 128K (tag 539). The three tags do not follow one rule \u2014 the first two round up, the third truncates \u2014 so read the 128K tag as 539.5 GB; at a 640 GB axis scale that 0.5 GB is not resolvable, the tag understates that one bar, and no capacity claim depends on it (539.5 < 640 either way).'),
]

for old, new in edits:
    n = s.count(old)
    if n != 1:
        print("FAIL count=%d for: %s" % (n, old[:80])); sys.exit(1)
    s = s.replace(old, new)

# pointer sentences (appended inside the same caption text, after the naming/rounding clauses)
edits2 = [
('so in-flight requests \u2265 resident slots, and the KV budget is sized by resident sequences (Ch 4 \u00a74.3).',
 'so in-flight requests \u2265 resident slots, and the KV budget is sized by resident sequences (Ch 4 \u00a74.3). The label string is set in the figure source (`render/fig_ch7_budget.py`); until that asset is regenerated, read the panel\u2019s \u201cin-flight\u201d as \u201cKV-resident slots\u201d.'),
('the tag understates that one bar, and no capacity claim depends on it (539.5 < 640 either way).',
 'the tag understates that one bar, and no capacity claim depends on it (539.5 < 640 either way). The tag strings are set in the figure source (`render/fig_ch7_tetris.py`).'),
]
for old, new in edits2:
    n = s.count(old)
    if n != 1:
        print("FAIL2 count=%d for: %s" % (n, old[:80])); sys.exit(1)
    s = s.replace(old, new)

io.open(p, "w", encoding="utf-8").write(s)
print("ok", len(edits) + len(edits2))
