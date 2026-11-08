---
library_name: transformers
license: other
license_name: lfm1.0
license_link: LICENSE
pipeline_tag: text-generation
tags:
- liquid
- lfm3
- edge
- conversational
- custom_code
language:
- en
- ar
- zh
- fr
- de
- it
- ja
- ko
- pt
- es
- vi
- th
- id
- hi
- ru
- pl
base_model: LiquidAI/LFM3-1.7B-Base
---

<div align="center">
  <img
    src="https://huggingface.co/LiquidAI/LFM3-1.7B/resolve/main/assets/liquid-ai-banner.webp"
    alt="Liquid AI"
    style="width: 100%; max-width: 100%; height: auto; display: block; margin: 0;"
  />
  <div align="center" style="display: flex; justify-content: center; align-items: center; gap: 1.25em; margin: 8px 0 1.7rem; padding: 0; line-height: 1.3;">
    <a href="https://console.liquid.ai/dashboard" style="display: inline-flex; align-items: center; gap: 6px;"><img src="https://huggingface.co/LiquidAI/LFM3-1.7B/resolve/main/assets/icons/api.svg" width="16" height="16" alt="" aria-hidden="true" style="display: block; flex: 0 0 16px; width: 16px; height: 16px; margin: 0;" /><strong>API</strong></a>
    <a href="https://playground.liquid.ai/" style="display: inline-flex; align-items: center; gap: 6px;"><img src="https://huggingface.co/LiquidAI/LFM3-1.7B/resolve/main/assets/icons/try.svg" width="16" height="16" alt="" aria-hidden="true" style="display: block; flex: 0 0 16px; width: 16px; height: 16px; margin: 0;" /><strong>Try</strong></a>
    <a href="https://docs.liquid.ai/lfm/getting-started/welcome" style="display: inline-flex; align-items: center; gap: 6px;"><img src="https://huggingface.co/LiquidAI/LFM3-1.7B/resolve/main/assets/icons/docs.svg" width="16" height="16" alt="" aria-hidden="true" style="display: block; flex: 0 0 16px; width: 16px; height: 16px; margin: 0;" /><strong>Docs</strong></a>
    <a href="https://www.liquid.ai/blog/lfm3" style="display: inline-flex; align-items: center; gap: 6px;"><img src="https://huggingface.co/LiquidAI/LFM3-1.7B/resolve/main/assets/icons/blog.svg" width="16" height="16" alt="" aria-hidden="true" style="display: block; flex: 0 0 16px; width: 16px; height: 16px; margin: 0;" /><strong>Blog</strong></a>
  </div>
</div>

# LFM3-1.7B

LFM3-1.7B is a **text model for local agents and specialized applications**, based on our new tri-hybrid architecture.

- **Agentic training:** post-trained for agentic harnesses such as Hermes Agent, Pi, and OpenClaw, with a 256K-token context window.
- **Designed for the edge:** at 4-bit precision, it takes about 1 GB of memory, so it fits on any phone or laptop.
- **Made to be specialized:** adapt the model to your domains, formats, and tools via quick single-GPU fine-tuning.

Find more information about the LFM3 family in [our release blog post](https://www.liquid.ai/blog/lfm3).

## Model details
<hr style="margin: -0.7em 0 1.2em 0; border: 0; border-top: 1px solid rgba(127, 127, 127, 0.3);" />

The [LFM3 family](https://huggingface.co/collections/LiquidAI/lfm3) includes base, text, vision, audio, omni, and decision models.

<table style="width: 100%; display: table; border: 0; border-radius: 0; border-collapse: collapse;">
<thead style="border: 0;">
<tr style="border: 0;">
<th scope="col" style="text-align: left; padding: 0.55em 0.75em; border: 0; border-bottom: 1px solid rgba(127, 127, 127, 0.55);">Property</th>
<th scope="col" style="text-align: left; padding: 0.55em 0.75em; border: 0; border-bottom: 1px solid rgba(127, 127, 127, 0.55);">Specification</th>
</tr>
</thead>
<tbody style="border: 0;">
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;"><strong>Checkpoint</strong></td>
<td style="border: 0; padding: 0.55em 0.75em;">Post-trained, text-only language model</td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;"><strong>Parameters</strong></td>
<td style="border: 0; padding: 0.55em 0.75em;">1.73B</td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;"><strong>Architecture</strong></td>
<td style="border: 0; padding: 0.55em 0.75em;">24 layers: 13 gated short convolutions, 5 sliding-window attention, 6 global attention</td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;"><strong>Context length</strong></td>
<td style="border: 0; padding: 0.55em 0.75em;">256K tokens (input + output)</td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;"><strong>Vocabulary</strong></td>
<td style="border: 0; padding: 0.55em 0.75em;">128,000 tokens</td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;"><strong>Languages</strong></td>
<td style="border: 0; padding: 0.55em 0.75em;">English, Arabic, Chinese, French, German, Italian, Japanese, Korean, Portuguese, Spanish, Vietnamese, Thai, Indonesian, Hindi, Russian, Polish</td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;"><strong>License</strong></td>
<td style="border: 0; padding: 0.55em 0.75em;"><a href="LICENSE">LFM Open License v1.0</a></td>
</tr>
</tbody>
</table>

LFM3-1.7B is designed for local agents, tool calling, structured outputs, and domain-specific fine-tuning. Use retrieval or search for knowledge-heavy tasks. It is not recommended for agentic coding or complex multi-step reasoning due to its small size.

## Inference
<hr style="margin: -0.7em 0 1.2em 0; border: 0; border-top: 1px solid rgba(127, 127, 127, 0.3);" />

Choose a checkpoint variant for your inference framework and hardware.

<table style="width: 100%; display: table; border: 0; border-radius: 0; border-collapse: collapse;">
<thead style="border: 0;">
<tr style="border: 0;">
<th scope="col" style="text-align: left; padding: 0.55em 0.75em; border: 0; border-bottom: 1px solid rgba(127, 127, 127, 0.55);">Checkpoint</th>
<th scope="col" style="text-align: left; padding: 0.55em 0.75em; border: 0; border-bottom: 1px solid rgba(127, 127, 127, 0.55);">Framework</th>
<th scope="col" style="text-align: left; padding: 0.55em 0.75em; border: 0; border-bottom: 1px solid rgba(127, 127, 127, 0.55);">Description</th>
</tr>
</thead>
<tbody style="border: 0;">
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;"><a href="https://huggingface.co/LiquidAI/LFM3-1.7B">BF16</a></td>
<td style="border: 0; padding: 0.55em 0.75em;"><a href="https://docs.liquid.ai/deployment/gpu-inference/vllm">vLLM</a>, <a href="https://docs.liquid.ai/deployment/gpu-inference/sglang">SGLang</a>, <a href="https://docs.liquid.ai/deployment/gpu-inference/transformers">Transformers</a></td>
<td style="border: 0; padding: 0.55em 0.75em;">BF16 weights for GPU inference.</td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;"><a href="https://huggingface.co/LiquidAI/LFM3-1.7B-FP8">FP8</a></td>
<td style="border: 0; padding: 0.55em 0.75em;"><a href="https://huggingface.co/LiquidAI/LFM3-1.7B-FP8#use-with-sglang">SGLang</a></td>
<td style="border: 0; padding: 0.55em 0.75em;">FP8 quantization for GPU inference.</td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;"><a href="https://huggingface.co/LiquidAI/LFM3-1.7B-NVFP4">NVFP4</a></td>
<td style="border: 0; padding: 0.55em 0.75em;"><a href="https://huggingface.co/LiquidAI/LFM3-1.7B-NVFP4#use-with-sglang">SGLang</a></td>
<td style="border: 0; padding: 0.55em 0.75em;">4-bit floating-point quantization for GPU inference.</td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;"><a href="https://huggingface.co/LiquidAI/LFM3-1.7B-GGUF">GGUF</a></td>
<td style="border: 0; padding: 0.55em 0.75em;"><a href="https://docs.liquid.ai/deployment/on-device/llama-cpp">llama.cpp</a>, <a href="https://docs.liquid.ai/deployment/on-device/ollama">Ollama</a>, <a href="https://docs.liquid.ai/deployment/on-device/lm-studio">LM Studio</a></td>
<td style="border: 0; padding: 0.55em 0.75em;">Local inference on CPUs and GPUs.</td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;"><a href="https://huggingface.co/LiquidAI/LFM3-1.7B-MLX-4bit">MLX</a></td>
<td style="border: 0; padding: 0.55em 0.75em;"><a href="https://docs.liquid.ai/deployment/on-device/mlx">MLX</a></td>
<td style="border: 0; padding: 0.55em 0.75em;">4-bit quantization for Apple Silicon.</td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;"><a href="https://huggingface.co/LiquidAI/LFM3-1.7B-ONNX">ONNX</a></td>
<td style="border: 0; padding: 0.55em 0.75em;"><a href="https://docs.liquid.ai/deployment/on-device/onnx">ONNX Runtime</a></td>
<td style="border: 0; padding: 0.55em 0.75em;">Cross-platform inference with ONNX Runtime.</td>
</tr>
</tbody>
</table>

**Sampling parameters:**

- **General** (chat, tool use, agents, coding): `temperature=0.1,top_k=50, repetition_penalty=1.1`
- **Math & STEM** (math, science): `temperature=1.0, top_p=0.95, top_k=20`

**Transformers quick start:**

```python
from transformers import pipeline

generator = pipeline(
    "text-generation",
    model="LiquidAI/LFM3-1.7B",
    trust_remote_code=True,
)

messages = [{"role": "user", "content": "What is C. elegans?"}]
output = generator(
    messages,
    do_sample=True,
    temperature=0.1,
    top_k=50,
    repetition_penalty=1.1,
    max_new_tokens=2048,
)
print(output[0]["generated_text"][-1]["content"])
```

For local agent setup, see the [Agent Harnesses guide](https://docs.liquid.ai/examples/agent-harnesses).

<details>
<summary><strong>Chat template</strong></summary>

LFM3 uses this ChatML format, generated from the checkpoint's [chat template](https://huggingface.co/LiquidAI/LFM3-1.7B/blob/main/chat_template.jinja):

```text
<|startoftext|><|im_start|>system
You are a helpful assistant trained by Liquid AI.<|im_end|>
<|im_start|>user
Explain how a heat pump works.<|im_end|>
<|im_start|>assistant
<think>
```

Use `tokenizer.apply_chat_template()` with `add_generation_prompt=True` to format messages automatically.

Reasoning is enabled by default. You can set `enable_thinking=False` to disable thinking traces, but this behavior can be inconsistent, especially for reasoning-heavy tasks.

Reasoning from turns before the latest user message is removed unless `preserve_thinking=True`.

</details>

<details>
<summary><strong>Tool calling</strong></summary>

Pass function schemas through `tools=...` to `apply_chat_template()`. The template formats tool definitions and results automatically. Generated calls use XML:

```text
<tool_call>
<function=get_weather>
<parameter=city>
Paris
</parameter>
</function>
</tool_call>
```

Execute the call in your application. Add the parsed assistant call to history as a `tool_calls` entry, then append the result as a `tool` message. Keep passing the tool schemas on subsequent requests and preserve the assistant's content and reasoning from the current tool-use turn.

`function.arguments` must be a Python mapping. Decode JSON strings with `json.loads()` before applying the template.

</details>

<details>
<summary><strong>Tool search</strong></summary>

LFM3 supports deferred tools. Set `defer_loading=True` to keep tool definitions out of the prompt until your harness's search tool returns their names as `tool_reference` parts. The chat template then inserts their definitions into `<additional_tools>`.

```python
tools = [
    search_tool,
    {"type": "function", "defer_loading": True, "function": get_weather_schema},
]
messages.append({
    "role": "tool",
    "tool_call_id": call_id,
    "content": [
        {"type": "text", "text": "Found 1 tool."},
        {"type": "tool_reference", "name": "get_weather"},
    ],
})
```

Your harness implements and runs the search. Keep the full `tools` list, including deferred tools, on every request. In the system prompt, tell the model when to search:

> You only have one tool right now: search_tools, which searches a catalog of many more tools. If none of your current tools can handle a request, call search_tools to find one, then call the tool it returns.

Works with vLLM, SGLang, and LFM3-compatible llama.cpp builds. For llama.cpp, use a GGUF with the current chat template or load it with `--chat-template-file`.

See [Deferred tools and tool search](https://docs.liquid.ai/lfm/key-concepts/tool-use) for the full guide.

</details>

## Fine-tuning
<hr style="margin: -0.7em 0 1.2em 0; border: 0; border-top: 1px solid rgba(127, 127, 127, 0.3);" />

LFM3-1.7B is designed for **easy customization** for a given domain, task, or application via [TRL](https://docs.liquid.ai/lfm/fine-tuning/trl).

<table style="width: 100%; display: table; border: 0; border-radius: 0; border-collapse: collapse;">
<thead style="border: 0;">
<tr style="border: 0;">
<th scope="col" style="text-align: left; padding: 0.55em 0.75em; border: 0; border-bottom: 1px solid rgba(127, 127, 127, 0.55);">Training</th>
<th scope="col" style="text-align: left; padding: 0.55em 0.75em; border: 0; border-bottom: 1px solid rgba(127, 127, 127, 0.55);">Use case</th>
<th scope="col" style="text-align: center; padding: 0.55em 0.75em; border: 0; border-bottom: 1px solid rgba(127, 127, 127, 0.55);">Notebook</th>
</tr>
</thead>
<tbody style="border: 0;">
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;"><strong>SFT</strong></td>
<td style="border: 0; padding: 0.55em 0.75em;">Extract structured JSON from messy documents</td>
<td style="text-align: center; border: 0; padding: 0.55em 0.75em;"><a href="https://colab.research.google.com/github/Liquid4All/cookbook/blob/main/finetuning/notebooks/lfm3_sft_with_trl.ipynb" title="SFT with TRL"><img src="https://colab.research.google.com/assets/colab-badge.svg" width="117" height="20" alt="Open in Colab" style="display: inline-block; width: 117px; height: 20px; margin: 0; vertical-align: middle;" /></a></td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;"><strong>DPO</strong></td>
<td style="border: 0; padding: 0.55em 0.75em;">Answer from retrieved documents, or decline</td>
<td style="text-align: center; border: 0; padding: 0.55em 0.75em;"><a href="https://colab.research.google.com/github/Liquid4All/cookbook/blob/main/finetuning/notebooks/lfm3_dpo_with_trl.ipynb" title="DPO with TRL"><img src="https://colab.research.google.com/assets/colab-badge.svg" width="117" height="20" alt="Open in Colab" style="display: inline-block; width: 117px; height: 20px; margin: 0; vertical-align: middle;" /></a></td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;"><strong>GRPO</strong></td>
<td style="border: 0; padding: 0.55em 0.75em;">Call the right tools in a 108-tool phone app</td>
<td style="text-align: center; border: 0; padding: 0.55em 0.75em;"><a href="https://colab.research.google.com/github/Liquid4All/cookbook/blob/main/finetuning/notebooks/lfm3_grpo_with_trl.ipynb" title="GRPO with TRL"><img src="https://colab.research.google.com/assets/colab-badge.svg" width="117" height="20" alt="Open in Colab" style="display: inline-block; width: 117px; height: 20px; margin: 0; vertical-align: middle;" /></a></td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;"><strong>CPT</strong></td>
<td style="border: 0; padding: 0.55em 0.75em;">Learn a new language (Turkish) from raw text</td>
<td style="text-align: center; border: 0; padding: 0.55em 0.75em;"><a href="https://colab.research.google.com/github/Liquid4All/cookbook/blob/main/finetuning/notebooks/lfm3_cpt_with_trl.ipynb" title="Continued pre-training with TRL"><img src="https://colab.research.google.com/assets/colab-badge.svg" width="117" height="20" alt="Open in Colab" style="display: inline-block; width: 117px; height: 20px; margin: 0; vertical-align: middle;" /></a></td>
</tr>
</tbody>
</table>

## Performance
<hr style="margin: -0.7em 0 1.2em 0; border: 0; border-top: 1px solid rgba(127, 127, 127, 0.3);" />

### Benchmarks

LFM3-1.7B can power agentic applications that used to need 9B parameters.

<div role="region" aria-labelledby="benchmarks" tabindex="0" style="width: 100%; max-width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch;">
<table style="width: 100%; min-width: 36rem; display: table; border: 0; border-radius: 0; border-collapse: collapse; font-size: calc(0.875em - 1pt);">
<thead style="border: 0;">
<tr style="border: 0;">
<th scope="col" style="text-align: left; padding: 0.55em 0.75em; border: 0; border-bottom: 1px solid rgba(127, 127, 127, 0.55);">Benchmark</th>
<th scope="col" style="text-align: center; background-color: rgba(108, 79, 224, 0.08); padding: 0.55em 0.75em; border: 0; border-bottom: 1px solid rgba(127, 127, 127, 0.55);"><strong>LFM3<br>1.7B</strong></th>
<th scope="col" style="text-align: center; padding: 0.55em 0.75em; border: 0; border-bottom: 1px solid rgba(127, 127, 127, 0.55);">LFM2.5<br>2.6B</th>
<th scope="col" style="text-align: center; padding: 0.55em 0.75em; border: 0; border-bottom: 1px solid rgba(127, 127, 127, 0.55);">MiniCPM5<br>2B</th>
<th scope="col" style="text-align: center; padding: 0.55em 0.75em; border: 0; border-bottom: 1px solid rgba(127, 127, 127, 0.55);">Gemma 4<br>E4B</th>
<th scope="col" style="text-align: center; padding: 0.55em 0.75em; border: 0; border-bottom: 1px solid rgba(127, 127, 127, 0.55);">Qwen3.5<br>4B</th>
<th scope="col" style="text-align: center; padding: 0.55em 0.75em; border: 0; border-bottom: 1px solid rgba(127, 127, 127, 0.55);">Qwen3.5<br>9B</th>
</tr>
</thead>
<tbody style="border: 0;">
<tr style="border: 0;"><th scope="rowgroup" style="text-align: left; background-color: transparent; padding: 0.55em 0.75em; border: 0; font-weight: 600; padding-top: 1em; padding-bottom: 0.5em;">Agents</th><td aria-hidden="true" style="border: 0; padding: 0.55em 0.75em; background-color: rgba(108, 79, 224, 0.08);"></td><td colspan="5" aria-hidden="true" style="border: 0; padding: 0.55em 0.75em;"></td></tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">LiveClaw</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;"><strong>45.60</strong></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">14.70</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">30.37</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">20.36</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">19.94</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><u>35.77</u></td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">Claw-Eval General (EN), average</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;"><strong>68.64</strong></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">62.63</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">60.74</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">56.14</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">61.96</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><u>66.53</u></td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">Claw-Eval General (EN), pass^3</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;"><u>51.40</u></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">37.52</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">34.58</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">22.43</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">42.99</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><strong>51.87</strong></td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">BrowseComp-Plus (OpenClaw subset)</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;"><u>37.00</u></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">26.33</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">16.83</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">21.00</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">24.67</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><strong>38.00</strong></td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">WebArena-Verified</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;"><strong>38.42</strong></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">3.02</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">9.11</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">17.06</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">21.92</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><u>28.94</u></td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">EnterpriseOps-Gym</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;"><u>28.20</u></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">7.94</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">13.41</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">9.86</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">25.96</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><strong>28.97</strong></td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">AutomationBench (public)</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;"><strong>41.29</strong></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">0.94</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">4.71</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">1.92</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">8.67</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><u>15.10</u></td>
</tr>
</tbody>
<tbody style="border: 0;">
<tr style="border: 0;"><th scope="rowgroup" style="text-align: left; background-color: transparent; padding: 0.55em 0.75em; border: 0; font-weight: 600; padding-top: 1em; padding-bottom: 0.5em; border-top: 1px solid rgba(127, 127, 127, 0.25);">Tool use</th><td aria-hidden="true" style="border: 0; padding: 0.55em 0.75em; background-color: rgba(108, 79, 224, 0.08); border-top: 1px solid rgba(127, 127, 127, 0.25);"></td><td colspan="5" aria-hidden="true" style="border: 0; padding: 0.55em 0.75em; border-top: 1px solid rgba(127, 127, 127, 0.25);"></td></tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">BFCL V4</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;"><strong>71.39</strong></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">55.89</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">62.65</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">48.25</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">55.12</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><u>62.83</u></td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">ToolSandbox</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;"><strong>80.36</strong></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><u>78.04</u></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">68.16</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">69.27</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">75.40</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">76.41</td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">MCP-Atlas</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;">32.57</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">16.45</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">26.38</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">6.19</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><u>41.37</u></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><strong>42.67</strong></td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">τ³-bench (4 domains), average</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;"><u>68.01</u></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">56.77</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><strong>69.44</strong></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">33.53</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">65.98</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">67.11</td>
</tr>
</tbody>
<tbody style="border: 0;">
<tr style="border: 0;"><th scope="rowgroup" style="text-align: left; background-color: transparent; padding: 0.55em 0.75em; border: 0; font-weight: 600; padding-top: 1em; padding-bottom: 0.5em; border-top: 1px solid rgba(127, 127, 127, 0.25);">Agentic coding</th><td aria-hidden="true" style="border: 0; padding: 0.55em 0.75em; background-color: rgba(108, 79, 224, 0.08); border-top: 1px solid rgba(127, 127, 127, 0.25);"></td><td colspan="5" aria-hidden="true" style="border: 0; padding: 0.55em 0.75em; border-top: 1px solid rgba(127, 127, 127, 0.25);"></td></tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">SWE-bench Verified (OpenCode)</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;"><u>43.40</u></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">18.00</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">34.80</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">0.50</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">41.20</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><strong>51.20</strong></td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">SWE-bench Multilingual (OpenCode)</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;">23.00</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">8.00</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">15.67</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">0.67</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><u>23.33</u></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><strong>35.00</strong></td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">Terminal-Bench 2.1 (OpenCode)</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;">12.92</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">0.00</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">5.62</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">0.00</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><u>13.48</u></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><strong>17.98</strong></td>
</tr>
</tbody>
<tbody style="border: 0;">
<tr style="border: 0;"><th scope="rowgroup" style="text-align: left; background-color: transparent; padding: 0.55em 0.75em; border: 0; font-weight: 600; padding-top: 1em; padding-bottom: 0.5em; border-top: 1px solid rgba(127, 127, 127, 0.25);">Coding</th><td aria-hidden="true" style="border: 0; padding: 0.55em 0.75em; background-color: rgba(108, 79, 224, 0.08); border-top: 1px solid rgba(127, 127, 127, 0.25);"></td><td colspan="5" aria-hidden="true" style="border: 0; padding: 0.55em 0.75em; border-top: 1px solid rgba(127, 127, 127, 0.25);"></td></tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">LiveCodeBench v6</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;"><strong>73.46</strong></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">60.57</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">70.52</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><u>71.00</u></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">61.99</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">69.86</td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">LiveCodeBench Pro 25Q2</td><td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;"><u>31.74</u></td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">19.16</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">29.34</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">29.94</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">24.25</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><strong>34.43</strong></td></tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">SciCode</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;"><u>28.47</u></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">16.32</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">27.78</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">25.00</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">23.02</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><strong>31.60</strong></td>
</tr>
</tbody>
<tbody style="border: 0;">
<tr style="border: 0;"><th scope="rowgroup" style="text-align: left; background-color: transparent; padding: 0.55em 0.75em; border: 0; font-weight: 600; padding-top: 1em; padding-bottom: 0.5em; border-top: 1px solid rgba(127, 127, 127, 0.25);">Instruction following</th><td aria-hidden="true" style="border: 0; padding: 0.55em 0.75em; background-color: rgba(108, 79, 224, 0.08); border-top: 1px solid rgba(127, 127, 127, 0.25);"></td><td colspan="5" aria-hidden="true" style="border: 0; padding: 0.55em 0.75em; border-top: 1px solid rgba(127, 127, 127, 0.25);"></td></tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">IFEval</td><td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;"><strong>96.66</strong></td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><u>95.39</u></td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">87.83</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">90.02</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">92.52</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">92.08</td></tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">IFBench</td><td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;"><strong>73.03</strong></td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">60.48</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><u>62.08</u></td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">44.56</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">38.16</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">48.84</td></tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">IFStruct</td><td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;"><strong>93.72</strong></td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">82.18</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">72.65</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">78.45</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">87.05</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><u>89.20</u></td></tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">Multi-IF</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;"><strong>89.10</strong></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><u>84.80</u></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">73.19</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">81.03</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">80.32</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">84.44</td>
</tr>
</tbody>
<tbody style="border: 0;">
<tr style="border: 0;"><th scope="rowgroup" style="text-align: left; background-color: transparent; padding: 0.55em 0.75em; border: 0; font-weight: 600; padding-top: 1em; padding-bottom: 0.5em; border-top: 1px solid rgba(127, 127, 127, 0.25);">Knowledge</th><td aria-hidden="true" style="border: 0; padding: 0.55em 0.75em; background-color: rgba(108, 79, 224, 0.08); border-top: 1px solid rgba(127, 127, 127, 0.25);"></td><td colspan="5" aria-hidden="true" style="border: 0; padding: 0.55em 0.75em; border-top: 1px solid rgba(127, 127, 127, 0.25);"></td></tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">GPQA Diamond</td><td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;">63.37</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">57.78</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">65.15</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">57.88</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><u>75.76</u></td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><strong>80.40</strong></td></tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">Humanity's Last Exam (no tools)</td><td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;">7.17</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">5.88</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">8.20</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">4.77</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><u>12.84</u></td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><strong>16.41</strong></td></tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">Humanity's Last Exam (with tools)</td><td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;"><u>13.90</u></td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">9.60</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">11.50</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">6.00</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">11.60</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><strong>17.50</strong></td></tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">AA-Omniscience (public)</td><td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;"><strong>0.50</strong></td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">-33.17</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><u>-5.00</u></td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">-15.33</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">-57.17</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">-28.00</td></tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">AA-Omniscience accuracy (public)</td><td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;">7.07</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">8.75</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">9.13</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">9.83</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><strong>15.67</strong></td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><u>13.17</u></td></tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">AA-Omniscience non-hallucination (public)</td><td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;"><strong>92.93</strong></td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">53.69</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><u>84.44</u></td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">72.09</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">13.64</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">52.59</td></tr>
</tbody>
<tbody style="border: 0;">
<tr style="border: 0;"><th scope="rowgroup" style="text-align: left; background-color: transparent; padding: 0.55em 0.75em; border: 0; font-weight: 600; padding-top: 1em; padding-bottom: 0.5em; border-top: 1px solid rgba(127, 127, 127, 0.25);">Long context</th><td aria-hidden="true" style="border: 0; padding: 0.55em 0.75em; background-color: rgba(108, 79, 224, 0.08); border-top: 1px solid rgba(127, 127, 127, 0.25);"></td><td colspan="5" aria-hidden="true" style="border: 0; padding: 0.55em 0.75em; border-top: 1px solid rgba(127, 127, 127, 0.25);"></td></tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">AA-LCR</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;"><u>52.83</u></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">6.00</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">49.34</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">39.33</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">52.67</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><strong>62.00</strong></td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;">RULER 128K</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em;">65.56</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">1.15</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">37.96</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;">18.82</td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><u>84.63</u></td>
<td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em;"><strong>87.11</strong></td>
</tr>
</tbody>
<tbody style="border: 0;">
<tr style="border: 0;"><td style="border: 0; padding: 0.55em 0.75em; border-top: 1px solid rgba(127, 127, 127, 0.25);"><strong>Average</strong></td><td style="text-align: center; font-variant-numeric: tabular-nums; background-color: rgba(108, 79, 224, 0.08); border: 0; padding: 0.55em 0.75em; border-top: 1px solid rgba(127, 127, 127, 0.25);"><strong>49.37</strong></td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em; border-top: 1px solid rgba(127, 127, 127, 0.25);">31.55</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em; border-top: 1px solid rgba(127, 127, 127, 0.25);">39.19</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em; border-top: 1px solid rgba(127, 127, 127, 0.25);">31.74</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em; border-top: 1px solid rgba(127, 127, 127, 0.25);">39.27</td><td style="text-align: center; font-variant-numeric: tabular-nums; border: 0; padding: 0.55em 0.75em; border-top: 1px solid rgba(127, 127, 127, 0.25);"><u>47.24</u></td></tr>
</tbody>
</table>
</div>

<details>
<summary><small>Evaluation details</small></summary>

<p><small>All models were served with vLLM in BF16 at their full context length: 262,144 tokens for LFM3-1.7B, Qwen3.5-4B, and Qwen3.5-9B, and 131,072 tokens for LFM2.5-2.6B, MiniCPM5-2B, and Gemma 4 E4B. Unless listed below, every eval uses temperature 0.6 and top_p 0.95, with no output limit other than the context length. The Average row is the unweighted mean of every score in the table.</small></p>

<p><small>
<strong>BFCL V4</strong>: greedy decoding, up to 32,768 output tokens.<br>
<strong>ToolSandbox</strong>: greedy decoding, up to 1,024 tokens per turn.<br>
<strong>LiveClaw</strong>: OpenClaw agent, up to 8,192 tokens per turn.<br>
<strong>Claw-Eval</strong>: greedy decoding, 3 trials per task.<br>
<strong>BrowseComp-Plus</strong>: OpenClaw agent, greedy decoding, up to 8,192 tokens per turn.<br>
<strong>WebArena-Verified</strong>: up to 40 steps.<br>
<strong>MCP-Atlas</strong>: up to 256 turns.<br>
<strong>EnterpriseOps-Gym</strong> and <strong>AutomationBench</strong>: up to 50 turns.<br>
<strong>SWE-bench</strong>: OpenCode agent, up to 250 turns.<br>
<strong>Terminal-Bench 2.1</strong>: OpenCode agent, up to 100 turns.
</small></p>

</details>

### Edge inference

At 32K context, LFM3-1.7B prefills at least 2.5x faster and decodes at least 1.8x faster than every compared model on all three devices, while using the least memory.

<img src="https://huggingface.co/LiquidAI/LFM3-1.7B/resolve/main/assets/lfm3-edge-inference.webp" alt="LFM3-1.7B edge inference at 32K context: prefill throughput, decode throughput, and host plus GPU memory on AMD Ryzen AI Max+ 395, Apple M5 Max, and iPhone 17 Pro, compared with MiniCPM5-2B, Qwen3.5-4B, Qwen3.5-9B, and Gemma 4 E4B." width="4200" height="4223" style="width: 100%; max-width: 4200px; height: auto;" />

<details>
<summary><small>Evaluation details</small></summary>

<p><small>All models run as Q4_0 GGUF files in llama.cpp with 32,768 tokens of context, batch size 1, 100 output tokens, and GPU offload. Prefill is the prompt processing speed and decode is the generation speed, both in tokens per second. LFM3-1.7B uses a llama.cpp build with LFM3 support, and the other models use llama.cpp release b11744.</small></p>

<p><small>
<strong>AMD Ryzen AI Max+ 395</strong>: Radeon 8060S integrated GPU, Windows, Vulkan backend.<br>
<strong>Apple M5 Max</strong>: macOS, Metal backend.<br>
<strong>iPhone 17 Pro</strong>: Apple A19 Pro, iOS app built on llama.cpp.<br>
<strong>Memory</strong>: peak usage in GB (10<sup>9</sup> bytes). On AMD, it adds the host and GPU peaks from the same run, which can slightly overstate usage if the two peaks do not coincide. On Apple devices, the process footprint already includes Metal allocations.
</small></p>

</details>

### GPU inference

At 1,024 concurrent requests, LFM3-1.7B can produce 3.6 billion tokens/day on one NVIDIA B300.

<img src="https://huggingface.co/LiquidAI/LFM3-1.7B/resolve/main/assets/lfm3-gpu-throughput-b300.png" alt="LFM3-1.7B GPU inference: output throughput versus concurrent requests on one NVIDIA B300, compared with MiniCPM5-2B, Gemma 4 E4B, Qwen3.5-4B, and Qwen3.5-9B." width="1200" height="675" style="width: 100%; max-width: 1200px; height: auto;" />

## Training
<hr style="margin: -0.7em 0 1.2em 0; border: 0; border-top: 1px solid rgba(127, 127, 127, 0.3);" />

<img src="https://huggingface.co/LiquidAI/LFM3-1.7B/resolve/main/assets/lfm3-pre-training-recipe.webp" alt="LFM3-1.7B pre-training: web and synthetic data (about 15T tokens), then code, math, and science (3T tokens at 4K context), followed by mid-training on curated agentic data (3T tokens at 32K context), a 128K extension (500B tokens), and a 256K extension (50B tokens), for 22T tokens in total." width="2000" height="754" style="width: 100%; max-width: 2000px; height: auto;" />

**Pre-training:** two stages build LFM3-1.7B-Base on 22T tokens in total.

- **Main pre-training:** compared with LFM2, the mix adds more scientific papers, repository-level code, math, and a wider range of knowledge sources.
- **Mid-training:** the last 3.5T tokens use curated, higher-quality data with a larger share of agentic traces and tool calls. This stage also extends the context window to 256K tokens.

<img src="https://huggingface.co/LiquidAI/LFM3-1.7B/resolve/main/assets/lfm3-post-training-recipe.webp" alt="LFM3-1.7B post-training recipe: the student goes through SFT and mixed RL, specialist RL teachers such as math, code, and tool RL start from the mixed RL checkpoint, MOPD distills them back into the student, and agentic RL comes last." width="2000" height="924" style="width: 100%; max-width: 2000px; height: auto;" />

**Post-training:** four stages develop conversation, reasoning, and tool-use capabilities.

- **Supervised fine-tuning (SFT):** 1.75T tokens across various tasks, including chat, reasoning, tool calling, and agentic traces.
- **Mixed reinforcement learning:** many domains trained at once, from math and code to SQL and structured outputs. A length penalty in the reward keeps answers concise.
- **Multi-domain on-policy distillation (MOPD):** six specialist RL teachers (code, math, tool use, long context, agentic work, and enterprise workflows) are distilled back into a single model.
- **Agentic RL:** tasks from web browsing to office work are run inside real agent harnesses, preparing the model for deployment.

## Citation
<hr style="margin: -0.7em 0 1.2em 0; border: 0; border-top: 1px solid rgba(127, 127, 127, 0.3);" />

```bibtex
@article{liquidAI2026LFM3,
  author  = {Liquid AI},
  title   = {Introducing LFM3: Every Modality for Specialized Intelligence},
  journal = {Liquid AI Blog},
  year    = {2026},
  note    = {www.liquid.ai/blog/lfm3},
}
```

For questions and feedback, join [Discord](https://discord.com/invite/liquid-ai). For custom deployment and fine-tuning support, [contact Liquid AI](https://www.liquid.ai/connect?utm_source=huggingface&utm_medium=referral&utm_campaign=huggingface).
