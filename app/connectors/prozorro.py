from datetime import datetime,timezone
import httpx
from app.core import Tender
from app.filters import relevant
from app.fx import eur_value
B='https://public-api.prozorro.gov.ua/api/2.5/tenders'
def dt(v):
 try:return datetime.fromisoformat(str(v).replace('Z','+00:00')).replace(tzinfo=None)
 except:return None
async def fetch(countries,published_from,min_eur,limit=250):
 out=[];offset=None;seen=0
 async with httpx.AsyncClient(timeout=45) as c:
  while seen<limit:
   p={'limit':100,'descending':1};
   if offset:p['offset']=offset
   f=await c.get(B,params=p);f.raise_for_status();body=f.json();rows=body.get('data',[])
   if not rows:break
   for row in rows:
    if seen>=limit:break
    seen+=1;r=await c.get(f"{B}/{row['id']}");r.raise_for_status();x=r.json().get('data',{});pub=dt(x.get('dateCreated') or x.get('dateModified'))
    if pub and pub<published_from:return out
    ddl=dt((x.get('tenderPeriod') or {}).get('endDate'))
    if not ddl or ddl<datetime.utcnow():continue
    items=x.get('items',[]);codes=[i.get('classification',{}).get('id','') for i in items];text=' '.join([x.get('title',''),x.get('description','')]+[i.get('description','') for i in items])
    if not relevant(codes,text):continue
    val=(x.get('value') or {}).get('amount');cur=(x.get('value') or {}).get('currency','UAH');ve=await eur_value(val,cur)
    if ve is None or ve<min_eur:continue
    n=x.get('tenderID',row['id']);out.append(Tender('prozorro:'+n,'prozorro','UKR',x.get('title') or n,(x.get('procuringEntity') or {}).get('name',''),val,cur,ddl,pub,x.get('status','active'),f'https://prozorro.gov.ua/tender/{n}',x.get('description',''),n,codes,value_eur=ve))
   offset=(body.get('next_page') or {}).get('offset')
   if not offset:break
 return out
