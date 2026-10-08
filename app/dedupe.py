import hashlib,re,unicodedata
def norm(v):return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',str(v or '')).encode('ascii','ignore').decode().lower()).strip()
def keys(x):
 out=[]
 if x.procurement_id:out.append(('id',x.country,x.procurement_id.lower()))
 raw='|'.join([x.country,norm(x.buyer),norm(x.title)[:180],x.deadline.date().isoformat() if x.deadline else '',str(round(x.value or 0,2)),x.currency])
 out.append(('fp',hashlib.sha256(raw.encode()).hexdigest()));return out
