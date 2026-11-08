"""Build the task-local evidence registry and reproducible analytical examples.
No network calls, manuscript writes, or measured benchmark data.
"""
from pathlib import Path
import datetime as dt
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
NOW = dt.datetime.now(dt.timezone.utc).isoformat()
ledger = json.loads((ROOT / 'citation-ledger.json').read_text())['sources']
retrievals = [json.loads(x) for x in (ROOT / 'retrievals.jsonl').read_text().splitlines()]
bykey = {x['key']: x for x in retrievals}
byid = {x['id']: x for x in ledger}
excluded = {15: 'Wrong SGLang path; fetched body is a 404 response.',
            48: 'SKU 230020 resolves to Flex 140, not the Flex 170 identity in the URL slug.',
            70: 'Fetched response is Page Not Found; not a valid support matrix.'}
sources = []
for src in ledger:
    record = dict(src)
    url = src['url']
    if src['id'] == 60:
        record['provenance'] = 'third_party_experiment_hardware_provided_by_Sparkle_with_Intel_technical_support'
    elif src['id'] == 61:
        record['provenance'] = 'independent_author_self_report_not_independently_reproduced'
    elif src['id'] == 56:
        record['provenance'] = 'commercial_provider_first_party_announcement'
    elif any(x in url for x in ('intel.com','intel.github.io','github.com/intel/','githubusercontent.com/intel/','docs.habana.ai','openvino','dgpu-docs')):
        record['provenance'] = 'vendor_or_vendor_maintained_project_first_party'
    else:
        record['provenance'] = 'upstream_project_first_party_not_independent_performance_validation'
    meta = bykey.get(src['title'], {})
    p = ROOT / meta.get('path', 'MISSING')
    record.update(retrieved_at=meta.get('retrieved_at'), status=meta.get('status'),
                  snapshot=meta.get('path'), response_sha256=meta.get('sha256'),
                  last_modified_header=meta.get('last_modified'),
                  acquisition_url=meta.get('fetch_url'),
                  usable=src['id'] not in excluded,
                  exclusion_reason=excluded.get(src['id']),
                  publication_date=None,
                  publication_date_note='Unknown unless an explicit date or release API is recorded below. Last-Modified is not publication date.')
    if p.is_file():
        text = p.read_text()
        record['extracted_text_sha256'] = hashlib.sha256(text.encode()).hexdigest()
        if '"published_at"' in text:
            try:
                api = json.loads(text)
                if isinstance(api, dict):
                    record['publication_date'] = api.get('published_at')
                    record['release_tag'] = api.get('tag_name')
            except ValueError:
                pass
        if 'raw.githubusercontent.com' in src['url']:
            pin = re.search(r'/([a-f0-9]{40})/', src['url'])
            record['immutable_commit'] = pin.group(1) if pin else None
    sources.append(record)
explicit_publication_dates={2:'2024-10-25',6:'2025-10-14',13:'2026-03-25',32:'2025-05-19',33:'2024-12-03',56:'2025-03-31',60:'2026-02-14',61:'2026-04-13'}
for source in sources:
    if source['id'] in explicit_publication_dates:
        source['publication_date']=explicit_publication_dates[source['id']]
        source['publication_date_note']='Explicit article dateline/date in fetched source; not a Last-Modified inference.'
source_index = {x['id']: x for x in sources}

def ev(sid, needle):
    src = source_index[sid]
    assert src['usable'], (sid, src['exclusion_reason'])
    lines = (ROOT / src['snapshot']).read_text().splitlines()
    hits = [i for i, line in enumerate(lines) if needle.lower() in line.lower()]
    assert hits, (sid, needle)
    i = hits[0]
    return {'source_id': sid, 'url': src['url'], 'retrieved_at': src['retrieved_at'], 'provenance': src['provenance'],
            'publication_date': src['publication_date'], 'snapshot': src['snapshot'],
            'line_start': i+1, 'line_end': min(i+4, len(lines)),
            'excerpt': '\n'.join(lines[i:i+4]), 'matched_text': needle}

claims = []
def add(num, claim, evidence, boundary, disposition='propose', kind='first_party_documented', date=None, chapter=None):
    claims.append({'id': f'IX-{num:03d}', 'claim': claim, 'evidence': [ev(*x) for x in evidence],
                   'source_release_or_event_date': date, 'conditions_and_support_boundary': boundary,
                   'epistemic_status': kind, 'local_execution_validation': 'NOT RUN',
                   'disposition': disposition, 'proposed_chapter': chapter,
                   'cutoff_policy': 'Mechanism text may enter the body; current-version facts belong in the 2026-10-28 supplement unless separately proved before 2026-08-30.'})

add(1, 'torch.xpu is the PyTorch device API for Intel GPU, not a generic name for every Intel accelerator.', [(66,'torch.xpu is the API')], 'Device availability is not an end-to-end LLM or SLO test.', chapter='08/11')
add(2, 'Gaudi PyTorch uses the hpu device and its own software stack; HCCL is a separate collective API.', [(55,'device = torch.device("hpu")'),(47,'HCCL')], 'GPU XPU documentation does not validate Gaudi engines or collectives.', chapter='09/11')
add(3, 'OpenVINO GenAI and Intel client CPU/GPU/NPU resources must be identified separately.', [(25,'NPU'),(35,'NPU Peak TOPS')], 'CPU+iGPU+NPU marketing TOPS do not describe one usable GPU execution resource.', chapter='08/18')
add(4, 'Upstream PyTorch Intel GPU support began as prototype support in PyTorch 2.5.', [(66,'Prototype'),(2,'2.5')], 'The pinned guide supports eager, torch.compile, FP32/BF16/FP16/AMP; not all model operators or serving configurations are thereby validated.', date='2024-10, PyTorch 2.5', chapter='08/27')
add(5, 'The retrieved PyTorch latest release is v2.14.1.', [(22,'"tag_name"')], 'Latest API observation only, not the version required by each serving engine; vLLM pinned requirements instead use torch 2.14.0.', date='2026-09-30T19:14:48Z', chapter='27')
add(6, 'The retrieved vLLM latest release is v0.32.0; its examined code is pinned.', [(21,'"tag_name"'),(39,'"sha"')], 'Pin 5df63a7203cdb9328d824a27b682e77c7b9928be. No wheel download, digest, install or hardware test performed.', date='2026-10-18T06:50:48Z', chapter='27')
add(7, 'IPEX retirement guidance recommends upstream PyTorch instead of assuming the extension remains required.', [(5,'March 2026')], 'Applies to current recommended path; historical deployments may retain extension-specific behavior.', chapter='11/27')
add(8, 'IPEX-LLM README announces archival, no guaranteed support and known security issues.', [(14,'THIS PROJECT IS ARCHIVED')], 'Archive warning is a deployment/support-risk finding, not proof every old artifact is exploitable.', disposition='exclude_as_default', chapter='16/27')
add(9, 'Arc Pro B70 is documented with 32 GB VRAM, 608 GB/s and 367 INT8 dense TOPS.', [(7,'32GB VRAM'),(7,'608 GB/s'),(7,'dense models'),(7,'Intel version not available')], 'B70 sheet says VRAM without naming its memory type. Board power 160–290 W, 230 W Intel reference. Native PCIe Gen5 x16; actual host link may be narrower. Datasheet render note says Intel version not available for purchase, conflicting with March 25 launch announcement. Do not silently resolve stock availability.', date='2026-03-25 availability announcement', chapter='27')
add(10, 'Arc Pro B65 is documented with 32 GB GDDR6, 608 GB/s and 197 INT8 dense TOPS.', [(8,'32GB of GDDR6'),(8,'197 AI TOPS'),(8,'608 GB/s')], '200 W total board power reference. Announcement expected mid-April availability; sheet updated April 20. Channel stock not independently verified.', date='2026-03-25 announcement; mid-April expected availability', chapter='27')
add(11, 'B70/B65 announcement dates and availability statements differ.', [(13,'starting March 25, 2026'),(13,'mid-april 2026')], 'Vendor-announced availability is not independently verified stock or adoption.', chapter='27')
add(12, 'Arc Pro B60 has 24 GB GDDR6, 456 GB/s, 197 INT8 dense TOPS and 120–200 W reference board power.', [(30,'24GB of GDDR6'),(30,'456 GB/s'),(30,'120-200W'),(32,'sampling')], 'Board-provider specifications and actual PCIe lane allocation must be checked. Multiple 24 GB devices do not form one allocation. May 19 announcement said June sampling, not June GA; April 2026 personal purchase is an attributed observation.', date='2025-05-19 announcement; June sampling plan', chapter='07/27')
add(13, 'Arc Pro B50 is a 16 GB product, not a 12 GB product.', [(31,'16GB'),(31,'224 GB/s'),(31,'70W')], 'Official press deck documents 170 peak TOPS; do not compare this headline against BF16 FLOP/s or transfer graphics tests to inference.', date='Computex 2025', chapter='27')
add(14, 'Arc B580 and B570 have different capacity and bandwidth despite sharing a product family.', [(68,'12 GB GDDR6'),(68,'456 GB/s'),(69,'10 GB GDDR6'),(69,'380 GB/s')], 'B580 12 GB/456 GB/s; B570 10 GB/380 GB/s. SKU launch quarter is not identical to retail on-sale date.', date='B580 2024-12-13; B570 2025-01-16 announced retail dates', chapter='27')
add(15, 'Max 1550 is a historical HBM GPU with lifecycle risk, not an unrestricted current procurement recommendation.', [(9,'Expected Discontinuance'),(9,'128 GB'),(9,'3276.8 GB/s'),(10,'HBM2e')], 'SKU lists expected discontinuance Jan 2026; this does not prove all support ended or every installed board disappeared.', date="Q1'23 launch; Jan 2026 expected discontinuance", chapter='27')
add(16, 'The verified Flex 170 identity is SKU 230019 with 16 GB GDDR6 and 576 GB/s.', [(58,'16 GB'),(58,'576 GB/s')], 'Exclude misleading slug carrying SKU 230020 (Flex 140); do not infer identity from URL spelling.', date="Q3'22 launch", chapter='27')
add(17, 'Intel GPU D-series / D270 (Crescent Island) is vendor-reported as sampling; GA is not established.', [(28,'customer sampling underway'),(27,'D270'),(28,'160GB LPDDR5x')], 'Intel-branded card 160 GB LPDDR5X; partner options up to 480 GB. October page gives 1.5 TB/s, 1.3 PFLOPS FP8 and 350 W. Sparsity qualification and SKU-specific bandwidth for each partner board need confirmation.', date='October 2026 OCP statement; 2025-10-14 original announcement', disposition='dated_supplement_only', chapter='27')
add(18, 'Core Ultra X9 388H integrates Arc B390 GPU and a separate NPU; system memory is not dedicated VRAM.', [(35,'Intel® Arc™ B390'),(35,'96 GB'),(35,'NPU Peak TOPS'),(37,'memory')], '96 GB is maximum supported system memory, not guaranteed GPU allocation. GPU 122 and NPU 50 INT8 TOPS are separate resources. iGPU allocation depends on OS/driver/runtime and other memory consumers.', date="Q1'26", chapter='07/18/27')
add(19, 'vLLM XPU requires a coherent versioned kernel/framework/runtime path.', [(53,'torch==2.14.0'),(53,'triton==3.8.0+xpu'),(53,'vllm_xpu_kernels==0.1.15.4'),(67,'Python: 3.12')], 'Pinned guide still mentions triton 3.7.2+xpu while requirements specify 3.8.0+xpu. Use resolved lock and tests, not copy-paste mixed snippets. Driver recommendation compute runtime 26.18.38308.1 is not a universal minimum for all hardware.', chapter='11/16/27')
add(20, 'vLLM XPU documents tensor parallelism and single-node multiprocessing pipeline parallelism as beta.', [(67,'pipeline parallel'),(67,'xccl')], 'torch>=2.8 uses xccl; older path torch-ccl. Ray discussion does not establish validated multi-node PP or every transport.', chapter='09/10/27')
add(21, 'vLLM graph capability cannot be reduced to a universal yes/no from one table.', [(52,'supports_xpu_graph'),(65,'| CUDA graph | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |'),(67,'xpu graph support requires')], 'Code and setup guidance expose conditional XPU graph support while generic feature table uses CUDA-graph terminology. Exact model, path, runtime and shapes require testing.', disposition='conditional_not_blanket', chapter='11/27')
add(22, 'vLLM quantization and model support need backend-specific checks, not engine-wide generalization.', [(52,'supported_quantization'),(4,'Qwen')], 'The quantization registration list is not proof every weight/KV/activation combination has working kernels. Model page is live, not immutable release certification.', chapter='05/11/27')
add(23, 'SGLang has a separately documented XPU path optimized for Arc B/Arc Pro B hardware.', [(49,'Arc™ Pro B-Series'),(49,'torch==2.14.0+xpu'),(51,'FROM'),(72,'"sha":"a1966e1b5d8b750b494d7e53cca1d2464f960038"')], 'Code/documentation commit a1966e1b5d8b750b494d7e53cca1d2464f960038 dated 2026-10-28T06:26:29Z, separately verified by commit API. Latest release v0.5.22 published 2026-10-19: newer main features must not be assigned to that release. Source-install sentence and prebuilt Docker section coexist; do not claim no images exist.', date='2026-10-19T02:55:19Z release metadata; 2026-10-28T06:26:29Z examined commit', chapter='11/27')
add(24, 'SGLang XPU MXFP4 MoE path has architecture, layer and parallelism boundaries.', [(49,'Xe2 / BMG only'),(49,'Fused MoE experts only'),(49,'Not yet validated on this path')], 'Tested example openai/gpt-oss-20b; W4A16 experts, BF16 activations and nonexpert layers. Expert parallelism not yet validated. No local reproduction of vendor-reported memory usage.', chapter='05/11/27')
add(25, 'SGLang experimental XPU graphs and DCP introduce constraints, not automatic speedups.', [(49,'XPU Graph [Experimental]'),(49,'Two-batch overlap'),(49,'decode gets slower')], 'Decode full graph and prefill breakable graph opt-in; prefill path not torch.compile. DCP extends context only under specified KV-head/TP relationship and can slow decode. Multi-node unverified here.', chapter='11/27')
add(26, 'llama.cpp has an engine-native SYCL path, not necessarily a PyTorch execution path.', [(54,'oneAPI'),(54,'level_zero'),(54,'--split-mode tensor')], 'Pin 8ca4060b7e30e76baaa5670ee1ec1b760b7f8552. Tensor split requires flash attention; f16 KV recommended; two-GPU optimization and generic all-reduce at other counts do not validate multi-node or arbitrary quantized KV.', chapter='08/11/27')
add(27, 'OpenVINO GenAI documents paged attention and dynamic continuous batching on CPU/GPU with fallback behavior.', [(36,'global pool of fixed-size blocks'),(36,'fall back to the SDPA'),(36,'ATTENTION_BACKEND="PA"')], 'Published documentation says supported CPU/GPU paths; this is not NPU feature parity. Explicit PA selection makes failure visible instead of silent fallback. Runtime 2026.4.1 and GenAI 2026.4.1.0 are distinct release identities.', chapter='11/18/27')
add(28, 'Gaudi 3 resources and collective bandwidth need form-factor and direction labels.', [(11,'128 GB'),(11,'1678'),(11,'1200 GB/s'),(11,'21 NICs')], 'July 2025 V1 Rev3 OAM context: 128 GB HBM2e, 3.7 TB/s; table 1678 TFLOPS BF16/FP8 differs from introductory rounded 1.8 PFLOPS. 24x200 Gb/s yields 600 GB/s per direction, 1200 bidirectional aggregate, not collective throughput.', chapter='09/27')
add(29, 'An IBM Cloud Gaudi 3 availability announcement is a commercial availability signal, not independently measured production utilization.', [(56,'available')], 'Provider is an interested party; no customer utilization, SLA telemetry, quality or TCO measured here.', disposition='adoption_signal_only', chapter='27')
add(30, 'EmbeddedLLM and an independent local deployment account do not establish a portable benchmark winner.', [(60,'Feb 14, 2026'),(61,'Apr 13, 2026'),(61,'state leaked between requests')], 'Hardware-supported/sponsored experiments and uncontrolled personal deployments differ from independent controlled tests. April failures are historical observations, not proof current releases retain the defect.', kind='attributed_observation', disposition='context_not_performance_ranking', chapter='14/27')
add(31, '2026-10-28 findings must not silently change the 2026-08-30 evidence snapshot.', [(57,'XPU')], 'Historical vLLM commit c92b29a1d40644da710209f862b1be0ebd5c2e74 is a pre-cutoff checkpoint only, not validation of all October capabilities. Manuscript cutoff is independently recorded in the read inventory.', kind='editorial_scope_rule', chapter='27')
add(32, 'No retrieved evidence establishes Intel market-share gains or broad production-scale inference dominance.', [(60,'benchmark'),(61,'local LLM')], 'This is a bounded search conclusion, not proof of no adoption. Upstream code, vendor availability and a home deployment are separate evidence classes.', kind='bounded_research_assessment', disposition='reject_unqualified_rise_claim', chapter='27')
add(33, 'The illustrative memory-fit and directional-bandwidth examples are derived arithmetic, not measured inference results.', [(30,'24GB of GDDR6'),(7,'608 GB/s'),(11,'1200 GB/s')], 'Assumed model: 8B FP16, 32 layers, 8 KV heads, head dimension 128, FP16 KV, 9500 resident tokens, 4 GB assumed workspace reserve. 70B ideal 4bit omits metadata. Nominal bandwidth is not achieved bandwidth.', kind='illustrative_derived', chapter='07/09')
claims[-1]['local_execution_validation'] = 'ARITHMETIC EXECUTED by this script; hardware inference NOT RUN'
claims[-1]['calculation_artifact'] = 'arithmetic.json'
chapter27=ROOT.parent.parent/'design/manuscript/chapter-27/chapter-27.md'
cutoff_lines=chapter27.read_text().splitlines()
claims[30]['local_source_evidence']={'path':str(chapter27.relative_to(ROOT.parent.parent)),'sha256':hashlib.sha256(chapter27.read_bytes()).hexdigest(),'excerpt':cutoff_lines[2]}

arithmetic = {
    'status': 'ILLUSTRATIVE DERIVED; not benchmark measurements',
    'units': 'Decimal GB=1e9 bytes; GiB=2**30 bytes; directional bandwidth unless labeled otherwise',
    'text_width_in': 8.5-1.2-1.2,
    'weight_only_70B_fp16_GB': 70e9*2/1e9,
    'weight_only_70B_ideal_4bit_GB': 70e9*4/8/1e9,
    'weight_only_8B_fp16_GB': 8e9*2/1e9,
    'example_GQA_KV_bytes_per_token': 2*32*8*128*2,
    'example_GQA_KV_9500_tokens_GB': 2*32*8*128*2*9500/1e9,
    'example_reserve_GB_assumed_not_measured': 4,
    'example_total_GB': 8e9*2/1e9 + 2*32*8*128*2*9500/1e9 + 4,
    'example_free_capacity_on_24GB_GB': 24-(16+2*32*8*128*2*9500/1e9+4),
    'weights_only_16GB_scan_at_456GBps_ms': 16/456*1000,
    'weights_only_16GB_scan_at_608GBps_ms': 16/608*1000,
    'gaudi24ports_directional_GBps': 24*200/8,
    'gaudi24ports_bidirectional_aggregate_GBps': 2*24*200/8,
    'gaudi21scaleup_ports_directional_GBps': 21*200/8,
    'gaudi3scaleout_ports_directional_GBps': 3*200/8,
    'capacity_of_two24GB_boards_GB_not_single_allocation': 2*24,
}
assert arithmetic['weight_only_70B_ideal_4bit_GB'] > 32
assert arithmetic['example_total_GB'] < 24
(ROOT/'arithmetic.json').write_text(json.dumps(arithmetic, indent=2)+'\n')
(ROOT/'claims.json').write_text(json.dumps({'schema_version':1,'generated_at':NOW,'scope':'research proposals, not certification','claim_count':len(claims),'sources':sources,'claims':claims,'retrieval_failures':[x for x in retrievals if x['status']!='FETCHED'],'excluded_sources':excluded},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'claims':len(claims),'source_records':len(sources),'excluded':excluded,'arithmetic':arithmetic},ensure_ascii=False,indent=2))
