# Figure plan — collective libraries

Scope: original explanatory figures only. No manuscript changes or release certification.

## Design and physical size

Read design/book-architecture.md (mechanism-first, anti-catalog, assumption labels), render/latex/book.sty:55–62,104–112 (sans headings; compute orange #E67E22, memory blue #27408B, constraint red #C0392B), and render/fig_batch1.py (existing communication figure conventions). The frozen proof is US Letter 612×792 pt. The active style has 1.2 in left and right margins, so available text width is 8.5−2.4=6.1 in, or 439.2 PostScript pt. Figures are authored at exactly that width, not scaled down from a wide canvas. Labels target 10–11 pt at placement, with no labels below 9.5 pt. White background, restrained fills, dark text, arrowheads, and explicit labels remain meaningful in grayscale. PDF is supplied in addition to editable SVG and 300 dpi PNG.

## CCL-F1 — A SUM becomes distributed shards, then a replicated result

Learning objective: separate collective semantics from a specific balanced ring execution, and count per-rank send and receive separately.

Mechanism: four ranks input four small integer-valued FP16 elements. Show original vectors; a three-neighbor-round reduce-scatter leaves one reduced scalar at each rank; a three-neighbor-round all-gather replicates the reduced vector. A small directed ring gives the neighbor order, not a fully enumerated timing trace. Explicitly label the state panels as phase boundaries so no straight-through edge implies a rank can reduce only its local input. With illustrative FP16 elements (all values/sums exactly representable), M=8 B and each phase sends/receives 6 B/rank. Both phases send 12 B and receive 12 B; endpoint sum is 24 B. SUM is not averaging.

Placement: Chapter 9 §1, immediately after the proposed semantics table (CCL-T1). Distinct from existing Fig 9.1 bandwidth curves. Cite in CCL-T1 and CCL-T3. Proposed width 6.1 in; height determined by the compact phase layout.

Composition: three full-width state rows and centered downward phase arrows; four aligned rank columns; one small directed ring row; a bottom accounting strip. No crossing all-to-all fan. Colors support, but do not encode, the numerical result.

Evidence/claims: CCL-001, CCL-002, CCL-006, CCL-007. MPI 5.0 semantics, nccl-tests normalization; toy FP16 data are illustrative and independently computed. Data and invariants live in the generator and independent_calculations.py.

## CCL-F2 — Payload layers and a separate bootstrap path

Learning objective: distinguish framework backend, collective library/algorithm, runtime/transport, physical topology, and communicator bootstrap. Make MPI and accelerator libraries coexist without calling MPI CPU-only.

Mechanism: two vertical example paths, CUDA/NCCL and Intel XPU/oneCCL, descend from framework backend through algorithms, device/transport paths, and physical resources. A separate dashed control path carries process launch/rank mapping/rendezvous. A dashed MPI-bootstrap connection enters NCCL communicator setup without becoming a payload edge. A note states that GPU-aware MPI is an alternative payload implementation, and legacy oneCCL may also use an MPI transport.

Placement: Chapter 9 §2 after CCL-T2's first paragraph. Cite explicitly from CCL-T2. Complements CCL-F1's data transformation; does not repeat the interconnect hierarchy.

Composition: two readable columns, shared horizontal layer labels, black solid downward payload arrows, red dashed control arrows in a dedicated margin corridor. No vendor logos, rankings, speed claims, or exhaustive backend catalog. Contemporary XCCL/oneCCL mapping is clearly a dated example, not a universal/historical ABI claim.

Evidence/claims: CCL-009 through CCL-016, CCL-019 through CCL-023. NCCL MPI bootstrap example, tagged headers/transport code, PyTorch v2.9.0 docs and pinned torch-xpu-ops code. Semantic layers are durable; named mappings are the 2026-10-28 research snapshot.

## Verification plan

Render SVG through PyMuPDF into vector PDF and 300 dpi PNG; also create grayscale and actual-width 96 dpi previews. Use deterministic text metrics/bounding boxes to reject clipping and inter-label collisions. Check ring counts against independent_calculations.py. Inspect every whole rendered PNG and cropped details with the vision tool, then perform a second self-critical review including grayscale. Record actual tool responses, limits and remaining [P0]/[P1]/[P2] issues in figures/QA.md. Rendering alone does not count as visual inspection. Parent must separately verify final typeset placement and automatic figure numbering.
