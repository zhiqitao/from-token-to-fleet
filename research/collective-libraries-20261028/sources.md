# Primary sources actually fetched in this run

Citation keys in research.md and proposed-insertions.md resolve here and in claims.json. Dates below distinguish release metadata from retrieval. Quotes come from local fetched files. Branch/docs snapshots are not historical support proof. Failed requests are retained separately in retrieval.json.

## deepep

URL: https://raw.githubusercontent.com/deepseek-ai/DeepEP/main/README.md

Retrieved UTC: 2026-10-28T06:44:16.680985+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: main branch retrieval snapshot; vendor performance numbers not adopted

Raw SHA-256: 86415f7fc11381dceb14c112b6c602103d975936444601666ab1fcfd65e8fceb

Local text: evidence/deepep.txt

Lines 2–6 (dispatch):

> 
> DeepEP (DeepEveryParallel) is a high-performance communication library for machine learning training and inference. It provides high-throughput and low-latency expert-parallel (EP) all-to-all GPU kernels for MoE dispatch and combine, including FP8 dispatch, and NVLink weight and gradient exchange for redundant experts. It also offers experimental primitives for pipeline parallelism (PP), context parallelism (CP), data parallelism (DP), and remote memory access (Engram). Communication kernels are compiled at runtime via [DeepJIT](https://github.com/deepseek-ai/DeepJIT), with the supporting extension built during installation.
> 
> ## News

Lines 2–6 (combine):

> 
> DeepEP (DeepEveryParallel) is a high-performance communication library for machine learning training and inference. It provides high-throughput and low-latency expert-parallel (EP) all-to-all GPU kernels for MoE dispatch and combine, including FP8 dispatch, and NVLink weight and gradient exchange for redundant experts. It also offers experimental primitives for pipeline parallelism (PP), context parallelism (CP), data parallelism (DP), and remote memory access (Engram). Communication kernels are compiled at runtime via [DeepJIT](https://github.com/deepseek-ai/DeepJIT), with the supporting extension built during installation.
> 
> ## News

## gloo

URL: https://raw.githubusercontent.com/pytorch/gloo/main/README.md

Retrieved UTC: 2026-10-28T06:42:17.432569+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: main branch retrieval snapshot

Raw SHA-256: 3f728c45902120dcdc50e8ce67ca89dd77265d65a0d3cf0cfbaa966519700d90

Local text: evidence/gloo.txt

Lines 8–12 (collective):

> <h3 align="center">
> Collective communications library with various primitives for multi-machine training.
> </h3>
> 
> <p align="center">

Lines 33–37 (GPU):

> IP can be used at all times, or InifiniBand (or RoCE) when available.
> In the latter case, if the InfiniBand transport is used, [GPUDirect][gpudirect]
> can be used to accelerate cross machine GPU-to-GPU memory transfers.
> 
> [gpudirect]: https://developer.nvidia.com/gpudirect

## h100-datasheet

URL: https://images.nvidia.cn/aem-dam/en-zz/Solutions/data-center/h100/nvidia-h100-datasheet-nvidia-a4-2287922-r7-zhCN.pdf

Retrieved UTC: 2026-10-28T06:43:55.031022+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: NVIDIA H100 datasheet r7 zhCN; publication date not established

Raw SHA-256: 8fc14be0168d9c5058645df0cff20f3ac4f5734e478c925a0f68073130343189

Local text: evidence/h100-datasheet.txt

Lines 86–90 (900):

> NVLink ：
> 900GB/s 
> PCIe 5.0 ：128GB/s
> NVLink ：
> 600GB/s PCIe 

Lines 48–52 (80):

> 1000 TFLOPS*
> 800 TFLOPS*
> BFLOAT16 
> Tensor Core
> 2000 TFLOPS*

## megatron-layers

URL: https://raw.githubusercontent.com/NVIDIA/Megatron-LM/main/megatron/core/tensor_parallel/layers.py

Retrieved UTC: 2026-10-28T06:44:16.761708+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: main branch retrieval snapshot

Raw SHA-256: 2bbca7430f3d9cc1f12e2bf1a5e436a9b0b7e57c00bed890bcf3934c1c8436cc

Local text: evidence/megatron-layers.txt

Lines 1527–1531 (RowParallelLinear):

> 
> class RowParallelLinear(torch.nn.Module):
>     """Linear layer with row parallelism.
> 
>     The linear layer is defined as Y = XA + b. A is parallelized along its first dimension and X

Lines 42–46 (reduce_from_tensor_model_parallel_region):

>     gather_from_tensor_model_parallel_region,
>     reduce_from_tensor_model_parallel_region,
>     reduce_scatter_to_sequence_parallel_region,
>     scatter_to_tensor_model_parallel_region,
> )

## megatron-mappings

URL: https://raw.githubusercontent.com/NVIDIA/Megatron-LM/main/megatron/core/tensor_parallel/mappings.py

Retrieved UTC: 2026-10-28T06:44:16.744946+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: main branch retrieval snapshot

Raw SHA-256: 4c9510443311f5dbb35b2ff50bbd9e434225e65ee5ffe5bebbfafcfc356af20b

Local text: evidence/megatron-mappings.txt

Lines 38–42 (all_reduce):

>     input_ = input_.contiguous()
>     torch.distributed.all_reduce(input_, group=group)
> 
>     return input_

Lines 16–20 (reduce_scatter):

>         dist_all_gather_func = torch.distributed.all_gather_into_tensor
>         dist_reduce_scatter_func = torch.distributed.reduce_scatter_tensor
>     else:
>         dist_all_gather_func = torch.distributed._all_gather_base
>         dist_reduce_scatter_func = torch.distributed._reduce_scatter_base

## mpi50-pdf

URL: https://www.mpi-forum.org/docs/mpi-5.0/mpi50-report.pdf

Retrieved UTC: 2026-10-28T06:43:17.597401+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: MPI 5.0 approved2025-06-05; PDF authoritative over discrepant HTML numbering

Raw SHA-256: 2d4e6ae09ed04cf5eaf1bda2716d5a1023e282d78f577aa84538a89623c18051

Local text: evidence/mpi50-pdf.txt

Lines 28393–28397 (such as floating point addition):

> This may change the result of the reduction for operations that are not strictly associative
> and commutative, such as floating point addition.
> Advice to implementors. It is strongly recommended that MPI_REDUCE be imple-
> mented so that the same result be obtained whenever the function is applied on the
> same arguments, appearing in the same order. Note that this may prevent optimiza-

Lines 8490–8494 (weak progress):

> independently of MPI procedure calls in other MPI processes (operation-related or not). An
> MPI implementation provides weak progress if it does not provide strong progress.
> Advice to users. The type of progress may influence the performance of MPI opera-
> tions. A correct MPI application must be written under the assumption that only weak
> progress is provided. Every MPI application that is correct under weak progress will

Lines 40105–40109 (The persistent collective operations):

> "mpi_assert_strict_persistent_collective_ordering" (boolean, default: "false"): If set to
> "true", then the implementation may assume that all the persistent collective operations
> are started in the same order across all MPI processes in the group of the communicator.
> It is required that if this assertion is made on one member of the communicator’s group,
> then it must be made on all members of that communicator’s group with the same value.

## mpich-release

URL: https://api.github.com/repos/pmodels/mpich/releases/latest

Retrieved UTC: 2026-10-28T06:43:53.038179+00:00

Release/publication timestamp: 2026-09-28T17:42:19Z; GitHub published_at from fetched release metadata, not necessarily documentation publication date.

Scope: Fetched current documentation/metadata; publication date not established

Raw SHA-256: a10e8786fd102427313813c74117cd159960e9a9d40e458e4083643702df77aa

Local text: evidence/mpich-release.txt

Lines 1–1 (published_at):

> "target_commitish":"main","name":"MPICH 5.0.2 Released","draft":false,"immutable":false,"prerelease":false,"created_at":"2026-09-28T14:49:25Z","updated_at":"2026-09-28T17:45:44Z","published_at":"2026-09-28T17:42:19Z","assets":[{"url":"https://api.github.com/repos/pmodels/mpich/releases/assets/596007683","id":596007683,"node_id":"RA_kwDOBDoiF84jhlsD","name":"hydra-5.0.2.tar.gz","label":null,"uploader":{"login":"hzhou","id":1496702,"node_id":"MDQ6VXNlcjE0OTY3MDI=","avatar_url":"https://avatars.githubusercontent.com/u/1496702?v=4","gravatar_id":"","url":"https://api.github.com/users/hzhou","html_url":"https://github.com/hzhou","followers_url":"https://api.github.com/users/hzhou/followers","following_url":"https://api.github.com/users/hzhou/following{/other_user}","gists_url":"https://api.github.com/users/hzhou/gists{/gist_id}","starred_url":"https://api.github.com/users/hzhou/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/hzhou/subscriptions","organizations_url":"https://api.github.com/users/hzhou/orgs","repos_url":"https://api.github.com/users/hzhou/repos","events_url":"https://api.github.com/users/hzhou/events{/privacy}","received_event

## mpich-v502

URL: https://raw.githubusercontent.com/pmodels/mpich/v5.0.2/README.md

Retrieved UTC: 2026-10-28T06:44:16.722255+00:00

Release/publication timestamp: 2026-09-28T17:42:19Z; GitHub published_at from fetched release metadata, not necessarily documentation publication date.

Scope: v5.0.2 published2026-09-28

Raw SHA-256: 149fc1e879cc8be2f784257cb4b0bdc5f0e882362794588d5effbb6b6af07efe

Local text: evidence/mpich-v502.txt

Lines 264–268 (automatically detects):

> 
> MPICH automatically detects and enables GPU support for CUDA, Intel Level Zero (ZE), and HIP runtimes during configuration.
> 
> ### Automatic Detection
> GPU support is automatically enabled if any supported GPU runtime is detected during the configure process.

Lines 264–268 (Level Zero):

> 
> MPICH automatically detects and enables GPU support for CUDA, Intel Level Zero (ZE), and HIP runtimes during configuration.
> 
> ### Automatic Detection
> GPU support is automatically enabled if any supported GPU runtime is detected during the configure process.

## nccl-api-header

URL: https://raw.githubusercontent.com/NVIDIA/nccl/v2.32.3-1/src/nccl.h.in

Retrieved UTC: 2026-10-28T06:44:16.739533+00:00

Release/publication timestamp: 2026-09-17T21:09:42Z; GitHub published_at from fetched release metadata, not necessarily documentation publication date.

Scope: v2.32.3-1 tagged code; live user guide separately identified as retrieval snapshot

Raw SHA-256: 4d844c73806b153deaab89fe8688b6c5f905cbe8fb076fbe5df3c337413a7211

Local text: evidence/nccl-api-header.txt

Lines 473–477 (ncclAvg):

>                ncclMin        = 3,
>                ncclAvg        = 4,
>                /* ncclNumOps: The number of built-in ncclRedOp_t values. Also
>                 * serves as the least possible value for dynamic ncclRedOp_t's
>                 * as constructed by ncclRedOpCreate*** functions. */

Lines 713–717 (ncclAlltoAll):

>     ncclComm_t comm, cudaStream_t stream, const ncclCollConfig_t* config);
> ncclResult_t pncclAlltoAllConfig(const void* sendbuff, void* recvbuff, size_t count, ncclDataType_t datatype,
>     ncclComm_t comm, cudaStream_t stream, const ncclCollConfig_t* config);
> 
> ncclResult_t  ncclGatherConfig(const void* sendbuff, void* recvbuff, size_t count, ncclDataType_t datatype,

Lines 392–396 (ncclCommGetAsyncError):

> ncclResult_t  ncclCommGetAsyncError(ncclComm_t comm, ncclResult_t *asyncError);
> ncclResult_t pncclCommGetAsyncError(ncclComm_t comm, ncclResult_t *asyncError);
> 
> /* Gets the number of ranks in the communicator clique. */
> ncclResult_t  ncclCommCount(const ncclComm_t comm, int* count);

## nccl-cost-model

URL: https://raw.githubusercontent.com/NVIDIA/nccl/v2.32.3-1/src/tuning/cost_model.cc

Retrieved UTC: 2026-10-28T06:44:16.726196+00:00

Release/publication timestamp: 2026-09-17T21:09:42Z; GitHub published_at from fetched release metadata, not necessarily documentation publication date.

Scope: v2.32.3-1 tagged code; live user guide separately identified as retrieval snapshot

Raw SHA-256: 16f02b51770a9cf388869a35347f1989eaa8089415e96e7ea0b729beb1e1f1e8

Local text: evidence/nccl-cost-model.txt

Lines 379–383 (NCCL_PROTO):

>       if (((algo != NCCL_ALGO_UNDEF && algoEnable[f * NCCL_NUM_ALGORITHMS + algo] != 0) &&
>            (proto != NCCL_PROTO_UNDEF && protoEnable[f * NCCL_NUM_PROTOCOLS + proto] != 0)) ||
>           (symKernelId != ncclSymkKernelId_Count && symKernelIdEnable[f * ncclSymkKernelId_Count + symKernelId] != 0)) {
>         comm->tuningContext.enabled[i][f] = 1;
>       }

Lines 252–256 (NVLS):

>   {nullptr, nullptr, nullptr, {0}}, // NVLSTree/LL128, disabled as there is no implementation
>   {ncclTuningNvlsModelInit, ncclTuningNvlsModelSim, nullptr, {0, 0, 0, 0, 1}}, // NVLSTree/Simple
>   {nullptr, nullptr, nullptr, {0}}, // PAT/LL
>   {nullptr, nullptr, nullptr, {0}}, // PAT/LL128
>   {ncclTuningPatModelInit, ncclTuningPatModelSim, nullptr, {0, 0, 1, 1, 0}}, // PAT/Simple

## nccl-device

URL: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/api/device.html

Retrieved UTC: 2026-10-28T06:41:56.163389+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: v2.32.3-1 tagged code; live user guide separately identified as retrieval snapshot

Raw SHA-256: 89b6a8e167448c721abd450d00c1c61c496fbc7324f4f9664450fbb583f10524

Local text: evidence/nccl-device.txt

Lines 629–633 (Device API):

> CFT Barriers
> Device API – Remote Reduce and Copy: Building Blocks for Custom Communication Kernels
> Compile-Time Requirements
> API Overview
> ReduceSum — N Sources to One Destination

Lines 620–624 (GIN):

> Device API – GIN
> GIN
> Device API - CFT
> Compute Fabric Transport
> CFT Communicator Requirements

## nccl-device-guide

URL: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/deviceapi.html

Retrieved UTC: 2026-10-28T06:43:13.320568+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: v2.32.3-1 tagged code; live user guide separately identified as retrieval snapshot

Raw SHA-256: 4f7ac42b30b9e4e909a6a5729f5d4aca6877b58b881e8c00e22813cdd6e89557

Local text: evidence/nccl-device-guide.txt

Lines 602–606 (Starting with version 2.28):

> Device-Initiated Communication
> Starting with version 2.28, NCCL provides a device-side communication API, making it possible to use communication
> primitives directly from user CUDA kernels.
> Device API
> Device API consists of the following modules:

Lines 606–610 (LSA (Load/Store Accessible)):

> Device API consists of the following modules:
> LSA (Load/Store Accessible) – for communication between devices accessible via memory load/store operations,
> using CUDA P2P. This includes devices connected over NVLink and some devices connected over PCIe, so long as they
> have P2P connectivity with each other (as indicated by nvidia-smi topo -p2p p). Up to NCCL 2.28.3, the
> availability of LSA was also subject to the NCCL_P2P_LEVEL distance check, but that is no longer the case

Lines 613–617 (GIN (GPU-Initiated Networking)):

> NVLink SHARP (available on some datacenter GPUs since the Hopper generation).
> GIN (GPU-Initiated Networking) – for communication over the network (since NCCL 2.28.7).
> CFT (Compute Fabric Transport) – for communication through CUDA fabric logical endpoints
> (since NCCL 2.31). See Compute Fabric Transport.
> Reduce, Broadcast, and Fused Building Blocks — Building Blocks for Computation-Fused Kernels: reduce, copy

## nccl-env

URL: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html

Retrieved UTC: 2026-10-28T06:42:17.425589+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: v2.32.3-1 tagged code; live user guide separately identified as retrieval snapshot

Raw SHA-256: 3673a70f960c76db0ed6186f93d5f75e5ae62032302cb77f16fd4a1643fb0974

Local text: evidence/nccl-env.txt

Lines 1788–1792 (enable NVLink SHARP):

> 0: Disable the use of NVLink SHARP. No NVLink SHARP resources will be allocated.
> 1: Enable NVLink SHARP. NCCL initialization will not fail if NVLink SHARP is not supported on a given system, but it will fail if the NVLink SHARP resources cannot be allocated.
> 2: (Default) Same as 1: not failing if there is no support, but failing if resources could not be allocated. In versions 2.27 and 2.28, NCCL tried to silently fall back on other transports if NVLS resource allocation failed. This, however, could result in a hang if the allocation failed on just some of the ranks, so in 2.29 the behavior reverted to pre-2.27 (i.e., same as 1). Future versions may re-enable the silent fallback if it can be made to work reliably.
> NCCL_IB_MERGE_NICS
> (since 2.20)

Lines 1555–1559 (LL, LL128):

> (since 2.5) Comma-separated list of protocols (not case sensitive) among:
> LL, LL128, and Simple. To specify protocols to exclude
> (instead of to include), start the list with ^.
> The default behavior enables all supported algorithms: equivalent to
> LL,LL128,Simple on platforms which support LL128, and LL,Simple

## nccl-example-mpi

URL: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/examples.html

Retrieved UTC: 2026-10-28T06:42:50.300886+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: v2.32.3-1 tagged code; live user guide separately identified as retrieval snapshot

Raw SHA-256: 49c09b8ed1ce20763576ce960dcb5a5a65c997caed0604b91c46eae7e2967774

Local text: evidence/nccl-example-mpi.txt

Lines 1004–1008 (MPI_Bcast):

> if (myRank == 0) ncclGetUniqueId(&id);
> MPICHECK(MPI_Bcast((void *)&id, sizeof(id), MPI_BYTE, 0, MPI_COMM_WORLD));
> NCCLCHECK(ncclCommInitRankConfig(&nonblockingComms[i], nRanks, id, myRank, &config));
> do {
> NCCLCHECK(ncclCommGetAsyncError(nonblockingComms[i], &state));

Lines 1024–1028 (ncclAllReduce):

> for (int i=0; i<ngpus; i++)
> ncclAllReduce(sendbuffs[i], recvbuff[i], count, datatype, op, comms[i], streams[i]);
> ncclGroupEnd();
> After ncclGroupEnd, all of the operations have been enqueued to the stream.  Therefore, you can now call cudaStreamSynchronize if you want to wait for the operation to be complete:
> for (int i=0; i<ngpus; i++)

## nccl-init

URL: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/api/comms.html

Retrieved UTC: 2026-10-28T06:42:50.228120+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: v2.32.3-1 tagged code; live user guide separately identified as retrieval snapshot

Raw SHA-256: 572b1ab1f7c36e3204a2ee2d19b6ed1f3be827c081c87b555994a31778e56564

Local text: evidence/nccl-init.txt

Lines 747–751 (ncclCommGetAsyncError):

> ncclSuccess as soon as the operation is posted on the stream but may also report errors through
> ncclCommGetAsyncError() until they are completed. If the return code of any NCCL function is ncclInProgress,
> it means the operation is in the process of being enqueued in the background, and users must query the states
> of the communicators until all the states become ncclSuccess before calling another NCCL function. Before the
> states change into ncclSuccess, users are not allowed to issue CUDA kernel to the streams being used by NCCL.

Lines 747–751 (until they are completed):

> ncclSuccess as soon as the operation is posted on the stream but may also report errors through
> ncclCommGetAsyncError() until they are completed. If the return code of any NCCL function is ncclInProgress,
> it means the operation is in the process of being enqueued in the background, and users must query the states
> of the communicators until all the states become ncclSuccess before calling another NCCL function. Before the
> states change into ncclSuccess, users are not allowed to issue CUDA kernel to the streams being used by NCCL.

Lines 623–627 (uniqueId should):

> called once when creating a communicator and the Id should be distributed to all ranks in the
> communicator before calling ncclCommInitRank. uniqueId should point to a ncclUniqueId object allocated by the user.
> ncclSetEncryption
> ncclResult_t ncclSetEncryption(const ncclEncryptionConfig_t *config)
> Configures process-global encryption for NCCL-owned TCP sockets. A configuration with mode set to

## nccl-performance

URL: https://raw.githubusercontent.com/NVIDIA/nccl-tests/master/doc/PERFORMANCE.md

Retrieved UTC: 2026-10-28T06:41:55.985791+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: v2.32.3-1 tagged code; live user guide separately identified as retrieval snapshot

Raw SHA-256: 2242493053a6f9d5db1c6542a8ce7740be919778645125b94eeae440efd31edf

Local text: evidence/nccl-performance.txt

Lines 62–66 (2*(n-1)):

> 
>  `B = S/t * (2*(n-1)/n) = algbw * (2*(n-1)/n)`
> 
> ### ReduceScatter

Lines 38–42 (point-to-point operations):

> 
> **Note : this is independent of the algorithm used (ring, tree, or other) as long as they use point-to-point operations (send/receive).**
> 
> A ring would do that operation in an order which follows the ring :

Lines 98–102 (sendcount*sizeof):

> 
> Note that here, S is the size in bytes of the total array, which for NCCL is equal to `sendcount*sizeof(datatype)*n` as the `sendcount` argument is the count per rank.
> 
> ### Broadcast

## nccl-proxy-code

URL: https://raw.githubusercontent.com/NVIDIA/nccl/v2.32.3-1/src/proxy.cc

Retrieved UTC: 2026-10-28T06:45:39.238213+00:00

Release/publication timestamp: 2026-09-17T21:09:42Z; GitHub published_at from fetched release metadata, not necessarily documentation publication date.

Scope: v2.32.3-1 tagged code; live user guide separately identified as retrieval snapshot

Raw SHA-256: ed231a22a846d24c7564a034df9d04cbd3f8533e1671fe0141208cf37bca6091

Local text: evidence/nccl-proxy-code.txt

Lines 1999–2003 (ncclProxyProgress):

>   // Wait for all operations to complete and stop progress thread before freeing any resource
>   if (ncclProxyProgressDestroy(proxyState) != ncclSuccess) {
>     ATTN("[Proxy Service] proxyDestroy failed");
>   }
>   for (int s = 0; s < maxnpeers; s++) {

## nccl-release

URL: https://api.github.com/repos/NVIDIA/nccl/releases/latest

Retrieved UTC: 2026-10-28T06:41:56.111285+00:00

Release/publication timestamp: 2026-09-17T21:09:42Z; GitHub published_at from fetched release metadata, not necessarily documentation publication date.

Scope: v2.32.3-1 tagged code; live user guide separately identified as retrieval snapshot

Raw SHA-256: 05bdf14e070070b0789f7138dfb94e8048c8dc5a966d9ec5a65155dec72ce01c

Local text: evidence/nccl-release.txt

Lines 1–1 (published_at):

> get_commitish":"master","name":"NCCL v2.32.3-1 Release","draft":false,"immutable":false,"prerelease":false,"created_at":"2026-09-17T21:07:53Z","updated_at":"2026-09-21T19:57:59Z","published_at":"2026-09-17T21:09:42Z","assets":[],"tarball_url":"https://api.github.com/repos/NVIDIA/nccl/tarball/v2.32.3-1","zipball_url":"https://api.github.com/repos/NVIDIA/nccl/zipball/v2.32.3-1","body":" ## Vera Rubin Support\r\n\r\n  - Adds initial Rubin platform support including support for sm107, CX9 rail and plane detection, and MPS+MLoPart.\r\n  - 2.32.3 focuses on new functionalities and does not contain performance model tuning for Rubin. This will be part of the next release to improve out-of-box experience for Rubin users.\r\n\r\n  ## Device API Enhancements\r\n\r\n  - Adds Compute Fabric Transport (CFT) counted-write and wait support.\r\n  - Adds socket-based GIN support, enabling custom kernel development with TCP sockets.\r\n  - Adds support in GDAKI for LAG-aware QP assignment based on the context ID. ([Github PR #2315](https://github.com/NVIDIA/nccl/pull/2315))\r\n  - Adds NCCL_WIN_GIN_ONLY so users can register a window only for GIN usage.\r\n  - Optimize GIN perfor

Lines 1–1 (tag_name):

> ","received_events_url":"https://api.github.com/users/bhramesh-nvidia/received_events","type":"User","user_view_type":"public","site_admin":false},"node_id":"RE_kwDOAsBApM4XTyRg","tag_name":"v2.32.3-1","target_commitish":"master","name":"NCCL v2.32.3-1 Release","draft":false,"immutable":false,"prerelease":false,"created_at":"2026-09-17T21:07:53Z","updated_at":"2026-09-21T19:57:59Z","published_at":"2026-09-17T21:09:42Z","assets":[],"tarball_url":"https://api.github.com/repos/NVIDIA/nccl/tarball/v2.32.3-1","zipball_url":"https://api.github.com/repos/NVIDIA/nccl/zipball/v2.32.3-1","body":" ## Vera Rubin Support\r\n\r\n  - Adds initial Rubin platform support including support for sm107, CX9 rail and plane detection, and MPS+MLoPart.\r\n  - 2.32.3 focuses on new functionalities and does not contain performance model tuning for Rubin. This will be part of the next release to improve out-of-box experience for Rubin users.\r\n\r\n  ## Device API Enhancements\r\n\r\n  - Adds Compute Fabric Transport (CFT) counted-write and wait support.\r\n  - Adds socket-based GIN support, enabling custom kernel development with TCP sockets.\r\n  - Adds support in GDAKI for LAG-aware QP

## nccl-ring-code

URL: https://raw.githubusercontent.com/NVIDIA/nccl/v2.32.3-1/src/device/all_reduce.h

Retrieved UTC: 2026-10-28T06:43:13.150481+00:00

Release/publication timestamp: 2026-09-17T21:09:42Z; GitHub published_at from fetched release metadata, not necessarily documentation publication date.

Scope: v2.32.3-1 tagged code; live user guide separately identified as retrieval snapshot

Raw SHA-256: bfb84015f985be9ee398e82082eaaa80a095f8636b83f1a0170ec9ceba2e68a7

Local text: evidence/nccl-ring-code.txt

Lines 778–782 (runRing):

>   __device__ __forceinline__ void run(int tid, int nthreads, struct ncclDevWorkColl* work) {
>     runRing<T, RedOp, ProtoLL128>(tid, nthreads, work);
>   }
> };

Lines 172–176 (directRecvReduceCopyDirectSend):

>       nelem = min(chunkCount, channelCount - elemOffset);
>       prims.directRecvReduceCopyDirectSend(offset, offset, nelem, /*doPost=*/true);
>     }
>   } else if (tid < nthreadsSplit) {
>     /* Reduce up. Max number of recv is 3, max number of send is 1 (binary tree + local).

## nccl-search-code

URL: https://raw.githubusercontent.com/NVIDIA/nccl/v2.32.3-1/src/graph/search.cc

Retrieved UTC: 2026-10-28T06:45:39.237393+00:00

Release/publication timestamp: 2026-09-17T21:09:42Z; GitHub published_at from fetched release metadata, not necessarily documentation publication date.

Scope: v2.32.3-1 tagged code; live user guide separately identified as retrieval snapshot

Raw SHA-256: 9892ac8e52910b83d279591ecae562142535176aed266f2719a43972f7c6ecac

Local text: evidence/nccl-search-code.txt

Lines 1150–1154 (ncclTopoCompute):

> 
> ncclResult_t ncclTopoCompute(ncclTopoSystem* system, struct ncclTopoGraph* graph) {
>   ncclResult_t ret = ncclSuccess;
>   struct ncclTopoGraph* tmpGraph = NULL;
>   int ccMin;

## nccl-streams

URL: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/streams.html

Retrieved UTC: 2026-10-28T06:41:56.082477+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: v2.32.3-1 tagged code; live user guide separately identified as retrieval snapshot

Raw SHA-256: 9ee63c1963839395833458df3762b286809de06071d2dc5a95c2e38d312bc0ed

Local text: evidence/nccl-streams.txt

Lines 602–606 (enqueued):

> CUDA Stream Semantics
> NCCL calls are associated to a stream which is passed as the last argument of the collective communication function. The NCCL call returns when the operation has been effectively enqueued to the given stream, or returns an error. The collective operation is then executed asynchronously on the CUDA device. The operation status can be queried using standard CUDA semantics, for example, calling cudaStreamSynchronize or using CUDA events.
> Mixing Multiple Streams within the same ncclGroupStart/End() group
> NCCL allows for using multiple streams within a group call. This will enforce
> a stream dependency of all streams before the NCCL kernel starts and block all

Lines 602–606 (cudaStream):

> CUDA Stream Semantics
> NCCL calls are associated to a stream which is passed as the last argument of the collective communication function. The NCCL call returns when the operation has been effectively enqueued to the given stream, or returns an error. The collective operation is then executed asynchronously on the CUDA device. The operation status can be queried using standard CUDA semantics, for example, calling cudaStreamSynchronize or using CUDA events.
> Mixing Multiple Streams within the same ncclGroupStart/End() group
> NCCL allows for using multiple streams within a group call. This will enforce
> a stream dependency of all streams before the NCCL kernel starts and block all

## nccl-tests-readme

URL: https://raw.githubusercontent.com/NVIDIA/nccl-tests/master/README.md

Retrieved UTC: 2026-10-28T06:43:52.816109+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: v2.32.3-1 tagged code; live user guide separately identified as retrieval snapshot

Raw SHA-256: 7e1aef831b6bcd0befec250e82333d58dd71078730bafda03c7a99532f452895

Local text: evidence/nccl-tests-readme.txt

Lines 88–92 (correctness):

>   * `-p,--parallel_init <0/1>` use threads to initialize NCCL in parallel. Default : 0.
>   * `-c,--check <check iteration count>` perform count iterations, checking correctness of results on each iteration. This can be quite slow on large numbers of GPUs. Default : 1.
>   * `-z,--blocking <0/1/2/3>` collective blocking mode. Default: 0.
>     * `0` : non-blocking (default)
>     * `1` : wait and barrier after each inner iteration (`-m`)

Lines 100–104 (Performance):

>   * `-V,--device_cta_count <number>` number of CTAs for device API implementation. Must be positive and less than 128. Default : 16.
>   * `-S,--report_timestamps <0/1>` Add timestamp (`"%Y-%m-%d %H:%M:%S"`) to each performance report line. Default : 0.
>   * `-J,--output_file <file>` Write [JSON] output to filepath. Infer type from suffix (only `json` supported presently).
>   * `-T,--timeout <time in seconds>` timeout each test after specified number of seconds. Default : disabled.
>   * `-M,--memory <0/1>` enable memory usage report. Default : 0.

## nccl-topo-code

URL: https://raw.githubusercontent.com/NVIDIA/nccl/v2.32.3-1/src/graph/topo.cc

Retrieved UTC: 2026-10-28T06:45:39.258041+00:00

Release/publication timestamp: 2026-09-17T21:09:42Z; GitHub published_at from fetched release metadata, not necessarily documentation publication date.

Scope: v2.32.3-1 tagged code; live user guide separately identified as retrieval snapshot

Raw SHA-256: 413e396fb61c4e80af22c089e932070017ea89ee5c3af5a732087457fcd9b018

Local text: evidence/nccl-topo-code.txt

Lines 2164–2168 (ncclTopoGetSystem):

>   if (dumpXmlFile == NULL) {
>     NCCLCHECKGOTO(ncclTopoGetSystemFromXml(xml, system, getHostHash()), ret, fail);
>     // store comm related information
>     (*system)->minDriverVersion = comm->minDriverVersion;
>     (*system)->cuMemGdrSupport = comm->cuMemGdrSupport;

## nccl-transport-code

URL: https://raw.githubusercontent.com/NVIDIA/nccl/v2.32.3-1/src/transport.cc

Retrieved UTC: 2026-10-28T06:45:39.258258+00:00

Release/publication timestamp: 2026-09-17T21:09:42Z; GitHub published_at from fetched release metadata, not necessarily documentation publication date.

Scope: v2.32.3-1 tagged code; live user guide separately identified as retrieval snapshot

Raw SHA-256: de688902eaa0060133f02bcd86e542be759946f542516ed87fee66987a15f17c

Local text: evidence/nccl-transport-code.txt

Lines 183–187 (selectTransport):

>       if (sendMask & (1ULL << c)) {
>         NCCLCHECKGOTO(selectTransport<1>(comm, graph, sendData[p] + sendChannels++, c, sendPeer, connIndex, &type), ret,
>                       fail);
>       }
>     }

## nccl-tree

URL: https://api.github.com/repos/NVIDIA/nccl/git/trees/v2.32.3-1?recursive=1

Retrieved UTC: 2026-10-28T06:43:52.918061+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: v2.32.3-1 tagged code; live user guide separately identified as retrieval snapshot

Raw SHA-256: ead2be687c8d61e5dbf2607fb12042e3a1bd7394e2b3391d632699478378bbc8

Local text: evidence/nccl-tree.txt

Lines 1–1 (sha):

> {"sha":"12df1a11afad322be5a204a2db890161cbf8131d","url":"https://api.github.com/repos/NVIDIA/nccl/git/trees/12df1a11afad322be5a204a2db890161cbf8131d","tree":[{"path":".clang-format","mode":"100644","type":"blob","sha":"2304064a026531d282373236ad4d0a1f552122fd","size":3514,"url":"https://api.github.com/repos/NVIDIA/nccl/git/blobs/2304064a026531d282373236ad4d0a1f552122fd"},{"path":".clang-format-ignore","mode":"100644","type":"blob","sha":"e63d980857e63c3f988281096d500f665ef9167a","size":537,"url":"https://api.github.com/repos/NVIDIA/nccl/git/blobs/e63d980857e63c3f988281096d500f665ef9167a"},{"path":".git-blame-ignore-revs","mode":"100644","type":"blob","sha":"12cb33e75fab86b407d043437956598af5d1a649","size":1851,"url":"https://api.github.com/repos/NVIDIA/nccl/git/blobs/12cb33e75fab86b407d043437956598af5d1a649"},{"path":".github","mode":"040000","type":"tree","sha":"7745fab9786034a99d8a045c01e00d3425371f98","url":"https://api.github.com/repos/NVIDIA/nccl/git/trees/7745fab9786034a99d8a045c01

## nccl-troubleshoot

URL: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting.html

Retrieved UTC: 2026-10-28T06:41:56.162336+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: v2.32.3-1 tagged code; live user guide separately identified as retrieval snapshot

Raw SHA-256: 02c0d65f062a7aea7e7172ed8ee164a8ff2562178372d9047613ff8f5eb8539f

Local text: evidence/nccl-troubleshoot.txt

Lines 608–612 (nccl):

> Logging covers NCCL logging levels, subsystem filters, output files, and timestamps.
> RAS covers NCCL’s built-in RAS subsystem for diagnosing hangs and crashes.
> Previous
> Next
> © Copyright 2020-2026, NVIDIA Corporation.

## oneccl-api-code

URL: https://raw.githubusercontent.com/uxlfoundation/oneCCL/2022.1.0/src/api.cpp

Retrieved UTC: 2026-10-28T07:17:31.925609+00:00

Release/publication timestamp: 2026-08-15T12:16:14Z; GitHub published_at from fetched release metadata, not necessarily documentation publication date.

Scope: 2022.1.0 tagged C API/plugin/code; legacy env docs separately scoped

Raw SHA-256: 98beedfd03353152fa58e5c5c9fff4d693b3675836f162e3a0f7d8640544cdd4

Local text: evidence/oneccl-api-code.txt

Lines 67–71 (onecclPluginException):

>         ONECCL_ERROR("[%s] caught std::exception: %s", func_name, ex.what());
>         return onecclPluginException;
>     } catch (...) {
>         ONECCL_ERROR("[%s] caught unknown exception", func_name);
>         return onecclPluginException;

Lines 735–739 (Plugin does not implement onecclCommAbort):

>     if (comm->abort == nullptr) {
>         ONECCL_WARN("Plugin does not implement onecclCommAbort");
>         return onecclNotImplemented;
>     }
>     return SAFE_CALL([=] { return comm->abort(comm); });

Lines 723–727 (Plugin does not implement onecclCommFinalize):

>     if (comm->finalize == nullptr) {
>         ONECCL_WARN("Plugin does not implement onecclCommFinalize");
>         return onecclNotImplemented;
>     }
>     return SAFE_CALL([=] { return comm->finalize(comm); });

## oneccl-atl-mpi

URL: https://raw.githubusercontent.com/uxlfoundation/oneCCL/2022.1.0/deps/libccl/src/atl/mpi/atl_mpi.cpp

Retrieved UTC: 2026-10-28T06:43:13.137815+00:00

Release/publication timestamp: 2026-08-15T12:16:14Z; GitHub published_at from fetched release metadata, not necessarily documentation publication date.

Scope: 2022.1.0 tagged C API/plugin/code; legacy env docs separately scoped

Raw SHA-256: 7c28f9d33431bcb2258754c05727e89df72db4dbc50e07821e78b0de5f105108

Local text: evidence/oneccl-atl-mpi.txt

Lines 270–274 (MPI_Allreduce):

>     if (ctx.sync_coll) {
>         ret = MPI_Allreduce_c((send_buf && (send_buf == recv_buf)) ? MPI_IN_PLACE : send_buf,
>                               recv_buf,
>                               len,
>                               mpi_dtype,

Lines 55–59 (MPI_Init):

> 
>     MPI_Initialized(&ctx.is_external_init);
>     if (!ctx.is_external_init) {
>         ret = MPI_Init_thread(argc, argv, required_thread_level, &provided_thread_level);
>         if (provided_thread_level < required_thread_level) {

## oneccl-atl-ofi

URL: https://raw.githubusercontent.com/uxlfoundation/oneCCL/2022.1.0/deps/libccl/src/atl/ofi/atl_ofi.cpp

Retrieved UTC: 2026-10-28T06:43:13.141229+00:00

Release/publication timestamp: 2026-08-15T12:16:14Z; GitHub published_at from fetched release metadata, not necessarily documentation publication date.

Scope: 2022.1.0 tagged C API/plugin/code; legacy env docs separately scoped

Raw SHA-256: 5f9031bd4cacf474bf978e2f34d2690be0c61cb9dfcc5775e8fd3f6f479904a5

Local text: evidence/oneccl-atl-ofi.txt

Lines 62–66 (fi_):

> 
>     struct fi_info* base_hints = nullptr;
>     int fi_version;
>     ssize_t ret = 0;
>     size_t idx = 0, ep_idx = 0;

## oneccl-env

URL: https://uxlfoundation.github.io/oneCCL/env-variables.html

Retrieved UTC: 2026-10-28T06:42:17.144437+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: Live legacy C++ API environment documentation; not universal v2 plugin defaults

Raw SHA-256: f1673964d39bad4203e96f42faffd489db5555f4911a329fa65d1dc215bf7fa1

Local text: evidence/oneccl-env.txt

Lines 940–944 (CCL_ATL_TRANSPORT=mpi):

> Description
> Set the CCL_KVS_MODE environment variable to choose the key-value store mechanism used during communicator creation. For the MPI-based transport (CCL_ATL_TRANSPORT=mpi), use mpi. For large-scale runs with the OFI transport and PMIx (CCL_ATL_TRANSPORT=ofi and CCL_PROCESS_LAUNCHER=pmix), we recommend using pmix_ofi or pmix_ofi_shm. The pmix_ofi modes bypass the default KVS layer in favor of the PMIx operations (put/get/fence/commit) and can yield performance benefits, especially at scale.
> ATL#
> The group of environment variables to control ATL (abstract transport layer).
> CCL_ATL_TRANSPORT#

Lines 967–971 (actual HMEM support):

> Set this environment variable to enable handling of HMEM/GPU buffers by the transport layer.
> The actual HMEM support depends on the limitations on the transport level and system configuration.
> CCL_ATL_SHM#
> Syntax
> CCL_ATL_SHM=<value>

## oneccl-header

URL: https://raw.githubusercontent.com/uxlfoundation/oneCCL/2022.1.0/include/oneapi/ccl.h

Retrieved UTC: 2026-10-28T06:43:13.136778+00:00

Release/publication timestamp: 2026-08-15T12:16:14Z; GitHub published_at from fetched release metadata, not necessarily documentation publication date.

Scope: 2022.1.0 tagged C API/plugin/code; legacy env docs separately scoped

Raw SHA-256: 52801e7b9a83398ef7db8adc68f7b045007a626477c44fde721393a778eda5bf

Local text: evidence/oneccl-header.txt

Lines 480–484 (onecclAllReduce):

>  */
> onecclResult_t CCL_C_API onecclAllReduce(void *sendbuff, void *recvbuff,
>                                         size_t count, onecclDataType_t datatype,
>                                         onecclRedOp_t reduction_op,
>                                         onecclComm_t comm, void *stream);

## oneccl-legacy-plugin

URL: https://raw.githubusercontent.com/uxlfoundation/oneCCL/2022.1.0/plugins/legacy/ccl_legacy.cpp

Retrieved UTC: 2026-10-28T06:43:13.132691+00:00

Release/publication timestamp: 2026-08-15T12:16:14Z; GitHub published_at from fetched release metadata, not necessarily documentation publication date.

Scope: 2022.1.0 tagged C API/plugin/code; legacy env docs separately scoped

Raw SHA-256: 8bf742c88d41d1081b27a633fc547cda722873fbb2c7b69711ea7deaf9a32738

Local text: evidence/oneccl-legacy-plugin.txt

Lines 214–218 (queue->is_in_order):

> 
>     if (!queue->is_in_order()) {
>         ONECCL_ERROR(
>             "oneCCL collective was called using out of order queue which is "
>             "not supported! Please use in order queues for correct results "

Lines 207–211 (event.wait):

>         auto event = cpu_collective(comm_legacy);
>         event.wait();
> 
>         return onecclSuccess;
>     }

Lines 271–275 (ccl::allreduce):

>         [=](CommunicatorLegacy *comm_legacy, sycl::queue *sycl_ext) {
>             auto attrs = ccl::create_operation_attr<ccl::allreduce_attr>();
> 
>             static itt::Task allreduce_s("CPU::AllReduce::Submit");

## oneccl-plugin-doc

URL: https://raw.githubusercontent.com/uxlfoundation/oneCCL/2022.1.0/docs/config/plugins.md

Retrieved UTC: 2026-10-28T06:43:52.826665+00:00

Release/publication timestamp: 2026-08-15T12:16:14Z; GitHub published_at from fetched release metadata, not necessarily documentation publication date.

Scope: File fetched at tag2022.1.0 but contains inherited2021.17/2025.3 release wording; implementation code overrides stale defaults

Raw SHA-256: 05471f219f846fc9e13a6eac58f4c57d25cca75742808332a1bbafd4190e5e42

Local text: evidence/oneccl-plugin-doc.txt

Lines 1–4 (plugin):

> # Plugin architecture
> 
> ```{eval-rst}
> .. note::

Lines 9–13 (legacy):

> 
> Alongside introduction of new API for oneCCL we introduced a concept of oneCCL plugins. The plugin interface was designed to provide dynamic selection of backends for different hardware platforms. Currently oneCCL provides two plugins - `onecclLegacy` and `onecclLegacyCpu`, which are based on `libccl.so.1.0` and provide the same functional capabilities. On startup oneCCL will load the most appropriate plugin unless user specifies [`CCL_PLUGIN`](project:./env.md#ccl-plugin) environment variable to override it.
> 
> ## Plugins and their features
>  * `onecclLegacy` - supports both CPU and GPU collectives, selected by default if `libsycl.so.8` is available on the platform. The plugin will select CPU or GPU backend on following conditions:

## oneccl-release

URL: https://api.github.com/repos/uxlfoundation/oneCCL/releases/latest

Retrieved UTC: 2026-10-28T06:41:56.327241+00:00

Release/publication timestamp: 2026-08-15T12:16:14Z; GitHub published_at from fetched release metadata, not necessarily documentation publication date.

Scope: 2022.1.0 tagged C API/plugin/code; legacy env docs separately scoped

Raw SHA-256: 9279a1e029dd2063d34977576adc678098c6e9fb520bf284114a696754f9cb0b

Local text: evidence/oneccl-release.txt

Lines 1–1 (published_at):

> PI Collective Communications Library (oneCCL) 2022.1.0","draft":false,"immutable":false,"prerelease":false,"created_at":"2026-07-22T09:14:15Z","updated_at":"2026-08-15T12:16:14Z","published_at":"2026-08-15T12:16:14Z","assets":[],"tarball_url":"https://api.github.com/repos/uxlfoundation/oneCCL/tarball/2022.1.0","zipball_url":"https://api.github.com/repos/uxlfoundation/oneCCL/zipball/2022.1.0","body":"What's New oneCCL 2022.1 \r\n\r\n- Fixed a potential invalid memory access in alltoall\r\n- Improved custom reductions for Battlemage \r\n- Improving concurrent insertion to shared resources\r\n- get_last_event no longer returns the runtime's stored last event\r\n- Added a support for custom pre-operations in allreduce and reduce-scatter\r\n- Correctly handle unaligned user buffers in allreduce, alltoall, reduce-scatter and allgatherv\r\n- Use GPU_RDMA for pt2pt when supported\r\n- Get scaleout_host_buff in a deterministic manner \r\n","reactions":{"url":"https://api.github.com/repos/uxlfoundation/oneCCL/releases/371041700/reactions","total_count":2,"+1":2,"-1":0,"laugh":0,"hooray":0,"confused":0,"heart":0,"rocket":0,"eyes":0}}

Lines 1–1 (tag_name):

> rivacy}","received_events_url":"https://api.github.com/users/pmeltsin/received_events","type":"User","user_view_type":"public","site_admin":false},"node_id":"RE_kwDODFzcOs4WHaWk","tag_name":"2022.1.0","target_commitish":"master-v2","name":"Intel(R) oneAPI Collective Communications Library (oneCCL) 2022.1.0","draft":false,"immutable":false,"prerelease":false,"created_at":"2026-07-22T09:14:15Z","updated_at":"2026-08-15T12:16:14Z","published_at":"2026-08-15T12:16:14Z","assets":[],"tarball_url":"https://api.github.com/repos/uxlfoundation/oneCCL/tarball/2022.1.0","zipball_url":"https://api.github.com/repos/uxlfoundation/oneCCL/zipball/2022.1.0","body":"What's New oneCCL 2022.1 \r\n\r\n- Fixed a potential invalid memory access in alltoall\r\n- Improved custom reductions for Battlemage \r\n- Improving concurrent insertion to shared resources\r\n- get_last_event no longer returns the runtime's stored last event\r\n- Added a support for custom pre-operations in allreduce and reduce-scatter\r\n- Correctly handle unaligned user buffers in allreduce, alltoall, reduce-scatter and allgatherv\r\n- Use GPU_RDMA for pt2pt when supported\r\n- Get scaleout_host_buff in a determini

## oneccl-repo

URL: https://api.github.com/repos/uxlfoundation/oneCCL

Retrieved UTC: 2026-10-28T06:41:56.161648+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: 2022.1.0 tagged C API/plugin/code; legacy env docs separately scoped

Raw SHA-256: 71b3bbe109ddcd94aa7f355c8cd1544ea52bc4aa568794b0033a92b0ff4f40c8

Local text: evidence/oneccl-repo.txt

Lines 1–1 (default_branch):

> olicy":"all","topics":["ai-machine-learning","ai-training","deep-learning","libraries","oneapi","swrepo","sycl"],"visibility":"public","forks":108,"open_issues":38,"watchers":272,"default_branch":"master-v2","temp_clone_token":null,"custom_properties":{},"organization":{"login":"uxlfoundation","id":144704571,"node_id":"O_kgDOCKAEOw","avatar_url":"https://avatars.githubusercontent.com/u/144704571?v=4","gravatar_id":"","url":"https://api.github.com/users/uxlfoundation","html_url":"https://github.com/uxlfoundation","followers_url":"https://api.github.com/users/uxlfoundation/followers","following_url":"https://api.github.com/users/uxlfoundation/following{/other_user}","gists_url":"https://api.github.com/users/uxlfoundation/gists{/gist_id}","starred_url":"https://api.github.com/users/uxlfoundation/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/uxlfoundation/subscriptions","organizations_url":"https://api.github.com/users/uxlfoundation/orgs","repos_url":"https://api.github.com/users/uxlfoundation/repos","events_url":"https://api.github.com/users/uxlfoundation/events{/privacy}","received_events_url":"https://api.github.com/users/uxlfoundation

Lines 1–1 (archived):

> unt":272,"language":"C++","has_issues":true,"has_projects":true,"has_downloads":false,"has_wiki":true,"has_pages":true,"has_discussions":false,"forks_count":108,"mirror_url":null,"archived":false,"disabled":false,"open_issues_count":38,"license":{"key":"other","name":"Other","spdx_id":"NOASSERTION","url":null,"node_id":"MDc6TGljZW5zZTA="},"allow_forking":true,"is_template":false,"web_commit_signoff_required":false,"has_pull_requests":true,"pull_request_creation_policy":"all","topics":["ai-machine-learning","ai-training","deep-learning","libraries","oneapi","swrepo","sycl"],"visibility":"public","forks":108,"open_issues":38,"watchers":272,"default_branch":"master-v2","temp_clone_token":null,"custom_properties":{},"organization":{"login":"uxlfoundation","id":144704571,"node_id":"O_kgDOCKAEOw","avatar_url":"https://avatars.githubusercontent.com/u/144704571?v=4","gravatar_id":"","url":"https://api.github.com/users/uxlfoundation","html_url":"https://github.com/uxlfoundation","followers_url":"https://api.github.com/users/uxlfoundation/followers","following_url":"https://api.github.com/users/uxlfoundation/following{/other_user}","gists_url":"https://api.github.com/user

## oneccl-v2-example

URL: https://uxlfoundation.github.io/oneCCL/v2/examples.html

Retrieved UTC: 2026-10-28T06:42:17.141039+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: Live v2 example page identifies itself as C API2021.17.0; not a2022.1.0 release matrix

Raw SHA-256: 7fd9fcf8a36b06feb4575b22d00da12e42cf3e5d36928014d8831dce50cd3b2c

Local text: evidence/oneccl-v2-example.txt

Lines 111–115 (onecclAllReduce):

> 7. Perform a Collective Operation#
> Execute onecclAllReduce to sum data across ranks.
> Pass a pointer to the SYCL queue as the last argument of the collective operation to ensure proper scheduling of the operation.
> result = onecclAllReduce(
> sendbuff, recvbuff, kCount, onecclInt, onecclSum, comm, &sycl_queue);

## oneccl-v2-readme

URL: https://raw.githubusercontent.com/uxlfoundation/oneCCL/2022.1.0/README.md

Retrieved UTC: 2026-10-28T06:42:16.885573+00:00

Release/publication timestamp: 2026-08-15T12:16:14Z; GitHub published_at from fetched release metadata, not necessarily documentation publication date.

Scope: 2022.1.0 tagged C API/plugin/code; legacy env docs separately scoped

Raw SHA-256: ce4c1b215df638cbc8eaa215f9721f23682cd2bd0c7e193d63a312b37a3f4858

Local text: evidence/oneccl-v2-readme.txt

Lines 111–115 (plugin based architecture):

> 
> C API version of oneCCL introduced a new plugin based architecture. Running examples or tests might require adjusting `LD_LIBRARY_PATH`, so it points to at least one directory with correct plugin. It can be done using `vars.sh` script or manually like `export LD_LIBRARY_PATH=<build_dir>/plugins/legacy/:$LD_LIBRARY_PATH`, so test binaries linking to `libccl.so.2` through **RUNPATH** can still discover required plugin. 
> 
> You can also use **CCL_PLUGIN** environment variable to set name of the plugin (`ONECCL_LEGACY`/`ONECCL_LEGACY_CPU`/`ONECCL_NULL`) or a whole path to a shared object implementing oneCCL plugin interface (`<build_dir>/plugins/legacy/libccl_legacy.so`).

Lines 113–117 (CCL_PLUGIN):

> 
> You can also use **CCL_PLUGIN** environment variable to set name of the plugin (`ONECCL_LEGACY`/`ONECCL_LEGACY_CPU`/`ONECCL_NULL`) or a whole path to a shared object implementing oneCCL plugin interface (`<build_dir>/plugins/legacy/libccl_legacy.so`).
> 
> ## Governance

## openmpi-cuda

URL: https://docs.open-mpi.org/en/v5.0.x/tuning-apps/networking/cuda.html

Retrieved UTC: 2026-10-28T06:41:56.966846+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: v5.0.x documentation path; not a current-latest release assertion

Raw SHA-256: 7c2c7cbdad53a7627cf0133200cb0cc9312995f4358d25490a4b4a2af636dcbb

Local text: evidence/openmpi-cuda.txt

Lines 434–438 (All non-blocking reduction):

> All window creation calls such as MPI_Win_create
> All non-blocking reduction collectives like MPI_Ireduce,
> MPI_Iallreduce, etc
> 11.2.6.16. Can I tell at compile time or runtime whether I have CUDA-aware support?
> There is both a compile time check and a run-time check available.

Lines 336–340 (MPI_Allreduce):

> MPI_Allgatherv
> MPI_Allreduce
> MPI_Alltoall
> MPI_Alltoallv
> MPI_Alltoallw

Lines 167–171 (GPUDirect):

> MPI, it is recommended to set PSM2_CUDA to 0 in the execution
> environment. PSM2 also has support for the NVIDIA GPUDirect support
> feature. To enable this, users will need to set PSM2_GPUDIRECT
> to 1 in the execution environment.
> Note: The PSM2 library and hfi1 driver with CUDA support are requirements

## rccl

URL: https://raw.githubusercontent.com/ROCm/rccl/develop/README.md

Retrieved UTC: 2026-10-28T06:42:17.385795+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: develop branch retrieval snapshot; not a release capability matrix

Raw SHA-256: 0e79bfe1ec028f9211ed52f2592e05eed4401931dc3a1188dd4ad7ef9bd7fbd9

Local text: evidence/rccl.txt

Lines 27–31 (HIP runtime):

> 1. ROCm supported GPUs
> 2. ROCm stack installed on the system (HIP runtime & HIP-Clang)
> 
> ## Quickstart RCCL Build

Lines 2–6 (collective):

> 
> ROCm Communication Collectives Library
> 
> [![RCCL](https://dev.azure.com/ROCm-CI/ROCm-CI/_apis/build/status%2Frccl?repoName=ROCm%2Frccl&branchName=develop)](https://dev.azure.com/ROCm-CI/ROCm-CI/_build/latest?definitionId=107&repoName=ROCm%2Frccl&branchName=develop)
> [![TheRock CI](https://github.com/ROCm/rccl/actions/workflows/therock-ci.yml/badge.svg?branch=develop&event=push)](https://github.com/ROCm/rccl/actions/workflows/therock-ci.yml)

## torch-ccl

URL: https://raw.githubusercontent.com/intel/torch-ccl/master/README.md

Retrieved UTC: 2026-10-28T06:41:56.401804+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: Fetched current documentation/metadata; publication date not established

Raw SHA-256: bafb4fe8d2cc5e95064624de72f99ba1090e412763b2a6d40bbf54b4f210176b

Local text: evidence/torch-ccl.txt

Lines 1–4 (THIS PROJECT IS ARCHIVED):

> ## THIS PROJECT IS ARCHIVED
> 
> Intel will not provide or guarantee development of or support for this project, including but not limited to, maintenance, bug fixes, new releases or updates. 
> Patches to this project are no longer accepted by Intel.  

Lines 8–12 (DEPRECATED):

> 
> **NOTE**: This repo has been **DEPRECATED**. Please use [PyTorch*](https://github.com/pytorch/pytorch) directly for distributed scenarios. We remain committed to providing robust support and high performance through PyTorch* for Intel® CPU and GPU platforms.
> 
> ===========================================================================

## torch-fsdp

URL: https://raw.githubusercontent.com/pytorch/pytorch/v2.9.0/torch/distributed/fsdp/_fully_shard/_fully_shard.py

Retrieved UTC: 2026-10-28T06:44:16.727882+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: PyTorch v2.9.0 tagged fully_shard.py

Raw SHA-256: 67a078d2a02423415f362891e3d4e23707aebe68099b5b822894d467620e0bee

Local text: evidence/torch-fsdp.txt

Lines 101–105 (all-gather):

>     At initialization, FSDP shards the module's parameters across the data
>     parallel workers given by ``mesh``. Before forward, FSDP all-gathers the
>     sharded parameters across the data-parallel workers to get the unsharded
>     parameters for forward computation. If ``reshard_after_forward`` is
>     ``True``, then FSDP frees the unsharded parameters after forward and

Lines 106–110 (reduce-scatter):

>     re-all-gathers them in backward before gradient computation. After gradient
>     computation, FSDP frees the unsharded parameters and reduce-scatters the
>     unsharded gradients across data-parallel workers.
> 
>     This implementation represents the sharded parameters as :class:`DTensor` s

## torch-v29-doc

URL: https://raw.githubusercontent.com/pytorch/pytorch/v2.9.0/docs/source/distributed.md

Retrieved UTC: 2026-10-28T06:43:52.820169+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: PyTorch v2.9.0 tagged distributed.md

Raw SHA-256: 4a0be0e435c4151ed89f67d02cec6208702718e85650d2c5566fa618e25bd08e

Local text: evidence/torch-v29-doc.txt

Lines 86–90 (Use the XCCL backend):

>   - Use the NCCL backend for distributed training with CUDA **GPU**.
>   - Use the XCCL backend for distributed training with XPU **GPU**.
>   - Use the Gloo backend for distributed training with **CPU**.
> 
> - GPU hosts with InfiniBand interconnect

Lines 133–137 (NCCL_DEBUG_SUBSYS):

> 
> You may also use `NCCL_DEBUG_SUBSYS` to get more details about a specific
> aspect of NCCL. For example, `NCCL_DEBUG_SUBSYS=COLL` would print logs of
> collective calls, which may be helpful when debugging hangs, especially those
> caused by collective type or message size mismatch. In case of topology

## torch-xccl-code

URL: https://raw.githubusercontent.com/intel/torch-xpu-ops/73a6552c3c122614d2651de2a0c6feb8f81ae613/src/xccl/ProcessGroupXCCL.cpp

Retrieved UTC: 2026-10-28T06:43:52.841543+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: torch-xpu-ops commit73a6552c3c122614d2651de2a0c6feb8f81ae613; development code, not wheel certification

Raw SHA-256: a666e398b2cc4b5f0bb37d3864b4066c574bb38ba7aebfac41e41edf892b85ab

Local text: evidence/torch-xccl-code.txt

Lines 557–561 (onecclComm_t):

> 
> std::shared_ptr<onecclComm_t> ProcessGroupXCCL::getXCCLComm(
>     const std::string& deviceKey) {
>   std::lock_guard<std::mutex> lock(mutex_);
>   auto it = devXCCLCommMap_.find(deviceKey);

Lines 1616–1620 (xccl::onecclAllGather):

>             at::xpu::XPUStream& stream) {
>           xccl::onecclAllGather(input, output, comm, stream);
>           return;
>         },
>         [](at::xpu::XPUStream&,

## ucc

URL: https://raw.githubusercontent.com/openucx/ucc/master/README.md

Retrieved UTC: 2026-10-28T06:42:17.447294+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: master branch retrieval snapshot

Raw SHA-256: dbea43b59bfabb67c894578d571857635e1751cedf229964f39979b2f8a42739

Local text: evidence/ucc.txt

Lines 69–73 (Open MPI and UCC):

> 
> ### Open MPI and UCC collectives
> 
> #### Compile UCX 
> ```sh

Lines 43–47 (CUDA collectives):

> * [CUDA](https://developer.nvidia.com/cuda-toolkit) (optional)
>    * UCC supports CUDA collectives. To compile with CUDA support, install
>      [NVIDIA CUDA](https://developer.nvidia.com/cuda-downloads) 11.0 or above.
> 
> * [HIP](https://rocmdocs.amd.com/en/latest/Programming_Guides/HIP-GUIDE.html) (optional)

## xccl2-rfc

URL: https://api.github.com/repos/pytorch/pytorch/issues/194761

Retrieved UTC: 2026-10-28T06:42:50.066829+00:00

Release/publication timestamp: not established; Retrieval time is not publication time.

Scope: issue194761 RFC; proposal status, not released behavior

Raw SHA-256: 05d5e6d1ab7ee20e65464bbc69bab3f52367d92b1e5988579b692b09ba5b522b

Local text: evidence/xccl2-rfc.txt

Lines 1–1 (XCCL):

> ues/194761/events","html_url":"https://github.com/pytorch/pytorch/issues/194761","id":5248887671,"node_id":"I_kwDOA-j9z88AAAABONurdw","number":194761,"title":"[draft][RFC] Add the xccl2 PrcoessGroup Backend for XPU","user":{"login":"frost-intel","id":121894376,"node_id":"U_kgDOB0P16A","avatar_url":"https://avatars.githubusercontent.com/u/121894376?v=4","gravatar_id":"","url":"https://api.github.com/users/frost-intel","html_url":"https://github.com/frost-intel","followers_url":"https://api.github.com/users/frost-intel/followers","following_url":"https://api.github.com/users/frost-intel/following{/other_user}","gists_url":"https://api.github.com/users/frost-intel/gists{/gist_id}","starred_url":"https://api.github.com/users/frost-intel/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/frost-intel/subscriptions","organizations_url":"https://api.github.com/users/frost-intel/orgs","repos_url":"https://api.github.com/users/frost-intel/repos","events_url":"https://api.github.com/users/frost-intel/events{/privacy}","received_events_url":"https://api.github.com/users/frost-intel/received_events","type":"User","user_view_type":"public","site_admin":

Lines 1–1 (RFC):

> h/pytorch/issues/194761/events","html_url":"https://github.com/pytorch/pytorch/issues/194761","id":5248887671,"node_id":"I_kwDOA-j9z88AAAABONurdw","number":194761,"title":"[draft][RFC] Add the xccl2 PrcoessGroup Backend for XPU","user":{"login":"frost-intel","id":121894376,"node_id":"U_kgDOB0P16A","avatar_url":"https://avatars.githubusercontent.com/u/121894376?v=4","gravatar_id":"","url":"https://api.github.com/users/frost-intel","html_url":"https://github.com/frost-intel","followers_url":"https://api.github.com/users/frost-intel/followers","following_url":"https://api.github.com/users/frost-intel/following{/other_user}","gists_url":"https://api.github.com/users/frost-intel/gists{/gist_id}","starred_url":"https://api.github.com/users/frost-intel/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/frost-intel/subscriptions","organizations_url":"https://api.github.com/users/frost-intel/orgs","repos_url":"https://api.github.com/users/frost-intel/repos","events_url":"https://api.github.com/users/frost-intel/events{/privacy}","received_events_url":"https://api.github.com/users/frost-intel/received_events","type":"User","user_view_type":"public",

