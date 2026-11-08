What's new in Gemini 4 Argon | Gemini API | Google AI for Developers
Skip to main content
/
English
Deutsch
Español – América Latina
Français
Indonesia
Italiano
Polski
Português – Brasil
Shqip
Tiếng Việt
Türkçe
Русский
עברית
العربيّة
فارسی
हिंदी
বাংলা
ภาษาไทย
中文 – 简体
中文 – 繁體
日本語
한국어
Get API key
Cookbook
Community
Sign in
Docs
API reference
Gemini API
Docs
API reference
Get API key
Cookbook
Community
Get started
Overview
Get started
API keys
Pricing
Coding agent setup
API CLI
Models
All models
Latest Gemini models
Nano Banana
Veo
Gemini Omni Flash
Lyria 3.5 & Lyria Clip
Overview
Lyria RealTime
Lyria prompt guide
Text-to-speech
Overview
Voice design
Voice replication
Transcribe
Live
Live translate
Embeddings
Robotics
Overview
Spatial reasoning
Agentic vision
Task orchestration
Robotics with streaming
Video understanding
Core capabilities
Text
Image
Image generation 🍌
Image understanding
Video
Video overview
Video understanding
Documents
Speech and audio
Speech generation
Audio understanding
Audio transcription
Thinking
Thinking
Thought signatures
Structured outputs
Function calling
Long context
Long decode
Agents
Overview
Quickstart
Antigravity agent
Building managed agents
Environments
Credentials
Hooks
Deep Research agent
Tools
Overview
Google Search
Google Maps
Code execution
URL context
Computer use
File search
Combine tools and function calling
Live API
Overview
Get started
Get started using the GenAI SDK
Get started using raw WebSockets
Capabilities
Thinking
Live transcription
Live translation
Tool use
Session management
Ephemeral tokens
Best practices
Optimization
Overview
Batch API
Webhooks
Flex inference
Priority inference
Context caching
Guides
Interactions API
Streaming
Background execution
File input
Input methods
Files API
OpenAI compatibility
Media resolution
Token counting
Prompt engineering
Logs and datasets
Get started with logs
Data logging and sharing
Safety
Safety settings
Safety guidance
Frameworks
LangChain & LangGraph
CrewAI
LlamaIndex
Vercel AI SDK
Temporal
Resources
Release notes
Deprecations
Libraries
Migration
Migrate to Gen AI SDK
Migrate to Interactions API
Interactions breaking changes (May 2026)
Rate limits
Billing info
API troubleshooting
API errors
Status
Partner and library integrations
Google AI Studio
Quickstart
Google AI plans
Vibe code in Build mode
Developing full-stack apps
Build Android apps
Deploying your app
Agents in AI Studio Playground
Try out LearnLM
Troubleshooting
Access for Workspace users
Google Cloud Platform
Gemini Enterprise Agent Platform Gemini API
OAuth authentication
Policies
Terms of service
Available regions
Abuse monitoring
Feedback information
Gemini 4 Argon is now available. Try it out.
Home
Gemini API
Docs
Send feedback
What's new in Gemini 4 Argon
Gemini 4 Argon (gemini-4-argon) is our latest, most capable model. It can reason longer on hard problems for better results on complex coding, agentic, math, and science tasks. Gemini 4 Argon is available through the Gemini API and in Google AI Studio.
Gemini 4 Argon supports a unified 1M-token context window, long decode up to 1M tokens, and tunable thinking levels (low, medium, high).
experiment
Try it in AI Studio
Build apps from scratch with Gemini 4 Argon and AI Studio.
smart_toy
App Gallery
Play and remix apps, built with Gemini 4 Argon.
rocket_launch
Get started
Get started with Gemini 4 Argon with starter prompts.
This guide explains what's new in Gemini 4 Argon, API changes, code examples, and migration guidance.
New model
Model
Model ID
Default thinking level
Pricing
Description
Gemini 4 Argon
gemini-4-argon
medium
Available through Nov 30, 2026 at an introductory price of $2/1M input tokens and $10/1M output tokens ($4/1M input and $20/1M output thereafter). See pricing for more details.
Our most capable model, built to solve the hardest problems with depth and precision across real-world software engineering and knowledge work tasks.
For complete details, see the Gemini 4 Argon model page. For introductory pricing details, see the pricing section later on this page or the pricing page.
Quickstart
Use the following example to send a request to gemini-4-argon with the recommended default thinking_level (medium) and a 64K output token limit:
Python
from google import genai
client = genai.Client()
interaction = client.interactions.create(
model="gemini-4-argon",
input="Write a three.js script that renders a realistic 3D black hole with gravitational lensing."
)
print(interaction.output_text)
JavaScript
import { GoogleGenAI } from "@google/genai";
const client = new GoogleGenAI({});
const interaction = await client.interactions.create({
model: "gemini-4-argon",
input: "Write a three.js script that renders a realistic 3D black hole with gravitational lensing.",
});
console.log(interaction.output_text);
REST
curl "https://generativelanguage.googleapis.com/v1beta/interactions" \
-H "x-goog-api-key: $GEMINI_API_KEY" \
-H 'Content-Type: application/json' \
-X POST \
-d '{
"model": "gemini-4-argon",
"input": "Write a three.js script that renders a realistic 3D black hole with gravitational lensing."
}'
What's new in Gemini 4 Argon
Unified 1M input-output token limit: Input, thinking, and output share one window of 1,048,576 tokens.
Long decode: A single response can now go past 64K tokens, up to 1M tokens minus your input. See Long decode.
Agentic video understanding is generally available: Agentic video understanding is now generally available.
Supported in Managed Agents: The Antigravity agent in Gemini Managed Agents now supports Gemini 4 Argon.
For complete specs, see the Gemini 4 Argon model page. For pricing details, see the pricing page.
Larger output and long decode
Gemini 4 Argon can think longer on hard math, science, and coding problems.
Use thinking_level to control reasoning depth: The thinking level decides how deeply the model reasons before it answers. max_output_tokens is a hard limit: the response stops once thinking and output together reach it, so set it high enough that it doesn't cut the answer short.
Generate up to 1M tokens with background execution: Use background execution with max_output_tokens greater than 65,536 to let a single response go past 64K tokens, up to 1M tokens. The model generates long responses in hops of up to 64K tokens, and each hop continues from where the previous one stopped. With background execution, our servers run these continuation hops for you. Because each hop adds a model_output step to interaction.steps, join the text across all model_output steps when the interaction completes.
Python
import time
from google import genai
client = genai.Client()
interaction = client.interactions.create(
model="gemini-4-argon",
input="Write a complete, rigorous proof of the prime number theorem.",
background=True,
generation_config={
"max_output_tokens": 262144,
"thinking_level": "high",
},
)
while interaction.status in ("in_progress", "queued"):
time.sleep(5)
interaction = client.interactions.get(id=interaction.id)
# Each hop adds a model_output step, so join the text of all of them.
text = "".join(
content.text
for step in interaction.steps
if step.type == "model_output"
for content in step.content
if content.type == "text"
)
print(text)
print("Status:", interaction.status)
print("Usage:", interaction.usage)
JavaScript
import { GoogleGenAI } from "@google/genai";
const client = new GoogleGenAI({});
let interaction = await client.interactions.create({
model: "gemini-4-argon",
input: "Write a complete, rigorous proof of the prime number theorem.",
background: true,
generation_config: {
max_output_tokens: 262144,
thinking_level: "high",
},
});
while (interaction.status === "in_progress" || interaction.status === "queued") {
await new Promise((resolve) => setTimeout(resolve, 5000));
interaction = await client.interactions.get(interaction.id);
}
// Each hop adds a model_output step, so join the text of all of them.
const text = interaction.steps
.filter((step) => step.type === "model_output")
.flatMap((step) => step.content ?? [])
.filter((content) => content.type === "text")
.map((content) => content.text)
.join("");
console.log(text);
console.log("Status:", interaction.status);
console.log("Usage:", interaction.usage);
REST
ID=$(curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
-H "x-goog-api-key: $GEMINI_API_KEY" \
-H "Content-Type: application/json" \
-d '{
"model": "gemini-4-argon",
"input": "Write a complete, rigorous proof of the prime number theorem.",
"background": true,
"generation_config": {
"max_output_tokens": 262144,
"thinking_level": "high"
}
}' | jq -r '.id')
while true; do
RESP=$(curl -s "https://generativelanguage.googleapis.com/v1beta/interactions/$ID" \
-H "x-goog-api-key: $GEMINI_API_KEY")
STATUS=$(echo "$RESP" | jq -r '.status')
if [[ "$STATUS" != "in_progress" && "$STATUS" != "queued" ]]; then
echo "$RESP" | jq -r '[.steps[]? | select(.type == "model_output") | .content[]? | select(.type == "text") | .text] | join("")'
break
fi
sleep 5
done
Note: If you set background: true without defining max_output_tokens, the server stops after 64K tokens.
Background execution is the easiest way to run long decode. It runs the continuation loop server-side until the model finishes or reaches max_output_tokens. If you need finer-grained control over retries, backoff, and error handling (or don't want your interactions stored), you can use client-side continuation in the GenerateContent API. Client-side continuation is also coming soon to the Interactions API. For streaming, reconnection, token counting, and when to use long decode, see the long decode guide.
Setting output token limits
max_output_tokens sets the total thinking and output tokens for a response. Set it high enough that thinking doesn't cut the answer short, and low enough to limit spend when a hard prompt uses all of it.
Use these values as a starting point:
Standard tasks: Keep the default of 65,536 or don't set any value.
Existing apps with a limit lower than 32K: Raise max_output_tokens to at least 32,768. Gemini 4 Argon can spend more of the limit on thinking than earlier models. To use fewer tokens, lower the thinking level instead.
Complex reasoning and coding: Set background: true and set max_output_tokens to 131,072 or 262,144, up to 1,048,576 minus your input tokens.
Understanding thinking levels
The thinking level is your main control over quality, latency, and token use in Gemini 4 Argon:
Thinking level
Token use
When to use
low
Fewest tokens, lowest latency
Simpler tasks and cost-sensitive work. Also works for analysis and writing tasks that need light thinking. Quality can drop on hard tasks.
medium (default)
Balanced
Recommended for most tasks, including complex code and agentic use cases.
high
Most tokens, slowest first token
Complex reasoning, hard math and science, and the most difficult code or agent tasks. Pairs well with long decode for long outputs.
Run your evaluations at all three levels, then pick the lowest level that meets your quality bar. To learn more, see the thinking guide.
Python
from google import genai
client = genai.Client()
interaction = client.interactions.create(
model="gemini-4-argon",
input="Analyze this payment processing pipeline for race conditions during retry attempts and rewrite the transaction locks safely.",
generation_config={
"thinking_level": "medium" # Balanced reasoning effort for complex tasks
}
)
print(interaction.output_text)
JavaScript
import { GoogleGenAI } from "@google/genai";
const client = new GoogleGenAI({});
const interaction = await client.interactions.create({
model: "gemini-4-argon",
input: "Analyze this payment processing pipeline for race conditions during retry attempts and rewrite the transaction locks safely.",
generation_config: {
thinking_level: "medium", // Balanced reasoning effort for complex tasks
},
});
console.log(interaction.output_text);
REST
curl "https://generativelanguage.googleapis.com/v1beta/interactions" \
-H "x-goog-api-key: $GEMINI_API_KEY" \
-H 'Content-Type: application/json' \
-X POST \
-d '{
"model": "gemini-4-argon",
"input": "Analyze this payment processing pipeline for race conditions during retry attempts and rewrite the transaction locks safely.",
"generation_config": {
"thinking_level": "medium"
}
}'
Gemini 4 Argon in Managed Agents
The Antigravity agent in Gemini Managed Agents supports Gemini 4 Argon. To use it, set the model in agent_config:
Python
from google import genai
client = genai.Client()
interaction = client.interactions.create(
agent="antigravity-preview-09-2026",
input=(
"Audit https://web.dev for performance, Core Web Vitals, and SEO. "
"Query Google's PageSpeed Insights API for both Mobile and Desktop strategies. "
"Check search indexing with Google Search for site:web.dev. "
"Format the output as a side-by-side scorecard table with prioritized fixes."
),
environment="remote",
agent_config={
"type": "antigravity",
"model": "gemini-4-argon",
},
)
print(interaction.output_text)
JavaScript
import { GoogleGenAI } from "@google/genai";
const client = new GoogleGenAI({});
const interaction = await client.interactions.create({
agent: "antigravity-preview-09-2026",
input:
"Audit https://web.dev for performance, Core Web Vitals, and SEO. " +
"Query Google's PageSpeed Insights API for both Mobile and Desktop strategies. " +
"Check search indexing with Google Search for site:web.dev. " +
"Format the output as a side-by-side scorecard table with prioritized fixes.",
environment: "remote",
agent_config: {
type: "antigravity",
model: "gemini-4-argon",
},
}, { timeout: 300000 });
console.log(interaction.output_text);
REST
curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
-H "Content-Type: application/json" \
-H "x-goog-api-key: $GEMINI_API_KEY" \
-d '{
"agent": "antigravity-preview-09-2026",
"input": "Audit https://web.dev for performance, Core Web Vitals, and SEO. Query Google'\''s PageSpeed Insights API for both Mobile and Desktop strategies. Check search indexing with Google Search for site:web.dev. Format the output as a side-by-side scorecard table with prioritized fixes.",
"environment": "remote",
"agent_config": {
"type": "antigravity",
"model": "gemini-4-argon"
}
}'
For more options, see model selection in the Antigravity agent guide.
Migration checklist
Note: Automate this migration with a coding agent. If you use a coding agent that supports skills (like Antigravity),
install the gemini-api-dev skill and run:
`/gemini-api-dev migrate my app to Gemini 4 Argon`
Migrate to gemini-4-argon
Update model ID: Change your target model string to gemini-4-argon.
Review max_output_tokens: If you set it explicitly today, consider raising it. We recommend at least 32,768, since Gemini 4 Argon can spend more of the limit on thinking.
Configure thinking level: Choose low, medium (default), or high, and test your workload at all three.
Move off explicit context caching: Explicit caching (cachedContents / caches.create) is not supported on Gemini 4 Argon. Remove calls that create or reference cached_content from your requests. Implicit caching is enabled by default for prompts of at least 4,096 tokens and discounts cached input tokens by 95% on cache hits.
Remove sampling parameters: Remove temperature, top_p, and top_k from your requests. If provided, they are ignored.
Use background execution for long outputs: For tasks that need more than 64K tokens, set background to true and max_output_tokens greater than 65,536.
Increase client timeouts: Hard prompts can take several minutes. Use background execution, or set HTTP client timeouts to at least 15 minutes.
Keep conversation state on the server: Use previous_interaction_id for multi-turn and function calling conversations.
Review your cost estimates: Every token the model processes is billed, including internal tool system instructions and function declarations when using grounding (see Pricing).
Pricing
Gemini 4 Argon is available at introductory pricing through November 30, 2026:
Input tokens: $2.00 per 1M tokens ($4.00 starting December 1, 2026)
Cached input tokens: Implicit caching discounts cached input by 95%, to $0.10 per 1M tokens ($0.20 starting December 1, 2026).
Output tokens, including thinking tokens: $10.00 per 1M tokens ($20.00 starting December 1, 2026)
Every token the model processes is counted and billed, including thinking tokens and internal tool system instructions and function declarations when using grounding. Grounding with Google Search also remains billed per query.
Gemini 4 Argon is not available on the Free tier. For complete pricing tiers, see the pricing page.
Other models
Gemini 3.8 Flash
Gemini 3.6 Flash and 3.5 Flash-Lite
See all models
What's next
Read the long decode guide for streaming, reconnection, and token counting.
Learn how thinking levels and thought summaries work in the thinking guide.
Learn about long-running jobs in the background execution guide.
Test and refine prompts in Google AI Studio.
Send feedback
Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2026-10-27 UTC.
Need to tell us more?
[[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Missing the information I need","missingTheInformationINeed","thumb-down"],["Too complicated / too many steps","tooComplicatedTooManySteps","thumb-down"],["Out of date","outOfDate","thumb-down"],["Samples / code issue","samplesCodeIssue","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-10-27 UTC."],[],[]]
Terms
Privacy
Manage cookies
English
Deutsch
Español – América Latina
Français
Indonesia
Italiano
Polski
Português – Brasil
Shqip
Tiếng Việt
Türkçe
Русский
עברית
العربيّة
فارسی
हिंदी
বাংলা
ภาษาไทย
中文 – 简体
中文 – 繁體
日本語
한국어