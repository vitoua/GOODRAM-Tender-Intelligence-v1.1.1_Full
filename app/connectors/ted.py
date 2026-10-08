from datetime import datetime
import httpx
from app.core import Tender
from app.filters import active_codes,keywords,relevant
from app.fx import eur_value
URL='https://api.ted.europa.eu/v3/notices/search'
def first(v):
 if isinstance(v,dict):return first(v.get('eng') or v.get('pol') or next(iter(v.values()),''))
 if isinstance(v,list):return first(v[0]) if v else ''
 return str(v or '')
def dt(v):
 try:return datetime.fromisoformat(first(v)[:10])
 except:return None
def num(v):
 try:return float(first(v))
 except:return None
def flat(v):return [first(x) for x in v] if isinstance(v,list) else ([first(v)] if v else [])
async def fetch(countries,published_from,min_eur,limit=250):
 cut=published_from.strftime('%Y%m%d');terms=' OR '.join(f'FT~"{k}"' for k in keywords()[:40]);cpv=' OR '.join(f'classification-cpv={c}' for c in active_codes());q=f'({terms} OR {cpv}) AND PD>={cut} SORT BY publication-date DESC';fields=['publication-number','notice-title','buyer-name','buyer-country','publication-date','deadline','description-proc','form-type','classification-cpv','total-value','total-value-cur'];payload={'query':q,'fields':fields,'page':1,'limit':limit,'scope':'ACTIVE','paginationMode':'PAGE_NUMBER','onlyLatestVersions':True}
 async with httpx.AsyncClient(timeout=55) as c:r=await c.post(URL,json=payload)
 if r.status_code!=200:raise RuntimeError(f'TED HTTP {r.status_code}: {r.text[:600]}')
 out=[]
 for x in r.json().get('notices',[]):
  co=first(x.get('buyer-country'))[:3];ddl=dt(x.get('deadline'));pub=dt(x.get('publication-date'));form=first(x.get('form-type')).lower();codes=flat(x.get('classification-cpv'));title=first(x.get('notice-title'));desc=first(x.get('description-proc'))
  if countries and co not in countries or not ddl or ddl<datetime.utcnow() or not pub or pub<published_from or any(z in form for z in ('result','award','completion')):continue
  if not relevant(codes,title+' '+desc):continue
  val=num(x.get('total-value'));cur=first(x.get('total-value-cur')) or 'EUR';ve=await eur_value(val,cur)
  if ve is None or ve<min_eur:continue
  n=first(x.get('publication-number'));out.append(Tender('ted:'+n,'ted',co,title or n,first(x.get('buyer-name')),val,cur,ddl,pub,'active',f'https://ted.europa.eu/en/notice/-/detail/{n}',desc,n,codes,value_eur=ve))
 return out
