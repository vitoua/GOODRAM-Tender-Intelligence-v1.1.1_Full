import httpx
CACHE={'EUR':1.0}
async def rates():
 if len(CACHE)>1:return CACHE
 try:
  async with httpx.AsyncClient(timeout=15) as c:
   r=await c.get('https://api.frankfurter.dev/v2/rates',params={'base':'EUR'});r.raise_for_status()
  for x in r.json():CACHE[x['quote'].upper()]=float(x['rate'])
 except:pass
 return CACHE
async def eur_value(value,currency):
 if value is None:return None
 r=await rates();cur=(currency or 'EUR').upper()
 return float(value) if cur=='EUR' else (float(value)/r[cur] if cur in r and r[cur] else None)
