#!/usr/bin/env python3
"""Build a claim ledger from explicitly inspected primary sources."""
from pathlib import Path
from datetime import datetime, timezone
from hashlib import sha256
import json
R=Path(__file__).resolve().parent
raw=json.loads((R/'evidence/sources.json').read_text())
sources={}
for s in raw:
    if s['status']=='fetched': sources[s['id']]=s.copy()
pins=json.loads((R/'evidence/code_pins.json').read_text())
dates={'AWQ-V1':'2023-06-01','AWQ-V5':'2024-07-18','AWQ-V6':'2026-04-25',
       'GPTQ-V1':'2022-10-31','GPTQ-PAPER':'2023-03-22','OCP-V1':'2023-09-07',
       'OCP-V11':'2026-10-09','OFP8-FIXED':'2023-12-01 correction; original 2023-06-20',
       'NVFP4-BLOG':'2025-06-24','NVFP4-PAPER':'2026-03-04 arXiv v2; document header 2026-03-06',
       'SMOOTHQUANT':'2024-03-29 v7','QLORA':'2023-05-23 v1','KIVI':'2024-07-25 v2'}
for sid,s in sources.items():
    p=R/s['raw_path']; assert p.exists() and sha256(p.read_bytes()).hexdigest()==s['sha256'],sid
    s['publication_or_commit_date']=dates.get(sid,'not established; retrieval date is not publication date')
    s['temporal_scope']='retrieved October 2026; no historical implementation-support inference'
    for pin in pins.values():
        if pin.get('sha','!') in s['url']:
            s['code_revision']=pin['sha']; s['publication_or_commit_date']=pin['commit_date']
    if sid in dates and dates[sid][:10]<='2026-08-30': s['temporal_scope']='specified paper/spec revision predates cutoff; not proof of then-current engine support'
claims=[]
def add(cid,text,refs,scope='Current source snapshot only',kind='FACT',provenance='1P',stage='UNMEASURED',limits='',placement='7'):
    for sid,anchor in refs:
        assert sid in sources,(cid,sid)
        content=(R/sources[sid]['text_path']).read_text()
        assert anchor.casefold() in content.casefold(),(cid,sid,anchor)
    claims.append({'id':cid,'claim_zh':text,'evidence':{'axis1_provenance':provenance,'axis2_epistemic':kind,'axis3_measurement':stage},
                   'verification':'source-checked' if kind=='FACT' else 'independently-derived' if kind=='DERIVED' else 'not-measured',
                   'source_refs':[{'source_id':sid,'text_anchor':anchor} for sid,anchor in refs],
                   'scope':scope,'limitations':limits,'proposed_chapter':placement,'applied':False})
add('Q01','AWQ 是 activation-aware 的 weight-only PTQ 方法；用激活统计搜索通道缩放，不等于激活也已量化。',[('AWQ-V6','weight-only'),('AWQ-V6','backpropagation')], 'Paper v6, 2026-04-25; mechanism predates cutoff',limits='论文的泛化和加速结果不能当作本部署结果。',placement='5,7')
add('Q02','AWQ 不等于永久保留 1% 权重为 FP16；论文以缩放保护显著通道，避免该混合精度实现成本。',[('AWQ-V6','without actually keeping them as FP16')], 'Paper mechanism predates cutoff',placement='7')
add('Q03','GPTQ 是用近似二阶信息补偿量化误差的 one-shot 权重量化方法；原论文未量化激活。',[('GPTQ-PAPER','second-order'),('GPTQ-PAPER','do not include activation quantization')], 'GPTQ v2, 2023-03-22',placement='7')
add('Q04','AWQ/GPTQ 方法名不能唯一决定 group、scale、zero、排列或 checkpoint 字节数。',[('AWQ-LINEAR','scaled_zeros'),('VLLM-AWQ-CURRENT','Convert AWQ weight and zero-point tensors'),('GPTQ-QUANT','self.scale')],limits='这是代码差异约束，不是新容器标准。',placement='7,11')
add('Q05','GGUF 是含 metadata、tensor descriptors、tensor types、alignment 的文件格式，不是单一数值编码。',[('GGUF-PINNED','tensor_infos'),('GGUF-PINNED','general.alignment')],placement='7')
add('Q06','GGUF 文件级量化标签不保证所有 tensor 同精度；Q4_K_M 路径可以提升某些 tensor 到 Q6_K。',[('LLAMA-MIX','LLAMA_FTYPE_MOSTLY_Q4_K_M'),('LLAMA-MIX','GGML_TYPE_Q6_K')],placement='7,18')
add('Q07','K-quants 使用层次化尺度；Q4_K 为 256 值、144 字节，即 4.5 bit/value。',[('GGML-BLOCKS','block_q4_K')],kind='DERIVED',stage='ANALYTICAL',limits='tensor block payload，不是 Q4_K_M 全模型平均。')
add('Q08','IQ 家族不等于一个规则：IQ2 有 grid/sign 解码，IQ4_NL 用非线性查表；并非所有 IQ 都要求 imatrix。',[('GGML-QUANTS','iq2xxs_grid'),('GGML-QUANTS','dequantize_row_iq4_nl'),('LLAMA-MIX','requires_imatrix')],limits='逐 tensor/类型核查 imatrix 条件。')
add('Q09','MXFP4 的 OCP 1.0 定义是 E2M1 数据、32 元素共享 8-bit E8M0 scale；没有 affine zero point。',[('OCP-V1','MXFP4'),('OCP-V1','E8M0')], 'OCP 1.0, September 2023')
add('Q10','MXFP4 block payload 为 17 B/32，等于 0.53125 B/value 或 4.25 bit/value。',[('GGML-BLOCKS','block_mxfp4'),('OCP-V1','MXFP4')],kind='DERIVED',stage='ANALYTICAL',limits='不含 tensor/global/container/对齐及运行时副本。')
add('Q11','OCP 1.1（2026-10-09）将 E8M0 改称 UE8M0，并澄清转换、舍入和边界情况；不应回填 August snapshot。',[('OCP-V11','Renamed E8M0 to UE8M0'),('OCP-V11','10/9/2026')], 'POST-CUTOFF; separately dated addendum only',placement='27')
add('Q12','NVFP4 1D 路径为 E2M1 × 每16值 E4M3 scale × tensor级 FP32 scale。',[('NVFP4-TE','x = x_e2m1 * s_block * s_global'),('NVFP4-BLOG','16')],limits='不是 OCP MXFP4 的别名。')
add('Q13','NVFP4 1D 权重 payload 为 0.5625 B/value，另加 tensor级 scale；4096² 权重加一个 global scale 为 9,437,188 B。',[('NVFP4-TE','s_global is a global FP32'),('GGML-BLOCKS','QK_NVFP4_SUB')],kind='DERIVED',stage='ANALYTICAL',limits='非训练总显存；不含额外 scale/amax/inverse 和 padding。')
add('Q14','TE 的 NVFP4 训练 recipe 默认权重可用 16×16 2D scaling；梯度舍入、RHT 和高精度层属于训练 recipe，不是 FP4 格式自动属性。',[('TE-PRIMER','16x16'),('NVFP4-TE','Stochastic rounding is enabled only for gradients'),('TE-PRIMER','Last few layers')],placement='7,8')
add('Q15','GGML block_nvfp4 是64值、4个 UE4M3 scale、32字节数据；已读 reference dequant 本身没有 tensor global-scale 参数。',[('GGML-BLOCKS','block_nvfp4'),('GGML-QUANTS','dequantize_row_nvfp4')],limits='并不证明与 NVIDIA checkpoint 逐字节/逐值互换；转换路径及量程需另查。')
add('Q16','FP8 不唯一：OFP8 E4M3 与 E5M2 的范围及 Inf/NaN 语义不同；规范没有规定 scaling 的选择和维护。',[('OFP8-FIXED','scaling factor selection'),('OFP8-FIXED','57,344')], 'OFP8 revision corrected 2023-12-01')
add('Q17','SmoothQuant 是面向 W8A8 的 PTQ 方法；NF4 是 QLoRA 的非均匀4位表示，不等于原生 FP4 GEMM。',[('SMOOTHQUANT','W8A8'),('QLORA','NormalFloat')], 'Source paper revisions predate cutoff',limits='这里不报告论文速度数字。',placement='7,8')
add('Q18','KIVI 研究 KV 独立量化，key 采用 per-channel、value per-token，并有高精度 residual；不是量化权重自动获得的节省。',[('KIVI','per-channel'),('KIVI','per-token'),('KIVI','residual')], 'KIVI v2 2024-07-25',placement='7,11')
add('Q19','vLLM 的 NVFP4 有 CUTLASS 原生低精度路径、Marlin W4A16，以及 dequant→BF16 fallback；加载成功不等于 native FP4。',[('VLLM-NV-CUTLASS','scaled_fp4_quant'),('VLLM-NV-MARLIN','W4A16'),('VLLM-NV-EMU','dequant')],placement='8,11')
add('Q20','vLLM pinned FP4 Marlin support helper 要求 CUDA 且 capability≥75，但 layer shape/group/activation 的限制仍独立存在。',[('VLLM-MARLIN-UTIL','has_device_capability(75)'),('VLLM-MARLIN-UTIL','FP4_MARLIN_SUPPORTED_GROUP_SIZES')],limits='helper 条件不是完整部署支持承诺。',placement='11')
add('Q21','vLLM MXFP4 Marlin 是 A16 kernel，并明确忽略所请求的 activation quantization。',[('VLLM-MX-MARLIN','requested activation quantization'),('VLLM-MX-MARLIN','weight-only')],placement='8,11')
add('Q22','TE 安装文档要求 CUDA12.1+，Blackwell 为12.8+，cuDNN9.12+；这是TE要求，不是所有 engine 的通用版本。',[('TE-INSTALL','12.8+ for Blackwell'),('TE-INSTALL','cuDNN 9.12')],placement='11')
add('Q23','CUDA minor compatibility 表的12.x≥525和13.x≥580不是 Blackwell/PTX 的充分支持条件；PTX和新功能可能要求新驱动。',[('CUDA-COMPAT','>= 580'),('CUDA-COMPAT','Applications using PTX')],limits='本任务未安装/运行驱动验证。',placement='11')
add('Q24','TensorRT-LLM 支持页仍出现25.06/10.11，而 pinned HEAD 依赖 CUDA13/PyTorch2.14；这些不是同一已验证软件组合。',[('TRT-SUPPORT','25.06'),('TRT-REQUIREMENTS','cuda-python>=13'),('TRT-REQUIREMENTS','torch>=2.14.0a0')],limits='不要用旧支持页给新 HEAD 认证。',placement='11,27')
add('Q25','ModelOpt 示例 NVFP4 推理要求 Blackwell+TensorRT-LLM1.2+；SGLang 另有SM80–SM90 Marlin fallback，两者说的是不同 compute path。',[('MO-HF-PTQ','TensorRT-LLM v1.2'),('SGLANG-QUANT','marlin')],placement='11')
add('Q26','vLLM 官方明确 GGUF 当前 highly experimental and under-optimized，并建议基座 tokenizer；格式可读不代表与 llama.cpp 覆盖等价。',[('VLLM-GGUF','highly experimental and under-optimized'),('VLLM-GGUF','tokenizer from base')],placement='11')
add('Q27','AutoAWQ 项目已声明 deprecated，最后测试 Torch2.6.0/Transformers4.51.3；不能把它的停维护当作 AWQ 方法不存在。',[('AUTOAWQ-README','officially deprecated'),('AUTOAWQ-README','Torch 2.6.0')],placement='11')
add('Q28','ModelOpt 的 int4_awq 与 nvfp4_awq_lite 共用 AWQ-lite 校准思路但数值表示不同，说明方法和编码是正交轴。',[('MO-AWQ-PRESET','awq_lite'),('MO-NV-AWQ-PRESET','NVFP4 W4A4')],placement='7,27')
add('Q29','PTQ/QAT/QAD 是不同恢复流程；ModelOpt QAT更新量化模型，QAD另用teacher；fake-quant准确度不是exported-kernel准确度证明。',[('MO-HF-QAT','Train with distillation'),('MO-HF-QAT','Native Fake-Quantized Evaluation')],placement='14')
add('Q30','GPT-OSS checkpoint 配置为 MXFP4 且排除若干层，官方描述量化 MoE weights；不能把总参数全乘0.5。',[('GPTOSS','MoE weights'),('GPTOSS-CONFIG','mxfp4')],limits='模型卡的单卡容量描述不是本研究的实测 fit。',placement='7,27')
add('Q31','NVFP4 更小block有更多scale，不能按数据4bit宣称与MXFP4一样大；scale swizzle也会扩大物理分配。',[('VLLM-NV-UTIL','M_padded = round_up(M, 128)'),('VLLM-NV-UTIL','K_padded = round_up(K, 4)')],kind='DERIVED',stage='ANALYTICAL',limits='完整示例见 calculations.json。')
add('Q32','量化内存必须分 disk/checkpoint、常驻HBM、加载峰值和workspace；密集weight-only roofline不等于实测带宽。',[('VLLM-NV-CUTLASS','pad_nvfp4_weight_for_cutlass'),('VLLM-NV-EMU','run_nvfp4_emulations')],kind='DERIVED',stage='ANALYTICAL',placement='7,8,15')
add('Q33','新示例以98% MXFP4+2% BF16 得39.24375GB权重；KV保持BF16时storage ceiling只从17到21，不是goodput。',[('GGML-BLOCKS','block_mxfp4')],scope='New illustrative 70B scenario sensitivity only; exact inputs in calculations.json',kind='DERIVED',provenance='ILLUSTRATIVE',stage='ILLUSTRATIVE',placement='7')
add('Q34','量化权重不自动量化KV；ModelOpt与vLLM均有单独KV配置/scale校准，long-context需另验。',[('MO-HF-PTQ','--kv_cache_qformat none'),('VLLM-FP8KV','curated calibration dataset')],placement='7,11,14')
add('Q35','模型类型/层的支持必须逐项看：ModelOpt部分条目export-only，VLM默认仅语言分支；一个model-family勾选不是全模型/全部模态认证。',[('MO-HF-PTQ','export to HF format only'),('MO-HF-PTQ','vision encoder is kept in high precision')],placement='5,11,14')
add('Q36','GPT-OSS MXFP4→NVFP4 的官方cast所称bit-exact受scale指数跨度≤17等条件限制，超范围有fallback，不能推论所有转换无损。',[('MO-HF-PTQ','k_max - k_j ≤ 17'),('MO-HF-PTQ','out-of-range blocks')],limits='未执行转换和逐值比对。',placement='27')
add('Q37','本任务没有同模型同硬件同上下文的推理/代码/工具/多模态量化质量与SLO实测，因此不选赢家。',[],kind='UNRESOLVED',provenance='ILLUSTRATIVE',stage='UNMEASURED',scope='Research boundary, not a model-quality claim',placement='14,18')
add('Q38','AWQ代码MIT、GPTQ代码Apache2、llama.cpp代码MIT、TE/ModelOpt/vLLM代码Apache2；这些不替代checkpoint或依赖许可。',[('AWQ-LICENSE','MIT License'),('GPTQ-LICENSE','Apache License'),('LLAMA-LICENSE','MIT License'),('TE-LICENSE','Apache License'),('MO-LICENSE','Apache License'),('VLLM-LICENSE','Apache License')],placement='5,11')
obj={'schema_version':'1.0','created_utc':datetime.now(timezone.utc).isoformat(),'research_root':str(R),
 'manuscript_evidence_cutoff':'2026-08-30','scope':'Independent unapplied research; no publication-readiness claim',
 'taxonomy_source':'render/latex/backmatter/sources.tex:7-55',
 'reproduction_status':'independent arithmetic executed; no inference/conversion/hardware tests',
 'sources':list(sources.values()),'retrieval_failures':[x for x in raw if x['status']!='fetched'],
 'claims':claims,'calculation_artifact':'calculations.json'}
(R/'claims.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
lines=['# Primary-source index','', 'All URLs below were fetched this run. Retrieval dates and SHA-256 are in claims.json. An accessible URL does not establish historical engine support.','']
for sid,s in sources.items(): lines +=[f"## {sid}",f"- URL: {s['url']}",f"- Source date/revision: {s['publication_or_commit_date']}",f"- Local text: {s['text_path']}",f"- SHA-256 (raw): {s['sha256']}",'']
(R/'source-index.md').write_text('\n'.join(lines))
print(json.dumps({'claims':len(claims),'successful_unique_source_ids':len(sources),'failed_attempts':len(obj['retrieval_failures']),'all_raw_hashes':'verified','all_claim_anchors':'verified'}))
