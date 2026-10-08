import json,re
from pathlib import Path
CPV=Path('data/cpv.json');KW=Path('data/keywords.json')
def cpvs():return json.loads(CPV.read_text())
def active_codes():return [x['code'] for x in cpvs() if x.get('active')]
def keywords():
 d=json.loads(KW.read_text());return list(dict.fromkeys(sum(d.values(),[])))
def relevant(codes,text):
 act=active_codes();norm=[re.sub(r'\D','',str(c))[:8] for c in codes]
 code_ok=any(any(c==a or (a.endswith('0000') and c.startswith(a.rstrip('0'))) for a in act) for c in norm)
 t=(text or '').casefold();kw_ok=any(k.casefold() in t for k in keywords())
 return code_ok or kw_ok
