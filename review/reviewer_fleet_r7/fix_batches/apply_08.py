import re, io, sys, json

p = "/home/ubuntu/hermes-work/from-token-to-fleet/design/manuscript/chapter-07/chapter-07.md"
s = io.open(p, encoding="utf-8").read()
orig = s

edits = []

# --- TERM-01: §7.1 "165 GB fits in 160 GB" -> weights-fit illustration
edits.append((
 'Conflating the two is exactly what produces a "165 GB fits in 160 GB" error.',
 'Conflating the two is exactly what produces a "140 GB fits in 160 GB" error — the weights fit, the weights + KV do not.'
))

# --- P1-045 (intro disambiguation wording)
edits.append((
 '8-bit here means FP8, not INT8',
 '8-bit here is FP8 raw byte-halving, not a block-scaled INT8 layout'
))

# --- P1-044: move alternate-basis KV-budget/concurrency recomputation out of §7.1
edits.append((
 'One conversion rule covers every capacity-dependent figure below: on that basis the KV budget becomes ~480 GB (684 \u2212 140 \u2212 64) and the per-host concurrency ceiling ~19 (480 \u00f7 24.9037 = 19.3; floor 19), against 436 GB and ~17.5 (floor 17) on the decimal basis.',
 'One conversion rule covers every capacity-dependent figure in this chapter: the pool capacities converted above, and the KV budget and concurrency ceiling once \u00a77.3 has derived them (the alternate-basis values are carried in \u00a77.3\u2019s technical note, after the decimal-basis numbers they convert).'
))

# --- P1-046: Table 7-1 3xH100 row head-divisibility phrasing
edits.append((
 'and the GQA variant\'s 64/8 head split fails the same way \u2014 8/3 = 2.7;',
 'and the GQA variant\u2019s 8 KV heads \u2014 64 query heads at an 8:1 ratio \u2014 do not divide into 3 ranks either, 8/3 = 2.67;'
))

# --- P1-060: scope note for the counterexample device
edits.append((
 'This is a separate GQA example, not the handbook\'s canonical 70B attention layout, and none of its constants feed the canonical tables in this chapter.',
 'This is a separate GQA example, not the handbook\u2019s canonical 70B attention layout, and none of its constants feed the canonical tables in this chapter. The 24 GB device is an illustrative placeholder with no vendor model named, and no number from this subsection is used anywhere else in the book \u2014 it is a geometry example, not a hardware recommendation.'
))

# --- F005: "KV budget ... 20 GB" relabel
edits.append((
 'The KV budget on a nominal 24 GB device is therefore 20 GB (24 \u2212 4).',
 'The model budget on a nominal 24 GB device is therefore 20 GB (24 \u2212 4) for weights and KV combined; after the 16 GB of weights, only 4 GB remains available for KV (24 \u2212 4 \u2212 16 = 4), and the 1.245184 GB of KV fits inside it.'
))

# --- P1-061: post-cutoff addendum marker on the Intel datasheet citations
edits.append((
 'retrieved 2026-10-28; the datasheets support the device capacities',
 'retrieved 2026-10-28 \u2014 post-cutoff addendum `v20260913+addendum-20261028`, outside the book\u2019s 2026-08-30 evidence cutoff, admitted as dated device-capacity documentation and not as a refresh of the August comparison; the datasheets support the device capacities'
))

# --- F-002: Table 7-2 label convention
edits.append((
 'The regime column separates the row classes, so the ~152 GB FP8-KV row reads as an inference variant, not a training floor.',
 'The regime column separates the row classes, so the ~152 GB FP8-KV row reads as an inference variant, not a training floor. **Label convention (applies to every row):** each total is [canonical scenario][DERIVED] from the bytes-per-param column \u2014 70B \u00d7 the stated bytes/param, plus the stated KV term where one applies \u2014 and the two vendor constants it divides by, the 640 GB aggregate pool and the 80 GB per-part capacity, are [1P: NVIDIA H100 spec]. Two rows carry an assumption inside the derivation: the Adam fine-tuning row\u2019s 16 B/param decomposition and the QLoRA row\u2019s nominal 0.5 B/param base are [canonical scenario][ASSUMPTION]. Activations are excluded from every row (note below), and so is the ~64 GB runtime/workspace reserve, which is stated once in \u00a77.1 as [canonical scenario][ASSUMPTION].'
))

# --- P1-089: QLoRA row basis
edits.append((
 'NF4: nominal 4-bit (~0.5 B/param) + quantization metadata; adds adapters/optimizer; no inference KV cache in a training step; activations excluded from this floor | ~36 GB |',
 'NF4: nominal 4-bit (~0.5 B/param) + quantization metadata; the ~36 GB assumes that 0.5 B/param basis \u2014 at \u00a77.3.3\u2019s block-scaled four-bit rate (0.53125 B/value) the base is 37.2 GB and this floor is ~38 GB; adds adapters/optimizer; no inference KV cache in a training step; activations excluded from this floor | ~36 GB (at 0.5 B/param; ~38 GB at 0.53125 B/param) |'
))

# --- P1-089 support in the Table 7-2 note
edits.append((
 'it holds the 4-bit base (~35 GB) + adapters + a small optimizer (~1 GB)',
 'it holds the 4-bit base (~35 GB at the nominal 0.5 B/param basis; ~37.2 GB at the 0.53125 B/value rate of \u00a77.3.3, which makes the same floor ~38 GB) + adapters + a small optimizer (~1 GB)'
))

# --- P1-087: Fig 7.4 caption exclusion list vs the worked example
edits.append((
 'Totals exclude padding, headers, extra copies, the separate per-tensor FP32 scale, and high-precision exceptions.',
 'Totals exclude padding, headers, extra copies, the separate per-tensor FP32 scale, and high-precision exceptions \u2014 so the bar totals omit the 4 B global scale that \u00a77.3.3\u2019s worked example adds back (16,777,216 \u00d7 0.5625 + 4 = 9,437,188 B). The caption and that example agree on the local 0.5625 B/value rate; they differ only by the 4 B the bars exclude.'
))

# --- P1-062: per-rank check for the MXFP4 sensitivity
edits.append((
 'so the storage-only integer ceiling rises from 17 (436 \u00f7 24.90368 = 17.51) to 21 \u2014 not in proportion to the weight compression.',
 'so the storage-only integer ceiling rises from 17 (436 \u00f7 24.90368 = 17.51) to 21 \u2014 not in proportion to the weight compression. The raised ceiling also survives this chapter\u2019s binding per-rank test: per-rank weights are 39.24375 \u00f7 8 = 4.906 GB, leaving 80 \u2212 4.906 \u2212 8 = 67.09 GB of KV budget per rank, which holds 67.09 \u00f7 3.11296 = 21.55 \u2192 floor 21 sequences \u2014 the same integer the aggregate division gives, so the ceiling is not an aggregate artifact.'
))

# --- P1-045: block-scaled 8-bit statement in §7.3.3
edits.append((
 '([OFP8](https://www.opencompute.org/documents/ocp-8-bit-floating-point-specification-ofp8-revision-1-0-2023-12-01-pdf-1); [SmoothQuant](https://arxiv.org/abs/2211.10438v7); [QLoRA](https://arxiv.org/abs/2305.14314v1)).',
 '([OFP8](https://www.opencompute.org/documents/ocp-8-bit-floating-point-specification-ofp8-revision-1-0-2023-12-01-pdf-1); [SmoothQuant](https://arxiv.org/abs/2211.10438v7); [QLoRA](https://arxiv.org/abs/2305.14314v1)). Read every \u201c8-bit\u201d KV figure in this book as FP8 raw byte-halving (one payload byte per K/V element, exactly 2\u00d7 against FP16). A block-scaled eight-bit layout \u2014 INT8 with per-group scales and zero points \u2014 adds metadata on top of that payload byte, so it does not realize exactly 2\u00d7 and must be re-derived from its own group size; the four-bit integer example above prices such metadata at 4 B per 128-value group, or 0.03125 B/value. [DERIVED]'
))

# --- P1-088: two multiples, two denominators (§5)
edits.append((
 'Full fine-tuning of 70B requires ~1.12 TB with Adam optimizer states \u2014 roughly 1.75\u00d7 the 8\u00d7H100 host.',
 'Full fine-tuning of 70B requires ~1.12 TB with Adam optimizer states \u2014 roughly 1.75\u00d7 the 640 GB capacity of the 8\u00d7H100 host.'
))

# --- P1-088: two multiples, two denominators (§6)
edits.append((
 'roughly 1.75\u00d7 the 8\u00d7H100 host. This is why the architect separates the serving fleet from the training fleet: the memory floors differ by roughly 7\u00d7 (~164 GB at 9.2K vs ~1,120 GB).',
 'roughly 1.75\u00d7 the 640 GB capacity of the 8\u00d7H100 host. This is why the architect separates the serving fleet from the training fleet: measured against the inference residency floor the same gap is \u22486.8\u00d7 (~164 GB at 9.2K vs ~1,120 GB). The two multiples have different denominators \u2014 1.75\u00d7 is against host capacity, 6.8\u00d7 against the ~164 GB floor \u2014 so neither checks the other.'
))

# --- F-008 + P1-047: Fig 7.5 per-rank annotation and crossover units
edits.append((
 'The axis and every series are aggregate whole-host GB; where a per-rank value appears it is the aggregate divided by 8 (24.9 \u00f7 8 \u2248 3.1 GB per rank at 9.5K, to be read against an 80 GB rank, not against the aggregate budget line).',
 'The axis and every plotted series are aggregate whole-host GB, and both crossover annotations are read in x-axis units on that same aggregate axis: the full-MHA FP16 line meets the 436 GB budget at \u2248166K tokens (436 \u00d7 10^9 \u00f7 2,621,440 B = 166,321) and the GQA FP16 line at \u22481.33M tokens. The per-rank figure is not a plotted series and is not read against the aggregate axis: 24.9 \u00f7 8 \u2248 3.1 GB is the per-rank share at 9.5K, read against a single 80 GB rank\u2019s HBM, and it is stated only to keep the aggregate pool and the per-rank partition visibly separate (technical note below; Ch 4 \u00a74.3).'
))

# --- P1-049 + P1-044: rank ceiling formula and the relocated vendor-binary budget
edits.append((
 'Byte-accurate, 436 \u00f7 24.9037 = 17.51, so the conservative integer "requests that fit" floor is 17, not 18.',
 'Byte-accurate, 436 \u00f7 24.9037 = 17.51, so the conservative integer "requests that fit" floor is 17, not 18. The integer 17 is therefore traceable to the binding constraint and not to a rounding of the aggregate quotient: rank ceiling = \u230a(80 \u2212 17.5 \u2212 8) \u00f7 3.11296\u230b = \u230a17.51\u230b = 17 slots. On the vendor-binary unit basis declared in \u00a77.1 the same subtraction gives 684 \u2212 140 \u2212 64 = 480 GB of KV budget; per rank 480 \u00f7 8 = 60 GB holds 60 \u00f7 3.11296 = 19.3 \u2192 floor 19 slots, against 17 on the decimal basis.'
))

for old, new in edits:
    n = s.count(old)
    if n != 1:
        print("FAIL count=%d for: %s" % (n, old[:90]))
        sys.exit(1)
    s = s.replace(old, new)

# --- P1-064: single figure-family note at the chapter head
anchor = 'so the chapter also reads correctly in grayscale.\n'
note = ('so the chapter also reads correctly in grayscale.\n\n'
        '**Figure-family reading rule (FIGS 7.5, 7.7, 7.8).** All three figures plot host *aggregate* GB against the 640 GB pool, and each carries the same caveat in its own caption. State it once here: the 80 GB rank-boundary rules and any per-rank figure in those figures are labelled guides, not plotted partitions of the bars, and every aggregate percentage they show is an upper bound on what any one rank can hold. Per-rank fit is the binding test and is derived once, in \u00a77.3\u2019s technical note; do not read an aggregate fill level as a per-rank allocation.\n')
assert s.count(anchor) == 1
s = s.replace(anchor, note)

io.open(p, "w", encoding="utf-8").write(s)
print("edits applied:", len(edits) + 1)
