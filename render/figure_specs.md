# Figure-generation specs

These authoring instructions for figure generation were moved out of the manuscript
source (design/manuscript/**) so they can no longer leak into a build and are kept
as a build-time input next to the figure scripts (render/fig_*.py).

## design/manuscript/chapter-04/chapter-04.md (original line 247)

Figure spec: mechanism-first diagram; one labeled axis per dimension, each arrow ending at its architectural consequence.

## design/manuscript/chapter-06/chapter-06.md (original line 120)

Figure spec: mechanism-first diagram; three stacked layers labeled Workload/Serving/Resource, arrows showing read-order on diagnostics.

## design/manuscript/chapter-07/chapter-07.md (original line 270)

Figure spec: X = context tokens (1K,4K,9.5K,32K,128K), Y = KV cache GB (log scale); four lines: full-MHA FP16, full-MHA FP8, GQA FP16, GQA FP8; horizontal 640 GB total-HBM line + 436 GB KV-budget line (curve compared to the 436 GB budget only); callouts at 9.5K (~24.9 GB FP16 bound; ~3.1 GB GQA).

## design/manuscript/chapter-07/chapter-07.md (original line 287)

Figure spec: one horizontal stacked bar (140 weights + 64 runtime + 436 KV = 640 GB pool); tick KV region in 24.9 GB slots -> C~17.5; faint FP8 overlay ~35.0 slots. Locks Ch7 <-> Ch17 handoff.

## design/manuscript/chapter-08/chapter-08.md (original line 189)

Figure spec: mechanism-first roofline diagram; arithmetic intensity on x-axis, achievable FLOP/s on y-axis, ridge line where FLOP-bound meets byte-bound; label the prefill and decode operating points.

## design/manuscript/chapter-10/chapter-10.md (original line 163)

Figure spec: mechanism-first diagram; model shown as weight-matrix + layer-stack + batch; arrows show TP slicing weights, PP stacking stages, DP replicating with all-reduce, EP sharding experts, CP splitting sequence; annotate comm cost + use-case per strategy.

## design/manuscript/chapter-11/chapter-11.md (original line 135)

Figure spec: mechanism-first serving-flow diagram; request stream → scheduler → KV page table (+ prefix cache) → optional prefill pool / decode pool split → output; annotate the resource each stage trades.

## design/manuscript/chapter-13/chapter-13.md (original line 99)

Figure spec: mechanism-first diagram; two axes (model residency on one, throughput demand on the other); four tier regions; arrow annotations for the three escalation triggers. Canonical workload dot in the server tier.

## design/manuscript/chapter-14/chapter-14.md (original line 148)

Figure spec: mechanism-first flowchart; left box = candidate models → capability screen (MMLU/GSM8K/retrieval-QA) → surviving models → deployment benchmark against canonical workload (TTFT/goodput/KV) → selection + TCO; annotate the SLO gate.

## design/manuscript/chapter-16/chapter-16.md (original line 238)

Figure spec: mechanism-first plot; x = requests/month, y = cost/month (log-log); self-host flat line at the 21-host included cost; cloud MARKER at the single priced operating point (6.24M req/mo, default paid-occupancy input) — never a flat line across the volume axis and not part of the crossover; managed-API zero-intercept linear; x-axis dimension = (A) duration/duty-cycle at fixed 40 rps peak + fixed 21-host fleet (fleet NOT re-sized per volume); feasible bound 40 rps x 624,000 active s = 24.96M req/mo with the region right of it shaded and labelled infeasible; mark break-even volume and price band; annotate the occupancy-input assumption; TWO noncomparability warnings (the header Caveat line and the Availability-scope caveat).

## design/manuscript/chapter-21/chapter-21.md (original line 88)

Figure spec: seven forward stages; decision ticks at the six transition seams; six labeled failure branches to a separate rollback node; production feedback to data/evaluation.

## design/manuscript/chapter-23/chapter-23.md (original line 100)

Figure spec: mechanism-first funnel diagram; top = vague ambition; five labeled question gates narrow it; bottom = quantified scope feeding the architecture loop.

