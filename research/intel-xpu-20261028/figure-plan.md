# Figure plan — Intel backend qualification

Scope: original research assets only. No manuscript changes. Author credit remains Zhiqi Tao in the book; no additional byline is proposed.

## IX-F1 — Device visibility is not an end-to-end serving path

Learning objective: distinguish three incompatible accelerator paths and locate the qualification boundary between an available API and a deployable service.

Mechanism: serving engines require framework/backend integration, compatible kernels and runtimes, a matching driver, and the correct hardware. A device-enumeration test exercises only a small part of this dependency chain. A model can load while paged attention, a quantized operator, a collective, or its target SLO still fails.

Proposed placement: Chapter 11, after Table 11-2 and its interpretation paragraph, beside proposed insertion IX-T3. Cross-reference from the Chapter 8 backend identity paragraph. This supplements the existing four-concern serving diagram; it does not redraw scheduling or cache algorithms.

Composition: three isolated vertical columns for Intel GPU, Intel Gaudi, and client NPU. Downward arrows mean dependency/dispatch requirements, not measured execution times or sequential transformer operators. The Intel GPU column explicitly separates PyTorch XPU from the alternative engine-native SYCL route. A bottom gate requires a specific model, numerical representation, memory budget, attention/cache path, collectives, correctness, and measured SLO. No cross-column arrows imply device/API interchangeability.

Necessity: a single table saying 'Intel supported' hides the exact wrong inference this investigation must prevent. The parallel paths and common qualification gate make that error visible. Product peak charts would add no transferable mechanism, so no additional figure is justified.

## Actual print constraints and style

Read `render/latex/book.sty`, especially lines 61 and 93–111. The live style uses 1.2-inch left and right margins. The immutable proof is 8.5 × 11 inches. Available width is therefore 8.5 − 1.2 − 1.2 = 6.1 inches (calculation also reproduced by the generator). Assets use exactly 6.1 inches, not a 6 × 9 book template. The nearby style constrains figures to `textwidth`.

Design language: white background, sans-serif figure labels, dark outlines and explicit labels. Reuse book memory blue #27408B, compute orange #E67E22, economics green #1E6B42, and binding-constraint red #C0392B only where their meanings apply. Hardware-family identities do not receive arbitrary semantic colors. Gray fills and textual labels preserve distinctions without color. The historical `render/REVIEW_PROMPT_VISUAL_FLEET_AMZ.md` still mentions 6 × 9; that obsolete trim statement does not override the live style or current user requirement.

Proposed dimensions: 6.1 × 6.3 inches. Source canvas: 610 × 630 units. Minimum source font 14 units, equivalent to 10.08 pt at intended width. Render color and grayscale at 300 ppi, plus an isolated US Letter placement proof with the exact text width. Captions are external to the figure and included in the manifest.

## Evidence and rights

Evidence claims: IX-001, IX-002, IX-003, IX-018, IX-019, IX-021, IX-023, IX-026. First-party public documentation, immutable source pins where available; see claims.json and citation-ledger.json. The NPU column represents the OpenVINO route only. It does not claim that PyTorch or all Intel accelerators share one stack. Gaudi has its own engine integrations and releases.

Original shapes and text only. No vendor slides, logos, benchmark curves, or artwork are copied. Source snapshots are provenance material, not assets proposed for publication. Figure-specific permissions are not expected for original geometry; legal review of third-party source redistribution remains outside this assignment.

## Verification plan

Render from editable SVG using PyMuPDF. Check dimensions, minimum placed font size, text extents, connector endpoints, edge margins, pixel content, and grayscale contrast. Inspect the complete rendered figure and a detail crop with the vision tool. Perform a second self-critical inspection of the Letter placement proof and grayscale version. Record actual results and [P0]/[P1]/[P2] unresolved items in figures/QA.md. Integration into the full manuscript and physical proof printing remain separate checks.
