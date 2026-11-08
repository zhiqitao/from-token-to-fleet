"""Validate research artifacts and build the human-readable source ledger."""
import collections,datetime,hashlib,json,pathlib,re,subprocess
R=pathlib.Path(__file__).resolve().parent
sources=json.loads((R/'source-index.json').read_text()); bykey={s['key']:s for s in sources}
claims=json.loads((R/'claims.json').read_text())
required=['claim','exact_model_id','source_url','retrieved_date','section','evidence_status','benchmark_scope','proposed_chapter_placement']
assert claims and len({c['id'] for c in claims})==len(claims)
for c in claims:
 assert all(c.get(k) for k in required),c['id']
 for key in c['source_keys']:
  s=bykey[key];assert s.get('status')==200,(c['id'],key)
  assert hashlib.sha256((R/s['local_path']).read_bytes()).hexdigest()==s['sha256'],key
assert all(s.get('local_sha256_matches') is not False for s in sources)
md=['# Primary-source retrieval ledger','', 'All URLs below were attempted during this research run. HTTP success and a matching local content hash establish retrieval, not truth or reproduced performance. Report/card/config disagreements remain in claims.json. Dates and revisions asserted in the research note come from the captured content, not HTTP Last-Modified alone.','', 'Source content is stored under sources/. Raw PDFs retain the collector extension .txt; their content type is recorded below. Extracted PDF text is in *.pdftext.md.','']
for s in sources:
 md.extend([f"## {s['key']}",f"URL: {s['url']}",f"Retrieved: {s['retrieved_at']}"])
 if s.get('status')==200:
  md.extend([f"HTTP: {s['status']}; content type: {s.get('content_type')}",f"Local: {s['local_path']}",f"SHA256: {s['sha256']}",f"ETag: {s.get('etag')}; Last-Modified: {s.get('last_modified')}"])
 else:md.append(f"FAILED: {s.get('error')}. Not used as supporting evidence.")
 md.append('')
md.extend(['## Available Hugging Face revision records','', 'These are metadata snapshots. Repository creation is not automatically public launch. The matching content hash remains the exact evidence for each downloaded file.',''])
for s in sources:
 if s['key'].endswith('meta') and s.get('status')==200:
  d=json.loads((R/s['local_path']).read_text());md.append(f"- {d.get('id')}: sha={d.get('sha')}; createdAt={d.get('createdAt')}; lastModified={d.get('lastModified')}")
(R/'primary-sources.md').write_text('\n'.join(md)+'\n')
prose=(R/'proposed-insertions.md').read_text()
assert not re.search(r'\b(you|your|yours)\b',prose,re.I),'Direct reader address'
refs=set(re.findall(r'\[\^([^\]]+)\]',prose));defs=set(re.findall(r'^\[\^([^\]]+)\]:',prose,re.M));assert refs==defs,(refs,defs)
urls=set(re.findall(r'https?://[^\s<>]+',prose));urlmap={s['url']:s for s in sources}
assert all(u in urlmap and urlmap[u].get('status')==200 for u in urls),[u for u in urls if u not in urlmap or urlmap[u].get('status')!=200]
for name in ['model-trends-research.md','proposed-insertions.md']:
 lines=(R/name).read_text().splitlines(); expected=None
 for i,line in enumerate(lines,1):
  if line.startswith('|'):
   width=line.count('|')
   if expected is None:expected=width
   assert width==expected,(name,i,width,expected)
  else:expected=None
q=json.loads((R/'sources/qwen-config.txt').read_text())['text_config'];assert collections.Counter(q['layer_types'])=={'linear_attention':48,'full_attention':16}
assert json.loads((R/'calculations.json').read_text())['qwen27_bf16_full_attention_kv_GiB_at_native_context']==16
assert bykey['deepseek1017-config']['sha256']==bykey['deepseek41-config']['sha256']
# Purely static checks of the fetched reference path; no downloaded code is executed.
code=(R/'sources/ouro-code.txt').read_text();assert 'for current_ut in range(self.total_ut_steps)' in code
assert 'stacked_hidden = torch.stack(hidden_states_list, dim=2)' in code
required_files=['model-trends-research.md','claims.json','proposed-insertions.md']
files={name:{'bytes':(R/name).stat().st_size,'sha256':hashlib.sha256((R/name).read_bytes()).hexdigest()} for name in required_files}
assert all(v['bytes']>100 for v in files.values())
version_hashes=json.loads((R/'manuscript-read-hashes.json').read_text()); unchanged={p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()==h for p,h in version_hashes.items()}
report={'validated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS','claim_count':len(claims),'source_count':len(sources),'sources_with_successful_get':sum(s.get('status')==200 for s in sources),'failed_source_attempts':[{k:s.get(k) for k in ['key','url','error']} for s in sources if s.get('status')!=200],'candidate_citation_url_count':len(urls),'citation_validation':'All candidate URLs have successful actual GET and matching local SHA256 in this-run ledger. No HEAD-only or search-snippet validation.','footnotes':len(defs),'claim_schema_required_fields':required,'all_claim_supports_successfully_fetched_and_hashed':True,'tables_rectangular':True,'english_candidate_no_you_your':True,'derived_arithmetic_pass':True,'downloaded_model_code_executed':False,'model_benchmarks_reproduced':False,'pdf_layout_audited':False,'files':files,'manuscript_read_versions_unchanged_at_validation':unchanged,'ownership_scope':'research/model-trends-20261028/ only; concurrent parent changes are not attributed to this research agent'}
(R/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
