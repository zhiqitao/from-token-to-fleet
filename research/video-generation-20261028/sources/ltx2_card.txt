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
new_version: Lightricks/LTX-2.3
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
pinned: true
demo: https://app.ltx.studio/ltx-2-playground/i2v
---

# LTX-2 Model Card

This model card focuses on the LTX-2 model, as presented in the paper [LTX-2: Efficient Joint Audio-Visual Foundation Model](https://huggingface.co/papers/2601.03233). The codebase is available [here](https://github.com/Lightricks/LTX-2).

LTX-2 is a DiT-based audio-video foundation model designed to generate synchronized video and audio within a single model. It brings together the core building blocks of modern video generation, with open weights and a focus on practical, local execution. 

[![LTX-2 Open Source](https://img.youtube.com/vi/8fWAJXZJbRA/maxresdefault.jpg)](https://www.youtube.com/watch?v=8fWAJXZJbRA)

# Model Checkpoints

| Name                           | Notes                                                                                                          |
|--------------------------------|----------------------------------------------------------------------------------------------------------------|
| ltx-2-19b-dev                  | The full model, flexible and trainable in bf16                                                                 |
| ltx-2-19b-dev-fp8              | The full model in fp8 quantization                                                                             |
| ltx-2-19b-dev-fp4              | The full model in nvfp4 quantization                                                                           | 
| ltx-2-19b-distilled            | The distilled version of the full model, 8 steps, CFG=1                                                        |
| ltx-2-19b-distilled-lora-384   | A LoRA version of the distilled model applicable to the full model                                             |
| ltx-2-spatial-upscaler-x2-1.0  | An x2 spatial upscaler for the ltx-2 latents, used in multi stage (multiscale) pipelines for higher resolution |
| ltx-2-temporal-upscaler-x2-1.0 | An x2 temporal upscaler for the ltx-2 latents, used in multi stage (multiscale) pipelines for higher FPS       |

## Model Details
- **Developed by:** Lightricks
- **Model type:** Diffusion-based audio-video foundation model
- **Language(s):** English

# Online demo
LTX-2 is accessible right away via the following links:
- [LTX-Studio text-to-video](https://app.ltx.studio/ltx-2-playground/t2v)
- [LTX-Studio image-to-video](https://app.ltx.studio/ltx-2-playground/i2v)

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

LTX-2 is supported in the [Diffusers Python library](https://huggingface.co/docs/diffusers/main/en/index) for text & image-to-video generation.
Read more on LTX-2 with diffusers [here](https://huggingface.co/docs/diffusers/main/en/api/pipelines/ltx2#diffusers.LTX2Pipeline.__call__.example). 

### Use with diffusers
To achieve production quality generation, it's recommended to use the two-stage generation pipeline. 
Example for 2-stage inference of text-to-video: 
```python
import torch
from diffusers import FlowMatchEulerDiscreteScheduler
from diffusers.pipelines.ltx2 import LTX2Pipeline, LTX2LatentUpsamplePipeline
from diffusers.pipelines.ltx2.latent_upsampler import LTX2LatentUpsamplerModel
from diffusers.pipelines.ltx2.utils import STAGE_2_DISTILLED_SIGMA_VALUES
from diffusers.pipelines.ltx2.export_utils import encode_video

device = "cuda:0"
width = 768
height = 512

pipe = LTX2Pipeline.from_pretrained(
    "Lightricks/LTX-2", torch_dtype=torch.bfloat16
)
pipe.enable_sequential_cpu_offload(device=device)

prompt = "A beautiful sunset over the ocean"
negative_prompt = "shaky, glitchy, low quality, worst quality, deformed, distorted, disfigured, motion smear, motion artifacts, fused fingers, bad anatomy, weird hand, ugly, transition, static."

# Stage 1 default (non-distilled) inference
frame_rate = 24.0
video_latent, audio_latent = pipe(
    prompt=prompt,
    negative_prompt=negative_prompt,
    width=width,
    height=height,
    num_frames=121,
    frame_rate=frame_rate,
    num_inference_steps=40,
    sigmas=None,
    guidance_scale=4.0,
    output_type="latent",
    return_dict=False,
)

latent_upsampler = LTX2LatentUpsamplerModel.from_pretrained(
    "Lightricks/LTX-2",
    subfolder="latent_upsampler",
    torch_dtype=torch.bfloat16,
)
upsample_pipe = LTX2LatentUpsamplePipeline(vae=pipe.vae, latent_upsampler=latent_upsampler)
upsample_pipe.enable_model_cpu_offload(device=device)
upscaled_video_latent = upsample_pipe(
    latents=video_latent,
    output_type="latent",
    return_dict=False,
)[0]

# Load Stage 2 distilled LoRA
pipe.load_lora_weights(
    "Lightricks/LTX-2", adapter_name="stage_2_distilled", weight_name="ltx-2-19b-distilled-lora-384.safetensors"
)
pipe.set_adapters("stage_2_distilled", 1.0)
# VAE tiling is usually necessary to avoid OOM error when VAE decoding
pipe.vae.enable_tiling()
# Change scheduler to use Stage 2 distilled sigmas as is
new_scheduler = FlowMatchEulerDiscreteScheduler.from_config(
    pipe.scheduler.config, use_dynamic_shifting=False, shift_terminal=None
)
pipe.scheduler = new_scheduler
# Stage 2 inference with distilled LoRA and sigmas
video, audio = pipe(
    latents=upscaled_video_latent,
    audio_latents=audio_latent,
    prompt=prompt,
    negative_prompt=negative_prompt,
    num_inference_steps=3,
    noise_scale=STAGE_2_DISTILLED_SIGMA_VALUES[0], # renoise with first sigma value https://github.com/Lightricks/LTX-2/blob/main/packages/ltx-pipelines/src/ltx_pipelines/ti2vid_two_stages.py#L218
    sigmas=STAGE_2_DISTILLED_SIGMA_VALUES,
    guidance_scale=1.0,
    output_type="np",
    return_dict=False,
)

encode_video(
    video[0],
    fps=frame_rate,
    audio=audio[0].float().cpu(),
    audio_sample_rate=pipe.vocoder.config.output_sampling_rate,
    output_path="ltx2_lora_distilled_sample.mp4",
)
```
For more inference examples, including generation with the distilled checkpoint, visit [here](https://huggingface.co/docs/diffusers/main/en/api/pipelines/ltx2#diffusers.LTX2Pipeline.__call__.example). 

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