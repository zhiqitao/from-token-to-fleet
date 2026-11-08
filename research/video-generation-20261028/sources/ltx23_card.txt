---
language:
- en
- de
- es
- fr
- ja
- ko
- zh
- it
- pt
library_name: diffusers
license: other
license_name: ltx-2-community-license-agreement
license_link: https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2
pipeline_tag: image-to-video
arxiv: 2601.03233
tags:
- image-to-video
- text-to-video
- video-to-video
- image-text-to-video
- audio-to-video
- text-to-audio
- video-to-audio
- audio-to-audio
- text-to-audio-video
- image-to-audio-video
- image-text-to-audio-video
- ltx-2
- ltx-video
- ltxv
- lightricks
- ltx
- ltx-2.3
pinned: true
demo: https://app.ltx.studio/ltx-2-playground/i2v
---

# LTX-2.3 Model Card

This model card focuses on the LTX-2.3 model, which is a significant update to the [LTX-2 model](https://huggingface.co/Lightricks/LTX-2) with improved audio and visual quality as well as enhanced prompt adherence.
LTX-2 was presented in the paper [LTX-2: Efficient Joint Audio-Visual Foundation Model](https://huggingface.co/papers/2601.03233).

💻💻 **If you want to dive in right to the code - it is available [here](https://github.com/Lightricks/LTX-2).** 💾💾

LTX-2.3 is a DiT-based audio-video foundation model designed to generate synchronized video and audio within a single model. It brings together the core building blocks of modern video generation, with open weights and a focus on practical, local execution. 

[![LTX-2 Open Source](ltx2.3-open.png)](https://youtu.be/o-7us-BR_gQ)

# Model Checkpoints

| Name                               | Notes                                                                                                              |
|------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| ltx-2.3-22b-dev                    | The full model, flexible and trainable in bf16                                                                     |
| ltx-2.3-22b-distilled              | The distilled version of the full model, 8 steps, CFG=1                                                            |
| ltx-2.3-22b-distilled-1.1              | The distilled v1.1 version of the full model, 8 steps, CFG=1 - A different aesthetic experience and improved audio compared to v1.0                                                           |
| ltx-2.3-22b-distilled-lora-384     | A LoRA version of the distilled model applicable to the full model                                                 |
| ltx-2.3-22b-distilled-lora-384-1.1     | A LoRA version of the v1.1 distilled model applicable to the full model                                                 |
| ltx-2.3-spatial-upscaler-x2-1.1    | An x2 spatial upscaler for the ltx-2.3 latents, used in multi stage (multiscale) pipelines for higher resolution   |
| ltx-2.3-spatial-upscaler-x1.5-1.0  | An x1.5 spatial upscaler for the ltx-2.3 latents, used in multi stage (multiscale) pipelines for higher resolution |
| ltx-2.3-temporal-upscaler-x2-1.0   | An x2 temporal upscaler for the ltx-2.3 latents, used in multi stage (multiscale) pipelines for higher FPS         |

## Model Details
- **Developed by:** Lightricks
- **Model type:** Diffusion-based audio-video foundation model
- **Language(s):** English

# Online demo
LTX-2.3 is accessible right away via the [API Playground](https://console.ltx.video/playground/).

# Run locally

## Direct use license
You can use the models - full, distilled, upscalers and any derivatives of the models - for purposes under the [license](https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2).

## ComfyUI
We recommend you use the built-in LTXVideo nodes that can be found in the ComfyUI Manager. 
For manual installation information, please refer to our [documentation site](https://docs.ltx.video/open-source-model/integration-tools/comfy-ui).

## PyTorch codebase

The [LTX-2 codebase](https://github.com/Lightricks/LTX-2) is a monorepo with several packages. From model definition in 'ltx-core' to pipelines in 'ltx-pipelines' and training capabilities in 'ltx-trainer'.
The codebase was tested with Python >=3.12, CUDA version >12.7, and supports PyTorch ~= 2.7.

### Installation

```bash
git clone https://github.com/Lightricks/LTX-2.git
cd LTX-2

# From the repository root
uv sync
source .venv/bin/activate
```

### Inference

To use our model, please follow the instructions in our [ltx-pipelines](https://github.com/Lightricks/LTX-2/blob/main/packages/ltx-pipelines/README.md) package.

## Diffusers 🧨

LTX-2.3 support in the [Diffusers Python library](https://huggingface.co/docs/diffusers/main/en/index) is coming soon!

## General tips:
* Width & height settings must be divisible by 32. Frame count must be divisible by 8 + 1. 
* In case the resolution or number of frames are not divisible by 32 or 8 + 1, the input should be padded with -1 and then cropped to the desired resolution and number of frames.
* For tips on writing effective prompts, please visit our [Prompting guide](https://ltx.video/blog/how-to-prompt-for-ltx-2) 

### Limitations
- This model is not intended or able to provide factual information.
- As a statistical model this checkpoint might amplify existing societal biases.
- The model may fail to generate videos that matches the prompts perfectly.
- Prompt following is heavily influenced by the prompting-style.
- The model may generate content that is inappropriate or offensive.
- When generating audio without speech, the audio may be of lower quality.

# Train the model

The base (dev) model is fully trainable.

It's extremely easy to reproduce the LoRAs and IC-LoRAs we publish with the model by following the instructions on the [LTX-2 Trainer Readme](https://github.com/Lightricks/LTX-2/blob/main/packages/ltx-trainer/README.md).

Training for motion, style or likeness (sound+appearance) can take less than an hour in many settings.

## Citation

```bibtex
@article{hacohen2025ltx2,
  title={LTX-2: Efficient Joint Audio-Visual Foundation Model},
  author={HaCohen, Yoav and Brazowski, Benny and Chiprut, Nisan and Bitterman, Yaki and Kvochko, Andrew and Berkowitz, Avishai and Shalem, Daniel and Lifschitz, Daphna and Moshe, Dudu and Porat, Eitan and Richardson, Eitan and Guy Shiran and Itay Chachy and Jonathan Chetboun and Michael Finkelson and Michael Kupchick and Nir Zabari and Nitzan Guetta and Noa Kotler and Ofir Bibi and Ori Gordon and Poriya Panet and Roi Benita and Shahar Armon and Victor Kulikov and Yaron Inger and Yonatan Shiftan and Zeev Melumian and Zeev Farbman},
  journal={arXiv preprint arXiv:2601.03233},
  year={2025}
}
```