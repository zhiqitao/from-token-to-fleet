#!/usr/bin/env python3
"""Independent exact byte accounting; not an inference benchmark.

Only stdlib. Writes calculations.json and calculations.md beside this script.
Block field counts are transcribed from the pinned GGML-BLOCKS snapshot.
No result here proves GPU residency, quality, latency, or deployable capacity.
"""
from fractions import Fraction as F
from pathlib import Path
import ctypes as C
import json

ROOT = Path(__file__).resolve().parent

def align(n, multiple):
    return ((n + multiple - 1) // multiple) * multiple

def fraction(value):
    return {'exact': str(value), 'decimal': float(value)}

# Field bytes, not nominal label bits. Half is 2 B, uint16 2 B.
BLOCKS = [
    ('Q4_0', 32, [2, 16]), ('Q4_1', 32, [2, 2, 16]),
    ('Q8_0', 32, [2, 32]),
    ('Q2_K', 256, [16, 64, 2, 2]),
    ('Q3_K', 256, [32, 64, 12, 2]),
    ('Q4_K', 256, [2, 2, 12, 128]),
    ('Q5_K', 256, [2, 2, 12, 32, 128]),
    ('Q6_K', 256, [128, 64, 16, 2]),
    ('IQ2_XXS', 256, [2, 64]), ('IQ2_XS', 256, [2, 64, 8]),
    ('IQ2_S', 256, [2, 64, 8, 8]), ('IQ3_XXS', 256, [2, 96]),
    ('IQ3_S', 256, [2, 64, 8, 32, 4]),
    ('IQ1_S', 256, [2, 32, 16]), ('IQ1_M', 256, [32, 16, 8]),
    ('IQ4_NL', 32, [2, 16]), ('IQ4_XS', 256, [2, 2, 4, 128]),
    ('MXFP4', 32, [1, 16]), ('GGML_NVFP4', 64, [4, 32]),
]
rows=[]
for name, count, fields in BLOCKS:
    size=sum(fields)
    rows.append({'encoding':name,'values_per_block':count,'field_bytes':fields,
                 'bytes_per_block':size,'bytes_per_value':fraction(F(size,count)),
                 'effective_bits_per_value':fraction(F(8*size,count))})
lookup={r['encoding']:r for r in rows}
# Independently instantiate selected C-compatible field layouts, checking ABI padding.
class Q4K(C.Structure):
    _fields_=[('d',C.c_uint16),('dmin',C.c_uint16),('scales',C.c_uint8*12),('qs',C.c_uint8*128)]
class MX4(C.Structure):
    _fields_=[('e',C.c_uint8),('qs',C.c_uint8*16)]
class NV4(C.Structure):
    _fields_=[('d',C.c_uint8*4),('qs',C.c_uint8*32)]
assert C.sizeof(Q4K)==144 and C.sizeof(MX4)==17 and C.sizeof(NV4)==36
assert lookup['Q6_K']['bytes_per_block']==210
assert lookup['IQ4_XS']['bytes_per_block']==136

# Representative 4096 x 4096 matrix; all group dimensions divide exactly.
N=K=4096
P=N*K
g=128
G=N*(K//g)
packed=P//2
matrix={
    'shape':[N,K], 'parameter_count':P, 'group_size':g,
    'bf16_bytes':P*2,
    'int4_packed_zp_fp16_scale_bytes':packed+G*2+G//2,
    'int4_fp16_scaled_zero_and_scale_bytes':packed+G*2+G*2,
    'symmetric_int4_fp16_scale_bytes':packed+G*2,
    'mxfp4_bytes':P//2+P//32,
    'nvfp4_1d_weight_bytes_one_global_scale':P//2+P//16+4,
    'nvfp4_2d_unique_scale_information_bytes':P//2+(N//16)*(K//16)+4,
    'fp8_per_tensor_one_fp32_scale_bytes':P+4,
    'int8_per_output_channel_fp32_scale_bytes':P+N*4,
    'gptq_optional_int32_g_idx_bytes':K*4,
}
for key,value in list(matrix.items()):
    if key.endswith('_bytes') or key.endswith('_scale'):
        matrix[key+'_effective_bpp']=float(F(value*8,P))
assert matrix['mxfp4_bytes']==8912896
assert matrix['nvfp4_1d_weight_bytes_one_global_scale']==9437188
assert F(matrix['int4_packed_zp_fp16_scale_bytes'],P)==F(133,256)
assert F(matrix['int4_fp16_scaled_zero_and_scale_bytes'],P)==F(17,32)
# The 2D value counts unique information only; physical scale replication,
# row/column copies, global inverse/amax buffers are deliberately excluded.

# AWQ reference qmodule exact buffer formula, FP16, group 128, K multiple 128.
def tinychat_weight_bytes(n,k,group=128):
    assert k%group==0 and n%8==0 and k%64==0
    pack=8
    mult=1 if group>=128 else 2 if group==64 else 4 if group==32 else None
    if mult is None: raise ValueError('unsupported group')
    zero_width=(((k//group+pack-1)//pack+mult-1)//mult)*mult
    slots=zero_width*pack
    return {'N':n,'K':k,'group':group,'padded_group_slots':slots,
            'qweight_bytes':n*k//2,'scales_bytes':slots*n*2,
            'scaled_zeros_bytes':slots*n*2,
            'total_bytes':n*k//2+slots*n*4,
            'effective_bpp':float(F((n*k//2+slots*n*4)*8,n*k))}
awq_padding=tinychat_weight_bytes(4096,4224)
assert awq_padding['padded_group_slots']==40
# Actual vLLM scale-swizzle allocation: pad M to 128 and K_scale to 4.
scale_padding: dict[str, object] = {'original_scale_shape':[129,257], 'padded_scale_shape':[align(129,128),align(257,4)]}
scale_padding['logical_bytes']=129*257
scale_padding['allocated_bytes']=align(129,128)*align(257,4)
scale_padding['extra_bytes']=align(129,128)*align(257,4)-129*257
# GGUF inter-tensor padding, excluding header and metadata lengths.
sizes=[18,144,17]
cursor=0; offsets=[]; pads=[]
for size in sizes:
    start=align(cursor,32); pads.append(start-cursor); offsets.append(start); cursor=start+size
padding={'alignment':32,'tensor_payload_sizes':sizes,'offsets':offsets,
         'gaps_before_tensors':pads,'payload_bytes':sum(sizes),'data_span_without_final_padding':cursor}
assert offsets==[0,32,192]

# Explicitly NEW illustrative variant, not replacement of canonical arithmetic.
params=70_000_000_000
low=F(98,100)*params
high=params-low
weight=low*F(17,32)+high*2
bf16_weight=params*2
kv_token=2*80*8192*2
kv=kv_token*9500
reserve=64_000_000_000
host=640_000_000_000
base_budget=host-bf16_weight-reserve
new_budget=host-weight-reserve
ledger={
 'assumptions':{'parameters':params,'mxfp4_fraction':0.98,'bf16_fraction':0.02,
                'host_bytes':host,'reserve_bytes':reserve,'layers':80,'kv_width_full_mha':8192,
                'tokens_per_sequence':9500,'kv_bytes_per_element':2},
 'bf16_weight_bytes':bf16_weight, 'mixed_weight_bytes':int(weight),
 'mixed_weight_GB':float(weight/10**9),'mixed_weight_GiB':float(weight/2**30),
 'mixed_effective_bits_per_parameter':float(weight*8/params),
 'kv_raw_bytes_per_token':kv_token,'kv_raw_bytes_per_sequence':kv,
 'bf16_weight_raw_KV_budget_bytes':base_budget,'mixed_weight_raw_KV_budget_bytes':int(new_budget),
 'bf16_weight_fractional_storage_ceiling':float(F(base_budget,kv)),
 'mixed_weight_fractional_storage_ceiling':float(new_budget/kv),
 'bf16_weight_integer_storage_ceiling':base_budget//kv,
 'mixed_weight_integer_storage_ceiling':int(new_budget//kv),
 'excluded':['tensor padding','global scales','KV scales/layout','load/repack peak',
             'per-rank imbalance','new workspace requirements','quality','SLO-goodput'],
}
assert weight==F(98*params*17,100*32)+F(2*params*2,100)
assert ledger['bf16_weight_integer_storage_ceiling']==17
assert ledger['mixed_weight_integer_storage_ceiling']==21
# Ideal dense weight-only decode count. Not hardware work, not runtime.
roofline={ 'flop_per_output_token':2*params,
 'bf16_weight_only_intensity_batch1':float(F(2*params,bf16_weight)),
 'mixed_weight_only_intensity_batch1':float(F(2*params,weight)),
 'scope':'weight-stream-only useful FLOPs/byte; KV, activations, scales traffic and conversion not modeled'}
result={'status':'DERIVED; no hardware measurements','blocks':rows,'matrix':matrix,
        'awq_padding_example':awq_padding,'scale_swizzle_padding_example':scale_padding,
        'gguf_alignment_example':padding,'resource_ledger':ledger,'ideal_weight_roofline':roofline,
        'abi_checks':{'Q4_K':C.sizeof(Q4K),'MXFP4':C.sizeof(MX4),'GGML_NVFP4':C.sizeof(NV4)}}
(ROOT/'calculations.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
md=['# Independent byte arithmetic','', 'Derived only. No model or GPU benchmark was run.','',
    '| Encoding | Values/block | Bytes/block | B/value | Effective bits/value |',
    '|---|---:|---:|---:|---:|']
for r in rows: md.append(f"| {r['encoding']} | {r['values_per_block']} | {r['bytes_per_block']} | {r['bytes_per_value']['decimal']} | {r['effective_bits_per_value']['decimal']} |")
md+=['','## Matrix, padding, resource ledger and intensity','', '```json',json.dumps({k:v for k,v in result.items() if k!='blocks'},indent=2,ensure_ascii=False),'```','']
(ROOT/'calculations.md').write_text('\n'.join(md))
print(json.dumps({'block_count':len(rows),'matrix':matrix,'resource_ledger':ledger,'roofline':roofline,
                  'padding':padding,'awq_padding':awq_padding,'scale_padding':scale_padding,'assertions':'passed'},indent=2))
