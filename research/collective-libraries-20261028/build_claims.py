"""Build machine-readable claims and a fetched-source catalog, task-local only.
This records evidence and scope, not deployment performance verification.
"""
from pathlib import Path
import datetime
import hashlib
import json
import re
import pymupdf

ROOT=Path(__file__).resolve().parent
records=json.loads((ROOT/'retrieval.json').read_text())
success={r['name']:r for r in records if 'error' not in r}

# Statements are authored; source records and quotations are read from fetched files.
# Status distinguishes documented capability, inspected code, and CPU-only derivation.
DATA=[
('CCL-001','Collective semantics specify result distribution, not a particular algorithm or fabric. The seven-operation table is scoped to one intracommunicator.','DOCUMENTED',['mpi50-pdf'],['CCL-T1']),
('CCL-002','All-reduce SUM is not intrinsically averaging; NCCL has a separately selected ncclAvg operation.','DOCUMENTED_AND_CODE_INSPECTED',['mpi50-pdf','nccl-api-header'],['CCL-T1']),
('CCL-003','Group, root, dtype/count/type signature, ordering and layout form a contract; MPI has derived datatypes and variable-count forms beyond equal-shaped tensors.','DOCUMENTED',['mpi50-pdf','nccl-api-header','oneccl-header'],['CCL-T1']),
('CCL-004','Floating-point reduction reordering can change bits. A fixed seed or mathematical SUM does not establish cross-version bitwise reproducibility.','DOCUMENTED_AND_CPU_EXAMPLE',['mpi50-pdf'],['CCL-T1']),
('CCL-005','Barrier is participant synchronization, not automatic completion of arbitrary GPU streams or outstanding operations.','DOCUMENTED_SCOPE',['mpi50-pdf'],['CCL-T1']),
('CCL-006','An all-reduce can be decomposed into reduce-scatter of corresponding elements followed by all-gather of the reduced shards; all-gather alone is not reduction.','DOCUMENTED_AND_CPU_DERIVED',['mpi50-pdf','nccl-performance'],['CCL-T1']),
('CCL-007','Balanced point-to-point ring sends 2(N-1)M/N per rank and receives the same amount. M=8 B,N=4 gives sent12 B,received12 B; M=140 GB,N=8 gives sent245 GB,received245 GB.','CPU_DERIVED',['nccl-performance'],['CCL-T1','CCL-T3']),
('CCL-008','nccl-tests algbw is size/time; busbw is collective-specific normalization, not a physical-link byte counter. All-gather and reduce-scatter use a full-array-size convention.','DOCUMENTED',['nccl-performance'],['CCL-T3','CCL-T6']),
('CCL-009','MPI is a standard; its interfaces include nonblocking and persistent collectives, with requests and completion rules.','DOCUMENTED',['mpi50-pdf'],['CCL-T2']),
('CCL-010','Open MPI v5.0.x documents CUDA device-buffer support and path-specific limitations, including unsupported nonblocking reduction collectives on the documented CUDA-aware UCX path.','DOCUMENTED_NOT_EXECUTED',['openmpi-cuda'],['CCL-T2']),
('CCL-011','MPICH v5.0.2 README documents CUDA, HIP and Level Zero configuration support, not all operation/provider/GPU combinations.','TAGGED_DOCUMENTATION_NOT_EXECUTED',['mpich-v502','mpich-release'],['CCL-T2']),
('CCL-012','MPI5 progress semantics require correct programs to tolerate weak progress; nonblocking submission is not proof of effective autonomous overlap.','DOCUMENTED',['mpi50-pdf'],['CCL-T2']),
('CCL-013','NCCL host stream submission is distinct from device completion and cross-stream result availability.','DOCUMENTED',['nccl-streams','nccl-init'],['CCL-T2']),
('CCL-014','NCCL official MPI example uses MPI for setup/ID distribution and NCCL for tensor all-reduce; launcher choice does not identify payload transport.','EXAMPLE_CODE_INSPECTED',['nccl-example-mpi','nccl-init'],['CCL-T2']),
('CCL-015','NCCL v2.32.3-1 contains topology discovery, graph search, transport selection and algorithm/protocol cost modeling, rather than a fixed ring-only implementation.','TAGGED_CODE_INSPECTED',['nccl-topo-code','nccl-search-code','nccl-transport-code','nccl-cost-model','nccl-ring-code'],['CCL-T2','CCL-T4']),
('CCL-016','NCCL includes CPU proxy code for eligible transport progress; communication may consume host and accelerator resources.','TAGGED_CODE_INSPECTED',['nccl-proxy-code'],['CCL-T2','CCL-T7d']),
('CCL-017','Current official NCCL guide describes a device API introduced in2.28 with capability-dependent local and network paths; no exhaustive hardware support certification was performed.','CURRENT_DOCUMENTATION_NOT_EXECUTED',['nccl-device-guide','nccl-device'],['CCL-T4']),
('CCL-018','NCCL asynchronous error/progress queries do not substitute for stream completion; failed communicators invalidate assumptions about enqueued operation correctness.','DOCUMENTED',['nccl-init','nccl-api-header'],['CCL-T6']),
('CCL-019','oneCCL API metadata at retrieval: archived=false,default_branch=master-v2; latest GitHub release2022.1.0 was published2026-08-15, not in year2022.','FETCHED_RELEASE_AND_REPOSITORY_METADATA',['oneccl-repo','oneccl-release'],['CCL-T4']),
('CCL-020','oneCCL2022.1.0 exposes a C API and plugin architecture, with a legacy plugin connecting to libccl and SYCL queue paths.','TAGGED_CODE_AND_DOCUMENTATION',['oneccl-header','oneccl-v2-readme','oneccl-legacy-plugin','oneccl-plugin-doc','oneccl-v2-example'],['CCL-T4']),
('CCL-021','Inspected oneCCL legacy queue path requires in-order SYCL queues; CPU/null-stream and some configured paths wait. No blanket all-path asynchronous claim is made.','TAGGED_CODE_INSPECTED',['oneccl-legacy-plugin'],['CCL-T4']),
('CCL-022','oneCCL2022.1.0 contains MPI and OFI transports; legacy env documentation makes heterogeneous-memory support dependent on transport and configuration.','TAGGED_CODE_AND_SCOPED_LEGACY_DOCUMENTATION',['oneccl-atl-mpi','oneccl-atl-ofi','oneccl-env'],['CCL-T2','CCL-T4']),
('CCL-023','Archived/deprecated torch-ccl bindings are distinct from the active oneCCL repository; PyTorchv2.9.0 docs name xccl for XPU, and pinned torch-xpu-ops code uses onecclComm_t.','DOCUMENTATION_AND_PINNED_CODE',['torch-ccl','torch-v29-doc','torch-xccl-code'],['CCL-T4']),
('CCL-024','A PyTorch RFC is not release evidence for a successor or ABI migration. Standalone intel/xccl endpoint fetch failed404; no successor-library status is asserted.','PROPOSAL_ONLY_AND_UNRESOLVED',['xccl2-rfc'],['CCL-T4']),
('CCL-025','NCCL online docs name ring/tree/LL/LL128/Simple and NVLS/NVLSTree SHARP offload. Point-to-point ring byte bounds are not universal offloaded-collective bounds.','DOCUMENTED_WITH_MECHANISM_LIMIT',['nccl-env','nccl-performance','nccl-cost-model'],['CCL-T2','CCL-T3']),
('CCL-026','H100 SXM900 GB/s is total bidirectional per-GPU NVLink nominal bandwidth, not450 GB/s each link or topology bisection. SXM80 GB does not fit a140 GB buffer.','VENDOR_SPECIFICATION_AND_CPU_DERIVATION',['h100-datasheet'],['CCL-T3']),
('CCL-027','Frozen physical141/printed123 divides245 GB send traffic by900 GB/s bidirectional; within its ring assumptions correct byte term is245/450=490/900=0.54444s, not0.27222s.','FROZEN_PDF_VERIFIED_AND_CPU_DERIVED',['nccl-performance','h100-datasheet'],['CCL-T3']),
('CCL-028','Corrected ring comparisons at assumed40 and2.5 GB/s are6.125s and98s; ratios vs450 directional are11.25x and180x. A280 GB input gives490/450=1.08889s.','CPU_DERIVED',['nccl-performance','h100-datasheet'],['CCL-T3','CCL-T5b']),
('CCL-029','TP communicates activation partial results/layout fragments rather than re-fetching all resident weights each ordinary decode step.','IMPLEMENTATION_MECHANISM_AND_DERIVATION',['megatron-layers','megatron-mappings'],['CCL-T5']),
('CCL-030','Illustrative TP shape16x8192x2 B,8 ranks,2 allreduces/block,80blocks gives256 KiB logical/call,448 KiB sent/call and70 MiB sent per step, with equal receive volume.','CPU_DERIVED_NOT_BENCHMARKED',['nccl-performance','megatron-layers'],['CCL-T5']),
('CCL-031','Illustrative uniform EP256tokens/rank,top2,hidden8192,BF16,8ranks sends7 MiB dispatch and7 MiB combine per rank, excluding metadata/dedup/skew. DeepEP motivates specialized dispatch/combine paths, not a benchmark assertion here.','CPU_DERIVED_AND_IMPLEMENTATION_CONTEXT',['deepep'],['CCL-T5']),
('CCL-032','PyTorchv2.9 FSDP fully_shard doc explains parameter all-gather and gradient reduce-scatter. A64 MiB unit over8-way ring sends/receives56 MiB per phase; no universal optimizer-state movement is claimed.','TAGGED_DOCUMENTATION_AND_CPU_DERIVATION',['torch-fsdp','nccl-performance'],['CCL-T5']),
('CCL-033','RCCL illustrates ROCm/HIP collectives; UCC illustrates reusable collectives and Open MPI integration; Gloo library support differs from framework backend exposure. No cross-platform ranking is inferred.','CURRENT_REPOSITORY_DOCUMENTATION_NOT_EXECUTED',['rccl','ucc','gloo','torch-v29-doc'],['CCL-T4']),
('CCL-034','A fair protocol records feasible allocations, matching shape/type/group/timing, correctness and repeatability, selected path and service-level contention/tails; microbenchmark busbw alone cannot validate serving capacity.','PROPOSED_EVALUATION_PROTOCOL',['nccl-tests-readme','nccl-performance','openmpi-cuda','oneccl-v2-example','torch-v29-doc'],['CCL-T6','CCL-T7c']),
('CCL-035','Release metadata at retrieval identifies NCCLv2.32.3-1 published2026-09-17. This and MPICHv5.0.2 postdate the frozen2026-08-30 evidence cutoff and require a dated update, not silent historical attribution.','FETCHED_METADATA_AND_FROZEN_PDF',['nccl-release','mpich-release'],['CCL-T4']),
('CCL-036','KV ownership transfer, PP stage P2P, DP gradient sync and TP/EP groups have different payload/population/frequency; model-parallel group size is not total serving-fleet host count.','SCOPED_ARCHITECTURAL_SYNTHESIS',['megatron-mappings','megatron-layers','torch-fsdp','deepep'],['CCL-T5','CCL-T7b','CCL-T7e','CCL-T7f']),
('CCL-037','oneCCL2022.1.0 C wrapper converts caught exceptions into onecclPluginException and returns onecclNotImplemented when finalize/abort callbacks are absent. This conditional code does not establish which plugins lack callbacks or guarantee queue completion.','TAGGED_CODE_INSPECTED',['oneccl-api-code','oneccl-legacy-plugin'],['CCL-T4'])
]

NEEDLES={
'mpi50-pdf':['such as floating point addition','weak progress','The persistent collective operations'],
'nccl-api-header':['ncclAvg','ncclAlltoAll','ncclCommGetAsyncError'],
'nccl-performance':['2*(n-1)','point-to-point operations','sendcount*sizeof'],
'openmpi-cuda':['All non-blocking reduction','MPI_Allreduce','GPUDirect'],
'mpich-v502':['automatically detects','Level Zero'],
'nccl-streams':['enqueued','cudaStream'],
'nccl-init':['ncclCommGetAsyncError','until they are completed','uniqueId should'],
'nccl-example-mpi':['MPI_Bcast','ncclAllReduce'],
'nccl-topo-code':['ncclTopoGetSystem'],
'nccl-search-code':['ncclTopoCompute'],
'nccl-transport-code':['selectTransport'],
'nccl-cost-model':['NCCL_PROTO','NVLS'],
'nccl-ring-code':['runRing','directRecvReduceCopyDirectSend'],
'nccl-proxy-code':['ncclProxyProgress'],
'nccl-device-guide':['Starting with version 2.28','LSA (Load/Store Accessible)','GIN (GPU-Initiated Networking)'],
'nccl-device':['Device API','GIN'],
'oneccl-header':['Stream - SYCL','onecclAllReduce'],
'oneccl-v2-readme':['plugin based architecture','CCL_PLUGIN'],
'oneccl-legacy-plugin':['queue->is_in_order','event.wait','ccl::allreduce'],
'oneccl-plugin-doc':['plugin','legacy'],
'oneccl-v2-example':['onecclAllReduce'],
'oneccl-atl-mpi':['MPI_Allreduce','MPI_Init'],
'oneccl-atl-ofi':['fi_'],
'oneccl-api-code':['onecclPluginException','Plugin does not implement onecclCommAbort','Plugin does not implement onecclCommFinalize'],
'oneccl-env':['CCL_ATL_TRANSPORT=mpi','actual HMEM support'],
'mpich-release':['published_at'],
'oneccl-repo':['default_branch','archived'],
'oneccl-release':['published_at','tag_name'],
'nccl-release':['published_at','tag_name'],
'nccl-tree':['sha'],
'nccl-readme':['NCCL'],
'h100-datasheet':['900','80'],
'xccl2-rfc':['XCCL','RFC'],
'torch-ccl':['THIS PROJECT IS ARCHIVED','DEPRECATED'],
'torch-v29-doc':['Use the XCCL backend','NCCL_DEBUG_SUBSYS'],
'torch-xccl-code':['onecclComm_t','xccl::onecclAllGather'],
'nccl-env':['enable NVLink SHARP','LL, LL128'],
'megatron-layers':['RowParallelLinear','reduce_from_tensor_model_parallel_region'],
'megatron-mappings':['all_reduce','reduce_scatter'],
'deepep':['dispatch','combine'],
'torch-fsdp':['all-gather','reduce-scatter'],
'rccl':['HIP runtime','collective'],
'ucc':['Open MPI and UCC','CUDA collectives'],
'gloo':['collective','GPU'],
'nccl-tests-readme':['correctness','Performance']
}

version_scopes={
'nccl':'v2.32.3-1 tagged code; live user guide separately identified as retrieval snapshot',
'oneccl':'2022.1.0 tagged C API/plugin/code; legacy env docs separately scoped',
'mpi50-pdf':'MPI 5.0 approved2025-06-05; PDF authoritative over discrepant HTML numbering',
'openmpi-cuda':'v5.0.x documentation path; not a current-latest release assertion',
'mpich-v502':'v5.0.2 published2026-09-28',
'h100-datasheet':'NVIDIA H100 datasheet r7 zhCN; publication date not established',
'torch-v29-doc':'PyTorch v2.9.0 tagged distributed.md',
'torch-xccl-code':'torch-xpu-ops commit73a6552c3c122614d2651de2a0c6feb8f81ae613; development code, not wheel certification',
'rccl':'develop branch retrieval snapshot; not a release capability matrix',
'ucc':'master branch retrieval snapshot',
'gloo':'main branch retrieval snapshot',
'megatron-layers':'main branch retrieval snapshot',
'megatron-mappings':'main branch retrieval snapshot',
'deepep':'main branch retrieval snapshot; vendor performance numbers not adopted',
'torch-fsdp':'PyTorch v2.9.0 tagged fully_shard.py',
'oneccl-v2-example':'Live v2 example page identifies itself as C API2021.17.0; not a2022.1.0 release matrix',
'oneccl-env':'Live legacy C++ API environment documentation; not universal v2 plugin defaults',
'oneccl-plugin-doc':'File fetched at tag2022.1.0 but contains inherited2021.17/2025.3 release wording; implementation code overrides stale defaults',
'xccl2-rfc':'issue194761 RFC; proposal status, not released behavior'
}

citation_pattern=r'\[([a-z][a-z0-9-]+)\]'
used=set()
for file in ['research.md','proposed-insertions.md']:
    used.update(re.findall(citation_pattern,(ROOT/file).read_text()))
for _,_,_,refs,_ in DATA: used.update(refs)
missing=sorted(used-success.keys())
if missing: raise AssertionError(f'Unfetched source citations: {missing}')
sources=[]
for name in sorted(used):
    row=dict(success[name]); path=ROOT/row['text_path']; text=path.read_text(); lines=text.splitlines()
    raw=ROOT/'evidence'/f'{name}.raw'
    assert hashlib.sha256(raw.read_bytes()).hexdigest()==row['sha256'],name
    excerpts=[]
    for needle in NEEDLES.get(name,[name.split('-')[0]]):
        matches=[i for i,line in enumerate(lines) if needle.casefold() in line.casefold()]
        if matches:
            # Prefer body over repeated navigation when a source has page menus.
            i=matches[-1] if name.startswith('nccl-') and len(matches)>1 else matches[0]
            lo=max(0,i-1); hi=min(len(lines),i+4)
            quote='\n'.join(lines[lo:hi])
            truncated=False
            if len(quote)>1800:
                pos=quote.casefold().find(needle.casefold())
                quote=quote[max(0,pos-180):pos+1000]
                truncated=True
            excerpts.append({'needle':needle,'line_start':lo+1,'line_end':hi,'quote':quote,'partial_line_window':truncated})
    if not excerpts:
        raise AssertionError(f'No substantive excerpt found: {name}')
    scope=version_scopes.get(name)
    if not scope:
        scope=version_scopes.get('oneccl' if name.startswith('oneccl-') else 'nccl' if name.startswith('nccl-') else '', 'Fetched current documentation/metadata; publication date not established')
    row.update({'source_id':name,'version_scope':scope,'excerpts':excerpts,
                'publication_or_release_date':None,'date_note':'Retrieval time is not publication time.'})
    release_name= 'nccl-release' if name.startswith('nccl-') and '/v2.32.3-1/' in row['url'] else 'oneccl-release' if '/2022.1.0/' in row['url'] else 'mpich-release' if name=='mpich-v502' else name if name.endswith('-release') else None
    if release_name and release_name in success:
        obj=json.loads((ROOT/success[release_name]['text_path']).read_text())
        row['publication_or_release_date']=obj.get('published_at')
        row['date_note']='GitHub published_at from fetched release metadata, not necessarily documentation publication date.'
    sources.append(row)

pdf_path=ROOT.parents[1]/'review/publication_v2_20261028/baseline/from-token-to-fleet-v20260913.pdf'
doc=pymupdf.open(pdf_path)
baseline={'path':str(pdf_path),'sha256':hashlib.sha256(pdf_path.read_bytes()).hexdigest(),'pages':len(doc),'page_size_pt':list(doc[0].rect),'evidence_cutoff':'2026-08-30','primary_finding':{'physical':141,'printed':'123','chapter':9,'anchor':'ring-adjusted estimate','text':doc[140].get_text()},'dependent_finding':{'physical':152,'printed':'134','chapter':10}}
claims=[]
for cid,claim,status,refs,anchors in DATA:
    derived='DERIVED' in status or 'CPU' in status
    claims.append({'claim_id':cid,'claim':claim,'verification_status':status,'sources':refs,'candidate_anchors':anchors,
                   'provenance':'ILLUSTRATIVE/canonical scenario + first-party inputs' if derived else '1P; author synthesis explicitly scoped',
                   'epistemic_status':'DERIVED' if derived else 'PROPOSED' if status=='PROPOSED_EVALUATION_PROTOCOL' else 'UNRESOLVED' if cid=='CCL-024' else 'FACT_SCOPED_TO_SOURCE',
                   'measurement_status':'ANALYTICAL/CPU checks only' if derived else 'NOT_ACCELERATOR_EXECUTED',
                   'calculation_artifacts':['independent_calculations.py','calculations.json'] if derived else [],
                   'limitations':'No accelerator execution, cross-platform performance claim, released-wheel compatibility certification, or publication readiness certification.'})
result={'schema_version':1,'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Independent research; unapplied prose and figures; all writes confined to task directory','baseline':baseline,'claims':claims,'sources':sources,'failed_requests':[r for r in records if 'error' in r],
        'figure_manifest':'figures/manifest.json','source_count':len(sources),'claim_count':len(claims)}
(ROOT/'claims.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
parts=['# Primary sources actually fetched in this run\n','Citation keys in research.md and proposed-insertions.md resolve here and in claims.json. Dates below distinguish release metadata from retrieval. Quotes come from local fetched files. Branch/docs snapshots are not historical support proof. Failed requests are retained separately in retrieval.json.\n']
for row in sources:
    parts.extend([f"## {row['source_id']}\n",f"URL: {row['url']}\n",f"Retrieved UTC: {row['retrieved_at']}\n",f"Release/publication timestamp: {row['publication_or_release_date'] or 'not established'}; {row['date_note']}\n",f"Scope: {row['version_scope']}\n",f"Raw SHA-256: {row['sha256']}\n",f"Local text: {row['text_path']}\n"])
    for ex in row['excerpts']:
        parts.append(f"Lines {ex['line_start']}–{ex['line_end']} ({ex['needle']}):\n\n"+'\n'.join('> '+line for line in ex['quote'].splitlines())+'\n')
(ROOT/'sources.md').write_text('\n'.join(parts)+'\n')
print(json.dumps({'claim_count':len(claims),'source_count':len(sources),'failed_request_count':len(result['failed_requests']),'baseline_sha256':baseline['sha256']},indent=2))
