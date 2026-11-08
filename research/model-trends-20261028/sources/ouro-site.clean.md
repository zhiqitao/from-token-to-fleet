Ouro: Looped Language Models
Ouro LoopLM
News
vLLM
Results
Strategy
Models
Training
Follow-ups
Cite
arXiv 2510.25741 · open weights on Hugging Face
Scaling Latent Reasoning via Looped Language Models
Ouro is a family of pre-trained Looped Language Models that reason by iterating a shared stack of layers in latent space. Trained on 7.7T tokens, the 1.4B and 2.6B models match dense LLMs of up to 12B parameters.
Paper
🤗Models
Code
Serve with vLLM v0.26.0
BibTeX
Show all 33 authors
Rui-Jie Zhu*, Zixuan Wang*, Kai Hua*, Tianyu Zhang*, Ziniu Li*, Haoran Que*, Boyi Wei*, Zixin Wen*, Fan Yin*, He Xing*, Lu Li, Jiajun Shi, Kaijing Ma, Shanda Li, Taylor Kergan, Andrew Smith, Xingwei Qu, Mude Hui, Bohong Wu, Qiyang Min, Hongzhi Huang, Xun Zhou, Wei Ye, Jiaheng Liu, Jian Yang, Yunfeng Shi, Chenghua Lin, Enduo Zhao, Tianle Cai, Ge Zhang*†, Wenhao Huang†, Yoshua Bengio, Jason Eshraghian†
* Core contributors · † Corresponding authors
LoopLM forward passR = 4 recurrent steps
Exit gatep(exit at step t)
LM headloss at every step
shared weights
Layer N
⋮
Layer 2
Layer 1
Input embedding
×R
7.7T
pre-training tokens
2–3×
parameter efficiency vs. standard Transformers
≤12B
dense SOTA models matched by 1.4B / 2.6B Ouro
158 papers
cite Ouro — see follow-up research →
Updates
News
2026-10
158 papers now cite Ouro. We curated 35 follow-ups that substantively extend looped LMs — 15 of them run directly on the Ouro checkpoints.
2026-07-25
Ouro was removed from vLLM main (#49786). vLLM v0.26.0 is the last release with native Ouro support — pin it to keep serving Ouro.
2025-11-18
vLLM v0.11.1 ships the first release with native OuroForCausalLM support.
2025-10-30
Ouro support merged into vLLM (#27794).
2025-10-29
Paper released on arXiv; Ouro-1.4B / 2.6B and their Thinking variants released on Hugging Face.
Fast inference
Serve Ouro with vLLM
Last version with Ouro support
vllm==0.26.0
Native Ouro support shipped in v0.11.1 and was removed after v0.26.0; newer versions refuse to load Ouro. Pin v0.26.0 to keep serving it.
v0.11.1Nov 2025 · added
v0.26.0 ✓Jul 2026 · last
v0.27.0+removed
Pass --trust-remote-code.
vLLM always runs all 4 loops (no adaptive early exit).
PyPI 0.26.0
Release notes
ouro.py @ v0.26.0
Docker image
1 · InstallCopy
$ pip install "vllm==0.26.0"
2 · Serve (OpenAI-compatible API)Copy
$ vllm serve ByteDance/Ouro-2.6B-Thinking \
--trust-remote-code
or · DockerCopy
$ docker run --gpus all --ipc=host -p 8000:8000 \
-v ~/.cache/huggingface:/root/.cache/huggingface \
vllm/vllm-openai:v0.26.0 \
--model ByteDance/Ouro-2.6B-Thinking --trust-remote-code
3 · Offline inference (Python)Copy
from vllm import LLM, SamplingParams
llm = LLM(model="ByteDance/Ouro-2.6B-Thinking",
trust_remote_code=True)
params = SamplingParams(temperature=1.0, top_p=0.7,
max_tokens=4096)
messages = [{"role": "user",
"content": "If 2x + 3 = 11, what is x?"}]
out = llm.chat(messages, params)
print(out[0].outputs[0].text)
Overview
Introducing Ouro
Instead of leaving reasoning to chain-of-thought after training, Ouro builds it into pre-training: iterative computation in latent space, an entropy-regularized objective that learns how deep to think, and 7.7T tokens of data.
Its gains come from better knowledge manipulation, not more knowledge storage, and its latent reasoning is more faithful than explicit chain-of-thought.
Looped architecture
One shared stack, applied R = 4 times.
Learned depth allocation
Easy tokens exit early; hard tokens loop longer.
Knowledge manipulation
Better at composing facts, not storing more.
Faithful latent reasoning
Latent steps track the final answer closely.
Results
Performance
Competitive with dense models 2–3× larger.
Ouro-1.4B
Ouro-2.6B
Base models
vs. dense base models up to 3× larger.
Ouro-1.4BQwen3-1.7BGemma3-4BQwen3-4B
Ouro-2.6BQwen3-4BQwen3-8BGemma3-12B
MMLU0–100
Ouro-1.4B67.3
Qwen3-1.7B62.5
Gemma3-4B58.4
Qwen3-4B73.2
Ouro-2.6B74.6
Qwen3-4B73.2
Qwen3-8B76.6
Gemma3-12B72.1MMLU-Pro0–100
Ouro-1.4B48.6
Qwen3-1.7B37.3
Gemma3-4B34.6
Qwen3-4B51.4
Ouro-2.6B55.7
Qwen3-4B51.4
Qwen3-8B53.7
Gemma3-12B49.2BBH0–100
Ouro-1.4B71.0
Qwen3-1.7B53.5
Gemma3-4B66.3
Qwen3-4B71.0
Ouro-2.6B80.5
Qwen3-4B71.1
Qwen3-8B77.7
Gemma3-12B78.4GSM8K0–100
Ouro-1.4B78.9
Qwen3-1.7B70.3
Gemma3-4B68.7
Qwen3-4B72.9
Ouro-2.6B81.6
Qwen3-4B72.9
Qwen3-8B83.1
Gemma3-12B77.2MATH5000–100
Ouro-1.4B82.4
Qwen3-1.7B25.8
Gemma3-4B68.6
Qwen3-4B59.6
Ouro-2.6B90.8
Qwen3-4B59.6
Qwen3-8B62.3
Gemma3-12B83.2HumanEval+0–100
Ouro-1.4B67.4
Qwen3-1.7B59.8
Gemma3-4B29.3
Qwen3-4B70.7
Ouro-2.6B70.7
Qwen3-4B70.7
Qwen3-8B75.3
Gemma3-12B37.2
All 12 benchmarks
Ouro-1.4B vs. 1.7–4B dense models
Ouro-1.4BQwen3-1.7BGemma3-4BQwen3-4B
MMLU67.3562.4658.3773.19
MMLU-Pro48.6237.2734.6151.40
BBH71.0253.5166.3270.95
ARC-C60.9255.7260.9263.65
HellaSwag74.2967.0975.5875.66
Winogrande72.3066.3071.0771.19
GSM8K78.9270.2868.6972.86
MATH50082.4025.8068.6059.60
HumanEval74.4066.5034.8077.40
HumanEval+67.4059.8029.3070.70
MBPP73.0068.0060.6078.80
MBPP+62.7058.5051.1065.90Ouro-2.6B vs. 4–12B dense models
Ouro-2.6BQwen3-4BQwen3-8BGemma3-12B
MMLU74.6073.1976.6372.14
MMLU-Pro55.7351.4053.7249.21
BBH80.4671.1477.6578.41
ARC-C66.4063.6566.1072.44
HellaSwag79.6975.6679.6083.68
Winogrande75.8571.1976.8077.74
GSM8K81.5872.8683.0977.18
MATH50090.8559.6062.3083.20
HumanEval78.7077.7084.8046.30
HumanEval+70.7070.7075.3037.20
MBPP80.4078.8079.0073.50
MBPP+66.6065.9067.9066.10
Thinking models
pass@1 · DeepSeek = R1-Distill-Qwen.
Ouro-1.4BDeepSeek-1.5BQwen3-1.7BQwen3-4B
Ouro-2.6BQwen3-4BDeepSeek-7BQwen3-8B
AIME240–100
Ouro-1.4B65.0
DeepSeek-1.5B29.6
Qwen3-1.7B32.0
Qwen3-4B61.3
Ouro-2.6B64.7
Qwen3-4B61.3
DeepSeek-7B57.3
Qwen3-8B73.0AIME250–100
Ouro-1.4B46.3
DeepSeek-1.5B23.0
Qwen3-1.7B22.0
Qwen3-4B51.3
Ouro-2.6B50.3
Qwen3-4B51.3
DeepSeek-7B36.0
Qwen3-8B66.7OlympiadBench0–100
Ouro-1.4B71.5
DeepSeek-1.5B56.4
Qwen3-1.7B56.4
Qwen3-4B73.2
Ouro-2.6B76.4
Qwen3-4B73.2
DeepSeek-7B72.0
Qwen3-8B75.2BeyondAIME0–100
Ouro-1.4B34.0
DeepSeek-1.5B9.00
Qwen3-1.7B15.0
Qwen3-4B31.0
Ouro-2.6B39.0
Qwen3-4B31.0
DeepSeek-7B30.0
Qwen3-8B38.0GPQA0–100
Ouro-1.4B45.5
DeepSeek-1.5B33.2
Qwen3-1.7B34.0
Qwen3-4B54.5
Ouro-2.6B52.7
Qwen3-4B54.5
DeepSeek-7B51.0
Qwen3-8B59.1SuperGPQA0–100
Ouro-1.4B47.4
DeepSeek-1.5B26.5
Qwen3-1.7B35.9
Qwen3-4B51.9
Ouro-2.6B53.7
Qwen3-4B51.9
DeepSeek-7B46.6
Qwen3-8B48.0
All 7 benchmarks
Reasoning benchmarks (pass@1)
Ouro-1.4B-ThinkingOuro-2.6B-ThinkingQwen3-1.7BQwen3-4BQwen3-8BDeepSeek-1.5BDeepSeek-7B
AIME2465.0064.7032.0061.3073.0029.6057.30
AIME2546.3050.3022.0051.3066.7023.0036.00
OlympiadBench71.5576.4456.4473.1875.2556.4472.00
BeyondAIME34.0039.0015.0031.0038.009.0030.00
HLE5.215.584.135.212.224.225.14
SuperGPQA47.3753.6835.9251.8948.0026.5046.60
GPQA45.4552.6934.0054.5459.1033.1651.01
Performance by recurrent depth
Average of 6 benchmarks. Trained with T = 4: quality peaks there and drops only slightly beyond.
Trained depths (T ≤ 4)Extrapolation (T > 4)
020406080
49.9
72.4
69.9
T=1T=2T=3T=4T=5T=6T=7T=8
020406080
60.0
77.4
76.4
T=1T=2T=3T=4T=5T=6T=7T=8
View data table
Ouro-1.4B by recurrent step
ARC-CARC-ECommonsenseQAHellaSwagMMLUWinograndeAverage
T=137.6363.8544.6455.2441.2156.9949.93
T=254.8680.3067.9871.1560.4366.6966.90
T=359.4783.3374.3774.0766.7171.3571.55
T=460.9283.9675.4374.2967.4572.3072.39
T=5 (extrapolated)58.9682.9175.3573.7266.6470.3271.32
T=6 (extrapolated)59.7382.5874.9472.7765.7771.0371.14
T=7 (extrapolated)58.9681.9974.2872.3565.2870.0970.49
T=8 (extrapolated)58.1982.0773.5571.6064.4969.3069.87Ouro-2.6B by recurrent step
ARC-CARC-ECommonsenseQAHellaSwagMMLUWinograndeAverage
T=147.9572.3957.5868.9451.5561.4859.98
T=262.3785.2376.9077.6167.6370.4873.37
T=365.3687.3379.7779.1273.5774.3576.58
T=466.3886.9581.6579.5674.6075.5377.44
T=5 (extrapolated)65.3686.8381.2479.5774.4375.9377.23
T=6 (extrapolated)65.0286.7481.0879.6373.7975.3776.94
T=7 (extrapolated)65.4486.5780.7579.5972.9275.7776.84
T=8 (extrapolated)64.7686.4981.0879.5072.2474.5976.44
Strategy
How a LoopLM decides how deep to think
01
Train every depth
Every loop gets an LM loss, weighted by a learned exit distribution with a uniform-prior entropy term.
02
Teach the exit gate
A second stage trains only the gate: continue while the next loop still lowers the loss.
03
Exit with Q-exit
Stop once the cumulative exit probability reaches q, a deploy-time compute knob.
Training with an entropy-regularized objective (left) and threshold-based early exit at inference (right).
Early-exit strategies
The trained gate is best at every budget (~66% MMLU at 2.5 loops).
Fixed depth: 1 loop ≈ 40%, 4 loops 67.35%.
KV cache sharing
When decoding, keeping only the last loop's cache matches the full cache at ¼ the memory.
GSM8KOuro-1.4B
Full cache78.9
Last-step only78.8
Averaged78.7
First-step only18.7MATH-500Ouro-1.4B
Full cache82.4
Last-step only80.4
Averaged78.5
First-step only8.43
Full cache (1× memory)Last-step only (¼)Averaged (¼)First-step only (¼)
View data table
KV cache sharing during decoding (Ouro-1.4B)
GSM8KMATH-500KV memory
Full cache78.9282.401×
Last-step only78.8580.40¼
Averaged78.7378.52¼
First-step only18.738.43¼
Open weights
Models
Four Apache-2.0 checkpoints: two base models and two reasoning (Thinking) models.
Base🤗
Ouro-1.4B
≈ 4B densematches 4B standard Transformers
Layers24 × 4 loopsHidden2048Tokens7.7T
Base🤗
Ouro-2.6B
≈ 8B denserivals 8B standard Transformers
Layers48 × 4 loopsHidden2048Tokens7.7T
Thinking🤗
Ouro-1.4B-Thinking
Reasoning SFTmath · code · science
Layers24 × 4 loopsSFT data~8.3MContext32K
Thinking🤗
Ouro-2.6B-Thinking
Reasoning SFTmath · code · science
Layers48 × 4 loopsSFT data~8.3MContext32K
Code: rkstgr/LoopLM (open-source training reimplementation). Inference: modeling_ouro.py with trust_remote_code=True; also MLX, chatllm.cpp, OpenVINO and TransformerLens.
Recipe
Training pipeline
7.7T tokens in total; the 2.6B model is upcycled from the shared 3T-token checkpoint.
Stable 1 · 3T
Stable 2 · 3T
CT anneal · 1.4T
Stable training 1 — 3T
Stable training 2 — 3T
CT annealing — 1.4T
LongCT — 20B
Mid-training — 300B
Warmup
Common warmup for both model sizes.
3T
Stable training I
Shared pre-training phase at 4K sequence length.
Model branching
Keep the 1.4B model; upcycle a 2.6B model by duplicating layers.
3T
Stable training II
Both sizes continue with 4 recurrent steps for stability.
1.4T
CT annealing
Continual training on higher-quality math & code data, 16K sequences.
20B
LongCT
Long-context training on ProLong at 64K tokens.
300B
Mid-training
Advanced capability refinement at 32K tokens.
Reasoning SFT
~8.3M examples yield the Thinking models.
Decoder-only Transformer with RoPE, SwiGLU and sandwich RMSNorm.
Community
Research building on Ouro
Follow-ups that substantively extend looped LMs, grouped by theme.
158citing papers
35featured follow-ups
15run on Ouro checkpoints
All 35
Reasoning & decoding 7
Efficient inference 9
Architecture & scaling 7
Models at scale 3
Retrofitting 3
Beyond language 6
Runs on Ouro 15
Reasoning, RL & decoding7 featured
Post-training, reinforcement learning and decoding methods that make looped models reason better.
RLTTRuns on Ouro
Prioritize the Process, Not Just the Outcome: Rewarding Latent Thought Trajectories Improves Reasoning in Looped Language Models
Jonathan Williams and Esin Tureci · Feb 2026
GRPO only credits the final latent state of a looped model. RLTT spreads reward across the whole latent thought trajectory as a drop-in replacement for GRPO with negligible overhead. On Ouro-1.4B/2.6B-Thinking it lifts mean accuracy on MATH-500, AIME24/26 and BeyondAIME by +5.8% and +10.9%, and transfers beyond math.
arXivCode
STARSRuns on Ouro
Stabilizing Recurrent Dynamics for Test-Time Scalable Latent Reasoning in Looped Language Models
Xiao-Wen Yang et al. · May 2026
Looped models often peak at some depth and then collapse as more loops are added. STARS regularizes the Jacobian spectral radius (with random loop sampling) so latent states settle into stable fixed points, giving reliable test-time scaling on arithmetic and far less degradation at depth on math, while also raising Ouro-1.4B's peak accuracy.
arXiv
LoopCDRuns on Ouro
LoopCD: Loop-wise Contrastive Decoding for Improving Reasoning in Looped Language Models
Byeongho Yu et al. · Sep 2026
Unstable refinement across loops leaves a few uncertain “hard” tokens that trigger reasoning errors. LoopCD contrasts an early loop's logits against the final loop at decoding time — training-free, with negligible overhead — and improves reasoning on Ouro-1.4B and Huginn.
arXiv
Loop DropoutRuns on Ouro
Loop Dropout: Regularizing Shared Updates in Looped Language Models
Zirui Zhu et al. · Sep 2026
Standard LoRA on a looped model mostly adapts the late loops. Loop Dropout randomly skips the shared adapter at some loops during training, with inverse-survival rescaling, yielding stronger early-loop adaptation and better math, instruction-following and code results on Ouro — still plain LoRA at inference.
arXivCode
TaH2Ouro-style baseline
Improving Test-Time Scaling with Adaptive Looped Transformers
Yichen You et al. · Sep 2026
Post-trains Ouro- and Huginn-style looping on Qwen3 and finds many tokens gain nothing from extra iterations. TaH2 learns which tokens to iterate via lookahead depth supervision, improving the AIME accuracy–compute slope by 53% over the non-looped baseline, with gains that keep growing up to depth 8.
arXivCode
LatentMTRuns on Ouro
LatentMT: Machine Translation with Latent Reasoning
Wei-Rui Chen et al. · Jul 2026
The first systematic study of latent-reasoning looped models for machine translation. A lightweight adaptation of Ouro-2.6B-Thinking matches models 3–5× larger across 32 directions and reaches state of the art on mid- and low-resource languages.
arXiv
Tool callingRuns on Ouro
Looped Language Models Improve Compositional Tool Calling
Andrei Cristian Popescu et al. · Aug 2026
Evaluates Ouro and retrofitted looped models on API-Bank, BFCL and NESTful under matched SFT. Extra recurrence helps most on compositional, dependency-aware multi-call tool use, and adaptive depth gives the best compute–accuracy trade-off.
arXiv
Efficient inference & deployment9 featured
KV-cache compression, speculative decoding, batching and quantization that turn parameter efficiency into real-world speed.
FlashLoopRuns on Ouro
FlashLoop: Fast and Memory-Efficient Looped Transformers via Lazy Updates
Wanqi Yang and Shiwei Liu · Sep 2026
Cross-loop computation is highly redundant: updates concentrate on few tokens, attention changes on a sparse set of keys, and inter-loop KV residuals quantize well. Training-free FlashLoop exploits all three for lossless accuracy with up to 1.64× speedup and 6× smaller KV cache on the Ouro family.
arXiv
MELTRuns on Ouro
Memory-Efficient Looped Transformer: Decoupling Compute from Memory in Looped Language Models
Victor Conchello Vendrell et al. · May 2026
Ouro keeps one KV cache per loop, so memory grows with reasoning depth. MELT shares a single gated KV cache per layer across loops and is distilled from Ouro with lightweight post-training, achieving constant-memory latent reasoning that still outperforms comparably sized LLMs.
arXiv
HLARuns on Ouro
Hybrid Latent Attention for Looped Language Models
Yuhan Chen et al. · Oct 2026
Keeps exact KV only for a sliding window and stores older tokens as compact latents that every loop queries directly. Uptrained on frozen Ouro-1.4B/2.6B, the cache shrinks 10.7×, batch capacity grows 4–8.8× and decoding speeds up 2.5–7.4× while retaining >97% of accuracy.
arXiv
Dynamic depthRuns on Ouro
Enabling Dynamic Computation in Looped LMs
Aayush Mishra et al. · Oct 2026
Explains why early exit saves little in practice (every depth needs its own KV) and proposes a “best-available” KV cache that works out of the box, cutting FLOPs and KV memory by up to 30% at full-depth quality, plus a fix to the exit prior so tokens exit at genuinely different depths.
arXiv
LLARuns on Ouro
Looped Latent Attention: Cross-Loop KV Compression for Looped Transformers
James O' Neill and Fergal Reid · Jul 2026
The loop-indexed KV cache traces short low-rank trajectories that converge across loops. Looped Latent Attention stores compact K/V latents instead; on one H200 it raises Ouro-1.4B batch capacity at 4K context from 32 to 768 sequences at 21.3× compression.
arXiv
WaveFrontRuns on Ouro
WaveFront Decoding: Parallelized Self-Speculative Decoding for Looped Language Models
Hyeongju Ha and Jae-Joon Kim · Sep 2026
Training-free self-speculative decoding: shallow-loop outputs act as drafts, and weight sharing lets drafting and verification at different depths run in one batched “wavefront” call. 2.42× faster on Ouro-2.6B and up to 4.81× on Huginn-3.5B.
arXivCode
LoopSpecRuns on Ouro
LoopSpec: Pipelined Self-Speculative Decoding for Looped Transformers
SangLyul Cho et al. · Sep 2026
Pipelined self-speculative decoding that drafts from early recurrent states while verifying the current token, with a selective second proposal from a deeper loop and closed-form optimal draft depths. Lossless, and up to 6.83× faster across Ouro and other looped models.
arXiv
Depth batchingRuns on Ouro
Depth-adaptive Inference of Looped Language Models via Continuous Depth Batching
Kristian Schwethelm et al. · Aug 2026
Depth-adaptive inference breaks standard batching because tokens exit at different loops. Continuous depth batching re-forms batches between loop steps and predicts exits ahead of time, realizing up to 99% of the attainable speedup on Ouro-1.4B — fully looped designs like Ouro suit it best.
arXiv
LoopyRuns on Ouro
Loopy: Low-Bit Quantization Framework for Looped Language Models
Zeyu LI et al. · Oct 2026
Quantization error in a shared core compounds across loops, and the best PTQ configuration changes with depth. Loopy selects scaling/rotation configurations by loss at the deployment depth; under W4A4 on Ouro-1.4B it cuts LAMBADA perplexity by 36.5% versus SpinQuant.
arXiv
Architecture, stability & scaling laws7 featured
New looped architectures, stabilization techniques and scaling laws for recurrent depth.
Parcae
Parcae: Scaling Laws For Stable Looped Language Models
Hayden Prairie et al. · Apr 2026
Recasts looping as a dynamical system over the residual stream and traces instability to large spectral norms in the injection parameters. Constraining them lowers perplexity by up to 6.3% over prior large-scale looped models and yields power laws for scaling loops together with data.
arXiv
Iso-depth laws
How Much Is One Recurrence Worth? Iso-Depth Scaling Laws for Looped Language Models
Kristian Schwethelm et al. · Apr 2026
How much is one recurrence worth? A joint scaling law gives a recurrence-equivalence exponent φ = 0.46; hyper-connections raise it to 0.65 while truncated backprop lowers it — a clean diagnostic that separates genuine loop improvements from training-side gains.
arXiv
Looped-MoE
Sparse Layers are Critical to Scaling Looped Language Models
Ryan Lee et al. · May 2026
Dense looped models scale worse than standard Transformers, but Looped-MoE models scale better: different experts fire on each pass through the shared layers. Loop boundaries also make superior early-exit points, pointing to Looped-MoE + early exit as a scaling recipe.
arXiv
Attractor Models
Solve the Loop: Attractor Models for Language and Reasoning
Jacob Fein-Ashley and Paria Rashidinejad · May 2026
A backbone proposes output embeddings and an attractor module solves for their fixed point with implicit differentiation, so training memory is constant in depth. A 770M model beats a 1.3B Transformer trained on twice the tokens; a 27M model solves 91.4% of Sudoku-Extreme.
arXiv
Shared memory (LPT)Builds on Ouro's looping
The Surprising Effectiveness of Shared Memory in Looped Transformers
Giovanni Monea et al. · Oct 2026
Pretrains looped models in which only the first recursion writes a KV cache and later recursions read it. Sharing memory improves quality: the hybrid lowers FineWeb-Edu perplexity by 1.1–1.8 versus a same-size Transformer with 76–79% less context memory.
arXiv
Hyperloop
Hyperloop Transformers
Abbas Zeitoun et al. · Apr 2026
Loops only a middle block and adds hyper-connections (matrix-valued residual streams) after each loop. Matches depth-matched Transformer and mHC baselines with ~50% fewer parameters, and the advantage survives weight quantization.
arXiv
LoopFormer
LoopFormer: Elastic-Depth Looped Transformers for Latent Reasoning via Shortcut Modulation
Ahmadreza Jeddi et al. · Feb 2026
Trains on variable-length loop trajectories with a shortcut-consistency objective, conditioning each loop on time and step size, so short budgets still give useful representations and longer budgets keep refining — budget-conditioned, elastic-depth reasoning.
arXiv
Looped models at scale3 featured
Larger and production-grade models that adopt looping as a core design choice.
Nanbeige4.2-3B
Nanbeige4.2-3B: Unlocking Agentic Capabilities in a Compact Model
Nanbeige Lab et al. · Jul 2026
A production-grade looped model: 3B non-embedding parameters pretrained from scratch on 28T tokens with a Looped Transformer, then agentic SFT and RL. It outperforms larger models such as Qwen3.5-9B and Gemma4-12B on agentic benchmarks.
arXiv
Loopie
Loop the Loopies!
Zitian Gao et al. · Jul 2026
Two looped MoE models (20B-A2B and 6B-A0.6B) that close the long-standing gap where scaling parameters beats looping. In compute-matched ablations, including against a vanilla 30B-A3B model, Loopie clearly outperforms Transformer baselines.
arXiv
SMELT
SMELT: Scaling Laws for Compute-Matched MoE Looped Transformers
Shaowen Wang et al. · Sep 2026
Loops the middle half of an MoE Transformer twice while matching FLOPs, parameters and KV cache. Scaled to 54B non-embedding parameters, it saves 6.8–18% of training FLOPs on the compute-optimal frontier, with the largest gains on code.
arXiv
Retrofitting pretrained LLMs3 featured
Turning existing fixed-depth checkpoints into looped models, with or without training.
LoopUS
LoopUS: Recasting Pretrained LLMs into Looped Latent Refinement Models
Taekhyun Park et al. · May 2026
Recasts a pretrained LLM into encoder → looped reasoning block → decoder, with a selective gate against hidden-state drift, random deep supervision and a confidence head for early exit — better reasoning without pretraining a recurrent model from scratch.
arXivProject
Growing ↔ Looping
From Growing to Looping: A Unified View of Iterative Computation in LLMs
Ferdinand Kapl et al. · Feb 2026
Looped and depth-grown models share the same depth-wise signatures of iterative computation, and the two compose: looping the middle block of a depth-grown model at inference improves some reasoning primitives by up to 2× without ever training it to loop.
arXiv
Training-free loops
Training-Free Looped Transformers
Lizhang Chen et al. · May 2026
Loops a mid-stack block of a frozen checkpoint at test time, replacing naive re-application with smaller, damped Euler-style sub-steps. Gains across seven model families, e.g. +2.64 pp MMLU-Pro on Qwen3-4B-Instruct.
arXiv
Beyond language modeling6 featured
Looping carried to vision, robotics, world models, diffusion LMs, state-space models and RL.
RD-VLA
Recurrent-Depth VLA: Implicit Test-Time Compute Scaling of Vision-Language-Action Models via Latent Iterative Reasoning
Yalcin Tur et al. · Feb 2026
A weight-tied recurrent action head for vision-language-action models that stops on latent convergence. Tasks at 0% success with one iteration exceed 90% with four, with constant memory and up to 80× faster inference than token-reasoning VLAs.
arXivProject
RecursiveVLM
Looping Back to Move Forward: Recursive Transformers for Efficient and Flexible Large Multimodal Models
Ruihan Xu et al. · Feb 2026
Recursion for large multimodal models: a Recursive Connector fuses intermediate states with modality-specific projections, and a Monotonic Recursion Loss makes every extra loop help — +3% over standard Transformers and +7% over vanilla recursive baselines.
arXiv
Looped World Models
Looped World Models
Hongyuan Adam Lu et al. · Jun 2026
The first looped architecture for world modeling: a shared block iteratively refines latent environment states with depth adapted to each prediction step, for up to 100× parameter efficiency.
arXiv
LoopMDM
Looped Diffusion Language Models
Sanghyun Lee et al. · May 2026
Looping the early-middle layers of masked diffusion LMs matches same-size models with up to 3.3× fewer training FLOPs, beats them by up to 8.5 points on GSM8K, and lets inference compute scale with the loop count.
arXiv
CHASEAdapts Ouro's exit gate
CHASE: Cache-Hole-Adapted Skip Exit for Looped State-Space Language Models
Zhenxuan Yu et al. · Jul 2026
Loops Mamba and hybrid Mamba-Transformer blocks and brings Ouro's learned exit gate to state-space models; a cache-hole adaptation keeps perplexity near full compute while running about half the recurrent steps.
arXiv
LoopViT
LoopViT: Scaling Visual ARC with Looped Transformers
Wen-Jie Shu et al. · Feb 2026
Iterates a weight-tied conv-attention block as a latent chain of thought with a parameter-free, entropy-based exit. The 18M model reaches 65.8% on ARC-AGI-1, beating 73M-parameter ensembles.
arXivCode
All papers citing Ouro
158 papers in eight categories. Featured papers are marked.
Search citing papers
Reasoning, RL & decoding 11
Decoding Looped Transformers Better for (Almost) FreeWeihao Liu et al. · Oct 2026
Scheduling Recursive Reasoning in Looped TransformersBoyuan Wang et al. · Sep 2026
Improving Test-Time Scaling with Adaptive Looped TransformersFeaturedYichen You et al. · Sep 2026
Loop Dropout: Regularizing Shared Updates in Looped Language ModelsFeaturedZirui Zhu et al. · Sep 2026
LoopCD: Loop-wise Contrastive Decoding for Improving Reasoning in Looped Language ModelsFeaturedByeongho Yu et al. · Sep 2026
Steering Recurrent Reasoners at Inference Time with Readout FeedbackShunsuke Kamiya et al. · Aug 2026
Looped Language Models Improve Compositional Tool CallingFeaturedAndrei Cristian Popescu et al. · Aug 2026
LatentMT: Machine Translation with Latent ReasoningFeaturedWei-Rui Chen et al. · Jul 2026
Bridging the Gap Between Latent and Explicit Reasoning with Looped TransformersYing Fan et al. · Jun 2026
Stabilizing Recurrent Dynamics for Test-Time Scalable Latent Reasoning in Looped Language ModelsFeaturedXiao-Wen Yang et al. · May 2026
Prioritize the Process, Not Just the Outcome: Rewarding Latent Thought Trajectories Improves Reasoning in Looped Language ModelsFeaturedJonathan Williams and Esin Tureci · Feb 2026
Efficient inference & deployment 14
Hybrid Latent Attention for Looped Language ModelsFeaturedYuhan Chen et al. · Oct 2026
Enabling Dynamic Computation in Looped LMsFeaturedAayush Mishra et al. · Oct 2026
Loopy: Low-Bit Quantization Framework for Looped Language ModelsFeaturedZeyu LI et al. · Oct 2026
A Tilted Bowl Is Not a Slippery Slope: Compressing Looped ModelsSteven Kolawole et al. · Sep 2026
Quantizing Looped Transformers: Feedback Exposure and Calibration BlindnessNux Li · Sep 2026
FlashLoop: Fast and Memory-Efficient Looped Transformers via Lazy UpdatesFeaturedWanqi Yang and Shiwei Liu · Sep 2026
WaveFront Decoding: Parallelized Self-Speculative Decoding for Looped Language ModelsFeaturedHyeongju Ha and Jae-Joon Kim · Sep 2026
LoopSpec: Pipelined Self-Speculative Decoding for Looped TransformersFeaturedSangLyul Cho et al. · Sep 2026
Depth-adaptive Inference of Looped Language Models via Continuous Depth BatchingFeaturedKristian Schwethelm et al. · Aug 2026
Looped Latent Attention: Cross-Loop KV Compression for Looped TransformersFeaturedJames O' Neill and Fergal Reid · Jul 2026
N-vium: Mixture-of-Exits Transformer for Accelerated Exact GenerationAleksander Lorenc et al. · May 2026
Memory-Efficient Looped Transformer: Decoupling Compute from Memory in Looped Language ModelsFeaturedVictor Conchello Vendrell et al. · May 2026
LoopQ: Quantization for Recursive TransformersRui Fang et al. · May 2026
LASER: Low-Rank Activation SVD for Efficient RecursionEge Çakar et al. · Apr 2026
Architecture, stability & scaling laws 43
Towards Looped Models Done Right, Part II: Rethinking at Fixed PointsBenhao Huang et al. · Oct 2026
The Surprising Effectiveness of Shared Memory in Looped TransformersFeaturedGiovanni Monea et al. · Oct 2026
Scaling Laws for Looped Mixture of ExpertsYanbei Chen et al. · Sep 2026
Random Recursive ModelsJama Hussein Mohamud and Mirco Ravanelli · Sep 2026
Looped Transformers as OptimizersYulong Huang et al. · Sep 2026
How to Loop MoE: Flatten the Experts, Untie the AttentionShouren Wang et al. · Sep 2026
Storing Is Not Remembering: LSTM-UT and Bounded Gated Memory for Looped TransformersAras Kavuncu and Muhammad Burhan Hafez · Sep 2026
T-LoopFormer: Token-Level Elastic-Depth Looped Transformers for Latent Reasoning with Dynamic RoutingMingqian Yu et al. · Sep 2026
RecurTrace: Adaptive Latent Reasoning with Loop-Time MemoryYuxiang Wang et al. · Sep 2026
Allocating Recurrent Compute in Looped Language ModelsRuhai Lin et al. · Aug 2026
Gated Recurrent Transformers: Expressive Depth through Recurrent ModulationAmr Hegazy et al. · Aug 2026
Full-bandwidth transformerXi Wang et al. · Aug 2026
LoopMTP: A looped transformer guided by latent multi-token predictionBehzad Shomali et al. · Aug 2026
T^2MLR: Transformer with Temporal Middle-Layer RecurrenceZiyang Cai et al. · Jul 2026
DeepLoop: Depth Scaling for Looped TransformersShuzhen Li et al. · Jul 2026
Energy-guided Recursive ModelYifei Zhao and Ying Tang · Jul 2026
DiscoLoop: Looping Discrete Embeddings and Continuous Hidden States for Multi-hop ReasoningHengyu Fu et al. · Jul 2026
Stabilizing Extrapolation in Looped Transformers via Learned Stochastic StoppingHsun-Yu Kuo et al. · Jun 2026
Fixed-Point Reasoners: Stable and Adaptive Deep Looped TransformersSajad Movahedi et al. · Jun 2026
On the Residual Scaling of Looped Transformers: Stability and TransferabilityShaowen Wang et al. · Jun 2026
Tying the Loop -- Tied Expert Layers in Mixture-of-Experts Language ModelsMartin Jaggi · Jun 2026
LoopMoE: Unifying Iterative Computation with Mixture-of-Experts for Language ModelingWenkai Chen et al. · Jun 2026
A Dual-Path Architecture for Scaling Compute and Capacity in LLMsMarkus Frey et al. · May 2026
Do Language Models Need Sleep? Offline Recurrence for Improved Online InferenceSangyun Lee et al. · May 2026
Equilibrium Reasoners: Learning Attractors Enables Scalable ReasoningBenhao Huang et al. · May 2026
HRM-Text: Efficient Pretraining Beyond ScalingGuan Wang et al. · May 2026
Solve the Loop: Attractor Models for Language and ReasoningFeaturedJacob Fein-Ashley and Paria Rashidinejad · May 2026
Simply Stabilizing the Loop via Fully Looped TransformerRao Fu et al. · May 2026
Sparse Layers are Critical to Scaling Looped Language ModelsFeaturedRyan Lee et al. · May 2026
Hyperloop TransformersFeaturedAbbas Zeitoun et al. · Apr 2026
How Much Is One Recurrence Worth? Iso-Depth Scaling Laws for Looped Language ModelsFeaturedKristian Schwethelm et al. · Apr 2026
One Step Forward and K Steps Back: Better Reasoning with Denoising Recursion ModelsChris Cameron et al. · Apr 2026
Parcae: Scaling Laws For Stable Looped Language ModelsFeaturedHayden Prairie et al. · Apr 2026
Exploration of Fast-Slow Latent Recurrence for Train-Short, Test-Long GeneralizationShota Takashiro et al. · Apr 2026
Sparse Growing Transformer: Training-Time Sparse Depth Allocation via Progressive Attention LoopingYao Chen et al. · Mar 2026
Adaptive Loops and Memory in Transformers: Think Harder or Know More?Markus Frey et al. · Mar 2026
AdaPonderLM: Gated Pondering Language Models with Token-Wise Adaptive DepthShixiang Song et al. · Mar 2026
SpiralFormer: Looped Transformers Can Learn Hierarchical Dependencies via Multi-Resolution RecursionChengting Yu et al. · Feb 2026
LoopFormer: Elastic-Depth Looped Transformers for Latent Reasoning via Shortcut ModulationFeaturedAhmadreza Jeddi et al. · Feb 2026
Depth-Recurrent Attention Mixtures: Giving Latent Reasoning the Attention it DeservesJonas Knupp et al. · Jan 2026
VersatileFFN: Achieving Parameter Efficiency in LLMs via Adaptive Wide-and-Deep ReuseYing Nie et al. · Dec 2025
Think-at-Hard: Dynamic Looped Transformers for Improved ReasoningTianyu Fu et al. · Nov 2025
White Matter: All-to-All Cross-Layer Connections via KV MixingWen-Bo Zhang and Xiang Ren
Looped models at scale 4
SMELT: Scaling Laws for Compute-Matched MoE Looped TransformersFeaturedShaowen Wang et al. · Sep 2026
Nanbeige4.2-3B: Unlocking Agentic Capabilities in a Compact ModelFeaturedNanbeige Lab et al. · Jul 2026
Loop the Loopies!FeaturedZitian Gao et al. · Jul 2026
LoopCoder∞: Scaling Code Intelligence via Looped Language ModelsJian Yang et al.
Retrofitting pretrained LLMs 3
Training-Free Looped TransformersFeaturedLizhang Chen et al. · May 2026
LoopUS: Recasting Pretrained LLMs into Looped Latent Refinement ModelsFeaturedTaekhyun Park et al. · May 2026
From Growing to Looping: A Unified View of Iterative Computation in LLMsFeaturedFerdinand Kapl et al. · Feb 2026
Beyond language modeling 20
ALoDLM: Adaptively Looped Diffusion Language ModelsLiancheng Fang et al. · Oct 2026
Looped Actor: Depth-Recurrent Reasoning Models for Reinforcement LearningT. Konstantin Rusch et al. · Sep 2026
Procedural Core: A Compact Recurrent Initialization for Vision TransformersZachary Shinnick et al. · Sep 2026
FlexLoop: Depth-Elastic Looped Policies for Adaptive Test-Time Computation in Deep RLXun Wang et al. · Sep 2026
CHASE: Cache-Hole-Adapted Skip Exit for Looped State-Space Language ModelsFeaturedZhenxuan Yu et al. · Jul 2026
Looped World ModelsFeaturedHongyuan Adam Lu et al. · Jun 2026
Rethinking Depth: A study of the Recursive-Transformer for Speech RecognitionThomas Rolland et al. · Jun 2026
Looped Diffusion Language ModelsFeaturedSanghyun Lee et al. · May 2026
LACO: Adaptive Latent Communication for Collaborative DrivingTianhao Chen et al. · May 2026
PERL: Parameter Efficient Reasoning in CLIP Latent SpaceSimone Carnemolla et al. · May 2026
TTE-Flash: Accelerating Reasoning-based Multimodal Representations via Think-Then-Embed TokensJianpeng Cheng et al. · May 2026
Reshape and Recur: Improving SSMs with Input Reshaping and Depth RecurrenceMónika Farsang et al. · May 2026
LoopVLA: Learning Sufficiency in Recurrent Refinement for Vision-Language-Action ModelsBoyang Shen et al. · May 2026
SMolLM: Small Language Models Learn Small Molecular GrammarAkhil Jindal and Harang Ju · May 2026
Recursive Multi-Agent SystemsJiaru Zou et al. · Apr 2026
LoopCTR: Unlocking the Loop Scaling Power for Click-Through Rate PredictionJiakai Tang et al. · Apr 2026
Looping Back to Move Forward: Recursive Transformers for Efficient and Flexible Large Multimodal ModelsFeaturedRuihan Xu et al. · Feb 2026
Recurrent-Depth VLA: Implicit Test-Time Compute Scaling of Vision-Language-Action Models via Latent Iterative ReasoningFeaturedYalcin Tur et al. · Feb 2026
LoopViT: Scaling Visual ARC with Looped TransformersFeaturedWen-Jie Shu et al. · Feb 2026
AdaPerceiver: Transformers with Adaptive Width, Depth, and TokensPurvish Jajal et al. · Nov 2025
Analysis, interpretability & theory 27
Shared Weights, Selected Computations: How Looped Transformers Route What Each Loop DoesJiaju Wu et al. · Sep 2026
Transformers Stop Thinking Too Early, and a Tiny LoRA Fixes ItZehao Jin et al. · Sep 2026
What Makes Recurrence Effective in Looped Language Models?Xinlin Zhuang et al. · Sep 2026
Stream Recursion Model (SRM)Asael Sorensen et al. · Sep 2026
Prediction Dynamics in Depth-Recurrent Language ModelsXinyue Luo and Fei Yu · Sep 2026
Right Direction, Wrong Step: Geometric Analysis of Finite-Step Failure in Looped TransformersZhihao Guo et al. · Sep 2026
Looped Transformers under the Jacobian Lens: Does the Global Workspace Survive Recurrence?Wenlong Wang and Fergal Reid · Sep 2026
Evaluating Tiny Recursive Models Across Training for Code GenerationAnjani Sirivella et al. · Aug 2026
Why Knowing Both Hops Is Not Enough: Understanding Two-Hop Generalization in Language ModelsZili Zhang et al. · Aug 2026
Operational Proto-Introspection in Looped Language Models: Process-Quality Taps, Executable Branching, and the Readout-Control BoundaryJan Kirin · Jul 2026
Per-Token Fixed-Point Convergence in Depth-Recurrent TransformersJoe Logan · Jul 2026
Adaptive Depth in Looped Transformers: Diagnosing Learned Halting Gates and Trajectory ReadoutsAndrei Cristian Popescu et al. · Jul 2026
Repeated Shared Access Enables Grokking, but Edit Propagation Depends on an Addressable MemoryYanan Niu · Jun 2026
Dense Supervision Is Not Enough: The Readout Blind Spot in Looped Language ModelsRituraj Sharma and Tu Vu · Jun 2026
Chain-of-Thought and Compressed Looped Transformers: A Memory-Budget SeparationHaozhou Zhang · May 2026
The Power of Power Law: Asymmetry Enables Compositional ReasoningZixuan Wang et al. · Apr 2026
The Topological Trouble With TransformersMichael C. Mozer et al. · Apr 2026
A Mechanistic Analysis of Looped Reasoning Language ModelsHugh Blayney et al. · Apr 2026
Loop, Think, & Generalize: Implicit Reasoning in Recurrent-Depth TransformersHarsh Kohli et al. · Apr 2026
Are Latent Reasoning Models Easily Interpretable?Connor Dilgren and Sarah Wiegreffe · Apr 2026
Step-resolved data attribution for looped transformersGeorgios Kaissis et al. · Feb 2026
Understanding Dynamic Compute Allocation in Recurrent TransformersIbraheem Muhammad Moosa et al. · Feb 2026
Emergent Search and Backtracking in Latent Reasoning ModelsJasmine Cui and Charles Ye · Feb 2026
Loop as a Bridge: Can Looped Transformers Truly Link Representation Space and Natural Language Outputs?Guanxu Chen et al. · Jan 2026
Transformers as Intrinsic Optimizers: Forward Inference through the Energy PrincipleRuifeng Ren et al. · Nov 2025
A Formal Comparison Between Chain of Thought and Latent ThoughtKevin Xu and Issei Sato · Sep 2025
Beyond Memorization: Extending Reasoning Depth with Recurrence, Memory and Test-Time Compute ScalingIvan Rodkin et al. · Aug 2025
Latent reasoning & related work 36
What Matters for Latent Reasoning with Flow MatchingYassine Ouali et al. · Oct 2026
LatentHarness: Learning Latent Actions for Memory and Reasoning via Counterfactual Policy DistillationXiaoqiang Wang et al. · Sep 2026
Making LLMs Say What They Think: Measuring and Improving CoT-Interpretability AlignmentYihuai Hong et al. · Sep 2026
Principled Thoughts for Latent Recursive LLM SystemsFahd Seddik and Fatemeh Fard · Sep 2026
Giving Credit Where It's Due: Redundancy-Aware Learning for Efficient ReasoningYuqing Zhou et al. · Sep 2026
Emergent Models: Intelligence from Tiny SubstratesGiacomo Bocchese et al. · Aug 2026
The Weight of Silence: A Causal Case for Weights Over the Scratchpad in Latent Chess ReasoningIshan S. Kshirsagar · Jul 2026
Training Continuous Chain of Thought Models: A Tale of Two RegimesVarun Yerram et al. · Jul 2026
Hidden Decoding at Scale: Latent Computation Scaling for Large Language ModelsAiwei Liu et al. · Jul 2026
Think in Latent, Explain in Language: Self-Explainable Latent ReasoningDayuan Zhao et al. · Jul 2026
Why Struggle with Continuous Latents? Interpretable Discrete Latent Reasoning via Rendered CompressionShuochen Chang et al. · Jun 2026
What Makes Effective Supervision in Latent Chain-of-Thought: An Information-Theoretic AnalysisXinghao Chen et al. · Jun 2026
Latent Reasoning with Normalizing FlowsGuancheng Tu et al. · Jun 2026
Unlocking the Black Box of Latent Reasoning: An Interpretability-Guided Approach to InterventionShuochen Chang et al. · May 2026
Incremental BPE TokenizationShenghu Jiang and Ruihao Gong · May 2026
On the Cost and Benefit of Chain of Thought: A Learning-Theoretic PerspectiveYue Zhang et al. · May 2026
Towards Generalization of Block Attention via Automatic Segmentation and Block DistillationShuaiyi Li et al. · May 2026
Scratchpad Patching: Decoupling Compute from Patch Size in Byte-Level Language ModelsLin Zheng et al. · May 2026
Efficient Pre-Training with Token SuperpositionBowen Peng et al. · May 2026
LEPO: Latent Reasoning Policy Optimization for Large Language ModelsYuyan Zhou et al. · Apr 2026
NeuroAI and Beyond: Bridging Between Advances in Neuroscience and Artificial IntelligenceAnthony Zador et al. · Apr 2026
The Silent Thought: Modeling Internal Cognition in Full-Duplex Spoken Dialogue Models via Latent ReasoningDonghang Wu et al. · Mar 2026
Beyond Test-Time Memory: State-Space Optimal Control for LLM ReasoningPeihao Wang et al. · Mar 2026
Towards efficient and reliable artificial intelligence through neuromorphic principlesB. Rajendran et al. · Feb 2026
ThinkRouter: Efficient Reasoning via Routing Thinking between Latent and Discrete SpacesXin Xu et al. · Feb 2026
Latent Thoughts Tuning: Bridging Context and Reasoning with Fused Information in Latent TokensWeihao Liu et al. · Feb 2026
Pretraining with Token-Level Adaptive Latent Chain-of-ThoughtBoyi Zeng et al. · Feb 2026
Dynamics Within Latent Chain-of-Thought: An Empirical Study of Causal StructureZirui Li et al. · Feb 2026
Internalizing LLM Reasoning via Discovery and Replay of Latent ActionsZhenning Shi et al. · Feb 2026
LaDi-RL: Latent Diffusion Reasoning Prevents Entropy Collapse in Reinforcement LearningHaoqiang Kang et al. · Feb 2026
Residual Context Diffusion Language ModelsYuezhou Hu et al. · Jan 2026
Beyond Test-Time Training: Learning to Reason via Hardware-Efficient Optimal ControlPeihao Wang et al. · 2026
Diversity or Precision? A Deep Dive into Next Token PredictionHaoyuan Wu et al. · Dec 2025
Catch Your Breath: Adaptive Computation for Self-Paced Sequence ProductionAlexandre Galashov et al. · Oct 2025
LaDiR: Latent Diffusion Enhances LLMs for Text ReasoningHaoqiang Kang et al. · Oct 2025
Reasoning Beyond Language: A Comprehensive Survey on Latent Chain-of-Thought ReasoningXinghao Chen et al. · May 2025
No papers match your search.
Citation data from Semantic Scholar, retrieved October 8, 2026; categories and summaries curated by the Ouro team. Figures are reproduced from the respective arXiv papers for illustration and remain © their authors. Missing your paper? Open an issue.
Citation
BibTeX
If you find Ouro useful, please cite:
Copy
@article{zhu2025scaling,
title = {Scaling Latent Reasoning via Looped Language Models},
author = {Zhu, Rui-Jie and Wang, Zixuan and Hua, Kai and Zhang, Tianyu and Li, Ziniu and Que, Haoran and Wei, Boyi and Wen, Zixin and Yin, Fan and Xing, He and Li, Lu and Shi, Jiajun and Ma, Kaijing and Li, Shanda and Kergan, Taylor and Smith, Andrew and Qu, Xingwei and Hui, Mude and Wu, Bohong and Min, Qiyang and Huang, Hongzhi and Zhou, Xun and Ye, Wei and Liu, Jiaheng and Yang, Jian and Shi, Yunfeng and Lin, Chenghua and Zhao, Enduo and Cai, Tianle and Zhang, Ge and Huang, Wenhao and Bengio, Yoshua and Eshraghian, Jason},
journal = {arXiv preprint arXiv:2510.25741},
year = {2025}
}
Ouro · Looped Language Models. Models are released for research purposes under Apache-2.0.
Website originally adapted from Nerfies; licensed under CC BY-SA 4.0.
Close