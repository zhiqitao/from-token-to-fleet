# Copyright 2025 Antgroup and The HuggingFace Inc. team. All rights reserved.
#
# This code is based on EleutherAI's GPT-NeoX library and the GPT-NeoX
# and OPT implementations in this library. It has been modified from its
# original forms to accommodate minor architectural differences compared
# to GPT-NeoX and OPT used by the Meta AI team that trained the model.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""PyTorch LLaDA2MoE model."""

import math
from typing import List, Callable, Optional, Tuple, Union

import torch
import torch.nn.functional as F
from torch import nn
from torch.nn import CrossEntropyLoss

from transformers.activations import ACT2FN
from transformers.cache_utils import Cache, DynamicCache
from transformers.masking_utils import create_bidirectional_mask
from transformers.modeling_outputs import (
    MoeModelOutputWithPast,
    MoeCausalLMOutputWithPast,
)
from transformers.modeling_rope_utils import ROPE_INIT_FUNCTIONS, dynamic_rope_update
from transformers.modeling_utils import ALL_ATTENTION_FUNCTIONS, PreTrainedModel
from transformers.processing_utils import Unpack
from transformers.pytorch_utils import (
    ALL_LAYERNORM_LAYERS,
)
from transformers.utils import (
    TransformersKwargs,
    add_start_docstrings,
    add_start_docstrings_to_model_forward,
    logging,
    replace_return_docstrings,
)
from .configuration_llada2_moe import LLaDA2MoeConfig
from transformers.generation.utils import GenerationMixin


logger = logging.get_logger(__name__)

_CONFIG_FOR_DOC = "LLaDA2MoeConfig"


def _get_unpad_data(attention_mask):
    seqlens_in_batch = attention_mask.sum(dim=-1, dtype=torch.int32)
    indices = torch.nonzero(attention_mask.flatten(), as_tuple=False).flatten()
    max_seqlen_in_batch = seqlens_in_batch.max().item()
    cu_seqlens = F.pad(
        torch.cumsum(seqlens_in_batch, dim=0, dtype=torch.torch.int32), (1, 0)
    )
    return (
        indices,
        cu_seqlens,
        max_seqlen_in_batch,
    )


class LLaDA2MoeRMSNorm(nn.Module):
    def __init__(self, hidden_size, eps=1e-6):
        """
        LLaDA2MoeRMSNorm is equivalent to T5LayerNorm
        """
        super().__init__()
        self.weight = nn.Parameter(torch.ones(hidden_size))
        self.variance_epsilon = eps

    def forward(self, hidden_states):
        input_dtype = hidden_states.dtype
        hidden_states = hidden_states.to(torch.float32)
        variance = hidden_states.pow(2).mean(-1, keepdim=True)
        hidden_states = hidden_states * torch.rsqrt(variance + self.variance_epsilon)
        return self.weight * hidden_states.to(input_dtype)


ALL_LAYERNORM_LAYERS.append(LLaDA2MoeRMSNorm)


class LLaDA2MoeRotaryEmbedding(nn.Module):
    inv_freq: torch.Tensor  # fix linting for register_buffer

    def __init__(self, config: LLaDA2MoeConfig, device=None):
        super().__init__()
        self.max_seq_len_cached = config.max_position_embeddings
        self.original_max_seq_len = config.max_position_embeddings

        self.config = config
        
        self.rope_type = self.config.rope_parameters["rope_type"]
        rope_init_fn: Callable = self.compute_default_rope_parameters
        if self.rope_type != "default":
            rope_init_fn = ROPE_INIT_FUNCTIONS[self.rope_type]
        inv_freq, self.attention_scaling = rope_init_fn(self.config, device)

        self.register_buffer("inv_freq", inv_freq, persistent=False)
        self.register_buffer("original_inv_freq", inv_freq.clone(), persistent=False)
    
    @staticmethod
    def compute_default_rope_parameters(
        config: LLaDA2MoeConfig = None,
        device=None,
        seq_len: int = None,
    ):
        base = config.rope_parameters["rope_theta"]
        partial_rotary_factor = config.rope_parameters.get("partial_rotary_factor", 1.0)
        head_dim = getattr(config, "head_dim", None) or config.hidden_size // config.num_attention_heads
        dim = int(head_dim * partial_rotary_factor)

        attention_factor = 1.0  # Unused in this type of RoPE

        inv_freq = 1.0 / (
            base ** (torch.arange(0, dim, 2, dtype=torch.int64).to(device=device, dtype=torch.float) / dim)
        )
        return inv_freq, attention_factor

    @torch.no_grad()
    @dynamic_rope_update  # power user: used with advanced RoPE types (e.g. dynamic rope)
    def forward(self, x, position_ids):
        inv_freq_expanded = (
            self.inv_freq[None, :, None]
            .float()
            .expand(position_ids.shape[0], -1, 1)
            .to(x.device)
        )
        position_ids_expanded = position_ids[:, None, :].float()

        device_type = (
            x.device.type
            if isinstance(x.device.type, str) and x.device.type != "mps"
            else "cpu"
        )
        with torch.autocast(device_type=device_type, enabled=False):  # Force float32
            freqs = (
                inv_freq_expanded.float() @ position_ids_expanded.float()
            ).transpose(1, 2)
            emb = torch.cat((freqs, freqs), dim=-1)
            cos = emb.cos() * self.attention_scaling
            sin = emb.sin() * self.attention_scaling

        return cos.to(dtype=x.dtype), sin.to(dtype=x.dtype)


# Copied from transformers.models.llama.modeling_llama.rotate_half
def rotate_half(x):
    """Rotates half the hidden dims of the input."""
    x1 = x[..., : x.shape[-1] // 2]
    x2 = x[..., x.shape[-1] // 2 :]
    return torch.cat((-x2, x1), dim=-1)


# Copied from transformers.models.llama.modeling_llama.apply_rotary_pos_emb
def apply_rotary_pos_emb(q, k, cos, sin, position_ids=None, unsqueeze_dim=1):
    """Applies Rotary Position Embedding to the query and key tensors.

    Args:
        q (`torch.Tensor`): The query tensor.
        k (`torch.Tensor`): The key tensor.
        cos (`torch.Tensor`): The cosine part of the rotary embedding.
        sin (`torch.Tensor`): The sine part of the rotary embedding.
        position_ids (`torch.Tensor`):
            The position indices of the tokens corresponding to the query and key tensors. For example, this can be
            used to pass offsetted position ids when working with a KV-cache.
        unsqueeze_dim (`int`, *optional*, defaults to 1):
            The 'unsqueeze_dim' argument specifies the dimension along which to unsqueeze cos[position_ids] and
            sin[position_ids] so that they can be properly broadcasted to the dimensions of q and k. For example, note
            that cos[position_ids] and sin[position_ids] have the shape [batch_size, seq_len, head_dim]. Then, if q and
            k have the shape [batch_size, heads, seq_len, head_dim], then setting unsqueeze_dim=1 makes
            cos[position_ids] and sin[position_ids] broadcastable to the shapes of q and k. Similarly, if q and k have
            the shape [batch_size, seq_len, heads, head_dim], then set unsqueeze_dim=2.
    Returns:
        `tuple(torch.Tensor)` comprising the query and key tensors rotated using the Rotary Position Embedding.
    """
    cos = cos.unsqueeze(unsqueeze_dim)
    sin = sin.unsqueeze(unsqueeze_dim)

    # Keep half or full tensor for later concatenation
    rotary_dim = cos.shape[-1]
    q_rot, q_pass = q[..., :rotary_dim], q[..., rotary_dim:]
    k_rot, k_pass = k[..., :rotary_dim], k[..., rotary_dim:]

    # Apply rotary embeddings on the first half or full tensor
    q_embed = (q_rot * cos) + (rotate_half(q_rot) * sin)
    k_embed = (k_rot * cos) + (rotate_half(k_rot) * sin)

    # Concatenate back to full shape
    q_embed = torch.cat([q_embed, q_pass], dim=-1)
    k_embed = torch.cat([k_embed, k_pass], dim=-1)
    return q_embed, k_embed


class LLaDA2MoeMLP(nn.Module):
    def __init__(self, config: LLaDA2MoeConfig, intermediate_size: int):
        super().__init__()
        self.config = config
        self.hidden_size = config.hidden_size
        self.intermediate_size = intermediate_size

        self.gate_proj = nn.Linear(self.hidden_size, self.intermediate_size, bias=False)
        self.up_proj = nn.Linear(self.hidden_size, self.intermediate_size, bias=False)
        self.down_proj = nn.Linear(self.intermediate_size, self.hidden_size, bias=False)
        self.act_fn = ACT2FN[config.hidden_act]

    def forward(self, x):
        return self.down_proj(self.act_fn(self.gate_proj(x)) * self.up_proj(x))


class LLaDA2MoeGate(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.top_k = config.num_experts_per_tok
        self.num_experts = config.num_experts

        # Block routing
        self.block_size = config.block_size
        self.expert_capacity = config.expert_capacity

        # topk selection algorithm
        self.gating_dim = config.hidden_size
        self.weight = nn.Parameter(torch.empty((self.num_experts, self.gating_dim)))
        self.routed_scaling_factor = config.routed_scaling_factor

        self.register_buffer("expert_bias", torch.zeros(self.num_experts))
        self.reset_parameters()

    def reset_parameters(self) -> None:
        import torch.nn.init as init

        init.kaiming_uniform_(self.weight, a=math.sqrt(5))

    def block_routing(self, scores_for_routing: torch.Tensor):
        """Block-level top-k routing: first select expert_capacity experts per block,
        then do per-token top-k within the allowed set."""
        num_tokens = scores_for_routing.shape[0]
        assert num_tokens % self.block_size == 0

        num_blocks = num_tokens // self.block_size
        # Reshape to (num_blocks, block_size, num_experts)
        block_routing_scores = scores_for_routing.view(num_blocks, self.block_size, self.num_experts)

        # Phase 1: compute block-level expert scores (max over tokens in each block)
        block_expert_scores = block_routing_scores.max(dim=1).values  # (num_blocks, num_experts)

        # Select top expert_capacity experts per block
        _, block_routing_indices = torch.topk(
            block_expert_scores, k=self.expert_capacity, dim=-1
        )  # (num_blocks, expert_capacity)

        # Build allowed mask: (num_blocks, num_experts)
        allowed_mask = torch.zeros(
            num_blocks, self.num_experts, dtype=torch.bool, device=scores_for_routing.device
        )
        allowed_mask.scatter_(1, block_routing_indices, True)

        # Expand mask to per-token level: (num_tokens, num_experts)
        allowed_mask = allowed_mask.unsqueeze(1).expand(-1, self.block_size, -1).reshape(num_tokens, self.num_experts)

        # Phase 2: per-token top-k within allowed experts
        masked_scores = scores_for_routing.masked_fill(~allowed_mask, -torch.inf)
        _, topk_idx = torch.topk(masked_scores, k=self.top_k, dim=-1)

        return topk_idx

    def forward(self, hidden_states):
        # compute gating score
        hidden_states = hidden_states.view(-1, hidden_states.shape[-1])
        logits = F.linear(
            hidden_states.type(torch.float32), self.weight.type(torch.float32)
        )

        scores = torch.sigmoid(logits.float()).type_as(logits)

        scores_for_routing = scores + self.expert_bias

        topk_idx = self.block_routing(scores_for_routing)

        scores = torch.gather(scores, dim=1, index=topk_idx).type_as(logits)
        topk_weight = (
            scores / (scores.sum(dim=-1, keepdim=True) + 1e-20)
            if self.top_k > 1
            else scores
        )
        topk_weight = topk_weight * self.routed_scaling_factor

        return topk_idx, topk_weight, logits


class LLaDA2MoeSparseMoeBlock(nn.Module):
    """
    A mixed expert module containing shared experts.
    """

    def __init__(self, config: LLaDA2MoeConfig):
        super().__init__()
        self.config = config
        self.num_experts_per_tok = config.num_experts_per_tok
        self._setup_experts()
        self.gate = LLaDA2MoeGate(config)
        if config.num_shared_experts is not None:
            self.shared_experts = LLaDA2MoeMLP(
                config=config,
                intermediate_size=config.moe_intermediate_size
                * config.num_shared_experts,
            )

    def _setup_experts(self):
        self.experts = nn.ModuleList(
            [
                LLaDA2MoeMLP(
                    config=self.config,
                    intermediate_size=self.config.moe_intermediate_size,
                )
                for _ in range(self.config.num_experts)
            ]
        )

    def forward(self, hidden_states):
        identity = hidden_states
        bsz, seq_len, h = hidden_states.shape
        topk_idx, topk_weight, router_logits = self.gate(hidden_states)
        hidden_states = hidden_states.view(-1, hidden_states.shape[-1])
        flat_topk_idx = topk_idx.view(-1)
        if self.training:
            hidden_states = hidden_states.repeat_interleave(
                self.num_experts_per_tok, dim=0
            )
            y = torch.empty_like(hidden_states)
            for i, expert in enumerate(self.experts):
                y[flat_topk_idx == i] = expert(hidden_states[flat_topk_idx == i])
            y = (y.view(*topk_weight.shape, -1) * topk_weight.unsqueeze(-1)).sum(dim=1)
            y = y.to(hidden_states.dtype).view(bsz, seq_len, h)
        else:
            y = self.moe_infer(hidden_states, topk_idx, topk_weight).view(
                bsz, seq_len, h
            )
        if self.config.num_shared_experts is not None:
            y = y + self.shared_experts(identity)
        return y, (
            router_logits.view(bsz, seq_len, -1),
            topk_idx.view(bsz, seq_len, -1),
        )

    @torch.no_grad()
    def moe_infer(self, x, topk_ids, topk_weight):
        cnts = topk_ids.new_zeros((topk_ids.shape[0], len(self.experts)))
        cnts.scatter_(1, topk_ids, 1)
        tokens_per_expert = cnts.sum(dim=0)
        idxs = topk_ids.view(-1).argsort()
        sorted_tokens = x[idxs // topk_ids.shape[1]]
        tokens_per_expert = tokens_per_expert.cpu().numpy()
        outputs = []
        start_idx = 0
        for i, num_tokens_tensor in enumerate(tokens_per_expert):
            num_tokens = num_tokens_tensor.item()
            if num_tokens == 0:
                continue
            end_idx = start_idx + num_tokens
            expert = self.experts[i]
            tokens_for_this_expert = sorted_tokens[start_idx:end_idx]
            expert_out = expert(tokens_for_this_expert)
            outputs.append(expert_out.to(x.device))
            start_idx = end_idx

        outs = torch.cat(outputs, dim=0) if len(outputs) else sorted_tokens.new_empty(0)
        new_x = torch.empty_like(outs)
        new_x[idxs] = outs
        final_out = (
            new_x.view(*topk_ids.shape, -1)
            .type(topk_weight.dtype)
            .mul_(topk_weight.unsqueeze(dim=-1))
            .sum(dim=1)
            .type(new_x.dtype)
        )
        return final_out


# Copied from transformers.models.llama.modeling_llama.repeat_kv
def repeat_kv(hidden_states: torch.Tensor, n_rep: int) -> torch.Tensor:
    """
    This is the equivalent of torch.repeat_interleave(x, dim=1, repeats=n_rep). The hidden states go from (batch,
    num_key_value_heads, seqlen, head_dim) to (batch, num_attention_heads, seqlen, head_dim)
    """
    batch, num_key_value_heads, slen, head_dim = hidden_states.shape
    if n_rep == 1:
        return hidden_states
    hidden_states = hidden_states[:, :, None, :, :].expand(
        batch, num_key_value_heads, n_rep, slen, head_dim
    )
    return hidden_states.reshape(batch, num_key_value_heads * n_rep, slen, head_dim)


def eager_attention_forward(
    module: nn.Module,
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    attention_mask: Optional[torch.Tensor],
    scaling: float,
    dropout: float = 0.0,
    **kwargs: Unpack[TransformersKwargs],
):
    key_states = repeat_kv(key, module.num_key_value_groups)
    value_states = repeat_kv(value, module.num_key_value_groups)

    attn_weights = torch.matmul(query, key_states.transpose(2, 3)) * scaling
    if attention_mask is not None:
        attn_weights = attn_weights + attention_mask[:, :, :, : key_states.shape[-2]]

    # upcast attention to fp32
    attn_weights = nn.functional.softmax(attn_weights, dim=-1, dtype=torch.float32).to(
        query.dtype
    )
    attn_weights = nn.functional.dropout(
        attn_weights, p=dropout, training=module.training
    )
    attn_output = torch.matmul(attn_weights, value_states)
    attn_output = attn_output.transpose(1, 2).contiguous()

    return attn_output, attn_weights


# Copied from transformers.models.llama.modeling_llama.LlamaAttention with Llama->LLaDA2Moe
class LLaDA2MoeAttention(nn.Module):
    """Multi-headed attention from 'Attention Is All You Need' paper"""

    def __init__(self, config: LLaDA2MoeConfig, layer_idx: Optional[int] = None):
        super().__init__()
        self.config = config
        self.layer_idx = layer_idx
        if layer_idx is None:
            logger.warning_once(
                f"Instantiating {self.__class__.__name__} without passing `layer_idx` is not recommended and will "
                "to errors during the forward call, if caching is used. Please make sure to provide a `layer_idx` "
                "when creating this class."
            )
        self.attention_dropout = config.attention_dropout
        self.hidden_size = config.hidden_size
        self.num_heads = config.num_attention_heads
        self.head_dim = config.head_dim or self.hidden_size // self.num_heads
        partial_rotary_factor = (
            config.partial_rotary_factor
            if hasattr(config, "partial_rotary_factor")
            else 1.0
        )
        self.rope_dim = int(self.head_dim * partial_rotary_factor)
        self.num_key_value_heads = config.num_key_value_heads
        self.num_key_value_groups = self.num_heads // self.num_key_value_heads
        self.max_position_embeddings = config.max_position_embeddings
        self.rope_theta = config.rope_theta
        self.scaling = self.head_dim**-0.5
        self.is_causal = False

        self.query_key_value = nn.Linear(
            self.hidden_size,
            (self.num_heads + 2 * self.num_key_value_heads) * self.head_dim,
            bias=config.use_qkv_bias,
        )

        if self.config.use_qk_norm:
            self.query_layernorm = LLaDA2MoeRMSNorm(
                self.head_dim, eps=config.rms_norm_eps
            )
            self.key_layernorm = LLaDA2MoeRMSNorm(
                self.head_dim, eps=config.rms_norm_eps
            )
        self.dense = nn.Linear(
            self.num_heads * self.head_dim, self.hidden_size, bias=config.use_bias
        )
        self.sliding_window = getattr(config, "sliding_window", None)

    def _shape(self, tensor: torch.Tensor, seq_len: int, bsz: int):
        return (
            tensor.view(bsz, seq_len, self.num_heads, self.head_dim)
            .transpose(1, 2)
            .contiguous()
        )

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_value: Optional[Cache] = None,
        output_attentions: bool = False,
        use_cache: bool = False,
        position_embeddings: Optional[
            Tuple[torch.Tensor, torch.Tensor]
        ] = None,  # necessary, but kept here for BC
        **kwargs,
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
        input_shape = hidden_states.shape[:-1]

        bsz, q_len, _ = hidden_states.size()

        qkv = self.query_key_value(hidden_states)
        qkv = qkv.view(
            bsz, q_len, self.num_heads + 2 * self.num_key_value_heads, self.head_dim
        )

        query_states, key_states, value_states = qkv.split(
            [self.num_heads, self.num_key_value_heads, self.num_key_value_heads], dim=-2
        )
        query_states = query_states.transpose(1, 2)
        key_states = key_states.transpose(1, 2)
        value_states = value_states.transpose(1, 2)

        if self.config.use_qk_norm:
            query_states = self.query_layernorm(query_states)
            key_states = self.key_layernorm(key_states)

        cos, sin = position_embeddings
        query_states, key_states = apply_rotary_pos_emb(
            query_states, key_states, cos, sin
        )

        if past_key_value is not None:
            if self.layer_idx is None:
                raise ValueError(
                    f"The cache structure has changed since version v4.36. If you are using {self.__class__.__name__} "
                    "for auto-regressive decoding with k/v caching, please make sure to initialize the attention class "
                    "with a layer index."
                )
            cache_kwargs = {"sin": sin, "cos": cos}
            key_states, value_states = past_key_value.update(
                key_states, value_states, self.layer_idx, cache_kwargs
            )

        attention_interface: Callable = eager_attention_forward
        if self.config._attn_implementation != "eager":
            attention_interface = ALL_ATTENTION_FUNCTIONS[
                self.config._attn_implementation
            ]

        attn_output, attn_weights = attention_interface(
            self,
            query_states,
            key_states,
            value_states,
            attention_mask,
            dropout=0.0 if not self.training else self.attention_dropout,
            scaling=self.scaling,
            sliding_window=self.sliding_window,  # diff with Llama
            **kwargs,
        )

        attn_output = attn_output.reshape(*input_shape, -1).contiguous()
        attn_output = self.dense(attn_output)

        return attn_output, attn_weights, past_key_value


class LLaDA2MoeDecoderLayer(nn.Module):
    def __init__(self, config: LLaDA2MoeConfig, layer_idx: int):
        super().__init__()
        self.hidden_size = config.hidden_size

        self.attention = LLaDA2MoeAttention(config=config, layer_idx=layer_idx)

        self.mlp = (
            LLaDA2MoeSparseMoeBlock(config)
            if (
                config.num_experts is not None
                and layer_idx >= config.first_k_dense_replace
            )
            else LLaDA2MoeMLP(config=config, intermediate_size=config.intermediate_size)
        )
        self.input_layernorm = LLaDA2MoeRMSNorm(
            config.hidden_size, eps=config.rms_norm_eps
        )
        self.post_attention_layernorm = LLaDA2MoeRMSNorm(
            config.hidden_size, eps=config.rms_norm_eps
        )

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_value: Optional[Tuple[torch.Tensor]] = None,
        output_attentions: Optional[bool] = False,
        output_router_logits: Optional[bool] = False,
        use_cache: Optional[bool] = False,
        position_embeddings: Optional[
            Tuple[torch.Tensor, torch.Tensor]
        ] = None,  # necessary, but kept here for BC
        **kwargs,
    ) -> Tuple[
        torch.FloatTensor, Optional[Tuple[torch.FloatTensor, torch.FloatTensor]]
    ]:
        """
        Args:
            hidden_states (`torch.FloatTensor`): input to the layer of shape `(batch, seq_len, embed_dim)`
            attention_mask (`torch.FloatTensor`, *optional*):
                attention mask of size `(batch_size, sequence_length)` if flash attention is used or `(batch_size, 1,
                query_sequence_length, key_sequence_length)` if default attention is used.
            position_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
                Indices of positions of each input sequence tokens in the position embeddings. Selected in the range `[0,
                config.n_positions - 1]`.
            past_key_value (`Tuple(torch.FloatTensor)`, *optional*):
                cached past key and value projection states
            output_attentions (`bool`, *optional*):
                Whether to return the attentions tensors of all attention layers. See `attentions` under
                returned tensors for more detail.
            output_router_logits (`bool`, *optional*):
                Whether or not to return the logits of all the routers. They are useful for computing the router loss,
                and should not be returned during inference.
            use_cache (`bool`, *optional*):
                If set to `True`, `past_key_values` key value states are returned and can be used to speed up decoding
                (see `past_key_values`).
        """
        residual = hidden_states

        hidden_states = self.input_layernorm(hidden_states)

        # Self Attention
        hidden_states, self_attn_weights, present_key_value = self.attention(
            hidden_states=hidden_states,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_value=past_key_value,
            output_attentions=output_attentions,
            position_embeddings=position_embeddings,
            use_cache=use_cache,
        )
        hidden_states = residual + hidden_states

        # Fully Connected
        residual = hidden_states
        hidden_states = self.post_attention_layernorm(hidden_states)
        hidden_states = self.mlp(hidden_states)
        if isinstance(hidden_states, tuple):
            hidden_states, router_logits = hidden_states
        else:
            router_logits = None
        hidden_states = residual + hidden_states.to(residual.device)

        outputs = (hidden_states,)

        if output_attentions:
            outputs += (self_attn_weights,)

        if use_cache:
            outputs += (present_key_value,)

        if output_router_logits:
            outputs += (router_logits,)

        return outputs


LLADA2MOE_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)

    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.

    Parameters:
        config ([`LLaDA2MoeConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""


@add_start_docstrings(
    "The bare LLaDA2Moe Model outputting raw hidden-states without any specific head on top.",
    LLADA2MOE_START_DOCSTRING,
)
class LLaDA2MoePreTrainedModel(PreTrainedModel):
    config_class = LLaDA2MoeConfig
    base_model_prefix = "model"
    supports_gradient_checkpointing = True
    _no_split_modules = ["LLaDA2MoeDecoderLayer"]
    _skip_keys_device_placement = ["past_key_values"]
    _supports_flash_attn_2 = False
    _supports_sdpa = True
    _supports_flex_attn = True
    _supports_cache_class = True

    @torch.no_grad()
    def _init_weights(self, module):
        super()._init_weights(module)
        std = self.config.initializer_range
        if isinstance(module, LLaDA2MoeGate):
            nn.init.normal_(module.weight, mean=0.0, std=std)


LLADA2MOE_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary. Padding will be ignored by default should you provide
            it.

            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.

            [What are input IDs?](../glossary#input-ids)
        attention_mask (`torch.Tensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:

            - 1 for tokens that are **not masked**,
            - 0 for tokens that are **masked**.

            [What are attention masks?](../glossary#attention-mask)

            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.

            If `past_key_values` is used, optionally only the last `input_ids` have to be input (see
            `past_key_values`).

            If you want to change padding behavior, you should read [`modeling_opt._prepare_decoder_attention_mask`]
            and modify to your needs. See diagram 1 in [the paper](https://arxiv.org/abs/1910.13461) for more
            information on the default strategy.

            - 1 indicates the head is **not masked**,
            - 0 indicates the head is **masked**.
        position_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Indices of positions of each input sequence tokens in the position embeddings. Selected in the range `[0,
            config.n_positions - 1]`.

            [What are position IDs?](../glossary#position-ids)
        past_key_values (`Cache` or `tuple(tuple(torch.FloatTensor))`, *optional*):
            Pre-computed hidden-states (key and values in the self-attention blocks and in the cross-attention
            blocks) that can be used to speed up sequential decoding. This typically consists in the `past_key_values`
            returned by the model at a previous stage of decoding, when `use_cache=True` or `config.use_cache=True`.

            Two formats are allowed:
            - a [`~cache_utils.Cache`] instance;
            - Tuple of `tuple(torch.FloatTensor)` of length `config.n_layers`, with each tuple having 2 tensors of
            shape `(batch_size, num_heads, sequence_length, embed_size_per_head)`). This is also known as the legacy
            cache format.

            The model will output the same cache format that is fed as input. If no `past_key_values` are passed, the
            legacy cache format will be returned.

            If `past_key_values` are used, the user can optionally input only the last `input_ids` (those that don't
            have their past key value states given to this model) of shape `(batch_size, 1)` instead of all `input_ids`
            of shape `(batch_size, sequence_length)`.
        inputs_embeds (`torch.FloatTensor` of shape `(batch_size, sequence_length, hidden_size)`, *optional*):
            Optionally, instead of passing `input_ids` you can choose to directly pass an embedded representation. This
            is useful if you want more control over how to convert `input_ids` indices into associated vectors than the
            model's internal embedding lookup matrix.
        use_cache (`bool`, *optional*):
            If set to `True`, `past_key_values` key value states are returned and can be used to speed up decoding (see
            `past_key_values`).
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""


@add_start_docstrings(
    "The bare LLaDA2Moe Model outputting raw hidden-states without any specific head on top.",
    LLADA2MOE_START_DOCSTRING,
)
class LLaDA2MoeModel(LLaDA2MoePreTrainedModel):
    """
    Transformer decoder consisting of *config.num_hidden_layers* layers. Each layer is a [`LLaDA2MoeDecoderLayer`]

    Args:
        config: LLaDA2MoeConfig
    """

    def __init__(self, config: LLaDA2MoeConfig):
        super().__init__(config)
        self.padding_idx = config.pad_token_id
        self.vocab_size = config.vocab_size

        self.word_embeddings = nn.Embedding(
            config.vocab_size, config.hidden_size, self.padding_idx
        )
        self.layers = nn.ModuleList(
            [
                LLaDA2MoeDecoderLayer(config, layer_idx)
                for layer_idx in range(config.num_hidden_layers)
            ]
        )
        self._use_sdpa = config._attn_implementation == "sdpa"
        self._use_flex_attention = config._attn_implementation == "flex_attention"
        self.norm = LLaDA2MoeRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.rotary_emb = LLaDA2MoeRotaryEmbedding(config=config)
        self.gradient_checkpointing = False
        # Initialize weights and apply final processing
        self.post_init()

    def get_input_embeddings(self):
        return self.word_embeddings

    def set_input_embeddings(self, value):
        self.word_embeddings = value

    @add_start_docstrings_to_model_forward(LLADA2MOE_INPUTS_DOCSTRING)
    def forward(
        self,
        input_ids: torch.LongTensor = None,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[List[torch.FloatTensor]] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        output_router_logits: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        **kwargs,
    ) -> Union[Tuple, MoeModelOutputWithPast]:
        output_attentions = (
            output_attentions
            if output_attentions is not None
            else self.config.output_attentions
        )
        output_hidden_states = (
            output_hidden_states
            if output_hidden_states is not None
            else self.config.output_hidden_states
        )
        output_router_logits = (
            output_router_logits
            if output_router_logits is not None
            else self.config.output_router_logits
        )
        use_cache = use_cache if use_cache is not None else self.config.use_cache

        return_dict = (
            return_dict if return_dict is not None else self.config.use_return_dict
        )

        # retrieve input_ids and inputs_embeds
        if input_ids is not None and inputs_embeds is not None:
            raise ValueError(
                "You cannot specify both input_ids and inputs_embeds at the same time"
            )
        elif input_ids is not None:
            batch_size, seq_length = input_ids.shape[:2]
        elif inputs_embeds is not None:
            batch_size, seq_length = inputs_embeds.shape[:2]
        else:
            raise ValueError("You have to specify either input_ids or inputs_embeds")

        if self.gradient_checkpointing and self.training:
            if use_cache:
                logger.warning_once(
                    "`use_cache=True` is incompatible with gradient checkpointing. Setting `use_cache=False`transformers."
                )
                use_cache = False

        if use_cache and past_key_values is None:
            past_key_values = DynamicCache()

        if inputs_embeds is None:
            inputs_embeds = self.word_embeddings(input_ids)

        past_seen_tokens = (
            past_key_values.get_seq_length() if past_key_values is not None else 0
        )

        if position_ids is None:
            position_ids = torch.arange(
                past_seen_tokens,
                past_seen_tokens + inputs_embeds.shape[1],
                device=inputs_embeds.device,
            )
            position_ids = position_ids.unsqueeze(0)

        attention_mask = create_bidirectional_mask(
            config=self.config,
            inputs_embeds=inputs_embeds,
            attention_mask=attention_mask,
        )

        # embed positions
        hidden_states = inputs_embeds

        # create position embeddings to be shared across the decoder layers
        position_embeddings = self.rotary_emb(hidden_states, position_ids)

        # decoder layers
        all_hidden_states = () if output_hidden_states else None
        all_self_attns = () if output_attentions else None
        all_router_logits = () if output_router_logits else None
        next_decoder_cache = None

        for decoder_layer in self.layers:
            if output_hidden_states:
                all_hidden_states += (hidden_states,)

            if self.gradient_checkpointing and self.training:
                layer_outputs = self._gradient_checkpointing_func(
                    decoder_layer.__call__,
                    hidden_states,
                    attention_mask,
                    position_ids,
                    past_key_values,
                    output_attentions,
                    output_router_logits,
                    use_cache,
                    position_embeddings,
                )
            else:
                layer_outputs = decoder_layer(
                    hidden_states,
                    attention_mask=attention_mask,
                    position_ids=position_ids,
                    past_key_value=past_key_values,
                    output_attentions=output_attentions,
                    output_router_logits=output_router_logits,
                    use_cache=use_cache,
                    position_embeddings=position_embeddings,
                )
            hidden_states = layer_outputs[0]

            if use_cache:
                next_decoder_cache = layer_outputs[2 if output_attentions else 1]

            if output_attentions:
                all_self_attns += (layer_outputs[1],)

            if output_router_logits and layer_outputs[-1] is not None:
                all_router_logits += (layer_outputs[-1],)

        hidden_states = self.norm(hidden_states)

        # add hidden states from the last decoder layer
        if output_hidden_states:
            all_hidden_states += (hidden_states,)

        next_cache = None
        if use_cache:
            next_cache = next_decoder_cache
        if not return_dict:
            return tuple(
                v
                for v in [
                    hidden_states,
                    next_cache,
                    all_hidden_states,
                    all_self_attns,
                    all_router_logits,
                ]
                if v is not None
            )
        return MoeModelOutputWithPast(
            last_hidden_state=hidden_states,
            past_key_values=next_cache,
            hidden_states=all_hidden_states,
            attentions=all_self_attns,
            router_logits=all_router_logits,
        )


class LLaDA2MoeModelLM(LLaDA2MoePreTrainedModel, GenerationMixin):
    _tied_weights_keys = ["lm_head.weight"]

    def __init__(self, config: LLaDA2MoeConfig):
        super().__init__(config)
        self.model = LLaDA2MoeModel(config)
        self.vocab_size = config.vocab_size
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)

        # Initialize weights and apply final processing
        self.post_init()

    def get_input_embeddings(self):
        return self.model.word_embeddings

    def set_input_embeddings(self, value):
        self.model.word_embeddings = value

    def get_output_embeddings(self):
        return self.lm_head

    def set_output_embeddings(self, new_embeddings):
        self.lm_head = new_embeddings

    def set_decoder(self, decoder):
        self.model = decoder

    def get_decoder(self):
        return self.model

    @add_start_docstrings_to_model_forward(LLADA2MOE_INPUTS_DOCSTRING)
    @replace_return_docstrings(
        output_type=MoeCausalLMOutputWithPast, config_class=_CONFIG_FOR_DOC
    )
    def forward(
        self,
        input_ids: torch.LongTensor = None,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[List[torch.FloatTensor]] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        labels: Optional[torch.LongTensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        output_router_logits: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        **kwargs,
    ) -> Union[Tuple, MoeCausalLMOutputWithPast]:
        r"""
        Args:
            labels (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
                Labels for computing the masked language modeling loss. Indices should either be in `[0, ...,
                config.vocab_size]` or -100 (see `input_ids` docstring). Tokens with indices set to `-100` are ignored
                (masked), the loss is only computed for the tokens with labels in `[0, ..., config.vocab_size]`.

        Returns:

        Example:

        ```python
        >>> from transformers import AutoTokenizer

        >>> model = LLaDA2MoeForCausalLM.from_pretrained(PATH_TO_CONVERTED_WEIGHTS)
        >>> tokenizer = AutoTokenizer.from_pretrained(PATH_TO_CONVERTED_TOKENIZER)

        >>> prompt = "Hey, are you conscious? Can you talk to me?"
        >>> inputs = tokenizer(prompt, return_tensors="pt")

        >>> # Generate
        >>> generate_ids = model.generate(inputs.input_ids, max_length=30)
        >>> tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
        "Hey, are you conscious? Can you talk to me?\nI'm not conscious, but I can talk to you."
        ```"""
        output_attentions = (
            output_attentions
            if output_attentions is not None
            else self.config.output_attentions
        )
        output_hidden_states = (
            output_hidden_states
            if output_hidden_states is not None
            else self.config.output_hidden_states
        )
        output_router_logits = (
            output_router_logits
            if output_router_logits is not None
            else self.config.output_router_logits
        )
        return_dict = (
            return_dict if return_dict is not None else self.config.use_return_dict
        )
        # decoder outputs consists of (dec_features, layer_state, dec_hidden, dec_attn)
        outputs = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            output_router_logits=output_router_logits,
            return_dict=return_dict,
            **kwargs,
        )

        loss = None
        aux_loss = None
        hidden_states = outputs[0]

        logits = self.lm_head(hidden_states)
        logits = logits.float()

        if labels is not None:
            # LLaDA2.0 will use same label position logits
            shift_logits = logits
            shift_labels = labels
            # Flatten the tokens
            loss_fct = CrossEntropyLoss()
            shift_logits = shift_logits.view(-1, self.config.vocab_size)
            shift_labels = shift_labels.view(-1)
            # Enable model parallelism
            shift_labels = shift_labels.to(shift_logits.device)
            loss = loss_fct(shift_logits, shift_labels)

        if not return_dict:
            output = (logits,) + outputs[1:]
            if output_router_logits:
                output = (aux_loss,) + output
            return (loss,) + output if loss is not None else output

        return MoeCausalLMOutputWithPast(
            loss=loss,
            aux_loss=aux_loss,
            logits=logits,
            past_key_values=outputs.past_key_values,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
            router_logits=outputs.router_logits,
        )

    def prepare_inputs_for_generation(
        self,
        input_ids,
        past_key_values=None,
        attention_mask=None,
        inputs_embeds=None,
        token_type_ids=None,
        **kwargs,
    ):
        if past_key_values is not None:
            if isinstance(past_key_values, Cache):
                cache_length = past_key_values.get_seq_length()
                past_length = past_key_values.seen_tokens
                max_cache_length = (
                    past_key_values.get_max_length()
                    if hasattr(past_key_values, "get_max_length")
                    else past_key_values.get_max_cache_shape()
                )
            else:
                cache_length = past_length = past_key_values[0][0].shape[2]
                max_cache_length = None

            # Keep only the unprocessed tokens:
            # 1 - If the length of the attention_mask exceeds the length of input_ids, then we are in a setting where
            # some of the inputs are exclusivelly passed as part of the cache (e.g. when passing input_embeds as input)
            if (
                attention_mask is not None
                and attention_mask.shape[1] > input_ids.shape[1]
            ):
                input_ids = input_ids[:, -(attention_mask.shape[1] - past_length) :]
            # 2 - If the past_length is smaller than input_ids', then input_ids holds all input tokens. We can discard
            # input_ids based on the past_length.
            elif past_length < input_ids.shape[1]:
                input_ids = input_ids[:, past_length:]
            # 3 - Otherwise (past_length >= input_ids.shape[1]), let's assume input_ids only has unprocessed tokens.

            # If we are about to go beyond the maximum cache length, we need to crop the input attention mask.
            if (
                max_cache_length is not None
                and attention_mask is not None
                and cache_length + input_ids.shape[1] > max_cache_length
            ):
                attention_mask = attention_mask[:, -max_cache_length:]

        position_ids = kwargs.get("position_ids", None)
        if attention_mask is not None and position_ids is None:
            # create position_ids on the fly for batch generation
            position_ids = attention_mask.long().cumsum(-1) - 1
            position_ids.masked_fill_(attention_mask == 0, 1)
            if past_key_values:
                position_ids = position_ids[:, -input_ids.shape[1] :]

        # if `inputs_embeds` are passed, we only want to use them in the 1st generation step
        if inputs_embeds is not None and past_key_values is None:
            model_inputs = {"inputs_embeds": inputs_embeds}
        else:
            model_inputs = {"input_ids": input_ids}

        model_inputs.update(
            {
                "position_ids": position_ids,
                "past_key_values": past_key_values,
                "use_cache": kwargs.get("use_cache"),
                "attention_mask": attention_mask,
            }
        )
        return model_inputs

    @staticmethod
    def _reorder_cache(past_key_values, beam_idx):
        reordered_past = ()
        for layer_past in past_key_values:
            reordered_past += (
                tuple(
                    past_state.index_select(0, beam_idx.to(past_state.device))
                    for past_state in layer_past
                ),
            )
        return reordered_past

    @staticmethod
    def _top_k_logits(logits, k):
        if k is None or k <= 0:
            return logits
        else:
            values, _ = torch.topk(logits, k)
            min_values = values[..., -1, None]
            return torch.where(
                logits < min_values, torch.full_like(logits, float("-inf")), logits
            )

    @staticmethod
    def _top_p_logits(logits, p):
        if p is None or p >= 1.0:
            return logits
        sorted_logits, sorted_indices = torch.sort(logits, descending=True)
        cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
        sorted_mask = cumulative_probs > p
        sorted_mask[..., 1:] = sorted_mask[..., :-1].clone()
        sorted_mask[..., 0] = False
        mask_indices = torch.scatter(
            torch.full_like(logits, False, dtype=torch.bool),
            -1,
            sorted_indices,
            sorted_mask,
        )
        return logits.masked_fill(mask_indices, float("-inf"))

    def _sample_with_temperature_topk_topp(
        self, logits, temperature=1.0, top_k=0, top_p=1.0
    ):
        orig_shape = logits.shape[:-1]
        vocab_size = logits.shape[-1]
        logits = logits.reshape(-1, vocab_size)
        if temperature > 0 and temperature != 1.0:
            logits = logits / temperature
        logits = self._top_k_logits(logits, top_k)
        logits = self._top_p_logits(logits, top_p)
        probs = F.softmax(logits, dim=-1)
        token = torch.multinomial(probs, num_samples=1)
        token_prob = torch.gather(probs, -1, token)
        return token.view(*orig_shape), token_prob.view(*orig_shape)

    @staticmethod
    def _get_num_transfer_tokens(block_length, steps):
        if steps == 0:
            return torch.tensor([], dtype=torch.int64)
        base = block_length // steps
        remainder = block_length % steps
        num_transfer_tokens = torch.full((steps,), base, dtype=torch.int64)
        num_transfer_tokens[:remainder] += 1
        return num_transfer_tokens

    @staticmethod
    def _apply_edit_operations_with_tracking(
        block_tokens,
        old_block_tokens,
        is_original_mask_snapshot,
        mask_id,
        block_length,
        delete_token_id,
        split_token_id,
    ):
        """Process DELETE and SPLIT tokens in a block while tracking ``is_original_mask``.

        The block is kept at a fixed ``block_length`` by truncating (when SPLIT grows it) or
        right-padding with masks (when DELETE shrinks it).

        Args:
            block_tokens: List of token ids in the block (current state after writes).
            old_block_tokens: List of token ids before this step (used to restore SPLIT's carried token).
            is_original_mask_snapshot: Per-position bools marking positions that were original masks.
            mask_id: The mask token id.
            block_length: Target (fixed) block length.
            delete_token_id / split_token_id: Special edit-operation token ids.

        Behaviour:
            - DELETE: skip the token (and its tracking entry).
            - SPLIT:  token -> [mask_id, old_token], tracking -> [False, snapshot_val].
            - Kept token: carried through with its snapshot tracking value.
            - Padding masks (from shrink) are tracked as non-original (False).

        Returns:
            (result_tokens, result_tracking): both lists of length ``block_length``.
        """
        result_tokens = []
        result_tracking = []
        for i, token in enumerate(block_tokens):
            if token == delete_token_id:
                continue
            elif token == split_token_id:
                old_token = old_block_tokens[i] if i < len(old_block_tokens) else mask_id
                snapshot_val = (
                    is_original_mask_snapshot[i] if i < len(is_original_mask_snapshot) else False
                )
                result_tokens.extend([mask_id, old_token])
                result_tracking.extend([False, snapshot_val])
            else:
                snapshot_val = (
                    is_original_mask_snapshot[i] if i < len(is_original_mask_snapshot) else False
                )
                result_tokens.append(token)
                result_tracking.append(snapshot_val)

        if len(result_tokens) > block_length:
            result_tokens = result_tokens[:block_length]
            result_tracking = result_tracking[:block_length]
        elif len(result_tokens) < block_length:
            pad_count = block_length - len(result_tokens)
            result_tokens.extend([mask_id] * pad_count)
            result_tracking.extend([False] * pad_count)

        return result_tokens, result_tracking

    def _diffusion_sample(self, logits, temperature=1.0, top_k=None, top_p=None):
        """Sample a token id per position and return its (raw-softmax) confidence.

        With ``temperature == 0`` this is greedy (argmax). Otherwise it applies
        temperature / top-k / top-p filtering and samples. The returned probability is always
        taken from the *unfiltered* softmax so it can be used directly as a confidence score.
        """
        orig_shape = logits.shape[:-1]
        vocab_size = logits.shape[-1]
        logits = logits.reshape(-1, vocab_size)
        probs_full = F.softmax(logits, dim=-1)

        if temperature is None or temperature == 0.0:
            token = torch.argmax(logits, dim=-1, keepdim=True)
        else:
            scaled = logits / temperature if temperature != 1.0 else logits
            scaled = self._top_k_logits(scaled, top_k or 0)
            scaled = self._top_p_logits(scaled, top_p if top_p is not None else 1.0)
            probs = F.softmax(scaled, dim=-1)
            token = torch.multinomial(probs, num_samples=1)

        token_prob = torch.gather(probs_full, -1, token)
        return token.view(*orig_shape), token_prob.view(*orig_shape)

    def _resample_to_escape_loop(
        self,
        block_ids,
        old_block_ids,
        block_logits,
        mt2_index,
        t2t_index,
        seen_block_results,
        temperature,
        top_k,
        top_p,
        max_iters=5,
    ):
        """Escape a decoding loop by resampling one changed position at a time.

        Called after M2T/T2T writes but BEFORE DELETE/SPLIT processing. If the current
        (pre-edit) block state repeats a previously seen state, repeatedly pick one random
        changed position (``block_ids != old_block_ids``) and resample it until the block is
        novel or ``max_iters`` is reached. The currently chosen token is masked out (-inf)
        before resampling. M2T positions resample with temperature/top-k/top-p; T2T positions
        resample greedily. Modifies ``block_ids`` in place.
        """
        if tuple(block_ids.tolist()) not in seen_block_results:
            return

        for _ in range(max_iters):
            changed_positions = (
                (block_ids != old_block_ids).nonzero(as_tuple=True)[0].tolist()
            )
            if not changed_positions:
                break

            # Use torch's RNG (not the ``random`` module) so the choice honors torch.manual_seed.
            rand_idx = torch.randint(len(changed_positions), (1,), device=block_ids.device).item()
            pos = changed_positions[rand_idx]
            current_token = block_ids[pos].item()
            pos_logits = block_logits[pos, :].clone()
            pos_logits[current_token] = float("-inf")

            if bool(mt2_index[pos]):
                new_token, _ = self._diffusion_sample(
                    pos_logits.unsqueeze(0), temperature=temperature, top_k=top_k, top_p=top_p
                )
            elif bool(t2t_index[pos]):
                new_token, _ = self._diffusion_sample(
                    pos_logits.unsqueeze(0), temperature=0.0, top_k=None, top_p=None
                )
            else:
                # A changed position must be M2T or T2T; skip anything unexpected.
                continue

            block_ids[pos] = new_token.view(-1)[0]
            if tuple(block_ids.tolist()) not in seen_block_results:
                break

    @torch.no_grad()
    def _joint_decode_block(
        self,
        x,
        block_start,
        block_end,
        attention_mask,
        position_ids,
        temperature,
        top_k,
        top_p,
        steps,
        threshold,
        editing_threshold,
        max_post_steps,
        mask_id,
        delete_token_id,
        split_token_id,
        max_steps_per_block,
    ):
        """Iteratively refine a single block in place using joint M2T + T2T + edit ops.

        The active block is ``x[0, block_start:block_end]`` (fixed length). Earlier positions
        of ``x`` provide frozen context via ``attention_mask`` / ``position_ids``. Each step:
          1. forward over ``x[:, :block_end]``,
          2. M2T: fill masks whose greedy confidence clears ``threshold`` (with a per-step floor
             from the ``steps`` transfer schedule),
          3. T2T: rewrite already-generated tokens whose greedy confidence clears
             ``editing_threshold`` and whose greedy token differs,
          4. anti-loop resample if the block state repeats,
          5. consume DELETE/SPLIT edit tokens (block stays fixed length).
        Once all *original* masks are gone, up to ``max_post_steps`` further refinement steps
        run; on the final such step DELETE/SPLIT are suppressed so the block can terminate.
        """
        device = x.device
        block_length = block_end - block_start

        # Positions that were NOT masks at block entry are prompt/context tokens: they are never
        # written and never carry DELETE/SPLIT, so this mask stays aligned across edits.
        prompt_mask_block = (x[0, block_start:block_end] != mask_id).clone()

        # A prompt/context position normally never holds a reserved edit token. If one does (bad
        # upstream template, history, or malformed input) it would be silently deleted/expanded by
        # the edit-op pass. Warn instead of failing silently.
        block_ids = x[0, block_start:block_end]
        prompt_edit_tokens = prompt_mask_block & (
            (block_ids == delete_token_id) | (block_ids == split_token_id)
        )
        if prompt_edit_tokens.any():
            logger.warning_once(
                "Reserved edit token(s) found in a prompt/context segment of block@%d; "
                "they will be deleted/expanded by the edit-op pass.",
                block_start,
            )

        is_original_mask = (x[0, block_start:block_end] == mask_id).tolist()
        initial_mask_count = sum(is_original_mask)
        if initial_mask_count == 0:
            return  # fully prompt/context block, nothing to decode

        # Per-step floor for M2T: spread the block's initial masks over ``steps`` steps. Fewer
        # steps -> more forced unmaskings per step. The schedule sums to ``initial_mask_count``.
        transfer_schedule = self._get_num_transfer_tokens(initial_mask_count, steps)
        seen_block_results = set()  # pre-edit block states seen this block, for loop detection
        post_steps = 0
        step_id = 0

        while True:
            blk = x[0, block_start:block_end]
            old_block = blk.clone()
            input_key = tuple(old_block.tolist())
            mask_index = (old_block == mask_id) & (~prompt_mask_block)

            original_mask_count = sum(
                1
                for i, v in enumerate(is_original_mask)
                if v and old_block[i].item() == mask_id
            )
            new_mask_count = mask_index.sum().item() - original_mask_count

            # Track post-mask refinement steps: reset while original masks remain.
            if original_mask_count == 0:
                post_steps += 1
            else:
                post_steps = 0

            logger.debug(
                "block@%d step=%d original_masks=%d new_masks=%d post_steps=%d/%d",
                block_start,
                step_id,
                original_mask_count,
                new_mask_count,
                post_steps,
                max_post_steps,
            )

            # Exit guard: require ZERO remaining masks (original *and* new), not just
            # original_mask_count == 0. An edit op can leave a fresh mask exactly when the last
            # original mask is resolved; keying off original masks alone would exit early and
            # return residual mask_id. The final round (below) force-resolves all masks, so this
            # normally holds immediately; the total-count guard is the belt-and-suspenders check.
            if mask_index.sum().item() == 0 and post_steps > max_post_steps:
                logger.debug(
                    "block@%d terminating: max_post_steps (%d) exceeded after %d steps",
                    block_start,
                    max_post_steps,
                    step_id,
                )
                break
            if step_id >= max_steps_per_block:
                logger.debug(
                    "block@%d terminating: max_steps_per_block (%d) reached",
                    block_start,
                    max_steps_per_block,
                )
                break

            # 1. Forward pass over the current window.
            logits = self.forward(
                x[:, :block_end],
                attention_mask=attention_mask,
                position_ids=position_ids,
            ).logits
            block_logits = logits[0, block_start:block_end, :]

            # 2. Sampled (temperature) result and greedy result + confidences.
            x_s, p_s = self._diffusion_sample(block_logits, temperature, top_k, top_p)
            if temperature != 0.0:
                x0, p0 = self._diffusion_sample(block_logits, 0.0, None, None)
            else:
                x0, p0 = x_s, p_s

            neg_inf = torch.full_like(p0, -float("inf"))

            # 3. M2T (mask -> token): threshold-gated with a per-step floor.
            # The gate uses ``p_s`` -- the confidence of the token that will actually be written
            # (``x_s``) -- so a position is only unmasked when the sampled token itself is
            # confident. When temperature == 0, ``p_s == p0``, so this reduces to greedy behavior.
            mt2_index = torch.zeros(block_length, dtype=torch.bool, device=device)
            if mask_index.any():
                if step_id < len(transfer_schedule):
                    num_need = transfer_schedule[step_id].item() + new_mask_count
                    mask_conf = torch.where(mask_index, p_s, neg_inf)
                    high_conf = (mask_conf > threshold) & mask_index
                    if high_conf.sum().item() >= num_need:
                        mt2_index = high_conf
                    else:
                        k_val = min(num_need, mask_index.sum().item())
                        if k_val > 0:
                            _, idx = torch.topk(mask_conf, k=k_val)
                            mt2_index[idx] = True
                else:
                    mt2_index = mask_index

            # 4. T2T (token -> token edit): high-confidence rewrites of generated tokens.
            editable_mask = (~mask_index) & (~prompt_mask_block)
            editing_confidence = torch.where(editable_mask, p0, neg_inf)
            high_conf_edit = (editing_confidence > editing_threshold) & editable_mask
            token_changed = old_block != x0
            t2t_index = high_conf_edit & token_changed

            fill_index_pre = mt2_index | t2t_index

            # Final round = the last refinement step, after which the block terminates. On it we
            # suppress SPLIT/DELETE (below) so no new masks appear.
            #
            # max_post_steps > 0: count-based -- fire once we've spent the post-mask step budget.
            # max_post_steps == 0: "no post steps" means the step that resolves the LAST original
            #   mask must itself finish the block. post_steps can't detect this (it is still 0 at
            #   the top of that step), so we detect it from mt2_index: this step is final iff its
            #   M2T covers every still-unresolved original mask. Guaranteed to fire eventually --
            #   the transfer schedule forces mt2_index == mask_index by step len(transfer_schedule).
            if max_post_steps > 0:
                final_round = post_steps >= max_post_steps
            else:
                remaining_original = mask_index & torch.tensor(is_original_mask, device=device)
                final_round = remaining_original.any() and (remaining_original <= mt2_index).all()

            # 5. On the final round, suppress SPLIT/DELETE so the block can terminate. Only the
            # positions that are actually written matter: M2T writes x_s, T2T writes x0. Other
            # positions may still contain S/D harmlessly since they are never written. Resampling
            # is batched over all offending positions (S/D columns masked to -inf).
            if final_round:
                # The final round must leave the block fully unmasked, so resolve EVERY remaining
                # mask here -- before the D/S suppression below, so these positions also get their
                # SPLIT/DELETE stripped and no fresh mask survives. For max_post_steps > 0 this is
                # already implied (once original masks are gone, new_mask_count inflates num_need so
                # M2T selects all masks anyway), so it is a no-op there; stating it makes the
                # invariant explicit and robust to changes in the M2T selection above.
                mt2_index = mask_index
                fill_index_pre = mt2_index | t2t_index

                m2t_sd = mt2_index & ((x_s == split_token_id) | (x_s == delete_token_id))
                if m2t_sd.any():
                    sd_logits = block_logits[m2t_sd].clone()
                    sd_logits[:, split_token_id] = float("-inf")
                    sd_logits[:, delete_token_id] = float("-inf")
                    new_tokens, _ = self._diffusion_sample(
                        sd_logits, temperature, top_k, top_p
                    )
                    x_s[m2t_sd] = new_tokens

                t2t_sd = t2t_index & ((x0 == split_token_id) | (x0 == delete_token_id))
                if t2t_sd.any():
                    sd_logits = block_logits[t2t_sd].clone()
                    sd_logits[:, split_token_id] = float("-inf")
                    sd_logits[:, delete_token_id] = float("-inf")
                    new_tokens, _ = self._diffusion_sample(
                        sd_logits, temperature=0.0, top_k=None, top_p=None
                    )
                    x0[t2t_sd] = new_tokens

            # 6. Apply writes: M2T writes the sampled token, T2T writes the greedy token.
            is_original_mask_snapshot = list(is_original_mask)
            if fill_index_pre.any():
                if mt2_index.any():
                    blk[mt2_index] = x_s[mt2_index]
                if t2t_index.any():
                    blk[t2t_index] = x0[t2t_index]

                # Anti-loop: escape a repeated pre-edit block state. Skipped on the final round,
                # where SD suppression already drives termination.
                if not final_round:
                    self._resample_to_escape_loop(
                        blk,
                        old_block,
                        block_logits,
                        mt2_index,
                        t2t_index,
                        seen_block_results,
                        temperature=temperature,
                        top_k=top_k,
                        top_p=top_p,
                    )

            seen_block_results.add(tuple(blk.tolist()))

            # 7. Consume DELETE/SPLIT edit tokens (block stays fixed length).
            edited_block, is_original_mask = self._apply_edit_operations_with_tracking(
                blk.tolist(),
                old_block.tolist(),
                is_original_mask_snapshot,
                mask_id,
                block_length,
                delete_token_id=delete_token_id,
                split_token_id=split_token_id,
            )
            x[0, block_start:block_end] = torch.tensor(
                edited_block, device=device, dtype=x.dtype
            )

            # 8. Stop when the block is stable and fully unmasked.
            if x[0, block_start:block_end].tolist() == list(input_key) and (
                x[0, block_start:block_end] == mask_id
            ).sum() == 0:
                step_id += 1
                break

            step_id += 1

    @torch.no_grad()
    def generate(
        self,
        inputs: Optional[torch.Tensor] = None,
        temperature: float = 0.0,
        block_length: int = 32,
        steps: int = 32,
        gen_length: int = 2048,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        threshold: float = 0.5,
        editing_threshold: float = 0.0,
        max_post_steps: int = 16,
        eos_early_stop: bool = False,
        eos_id: int = 156892,
        mask_id: int = 156895,
        delete_token_id: int = 156930,
        split_token_id: int = 156931,
        max_steps_per_block: int = 1000,
    ):
        r"""
        Generate tokens with a block-wise, edit-based iterative refinement strategy.

        Unlike autoregressive generation, this method lays out a full masked template and
        refines it block by block. Within each block it jointly performs:

        - **M2T** (mask -> token): converts ``mask_id`` placeholders into concrete tokens once
          their confidence exceeds ``threshold`` (with a per-step floor so progress is
          guaranteed).
        - **T2T** (token -> token): rewrites already-generated tokens whose greedy confidence
          exceeds ``editing_threshold`` and whose greedy prediction differs from the current
          token.
        - **DELETE / SPLIT**: consumes special edit tokens to remove positions or insert new
          masks, letting the block change its content length (kept fixed by pad/truncate).

        An anti-loop resampler perturbs the block whenever a pre-edit state repeats. After all
        original masks in a block are resolved, up to ``max_post_steps`` further refinement
        steps run; the final one suppresses DELETE/SPLIT so the block terminates.

        A block-diagonal causal attention mask lets a block attend to all previous blocks (and
        bidirectionally within itself) but not to future blocks.

        Parameters:
            inputs (`torch.Tensor`): Prompt token ids of shape ``(1, prompt_length)``.
            temperature (`float`, defaults to 0.0): 0.0 is greedy; >0 enables sampling for M2T.
            block_length (`int`, defaults to 32): Fixed length of each generation block.
            steps (`int`, defaults to 32): Number of steps the M2T transfer schedule spreads a
                block's initial masks over (per-step unmasking floor). Fewer steps forces more
                unmaskings per step. Independent of the actual number of iterations, which is
                driven by the confidence thresholds and the post-mask refinement phase.
            gen_length (`int`, defaults to 2048): Number of tokens to generate after the prompt.
            top_p / top_k (`float`/`int`, *optional*): Nucleus / top-k filtering for sampling.
            threshold (`float`, defaults to 0.5): Confidence threshold for M2T unmasking.
            editing_threshold (`float`, defaults to 0.0): Confidence threshold for T2T edits.
            max_post_steps (`int`, defaults to 16): Max refinement steps after a block's original
                masks are all resolved.
            eos_early_stop (`bool`, defaults to False): Stop after a block that produced ``eos_id``.
            eos_id / mask_id (`int`): End-of-sequence and mask placeholder token ids.
            delete_token_id / split_token_id (`int`): Special edit-operation token ids.
            max_steps_per_block (`int`, defaults to 1000): Hard safety cap on steps per block.

        Return:
            `torch.Tensor`: The generated token ids after the prompt, up to and including the
            first ``eos_id`` (or ``gen_length`` if none is produced).
        """
        input_ids = inputs.to(self.device)

        prompt_length = input_ids.shape[1]
        num_blocks = (prompt_length + gen_length + block_length - 1) // block_length
        total_length = num_blocks * block_length

        block_mask = torch.tril(torch.ones(num_blocks, num_blocks, device=self.device))
        block_diffusion_attention_mask = (
            (
                block_mask.repeat_interleave(block_length, dim=0)
                .repeat_interleave(block_length, dim=1)
                .unsqueeze(0)
                .unsqueeze(0)
            )
            .log()
            .to(torch.bfloat16)
        )

        position_ids = torch.arange(total_length, device=self.device).unsqueeze(0)
        x = torch.full((1, total_length), mask_id, dtype=torch.long, device=self.device)
        x[:, :prompt_length] = input_ids.clone()

        prefill_blocks = prompt_length // block_length

        for num_block in range(prefill_blocks, num_blocks):
            block_start = num_block * block_length
            block_end = (num_block + 1) * block_length
            cur_attn_mask = block_diffusion_attention_mask[
                :, :, :block_end, :block_end
            ]
            cur_position_ids = position_ids[:, :block_end]

            self._joint_decode_block(
                x,
                block_start,
                block_end,
                cur_attn_mask,
                cur_position_ids,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                steps=steps,
                threshold=threshold,
                editing_threshold=editing_threshold,
                max_post_steps=max_post_steps,
                mask_id=mask_id,
                delete_token_id=delete_token_id,
                split_token_id=split_token_id,
                max_steps_per_block=max_steps_per_block,
            )

            if (
                eos_early_stop
                and eos_id is not None
                and (x[0, prompt_length:block_end] == eos_id).any()
            ):
                break

        generated_answer = x[:, : prompt_length + gen_length]

        eos_positions = (generated_answer[0][prompt_length:] == eos_id).nonzero(
            as_tuple=True
        )[0]
        if len(eos_positions) > 0:
            first_eos_position = eos_positions[0].item()
        else:
            first_eos_position = gen_length
        output = generated_answer[
            :, prompt_length : prompt_length + first_eos_position + 1
        ]

        # Safety net: a well-formed decode leaves no mask / edit tokens in the output. If any
        # survive (e.g. a degenerate config such as max_post_steps=0 that fails to converge, or a
        # block that hit max_steps_per_block), warn instead of silently returning residual
        # mask_id / split / delete tokens to the caller.
        residual = (
            (output == mask_id)
            | (output == split_token_id)
            | (output == delete_token_id)
        )
        if residual.any():
            logger.warning(
                "Decoding finished with %d residual mask/split/delete token(s) in the output; "
                "the generation may be malformed.",
                int(residual.sum().item()),
            )

        return output
