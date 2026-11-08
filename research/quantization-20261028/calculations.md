# Independent byte arithmetic

Derived only. No model or GPU benchmark was run.

| Encoding | Values/block | Bytes/block | B/value | Effective bits/value |
|---|---:|---:|---:|---:|
| Q4_0 | 32 | 18 | 0.5625 | 4.5 |
| Q4_1 | 32 | 20 | 0.625 | 5.0 |
| Q8_0 | 32 | 34 | 1.0625 | 8.5 |
| Q2_K | 256 | 84 | 0.328125 | 2.625 |
| Q3_K | 256 | 110 | 0.4296875 | 3.4375 |
| Q4_K | 256 | 144 | 0.5625 | 4.5 |
| Q5_K | 256 | 176 | 0.6875 | 5.5 |
| Q6_K | 256 | 210 | 0.8203125 | 6.5625 |
| IQ2_XXS | 256 | 66 | 0.2578125 | 2.0625 |
| IQ2_XS | 256 | 74 | 0.2890625 | 2.3125 |
| IQ2_S | 256 | 82 | 0.3203125 | 2.5625 |
| IQ3_XXS | 256 | 98 | 0.3828125 | 3.0625 |
| IQ3_S | 256 | 110 | 0.4296875 | 3.4375 |
| IQ1_S | 256 | 50 | 0.1953125 | 1.5625 |
| IQ1_M | 256 | 56 | 0.21875 | 1.75 |
| IQ4_NL | 32 | 18 | 0.5625 | 4.5 |
| IQ4_XS | 256 | 136 | 0.53125 | 4.25 |
| MXFP4 | 32 | 17 | 0.53125 | 4.25 |
| GGML_NVFP4 | 64 | 36 | 0.5625 | 4.5 |

## Matrix, padding, resource ledger and intensity

```json
{
  "status": "DERIVED; no hardware measurements",
  "matrix": {
    "shape": [
      4096,
      4096
    ],
    "parameter_count": 16777216,
    "group_size": 128,
    "bf16_bytes": 33554432,
    "int4_packed_zp_fp16_scale_bytes": 8716288,
    "int4_fp16_scaled_zero_and_scale_bytes": 8912896,
    "symmetric_int4_fp16_scale_bytes": 8650752,
    "mxfp4_bytes": 8912896,
    "nvfp4_1d_weight_bytes_one_global_scale": 9437188,
    "nvfp4_2d_unique_scale_information_bytes": 8454148,
    "fp8_per_tensor_one_fp32_scale_bytes": 16777220,
    "int8_per_output_channel_fp32_scale_bytes": 16793600,
    "gptq_optional_int32_g_idx_bytes": 16384,
    "bf16_bytes_effective_bpp": 16.0,
    "int4_packed_zp_fp16_scale_bytes_effective_bpp": 4.15625,
    "int4_fp16_scaled_zero_and_scale_bytes_effective_bpp": 4.25,
    "symmetric_int4_fp16_scale_bytes_effective_bpp": 4.125,
    "mxfp4_bytes_effective_bpp": 4.25,
    "nvfp4_1d_weight_bytes_one_global_scale_effective_bpp": 4.500001907348633,
    "nvfp4_2d_unique_scale_information_bytes_effective_bpp": 4.031251907348633,
    "fp8_per_tensor_one_fp32_scale_bytes_effective_bpp": 8.000001907348633,
    "int8_per_output_channel_fp32_scale_bytes_effective_bpp": 8.0078125,
    "gptq_optional_int32_g_idx_bytes_effective_bpp": 0.0078125
  },
  "awq_padding_example": {
    "N": 4096,
    "K": 4224,
    "group": 128,
    "padded_group_slots": 40,
    "qweight_bytes": 8650752,
    "scales_bytes": 327680,
    "scaled_zeros_bytes": 327680,
    "total_bytes": 9306112,
    "effective_bpp": 4.303030303030303
  },
  "scale_swizzle_padding_example": {
    "original_scale_shape": [
      129,
      257
    ],
    "padded_scale_shape": [
      256,
      260
    ],
    "logical_bytes": 33153,
    "allocated_bytes": 66560,
    "extra_bytes": 33407
  },
  "gguf_alignment_example": {
    "alignment": 32,
    "tensor_payload_sizes": [
      18,
      144,
      17
    ],
    "offsets": [
      0,
      32,
      192
    ],
    "gaps_before_tensors": [
      0,
      14,
      16
    ],
    "payload_bytes": 179,
    "data_span_without_final_padding": 209
  },
  "resource_ledger": {
    "assumptions": {
      "parameters": 70000000000,
      "mxfp4_fraction": 0.98,
      "bf16_fraction": 0.02,
      "host_bytes": 640000000000,
      "reserve_bytes": 64000000000,
      "layers": 80,
      "kv_width_full_mha": 8192,
      "tokens_per_sequence": 9500,
      "kv_bytes_per_element": 2
    },
    "bf16_weight_bytes": 140000000000,
    "mixed_weight_bytes": 39243750000,
    "mixed_weight_GB": 39.24375,
    "mixed_weight_GiB": 36.548590287566185,
    "mixed_effective_bits_per_parameter": 4.485,
    "kv_raw_bytes_per_token": 2621440,
    "kv_raw_bytes_per_sequence": 24903680000,
    "bf16_weight_raw_KV_budget_bytes": 436000000000,
    "mixed_weight_raw_KV_budget_bytes": 536756250000,
    "bf16_weight_fractional_storage_ceiling": 17.50745271381579,
    "mixed_weight_fractional_storage_ceiling": 21.55329051770662,
    "bf16_weight_integer_storage_ceiling": 17,
    "mixed_weight_integer_storage_ceiling": 21,
    "excluded": [
      "tensor padding",
      "global scales",
      "KV scales/layout",
      "load/repack peak",
      "per-rank imbalance",
      "new workspace requirements",
      "quality",
      "SLO-goodput"
    ]
  },
  "ideal_weight_roofline": {
    "flop_per_output_token": 140000000000,
    "bf16_weight_only_intensity_batch1": 1.0,
    "mixed_weight_only_intensity_batch1": 3.5674470457079153,
    "scope": "weight-stream-only useful FLOPs/byte; KV, activations, scales traffic and conversion not modeled"
  },
  "abi_checks": {
    "Q4_K": 144,
    "MXFP4": 17,
    "GGML_NVFP4": 36
  }
}
```
