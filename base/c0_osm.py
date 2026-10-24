"""C0: Overpass por freguesia (area da relação). 15 s entre pedidos, repete em 429/504. Grava polígono + elementos."""
import gzip, json, time, datetime, urllib.parse, urllib.request
REL = {"lumiar": 6384124, "benfica": 6385130}
EP = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"]
def pede(q):
    for t in range(8):
        for ep in EP:
            try:
                req = urllib.request.Request(ep, urllib.parse.urlencode({"data": q}).encode(), {"User-Agent": "companheiro-viagem/1.0 (base geo)"})
                return json.load(urllib.request.urlopen(req, timeout=180))
            except Exception as e:
                print("  retry", ep[8:25], str(e)[:40]); time.sleep(15)
    raise SystemExit("Overpass indisponível")
hoje = datetime.date.today().isoformat()
for slug, rid in REL.items():
    a = 3600000000 + rid
    q1 = f"[out:json][timeout:120];rel({rid});out geom;"
    q2 = f"""[out:json][timeout:150];area({a})->.a;(
 nwr(area.a)[historic];nwr(area.a)[tourism~"museum|attraction|artwork|viewpoint|gallery"];nwr(area.a)[amenity=place_of_worship];
 nwr(area.a)[wikidata][name];way(area.a)[highway][name];nwr(area.a)[memorial];nwr(area.a)[shop][heritage];nwr(area.a)[building][name];
 );out tags center;"""
    pol = pede(q1); time.sleep(15); els = pede(q2); time.sleep(15)
    with gzip.open(f"base/bruto/osm/{slug}-{hoje}.json.gz", "wt", encoding="utf-8") as g:
        json.dump({"fonte": "Overpass (ODbL)", "recolhido": hoje, "relacao": rid, "poligono": pol, "elementos": els["elements"]}, g, ensure_ascii=False)
    print(slug, len(els["elements"]))
