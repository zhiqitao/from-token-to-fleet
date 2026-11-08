<div align="center">
  <img src="assets/logo.svg" width="40%" alt="dInfer" />
</div>

<h4 align="center">

[![License: MIT](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](./LICENSE)
[![HuggingFace: Models](https://img.shields.io/badge/HuggingFace-Models-yellow)](https://huggingface.co/inclusionAI/LLaDA-MoE-7B-A1B-Instruct)
[![Technical Report: Arxiv](https://img.shields.io/badge/Technical%20Report-Arxiv-red)](https://arxiv.org/abs/2510.08666)

<!-- [![arXiv][arxiv-image]][arxiv-url] -->

</h4>

## Introduction
dInfer is an efficient and extensible inference framework for dLLMs. As illustrated in the following architecture, it modularizes inference into four components:
*model*, *diffusion iteration manager*, *decoder* and *KV-cache manager*. It provides well-designed APIs for
flexible algorithms combinations in each component. It now supports batched inference for improved throughput.

<p align="center">
  <img src="assets/Framework2.png" alt="dInfer v0.1 architecture" width="600">
  <br>
  <b>Figure</b>: Overall Architecture of dInfer
</p>

dInfer supports multiple dLLM variants, including LLaDA, LLaDA-MoE and LLaDA2.

## News
**\[2025/12/21\]** release v0.2. The major features of this release can be found [here](https://github.com/inclusionAI/dInfer/releases/tag/v0.2.0).

**\[2025/12/10\]** Support and speed up the formal version of block diffusion LLMs (LLaDA2-mini and LLaDA2-flash). Support quant versions of LLaDA2-mini and LLaDA2-flash.

**\[2025/11/15\]** Support the inference on block diffusion LLMs (LLaDA2-mini-preview and LLaDA2-flash-preview).

**\[2025/10/10\]** Release the first version of the dInfer framework.

## Contents
- [Supported Models](#supported-models)
- [Quick Start](#quick-start)
- [Benchmark Results](#benchmark-results)

## Supported Models

dInfer supports multiple diffusion language model variants with different architectures and sizes. Below are the HuggingFace model links and their corresponding implementation files:

| Model | Size | Implementation | HuggingFace Link |
|-------|------|----------------|------------------|
| LLaDA2.0-mini | 16B | [LLaDA2MoeModelLM](python/dinfer/model/modeling_llada2_moe.py) | [inclusionAI/LLaDA2.0-mini](https://huggingface.co/inclusionAI/LLaDA2.0-mini) |
| LLaDA2.0-flash | 100B | [LLaDA2MoeModelLM](python/dinfer/model/modeling_llada2_moe.py) | [inclusionAI/LLaDA2.0-flash](https://huggingface.co/inclusionAI/LLaDA2.0-flash) |
| LLaDA2.0-mini-preview | 16B | [LLaDA2MoeModelLM](python/dinfer/model/modeling_llada2_moe.py) | [inclusionAI/LLaDA2.0-mini-preview](https://huggingface.co/inclusionAI/LLaDA2.0-mini-preview) |
| LLaDA2.0-flash-preview | 100B | [LLaDA2MoeModelLM](python/dinfer/model/modeling_llada2_moe.py) | [inclusionAI/LLaDA2.0-flash-preview](https://huggingface.co/inclusionAI/LLaDA2.0-flash-preview) |
| LLaDA-MoE-7B-A1B-Base | 7B | [LLaDAMoeModelLM](python/dinfer/model/modeling_fused_olmoe.py) | [inclusionAI/LLaDA-MoE-7B-A1B-Base](https://huggingface.co/inclusionAI/LLaDA-MoE-7B-A1B-Base) |
| LLaDA-MoE-7B-A1B-Instruct | 7B | [LLaDAMoeModelLM](python/dinfer/model/modeling_fused_olmoe.py) | [inclusionAI/LLaDA-MoE-7B-A1B-Instruct](https://huggingface.co/inclusionAI/LLaDA-MoE-7B-A1B-Instruct) |
| LLaDA-8B-Base | 8B | [LLaDAModelLM](python/dinfer/model/modeling_llada.py) | [GSAI-ML/LLaDA-8B-Base](https://huggingface.co/GSAI-ML/LLaDA-8B-Base) |
| LLaDA-8B-Instruct | 8B | [LLaDAModelLM](python/dinfer/model/modeling_llada.py) | [GSAI-ML/LLaDA-8B-Instruct](https://huggingface.co/GSAI-ML/LLaDA-8B-Instruct) |
| LLaDA-1.5 | 8B | [LLaDAModelLM](python/dinfer/model/modeling_llada.py) | [GSAI-ML/LLaDA-1.5](https://huggingface.co/GSAI-ML/LLaDA-1.5) |

## Quick Start

### Install dInfer

```
git clone https://github.com/inclusionAI/dInfer.git
cd dInfer
pip install .
```

To use it with vLLM backend (it works with LLaDA and LLaDA-MoE), please install vLLM.

```
pip install vllm==0.10.2
```

To use it with SGLang backend (it works with LLaDA2), please install SGLang.
```
pip install sglang==0.5.3.post1
```

### Convert to FusedMoE (LLaDA-MoE only)

To run LLaDA-MoE model downloaded from HuggingFace, we need to first convert it to a format supported by dInfer. dInfer provides a script `tools/transfer.py` for the format conversion.

#### 1) Download and Convert

```bash
pip install -U huggingface_hub hf_transfer
export HF_HUB_ENABLE_HF_TRANSFER=1

# Download Instruct checkpoint
hf download inclusionAI/LLaDA-MoE-7B-A1B-Instruct \
  --repo-type model \
  --local-dir /path/to/LLaDA-MoE-7B-A1B-Instruct

# Convert to FusedMoE
python -m tools.transfer \
  --input  /path/to/LLaDA-MoE-7B-A1B-Instruct \
  --output /path/to/LLaDA-MoE-7B-A1B-Instruct-fused
```

#### 2) Load the model

```python
from dinfer.model import AutoModelForCausalLM
from transformers import AutoTokenizer
m = "/path/to/LLaDA-MoE-7B-A1B-Instruct-fused"
tok = AutoTokenizer.from_pretrained(m, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(m, trust_remote_code=True, torch_dtype="bfloat16")
```

### Run Inference

#### Benchmark (speed only)

Measure throughput (TPS) only; predictions are saved under `--output_dir` with no automatic scoring. 

- **LLaDA2 model** 

  - LLaDA2-flash Dataset profiling (threshold decoder, TP across 4 GPUs):

  ```bash
  python benchmarks/benchmark_dataset_sglang.py \
        --model_name inclusionAI/LLaDA2.0-flash \
        --dataset dataset_path \
        --gen_len 2048 \
        --block_length 32 \
        --gpu 0,1,2,3 \
        --output_dir runs/llada2_flash \
        --use_tp \
      	--parallel_decoding threshold \
      	--threshold 0.9 \
      	--cache prefix \
      	--use_bd
  ```

  - LLaDA2-mini Dataset profiling (threshold decoder, TP across 4 GPUs):

  ```bash
  python benchmarks/benchmark_dataset_sglang.py \
        --model_name inclusionAI/LLaDA2.0-mini \
        --dataset dataset_path \
        --gen_len 2048 \
        --block_length 32 \
        --gpu 0,1,2,3 \
        --output_dir runs/llada2_mini \
        --use_tp \
      	--parallel_decoding threshold \
      	--threshold 0.9 \
      	--cache prefix \
      	--use_bd
  ```

- **LLaDA, LLaDA1.5 and LLaDA-MoE model** 

  - LLaDA-MoE Dataset profiling (threshold decoder, TP across 4 GPUs):

  ```bash
  python benchmarks/benchmark_dataset.py \
  --model_name inclusionAI/LLaDA-MoE-7B-A1B-Instruct \
  --model_type llada_moe \
  --dataset dataset_path \
  --gen_len 1024 \
  --block_length 64 \
  --gpu 0,1,2,3 \
  --output_dir runs/llada_moe_threshold \
  --use_tp \
  --parallel_decoding threshold \
  --threshold 0.8 \
  --cache dual \
  --prefix_look 16 \
  --after_look 16 \
  --warmup_times 4 \
  --cont_weight 0.3
  ```

  - LLaDA Single-sample profiling (threshold decoder, TP across 4 GPUs):

  ```bash
  python benchmarks/benchmark.py \
    --model_name GSAI-ML/LLaDA-8B-Instruct \
    --model_type llada \
    --gen_len 2048 \
    --block_length 32 \
    --gpu 0,1,2,3 \
    --use_tp \
    --parallel_decoding threshold \
    --threshold 0.9 \
    --cache prefix
  ```

  - LLaDA, LLaDA1.5, LLaDA-MoE can use benchmark_dataset.py and benchmark.py. 

#### Evaluation with lm-eval (speed + accuracy)

- Built on HuggingFace `lm-eval-harness` to compute TPS and benchmark scores.
- Tasks provided:
  - `gsm8k_llada`: math reasoning.
  - `mbpp_sanitized_llada`: sanitized Python code generation.
- For more examples and comprehensive instructions, see [our quickstart guide](https://github.com/inclusionAI/dInfer/blob/master/evaluations/eval_guide.md).

## Benchmark Results

### The inference speed (TPS) on LLaDA-MoE

dInfer delivers over 1,100 TPS at batch size 1 on HumanEval and on average 800+ TPS across six benchmarks on a single node with 8×H800 GPUs.
<p align="center">
  <img src="assets/dinfer_tps.png" alt="dInfer v0.1 speedup" width="600">
  <br>
  <b>Figure</b>: Benchmark results on LLaDA-MoE
</p>

**Speedup comparisons:**
- 10× faster than Fast-dLLM while maintaining accuracy
- 2-3× faster than Qwen2.5-3B on vLLM (LLaDA-MoE) with comparable quality

### The inference speed (TPS) on LLaDA2-flash-CAP

The inference speed is measured on LLaDA2-flash-CAP (with 100B parameters) on 8 H20 GPUs (parallel decoding threshold=0.95, generation length=1000).

| Benchmark        | batch size = 1 | batch size = 32 |
|------------------|----------------|-----------------|
| openai_humaneval | 753.10         | 2558.51         |
| gsm8k            | 591.90         | 2111.79         |
| IFEval           | 222.60         | 931.89          |
| CruxEval-O       | 562.90         | 1967.08         |
| mbpp             | 773.00         | 2262.45         |
| AVG              | 580.70         | 1966.34         |

## Limitations
- **Block Diffusion**: Not supported on LLaDA Dense/MoE models (use `--use_bd` with LLaDA2 only)

## Contact us
- Wechat Group
<p align="left">
  <img src="assets/Wechat.JPG" alt="Wechat Group" width="150">
</p>

## Citation
```
@article{dinfer,
    title={dInfer: An Efficient Inference Framework for Diffusion Language Models},
    author={Yuxin Ma, Lun Du, Lanning Wei, Kun Chen, Qian Xu, Kangyu Wang, Guofeng Feng, Guoshan Lu, Lin Liu, Xiaojing Qi, Xinyuan Zhang, Zhen Tao, Haibo Feng, Ziyun Jiang, Ying Xu, Zenan Huang, Yihong Zhuang, Haokai Xu, Jiaqi Hu, Zhenzhong Lan, Junbo Zhao, Jianguo Li, Da Zheng},
    year={2025},
    journal={arXiv preprint arXiv:2510.08666}
}
```
