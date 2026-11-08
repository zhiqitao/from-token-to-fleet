"""Verify source pins and compute analytical video budgets (no inference)."""
from pathlib import Path
import json, hashlib, urllib.request, concurrent.futures, datetime
R=Path(__file__).resolve().parent
S=R/'sources'
manifest=json.loads((S/'manifest.json').read_text())
commits={
 'https://raw.githubusercontent.com/Wan-Video/Wan2.2/main/':json.loads((S/'wan22_commit.raw').read_text())['sha'],
 'https://raw.githubusercontent.com/Lightricks/LTX-2/main/':json.loads((S/'ltx_commit.raw').read_text())['sha'],
 'https://raw.githubusercontent.com/Tencent-Hunyuan/HunyuanVideo-1.5/main/':json.loads((S/'hunyuan_commit.raw').read_text())['sha'],
}
def pin(m):
 for prefix,sha in commits.items():
  if m['url'].startswith(prefix) and m['status']=='retrieved':
   url=prefix.replace('/main/',f'/{sha}/')+m['url'][len(prefix):]
   try:
    with urllib.request.urlopen(url,timeout=60) as f: b=f.read()
    same=hashlib.sha256(b).hexdigest()==m['sha256']
    return {'source_id':m['id'],'url':url,'same_bytes_as_snapshot':same,'sha256':hashlib.sha256(b).hexdigest(),'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
   except Exception as e: return {'source_id':m['id'],'url':url,'error':str(e)}
 return None
pins=[p for p in concurrent.futures.ThreadPoolExecutor(max_workers=8).map(pin,manifest) if p]
(S/'pinned-sources.json').write_text(json.dumps(pins,indent=2))

def budget(F,H,W,D=3072,heads=24,layers=30,C=48):
 assert (F-1)%4==0 and H%32==0 and W%32==0
 T=(F-1)//4+1; lh=H//16; lw=W//16; N=T*(lh//2)*(lw//2)
 return dict(frames=F,height=H,width=W,latent_frames=T,latent_height=lh,latent_width=lw,latent_cells=T*lh*lw,latent_channels=C,video_tokens=N,hidden_dim=D,heads=heads,layers=layers,
  clip_seconds_container=F/24,frame_timestamp_span_seconds=(F-1)/24,
  latent_BF16_bytes=T*lh*lw*C*2,
  initial_latent_FP32_bytes=T*lh*lw*C*4,
  hidden_BF16_bytes=N*D*2,
  QKV_BF16_bytes=3*N*D*2,
  one_materialized_score_BF16_bytes=heads*N*N*2,
  one_materialized_score_BF16_GiB=heads*N*N*2/2**30,
  full_attention_core_FLOP_per_layer=4*N*N*D,
  full_attention_core_FLOP_per_evaluation=layers*4*N*N*D,
  full_attention_core_FLOP_50_steps_two_CFG_branches=100*layers*4*N*N*D,
  text_cross_attention_core_FLOP_per_layer_M512=4*N*512*D)
a=budget(121,704,1280); b=budget(241,704,1280)
# The larger shape is sensitivity algebra only, not a supported quality claim.
c=budget(121,1408,2560)
results={'status':'ANALYTICAL, no GPU performance measured','convention':'multiply-add=2 FLOP; batch=1; BF16 payload=2 bytes; full noncausal attention; excludes QKV/output projections, MLPs, softmax, conditioning, VAE, allocator and communications','wan22_ti2v5_121':a,'sensitivity_241_frames':b,'sensitivity_double_each_spatial_axis_not_release_support':c,
 'ratios':{'241_vs121_tokens':b['video_tokens']/a['video_tokens'],'241_vs121_pairwise_work':(b['video_tokens']/a['video_tokens'])**2,'double_each_spatial_axis_tokens':c['video_tokens']/a['video_tokens'],'double_each_spatial_axis_pairwise_work':(c['video_tokens']/a['video_tokens'])**2},
 'approx_weight_payloads_bytes':{'5B_BF16':5e9*2,'A14B_total_27B_BF16':27e9*2,'A14B_active_about14B_BF16':14e9*2},
 'parameter_payload_warning':'rounded advertised counts; not measured checkpoint size or peak HBM',
 'benchmark_ratios_derived_only':{'ltx_report_Wan_seconds_perstep_div_LTX':22.30/1.22,'hunyuan_241_dense_over_sparse_no_eng':5.5070/2.9475,'hunyuan_241_dense_over_sparse_eng':96.78/58.39}}
(R/'calculations.json').write_text(json.dumps(results,indent=2))
print('pinned source matches',sum(x.get('same_bytes_as_snapshot',False) for x in pins),'/',len(pins))
print(json.dumps(results,indent=2))
# Machine inventory is exhaustive only within the returned official public HF list.
hf=json.loads((S/'wan_hf_models.raw').read_text())
(R/'official-wan-model-inventory.json').write_text(json.dumps([{'id':m['id'],'revision':m.get('sha'),'created_at_NOT_release_date':m.get('createdAt'),'last_modified_NOT_release_date':m.get('lastModified')} for m in hf],indent=2))
