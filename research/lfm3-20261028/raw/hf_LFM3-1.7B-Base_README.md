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
---

<div align="center">
  <img
    src="https://huggingface.co/LiquidAI/LFM3-1.7B-Base/resolve/main/assets/liquid-ai-banner.webp"
    alt="Liquid AI"
    style="width: 100%; max-width: 100%; height: auto; display: block; margin: 0;"
  />
  <div align="center" style="display: flex; justify-content: center; align-items: center; gap: 1.25em; margin: 8px 0 1.7rem; padding: 0; line-height: 1.3;">
    <a href="https://console.liquid.ai/dashboard" style="display: inline-flex; align-items: center; gap: 6px;"><img src="https://huggingface.co/LiquidAI/LFM3-1.7B-Base/resolve/main/assets/icons/api.svg" width="16" height="16" alt="" aria-hidden="true" style="display: block; flex: 0 0 16px; width: 16px; height: 16px; margin: 0;" /><strong>API</strong></a>
    <a href="https://playground.liquid.ai/" style="display: inline-flex; align-items: center; gap: 6px;"><img src="https://huggingface.co/LiquidAI/LFM3-1.7B-Base/resolve/main/assets/icons/try.svg" width="16" height="16" alt="" aria-hidden="true" style="display: block; flex: 0 0 16px; width: 16px; height: 16px; margin: 0;" /><strong>Try</strong></a>
    <a href="https://docs.liquid.ai/lfm/getting-started/welcome" style="display: inline-flex; align-items: center; gap: 6px;"><img src="https://huggingface.co/LiquidAI/LFM3-1.7B-Base/resolve/main/assets/icons/docs.svg" width="16" height="16" alt="" aria-hidden="true" style="display: block; flex: 0 0 16px; width: 16px; height: 16px; margin: 0;" /><strong>Docs</strong></a>
    <a href="https://www.liquid.ai/blog/lfm3" style="display: inline-flex; align-items: center; gap: 6px;"><img src="https://huggingface.co/LiquidAI/LFM3-1.7B-Base/resolve/main/assets/icons/blog.svg" width="16" height="16" alt="" aria-hidden="true" style="display: block; flex: 0 0 16px; width: 16px; height: 16px; margin: 0;" /><strong>Blog</strong></a>
  </div>
</div>

# LFM3-1.7B-Base

LFM3-1.7B-Base is the **pre-trained checkpoint** behind [LFM3-1.7B](https://huggingface.co/LiquidAI/LFM3-1.7B), a text model for local agents and specialized applications based on our new tri-hybrid architecture.

- **Pre-trained on 22T tokens:** the last 3.5T tokens are curated mid-training data with agentic traces and tool calls, and extend the context window to 256K tokens.
- **Designed for the edge:** at 4-bit precision, it takes about 1 GB of memory, so it fits on any phone or laptop.
- **Made to be specialized:** a starting point for continued pre-training and your own post-training.

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
<td style="border: 0; padding: 0.55em 0.75em;">Pre-trained, text-only base model</td>
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

LFM3-1.7B-Base is the checkpoint used to create LFM3-1.7B. It is only recommended for tasks that require heavy fine-tuning, like language-specific or domain-specific assistants, training on proprietary data, or experimenting with novel post-training approaches. For chat, tool calling, and agents, use [LFM3-1.7B](https://huggingface.co/LiquidAI/LFM3-1.7B).

## Inference
<hr style="margin: -0.7em 0 1.2em 0; border: 0; border-top: 1px solid rgba(127, 127, 127, 0.3);" />

LFM3-1.7B-Base uses the same architecture and modeling code as [LFM3-1.7B](https://huggingface.co/LiquidAI/LFM3-1.7B), with BF16 weights.

**Transformers quick start:**

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "LiquidAI/LFM3-1.7B-Base"
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    dtype="bfloat16",
    trust_remote_code=True,
)
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)

prompt = "The nematode C. elegans is"
input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(model.device)
output = model.generate(input_ids, max_new_tokens=128, do_sample=False)
print(tokenizer.decode(output[0], skip_special_tokens=True))
```

Mid-training included chat data with and without thinking traces, formatted with the same chat template as LFM3-1.7B. With `apply_chat_template`, reasoning is enabled by default, so responses start with a thinking trace. Set `enable_thinking=False` to prefill an empty thinking trace and have the model answer directly.

## Fine-tuning
<hr style="margin: -0.7em 0 1.2em 0; border: 0; border-top: 1px solid rgba(127, 127, 127, 0.3);" />

LFM3-1.7B-Base is the starting point for substantial customization, such as adapting to new domains, languages, or behaviors that diverge significantly from those of LFM3-1.7B, through continued pre-training or full post-training via [TRL](https://docs.liquid.ai/lfm/fine-tuning/trl).

These notebooks start from LFM3-1.7B. To start from the base model, set `model_id = "LiquidAI/LFM3-1.7B-Base"`.

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
<td style="text-align: center; border: 0; padding: 0.55em 0.75em;"><a href="https://colab.research.google.com/drive/1_azJLYp0vZSxbfWwNX_Hx1w6cxALgUO0?usp=sharing" title="SFT with TRL"><img src="https://colab.research.google.com/assets/colab-badge.svg" width="117" height="20" alt="Open in Colab" style="display: inline-block; width: 117px; height: 20px; margin: 0; vertical-align: middle;" /></a></td>
</tr>
<tr style="border: 0;">
<td style="border: 0; padding: 0.55em 0.75em;"><strong>CPT</strong></td>
<td style="border: 0; padding: 0.55em 0.75em;">Learn a new language (Turkish) from raw text</td>
<td style="text-align: center; border: 0; padding: 0.55em 0.75em;"><a href="https://colab.research.google.com/drive/1iiv_jr19kVPH0YTwx96O8k_VBkFli_r9?usp=sharing" title="Continued pre-training with TRL"><img src="https://colab.research.google.com/assets/colab-badge.svg" width="117" height="20" alt="Open in Colab" style="display: inline-block; width: 117px; height: 20px; margin: 0; vertical-align: middle;" /></a></td>
</tr>
</tbody>
</table>

## Training
<hr style="margin: -0.7em 0 1.2em 0; border: 0; border-top: 1px solid rgba(127, 127, 127, 0.3);" />

<img src="https://huggingface.co/LiquidAI/LFM3-1.7B-Base/resolve/main/assets/lfm3-pre-training-recipe.webp" alt="LFM3-1.7B pre-training: web and synthetic data (about 15T tokens), then code, math, and science (3T tokens at 4K context), followed by mid-training on curated agentic data (3T tokens at 32K context), a 128K extension (500B tokens), and a 256K extension (50B tokens), for 22T tokens in total." width="2000" height="754" style="width: 100%; max-width: 2000px; height: auto;" />

**Pre-training:** two stages build LFM3-1.7B-Base on 22T tokens in total.

- **Main pre-training:** compared with LFM2, the mix adds more scientific papers, repository-level code, math, and a wider range of knowledge sources.
- **Mid-training:** the last 3.5T tokens use curated, higher-quality data with a larger share of agentic traces and tool calls. This stage also extends the context window to 256K tokens.

Post-training from this checkpoint (SFT, mixed RL, multi-domain on-policy distillation, and agentic RL) produces [LFM3-1.7B](https://huggingface.co/LiquidAI/LFM3-1.7B).

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

For questions and feedback, join [Discord](https://discord.com/invite/liquid-ai). For custom deployment and fine-tuning support, [contact Liquid AI](https://www.liquid.ai/contact).
