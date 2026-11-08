Ornith-1.5: From Self-Scaffolding to Self-Improvement | Ornith Blog
Ornith-1.5: From Self-Scaffolding to Self-Improvement
Aug. 2026
Twitter
Hugging Face
Today, we are introducing Ornith-1.5, a major step toward building foundation models through end-to-end self-improvement. Ornith-1.5 extends the self-scaffolding framework
introduced in Ornith-1.0 into a more complete self-improvement loop: the model
proposes new tasks, generates task-specific scaffolds, and produces solution rollouts for reinforcement learning, continuously creating new learning
experiences from which it can improve.
Ornith-1.5 spans three model scales: 397B MoE, 35B MoE, and 9B Dense. It extends Ornith-1.0, which was developed on top of Qwen3.5 and Gemma 4 with additional continued
pretraining (CPT), mid-training, and post-training. Ornith-1.5 achieves state-of-the-art performance among open-source models of comparable size across a broad range of
reasoning, coding, and agentic benchmarks. Ornith-1.5-397B scores 86.1 on Terminal-Bench 2.1 and 56.0 on DeepSWE, performing on par with Claude Opus 4.8 (85.0 and 59.0) while
outperforming leading open-source models of similar scale, including GLM-5.2 (82.7 and 46.2) and DeepSeek-V4-Flash-0731 (82.7 and 54.4). At the other end of the spectrum,
Ornith-1.5-9B, with its quantized Ornith-1.5-9B-Mobile version, can be readily deployed on iPhone and Android devices while substantially outperforming larger models such as
Gemma 4-31B and Qwen 3.6-35B.
At the flagship scale, Ornith-1.5-397B achieves 86.1 on Terminal-Bench 2.1 and 56 on DeepSWE, matching Claude Opus 4.8 on both benchmarks and outperforming leading
open-source models of similar size, including GLM-5.2 and DeepSeek-V4-Flash-0731.
Ornith-1.5-35B significantly outperforms its similar-sized peer Qwen 3.6-35B across all coding and agentic benchmarks, and despite activating only 3B parameters per token,
it also outperforms dense models—Gemma 4-31B and Meta’s Muse Glimmer-30B—by wide margins on agentic coding (68.5 vs. 43.4 and 51.7 on Terminal-Bench 2.1; 79.0 vs. 52.0 and
76.0 on SWE-Bench Verified).
The edge-deployable Ornith-1.5-9B also delivers remarkably strong results, achieving 47.0 on Terminal-Bench 2.1 and 70.6 on SWE-Bench Verified. Despite being a compact
9B-parameter model, it matches or exceeds the performance of much larger models such as Gemma 4-31B and Qwen 3.6-35B.
Self-Improvement through Self-Generated Tasks, Harnesses, and Solutions
Ornith-1.5 extends Ornith-1.0 by expanding the self-improvement loop from scaffold and rollout optimization to jointly optimizing task generation, scaffold construction, and
solution rollouts. Rather than relying on a fixed set of human-curated tasks and manually designed harnesses, Ornith-1.5 continuously generates new training tasks, discovers
effective strategies for solving them, and improves the policy through reinforcement learning.
Each training cycle proceeds in three stages. Given an environment or codebase, high-level instructions about the task type, and access to the model’s previous task-solving
history, the system proposes progressively harder tasks that go beyond what the model has already solved, exposing capability gaps and continuously pushing the training
frontier.
For each task, the model then generates or refines a task-specific scaffold—the instructions, tools, decomposition strategy, and orchestration used to approach the problem.
Conditioned on the task and scaffold, the policy produces a solution rollout. Reward from the rollout is propagated across all three stages, so the system learns not only to
produce better solutions, but also to generate more useful training tasks and construct more effective scaffolds.
Repeated over training, this creates a closed self-improvement loop in which stronger policies enable the generation of harder and more informative tasks, evolving scaffolds
discover better ways to elicit the model’s capabilities, and higher-quality rollouts provide increasingly effective learning signals. Instead of relying on a static training
distribution or hand-engineered agent design, Ornith-1.5 continually expands its own curriculum and adapts its problem-solving strategies, driving sustained capability gains
across reasoning, coding, and agentic tasks.
Task Reward
For the question → scaffold → rollout setup, we define the task reward using three signals: validity, frontier difficulty, and novelty. Let
\(q\) denote a generated question, \(s\) its scaffold, and \(\{\tau_i\}_{i=1}^{N}\) a set of solution rollouts. We define
\[ R_{\text{task}} = \underbrace{V(q,s)}_{\text{Is it valid and verifiable?}} \times \underbrace{D\!\left(q,s,\{\tau_i\}_{i=1}^{N}\right)}_{\text{Is it at the right
difficulty?}} \times \underbrace{N(q)}_{\text{Is it sufficiently novel?}}. \]
Here, \(V\) measures whether the generated task and scaffold form a valid and verifiable learning environment, \(D\) measures whether the task lies near the model’s current
capability frontier based on rollout performance, and \(N\) measures novelty relative to previously generated or trained-on tasks. The multiplicative formulation encourages the
proposer to generate tasks that satisfy all three properties simultaneously: valid, appropriately challenging, and non-redundant.
Validity and Verifiability
A useful task must form a well-defined learning environment. The question should be coherent and solvable, while the scaffold should execute correctly and reliably evaluate
candidate solutions. We define
\[ V(q,s) \in [0,1], \]
based on checks such as whether the scaffold runs successfully, high-confidence solutions pass, clearly incorrect solutions fail, and the evaluation matches the task
specification. Validity can also be treated as a hard gate:
\[ V(q,s)=0 \quad\Rightarrow\quad R_{\text{task}}=0. \]
This prevents malformed tasks or unreliable scaffolds from receiving reward simply because they appear difficult.
Frontier Difficulty
Among valid tasks, the most useful ones are neither trivial nor impossible. We estimate difficulty directly from the model’s rollouts.
For each task, we sample \(N\) rollouts and compute the empirical success rate
\[ p = \frac{1}{N} \sum_{i=1}^{N} \mathbf{1}\!\left[s(q,\tau_i)=\text{success}\right]. \]
We then reward tasks whose success rate is close to a target frontier \(p^*\):
\[ D(q,s,\{\tau_i\}) = \exp\!\left(-\frac{(p-p^*)^2}{2\sigma^2}\right). \]
\(p^*\) is set to 0.2, which favors tasks that are challenging but still yield enough successful trajectories for reinforcement learning. As the model improves and solves a
task more reliably, its reward naturally decreases, pushing the generator toward harder problems.
Novelty and Diversity
Frontier difficulty alone may lead the model to repeatedly generate small variations of the same tasks. We therefore add a novelty term:
\[ N(q) = 1 - \max_{q_j \in \mathcal{B}} \operatorname{sim}(q,q_j), \]
where \(\mathcal{B}\) is a buffer of previously generated or trained-on tasks. Novelty should remain secondary to validity and difficulty: its role is to reduce redundancy, not
to reward arbitrarily unusual tasks.
Together, these signals encourage the proposer to generate tasks that are valid, verifiable, challenging but learnable, and sufficiently diverse. Because
frontier difficulty is measured using the current model’s own rollouts, the resulting curriculum automatically evolves with model capability.
Harness and Rollout Rewards
For a generated question \(q\), the harness \(h\) is rewarded for providing an evaluation environment that is
aligned with the task, faithful to solution quality, and resistant to reward hacking:
\[ R_{\text{harness}} = \underbrace{C(q,h)}_{\text{Task alignment}} \times \underbrace{F\!\left(h,\{\tau_i\}\right)}_{\text{Reward fidelity}} \times
\underbrace{H(h)}_{\text{Hack resistance}}. \]
Here, \(C\) measures whether the harness faithfully reflects the task specification, \(F\) measures whether its rewards track the true quality of candidate solutions, and \(H\)
measures its resistance to evaluator failures, shortcuts, and reward-hacking behaviors.
Each rollout \(\tau_i\) is scored directly by the generated harness:
\[ R_{\text{rollout}}(\tau_i) = \underbrace{h(q,\tau_i)}_{\text{Task success}}. \]
For verifiable tasks, this can be a binary pass/fail reward; for richer environments, it can combine correctness, task completion, efficiency, and constraint satisfaction.
Question generation, harness generation, and solution rollouts are all optimized with GRPO using their respective rewards, enabling the three stages to improve
jointly within the same self-improvement loop.
Full Table
Ornith-1.5-397B
Benchmark
Ornith-1.5
(397B)
DeepSeek-V4-Flash-0731
(284B)
GLM-5.2
(753B)
Claude Opus 4.8
Kimi K3
(2.8T)
Ornith-1.0
(397B)
Coding
Terminal Bench 2.1 (Terminus-2)
86.1
82.7
81
85
88.3
77.5
Terminal Bench 2.1 (Claude Code)
85.2
81.8
82.7
78.9
–
78.2
SWE-bench Verified
86
81.6
83
85.8
86.2
82.4
SWE-bench Pro
65.1
64.4
62.1
68
–
62.2
SWE-bench Multilingual
79.6
77.9
78.4
75.7
–
78.9
DeepSWE
56
54.4
46.2
59
67.5
8
Frontier-Bench v0.1
13.5
6.1
5.1
21.1
23
2.7
NL2Repo
59.5
54.2
48.9
69.7
–
48.2
SWE Atlas – QnA
55.6
51.6
50
59.7
59.7
41.2
Reasoning
HLE (no tools)
44.6
35
40.5
49.8
43.5
30.2
HLE (with tools)
56.1
50.8
54.7
57.9
56
47.5
GPQA Diamond
92.8
91.4
91.2
93.6
93.5
88.1
Agentic
MCP-Atlas
80
74.6
77.8
82.2
82.3
76.4
Toolathlon-Verified
71.2
70.3
48.2
76.2
73.2
43.2
WideSearch
80.8
77.3
79
72.9
–
75.2
BrowseComp
86.6
84.8
85.6
84.3
91.2
79.7
ClawEval
81.4
77.6
78.8
80.2
–
77.1
Ornith-1.5-35B
Benchmark
Ornith-1.5-35B-A3B
Ornith-1.0-35B-A3B
Qwen3.6-35B-A3B
Gemma-4-31B
(dense)
Muse-Glimmer-30B
(dense)
Qwen3.5-397B
(397B)
Coding
Terminal Bench 2.1 (Terminus-2)
67.8
64.2
52.5
42.1
51.7
53.5
Terminal Bench 2.1 (Claude Code)
68.5
62.8
49.2
–
–
48.6
SWE-bench Verified
79
75.6
73.4
52
76
76.4
SWE-bench Pro
59.6
50.4
49.5
35.7
51.2
51.6
SWE-bench Multilingual
71.4
69.3
67.2
51.7
–
69.3
DeepSWE
22
0
0
–
–
1
Frontier-Bench v0.1
5.1
1.4
1.4
–
–
1.4
NL2Repo
46.2
34.6
29.4
15.5
–
36.8
SWE Atlas – QnA
39.8
37.1
15.5
–
–
20.4
Reasoning
HLE (no tools)
25.6
20.8
21.4
19.5
22
28.7
HLE (with tools)
33.4
30.1
28.9
26.5
–
48.3
GPQA Diamond
89.2
86.2
86
84.3
83.5
88.4
Agentic
MCP-Atlas
70.2
64.4
62.8
55
75.5
72.3
Toolathlon-Verified
48.7
42.4
41.7
40.8
–
38.3
WideSearch
67.8
63.4
60.1
54.2
–
74
BrowseComp
67.6
63.5
62
–
–
78.6
ClawEval
72.5
69.8
68.7
48.5
–
70.7
Ornith-1.5-9B
Benchmark
Ornith-1.5-9B
Ornith-1.0-9B
Qwen3.5-9B
Qwen3.6-35B-A3B
Gemma-4-31B
(dense)
Coding
Terminal Bench 2.1 (Terminus-2)
46.2
43.1
21.3
52.5
42.1
Terminal Bench 2.1 (Claude Code)
47
40.6
18.9
49.2
–
SWE-bench Verified
70.6
69.4
53.2
73.4
52
SWE-bench Pro
47.5
42.9
31.3
49.5
35.7
SWE-bench Multilingual
54.4
52
39.7
67.2
51.7
NL2Repo
32.4
27.2
16.2
29.4
15.5
SWE Atlas – QnA
20.6
17.9
9.2
15.5
–
Reasoning
HLE (no tools)
20.2
16.8
14.7
21.4
19.5
HLE (with tools)
30.5
26.4
24.5
28.9
26.5
GPQA Diamond
86.4
82.5
81.7
86
84.3
Agentic
MCP-Atlas
54.2
49.4
46.8
62.8
55
Toolathlon-Verified
41.2
33.4
29.6
41.7
52.8
WideSearch
59.5
55.8
53.6
60.1
54.2
BrowseComp
56.4
44.8
41.5
62
–
ClawEval
66.5
63.1
53.2
68.7
48.5
Footnote
All results reported for Ornith-1.5 are averaged over five independent runs.
Terminal-Bench 2.1 (Terminus-2): We evaluate Terminal-Bench 2.1 using the Harbor/Terminus-2 framework with parser=json, temperature=1.0, top_p=1.0, and a 128K context
window. Each run uses a 4-hour timeout with 32 CPU cores and 48GB RAM, and results are averaged over 5 runs. We adjust the Qwen chat template to ensure consistency between
training and inference, and modify Harbor to align with vLLM’s reasoning_content key.
Terminal-Bench 2.1 (Claude Code): We evaluate Terminal-Bench 2.1 using Claude Code 2.1.126 with parser=json, temperature=1.0, top_p=1.0, max_new_tokens=131072. Results are
averaged over 5 runs. Again, Qwen chat template needs to be modified.
SWE-Bench Verified, Pro and Multilingual: using OpenHands harness with temp=1.0, top_p=0.95, 256k context window. Anti-hacking safeguards are applied throughout evaluation:
Git history is removed from the local repository image to prevent access to prior solutions or commits; network access is disabled, preventing the model from retrieving
external information or resources.
DeepSWE: Evaluated using the Claude Code harness with temperature=1.0, top_p=0.95, and a 256K context window.
SWE Atlas QnA, RF, TW: using mini SWE agent harness with temp=1.0, top_p=0.95, 128K context window. Results are averaged over 5 runs.
NL2Repo: with temperature=1.0, top_p=1.0, 400K context, 48K output. Access to specified GitHub repositories and pip packages is blocked to prevent reward hacking.
HLE: Evaluated using Claude 4.6 Opus as the judge model.
MCP-Atlas: All models were evaluated in thinking mode on the 500-task public subset, with a 10-minute timeout per task. We use Claude 4.8 Opus as the judge model.
Tool-Decathlon: We use the official evaluation service with the maximum token limit set to 128K.
ClawEval: An agentic code benchmark over real-user task distributions; temp=0.6 and 256K context.
© 2026 Ornith Team. All rights reserved.