from dataclasses import dataclass,field
from datetime import datetime
from collections import Counter
@dataclass
class Tender:
 id:str;source:str;country:str;title:str;buyer:str='';value:float|None=None;currency:str='';deadline:datetime|None=None;published:datetime|None=None;status:str='active';url:str='';description:str='';procurement_id:str='';cpv:list[str]=field(default_factory=list);source_links:dict=field(default_factory=dict);value_eur:float|None=None;translations:dict=field(default_factory=dict)
 def display_title(self,lang):return self.translations.get(lang,{}).get('title') or self.title
 def display_description(self,lang):return self.translations.get(lang,{}).get('description') or self.description
class Store:
 def __init__(self):self.data={};self.runs=[];self.idx={}
 def add(self,src,rows):
  from app.dedupe import keys
  added=dupes=0
  for x in rows:
   x.source_links=x.source_links or ({src:x.url} if x.url else {});ks=keys(x);hit=next((self.idx[k] for k in ks if k in self.idx),None)
   if hit is None:
    self.data[x.id]=x;added+=1
    for k in ks:self.idx[k]=x.id
   else:
    old=self.data[hit];primary=x if x.source!='ted' and old.source=='ted' else old;primary.source_links={**old.source_links,**x.source_links};self.data[hit]=primary;dupes+=1
  self.runs.insert(0,{'source':src,'status':'ok','count':len(rows),'added':added,'duplicates':dupes,'error':''})
 def error(self,src,e):self.runs.insert(0,{'source':src,'status':'error','count':0,'added':0,'duplicates':0,'error':str(e)[:400]})
store=Store()
def active(x):return (x.status or '').lower() not in {'complete','completed','awarded','cancelled','closed'} and (not x.deadline or x.deadline>=datetime.utcnow())
def analytics(rows):
 return {'countries':dict(Counter(x.country for x in rows).most_common(12)),'sources':dict(Counter(x.source for x in rows).most_common(12)),'cpv':dict(Counter(c for x in rows for c in x.cpv).most_common(12)),'buyers':dict(Counter(x.buyer for x in rows if x.buyer).most_common(12)),'days':dict(sorted(Counter((x.published or x.deadline).strftime('%Y-%m-%d') for x in rows if x.published or x.deadline).items()))}
