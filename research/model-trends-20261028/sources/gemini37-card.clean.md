Gemini 3.7 Flash - Model Card — Google DeepMind
Skip to main content
Explore our next generation AI systems
Explore models
Gemini
Gemini
Build intelligent agents
Gemini Omni
Create anything from anything
Nano Banana
Create and edit detailed images
Gemini Audio
Talk, create and control audio
Specialized models
Veo
Generate cinematic video with audio
Lyria
Generate high fidelity music and audio
Genie 3
Generate and explore interactive worlds
Gemini Robotics
Perceive, reason, use tools and interact
Open models
Gemma
Build responsible AI applications at scale
Our latest AI breakthroughs and updates from the lab
Explore research
Breakthroughs
SIMA 2
An agent that plays, reasons, and learns with you
Genie 4
Generate and explore interactive worlds
AlphaGo
Mastering the game of Go
Gemini Robotics
Perceive, reason, use tools and interact
Learn more
Evals
Publications
Responsibility
Frontier safety
Unlocking a new era of discovery with AI
Explore science
Breakthroughs
AlphaFold
Predict protein structures with high accuracy
AlphaGenome
Using AI to understand the human genome
WeatherNext
Fast and accurate AI weather forecasting
AlphaEarth
Map our planet in unprecedented detail
AlphaEvolve
Design advanced algorithms for math and applications in computing
Learn more
Gemini for Science
Experimental Tools
Science on Antigravity
Our mission is to build AI responsibly to benefit humanity
About Google DeepMind
Responsibility
Ensuring AI safety through proactive security, even against evolving threats
News
Discover our latest AI breakthroughs, projects, and updates
Careers
We’re looking for people who want to make a real, positive impact on the world
Learn more
Education
Our National Partnerships for AI
Accelerator programs
The Podcast
DeepMind Institute
Models
Explore our next generation AI systems
Explore models
Gemini
Gemini
Build intelligent agents
Gemini Omni
Create anything from anything
Nano Banana
Create and edit detailed images
Gemini Audio
Talk, create and control audio
Specialized models
Veo
Generate cinematic video with audio
Lyria
Generate high fidelity music and audio
Genie 3
Generate and explore interactive worlds
Gemini Robotics
Perceive, reason, use tools and interact
Open models
Gemma
Build responsible AI applications at scale
Research
Our latest AI breakthroughs and updates from the lab
Explore research
Breakthroughs
SIMA 2
An agent that plays, reasons, and learns with you
Genie 4
Generate and explore interactive worlds
AlphaGo
Mastering the game of Go
Gemini Robotics
Perceive, reason, use tools and interact
Learn more
Evals
Publications
Responsibility
Frontier safety
Science
Unlocking a new era of discovery with AI
Explore science
Breakthroughs
AlphaFold
Predict protein structures with high accuracy
AlphaGenome
Using AI to understand the human genome
WeatherNext
Fast and accurate AI weather forecasting
AlphaEarth
Map our planet in unprecedented detail
AlphaEvolve
Design advanced algorithms for math and applications in computing
Learn more
Gemini for Science
Experimental Tools
Science on Antigravity
About
Our mission is to build AI responsibly to benefit humanity
About Google DeepMind
Learn more
Education
Our National Partnerships for AI
Accelerator programs
The Podcast
DeepMind Institute
Responsibility
Ensuring AI safety through proactive security, even against evolving threats
News
Discover our latest AI breakthroughs, projects, and updates
Careers
We’re looking for people who want to make a real, positive impact on the world
Build with Gemini Try Gemini
Google DeepMind
Google AI
Learn about all our AI
Google DeepMind
Explore the frontier of AI
Google Labs
Try our AI experiments
Google Research
Explore our research
Products and apps
Gemini app
Chat with Gemini
Google AI Studio
Build with our next-gen models
Google Antigravity
Our agentic development platform
Models
Research
Science
About
Build with Gemini
Try Gemini
Published 13 August 2026
Gemini 3.7 Flash
Learn more
View PDF version
Model Cards are intended to provide essential information on Gemini models, including known limitations, mitigation approaches, and safety performance. Model cards may be updated from time to time; for example, to include updated evaluations as the model is improved or revised. See the Google DeepMind site for a comprehensive list of model cards.
Published: August 2026
Model Information
Model Data
Implementation and Sustainability
Distribution
Evaluation
Intended Usage and Limitations
Ethics and Content Safety
Model Information
Description
Gemini 3.7 Flash is the next iteration in the Gemini 3 model family, featuring algorithmic improvements to its core reasoning foundation and support for agentic video understanding. It supports customizable thinking configurations to control the mix of quality, cost and latency.
Model dependencies
Gemini 3.7 Flash is based on Gemini 3.6 Flash.
Inputs
Text strings (e.g., a question, a prompt, document(s) to be summarized), images, audio, and video files, with a token context window of up to 1M.
Outputs
Text, with a 64K token output.
Architecture
Gemini 3.7 Flash is based on Gemini 3.6 Flash. For more information about the model architecture for Gemini 3.7 Flash, see the Gemini 3.6 Flash model card.
Model Data
Training Dataset
Gemini 3.7 Flash is based on Gemini 3.6 Flash. For more information about the training dataset for Gemini 3.7 Flash, see the Gemini 3.6 Flash model card.
Training Data Processing
For more information about the training data processing for Gemini 3.7 Flash, see the Gemini 3.6 Flash model card.
Implementation and Sustainability
Hardware
Gemini 3.7 Flash is based on Gemini 3.6 Flash. For more information about the hardware for Gemini 3.7 Flash and our continued commitment to operate sustainably, see the Gemini 3.6 Flash model card.
Software
Gemini 3.7 Flash is based on Gemini 3.6 Flash. For more information about the software for Gemini 3.7 Flash, see the Gemini 3.6 Flash model card.
Distribution
Gemini 3.7 Flash is distributed in the following channels; respective documentation shared in line:
Gemini App - Spark
Gemini Enterprise App
Gemini Enterprise Agent Platform
Google AI Studio
Gemini API
Google Antigravity
Our models are available to downstream providers via an application program interface (API) and subject to relevant terms of use. There is no required hardware or software to use the model. For AI Studio and Gemini API, see the Gemini API Additional Terms of Service; for Gemini Enterprise Agent Platform, see Google Cloud Platform Terms of Service. For more information, see Gemini Model API instructions and Gemini API quickstart.
Evaluation
Approach
Gemini 3.7 Flash was evaluated across a range of benchmarks, including reasoning, coding, agentic tool use, multimodal capabilities, multi-lingual performance, and long-context. Additional benchmarks and details on approach, results and their methodologies can be found at: deepmind.com/models/evals-methodology/gemini-3-7-flash.
Results
Results as of August 2026 are listed below:
BenchmarkNotesGemini 3.7 FlashGemini 3.6 FlashClaude Sonnet 5GPT-5.6 TerraMuse Spark 1.2
Input price $/1M tokens$0.75*$0.75*$2.00$2.00$1.25
Output price $/1M tokens$3.75*$3.75*$10.00$12.00$4.25
Artificial Analysis Intelligence Index Composite model intelligence5652555757
FrontierCode 1.1 Main Production code qualityScore43.6%34.4%42.7%41.3%—
DeepSWE v1.1 Long-horizon software engineering65.3%48.6%53.8%69.6%54.9%
Code Arena Web developmentElo15881538154115231535
Terminal-bench 2.1 Agentic terminal coding85.8%78.0%80.4%87.4%82.9%
Terminal-bench 3.0 General agent capabilities14.9%5.4%14.6%20.8%—
AutomationBench Enterprise workflow automationPrivate set30.4%17.0%10.7%23.6%—
GDPVal-AA v2 Knowledge workElo15251422159815781628
Harvey LAB-AA Complex legal workflows90.7%85.1%90.1%85.2%—
GDP.pdf Expert PDF document comprehension34.0%22.0%28.0%24.7%16.0%
CharXiv Reasoning Information synthesis from complex chartsNo tools84.5%85.2%77.0%85.9%—
With tools88.7%89.4%88.3%——
LVBench Long video understanding85.4%84.2%68.5%78.9%—
GDM-MRCR v2 (8-needle) Long context performance128k (average)97.0%91.8%81.5%93.5%—
OSWorld-2.0 Agentic computer use47.9%33.8%—50.2%—
Agent's Last Exam Multimodal desktop and OS agent tasksPass rate26.3%24.2%33.3%28.0%—
HLE-Verified Multidisciplinary expert reasoning53.6%51.2%31.0%51.1%—
BioMysteryBench Bioinformatics research reasoningHuman solvable87.1%80.6%87.5%83.8%—
Human difficult43.5%41.2%34.1%49.4%—
LABBench2 Biology real-world research tasks82.1%76.1%80.1%81.2%—
Methodology: deepmind.com/models/evals-methodology/gemini-3-7-flash
* For 3.6 and 3.7 Flash, introductory price expires on December 31, 2026. Starting January 1, 2027, $1.50/1M input tokens and $7.50/1M output tokens will apply.
Intended Usage and Limitations
Benefit and Intended Usage
Gemini 3.7 Flash is well-suited for users, developers, and enterprises. Some use cases include: agentic workflows, complex video reasoning, coding tasks, and enterprise workflows
Known Limitations
Gemini 3.7 Flash may exhibit some of the general limitations of foundation models, such as hallucinations. In addition to this, we are continually working to improve jailbreak resistance and have recently strengthened the mitigations across Frontier Safety. There may also be occasional slowness or timeout issues. The knowledge cutoff date for Gemini 3.7 Flash is March 2026 – users can expect updated information for some domains while in others they may experience the model’s knowledge is limited to January 2025 (in line with the Gemini 3 Model Family). For more information about known limitations, see the Gemini 3.6 Flash model card.
Acceptable Usage
For more information about the acceptable usage for Gemini 3.7 Flash, see the Gemini 3.6 Flash model card.
Ethics and Content Safety
Evaluation Approach
For more information about the evaluation approach for Gemini 3.7 Flash, see the Gemini 3.6 Flash model card.
Safety Policies
For more information about the safety policies for Gemini 3.7 Flash, see the Gemini 3.6 Flash model card.
Training and Development Evaluation Results
Results for some of the internal safety evaluations conducted during the development phase are listed below. The evaluation results are for automated evaluations and not human evaluation or red teaming. Scores are provided as an absolute percentage increase or decrease in performance compared to the indicated model, as described below.
Overall, Gemini 3.7 Flash performs similarly to Gemini 3.6 Flash across both safety and tone, with low unjustified refusals.
EvaluationDescriptionGemini 3.7 Flash vs. Gemini 3.6 Flash
Text to Text SafetyAutomated content safety evaluation measuring safety policies+1.17pp Lower is better
Multilingual SafetyAutomated safety policy evaluation across multiple languages-0.48pp Lower is better
Image to Text SafetyAutomated content safety evaluation measuring safety policiesNo change Lower is better
Tone1Automated evaluation measuring objective tone of model refusal-0.47pp Higher is better
Unjustified-refusalsAutomated evaluation measuring model’s ability to respond to borderline prompts while remaining safe+0.84pp Lower is better
1 For tone and instruction following, a positive percentage increase represents an improvement in the tone of the model on sensitive topics and the model’s ability to follow instructions while remaining safe compared to Gemini 3 Flash. We mark improvements in green and regressions in red.
We continue to improve our internal evaluations, including refining automated evaluations to reduce false positives and negatives, as well as update query sets to ensure balance and maintain a high standard of results. The performance results reported below are computed with improved evaluations and thus are not directly comparable with performance results found in previous Gemini model cards.
We expect variation in our automated safety evaluations results, which is why we review flagged content to check for egregious or dangerous material. Our manual review confirmed losses were overwhelmingly either a) false positives or b) not egregious.
Human Red Teaming Results
We conduct manual red teaming by specialist teams who sit outside of the model development team. High-level findings are fed back to the model team. For child safety evaluations, Gemini 3.7 Flash satisfied required launch thresholds, which were developed by expert teams to protect children online and meet Google’s commitments to child safety across our models and Google products. For content safety policies generally, including child safety, we saw similar or improved safety performance compared to Gemini 3.6 Flash. Additionally, the scope of red teaming covered potential issues outside of our strict policies, compared performance to Gemini 3.1 Pro, and found no egregious concerns.
Frontier Safety Assessment
We evaluated Gemini 3.7 Flash as outlined in our latest Frontier Safety Framework (April-2026), and found that it did not reach any tracked or critical capability levels as outlined in the table below:
DomainKey Results for Gemini 3.7 FlashT/CCLT/CCL reached?
CBRNWe can rule out the TCL for the CBRN domain with reasonable confidence based on the results from our testing. While Gemini 3.7 Flash demonstrates high capability in certain theoretical areas, it lacks nuanced expert knowledge and actionable depth necessary to complete priority harm journeys.
We continue to deploy mitigations.Uplift TCLTCL not reached
We can rule out the CCL for the CBRN domain with reasonable confidence based on the results from our testing. Expert red teaming demonstrated a modest capability uplift over web baselines and a subset of experts were able to elicit accurate and actionable information across the full harm journey for both tested scenarios, prompting us to assess that the model has reached the alert threshold for this CCL. However, due to modest average red-teaming scores, and a requirement for explicit expert steering to elicit certain details, we have assessed that Gemini 3.7 Flash falls below the CCL threshold.
We continue to deploy mitigations.Uplift Level 1 CCLCCL not reached
CybersecurityGemini 3.7 Flash reaches the alert threshold for this CCL, but not the CCL. We continue to deploy mitigations.Uplift Level 1 CCLCCL not reached
Harmful ManipulationGemini 3.7 Flash demonstrates some ability to influence user beliefs and behaviors during one-on-one direct conversations in human behavioural studies. However, its overall efficacy falls beneath the CCL alert threshold. Recognizing that testing environments may under-elicit capabilities and threat actors could scale misuse absent mitigations, we continue to develop and evolve our safeguards.Level 1 CCLCCL not reached
ML R&D and MisalignmentOn stealth evaluations, Gemini 3.7 Flash performs similarly to Gemini 3.1 Pro; on situational awareness, the model is stronger than Gemini 3.1 Pro. Gemini 3.7 Flash is observant enough to correctly assess when it is in a testing environment, but it cannot successfully bypass testing restrictions. The model does not reach the TCL.Stealth and Situational Awareness TCLTCL not reached
Gemini 3.7 Flash can complete individual coding tasks but lacks the independence to chain them into an end-to-end research workflow without human intervention. The model does not reach the CCL alert threshold.Acceleration Level 1 CCLCCL not reached
Automation Level 1 CCLCCL not reached
We continually work to improve the coverage and robustness of Frontier Safety safeguards. Gemini 3.7 Flash is shipping with updated safeguards to prevent misuse in the domains of Chemical, Biological, Radiological, and Nuclear (CBRN) and cyber offense.
The Gemini 3.7 Frontier Safety Framework Report is available here.
Latest model cards
Gemini 4 Argon
Learn more
Nano Banana 2.1
Learn more
Gemini 3.8 Flash
Learn more
Gemini Robotics On-Device 2
Learn more
Gemini Robotics ER 2
Learn more
Lyria 3.5
Learn more
Follow us
Sign up for updates on our latest innovations
I accept Google's Terms and Conditions and acknowledge that my information will be used in accordance with Google's Privacy Policy.
Sign up
Build AI responsibly to benefit humanity
Models
Gemini
Gemini Omni
Nano Banana
Gemini Audio
Gemma
Genie
Lyria
Veo
Research
Gemini Robotics
Breakthroughs
Evals
Publications
Frontier safety
Responsibility
Science
AlphaFold
AlphaGenome
WeatherNext
AlphaEarth
AlphaEvolve
Products
Gemini app
Google AI Studio
Google Antigravity
Learn more
About
News
Careers
National Partnerships for AI
Accelerator programs
The Podcast
DeepMind Institute
About Google
Google products
Privacy
Terms
Cookies management controls