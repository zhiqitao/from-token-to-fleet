import json,pathlib,re,sys
p=pathlib.Path(__file__).parent
if len(sys.argv)>1:
 for name in sys.argv[1:]:
  text=(p/'evidence'/f'{name}.txt').read_text()
  print('\n###',name)
  if name=='oneccl-tree':
   t=json.loads(text); print('SHA',t['sha']); print('\n'.join(x['path'] for x in t['tree'] if x['type']=='blob' and any(s in x['path'].lower() for s in ['ccl.h','plugin','stream','event','atl_mpi','atl_ofi'])))
  else:
   for needle in ['Device API','device-initiated','LSA','GIN','CCL_ATL_TRANSPORT','MPI','OFI','onecclCommInitRank','Stream','stream','queue','completion','cudaStream','SUM','oneCCL','XCCL','NVLS','NCCL_ALGO','NCCL_PROTO']:
    hits=list(re.finditer(re.escape(needle),text,re.I))
    if hits:
     print('\nTERM',needle)
     for m in hits[-2:]: print(text[max(0,m.start()-160):m.end()+650])
else:
 import pymupdf,hashlib
 f=pathlib.Path('review/publication_v2_20261028/baseline/from-token-to-fleet-v20260913.pdf'); d=pymupdf.open(f)
 for i,page in enumerate(d):
  text=page.get_text()
  if any(s in text for s in ['2026-08-30','three orthogonal axes','At node NVLink 900','Sources, Method, and Reproducibility']):
   print('PHYSICAL',i+1, text[:150] )
   if 'three orthogonal axes' in text or '2026-08-30' in text: print(text)
 for i in [139,140,141,148]:
  text=d[i].get_text(); (p/f'baseline-physical{i+1}.txt').write_text(text)
 print('MPI COLLECTIVE LINKS')
 from html.parser import HTMLParser
 class Links(HTMLParser):
  def handle_starttag(self,t,a):
   if t=='a':
    for k,v in a:
     if k=='href': print(v)
 Links().feed((p/'evidence/mpi-collectives.raw').read_text())
