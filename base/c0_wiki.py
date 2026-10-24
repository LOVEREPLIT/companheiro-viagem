"""C0: Wikidata (rótulo, descrição, P569/P570, P31, ptwiki) para os QIDs do OSM (wikidata + name:etymology:wikidata) e
extractos da Wikipédia PT para os títulos encontrados. Licenças: Wikidata CC0, Wikipédia CC BY-SA 4.0."""
import gzip, json, glob, time, datetime, urllib.parse, urllib.request
hoje = datetime.date.today().isoformat()
UA = {"User-Agent": "companheiro-viagem/1.0 (base geo; jvmpcosta@gmail.com)"}
def get(u):
    for t in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60))
        except Exception as e: print(" retry", str(e)[:50]); time.sleep(5 * (t + 1))
    return {}
qids = set()
for f in glob.glob("base/bruto/osm/*.json.gz"):
    for e in json.load(gzip.open(f, "rt", encoding="utf-8"))["elementos"]:
        for k in ("wikidata", "name:etymology:wikidata", "subject:wikidata"):
            for q in (e.get("tags", {}).get(k) or "").split(";"):
                if q.strip().startswith("Q"): qids.add(q.strip())
qids = sorted(qids); print(len(qids), "QIDs")
ents = {}
for i in range(0, len(qids), 50):
    d = get("https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode({"action": "wbgetentities", "ids": "|".join(qids[i:i+50]), "props": "labels|descriptions|claims|sitelinks", "languages": "pt|en", "sitefilter": "ptwiki", "format": "json"}))
    for q, e in d.get("entities", {}).items():
        c = e.get("claims", {})
        val = lambda p: [x["mainsnak"]["datavalue"]["value"] for x in c.get(p, []) if "datavalue" in x["mainsnak"]]
        ents[q] = {"rotulo": (e.get("labels", {}).get("pt") or e.get("labels", {}).get("en") or {}).get("value"),
                   "descricao": (e.get("descriptions", {}).get("pt") or e.get("descriptions", {}).get("en") or {}).get("value"),
                   "nasc": [v["time"] for v in val("P569")], "morte": [v["time"] for v in val("P570")],
                   "instancia": [v["id"] for v in val("P31")], "ptwiki": e.get("sitelinks", {}).get("ptwiki", {}).get("title")}
    time.sleep(1)
tit = sorted({e["ptwiki"] for e in ents.values() if e["ptwiki"]}); wp = {}
for i in range(0, len(tit), 20):
    d = get("https://pt.wikipedia.org/w/api.php?" + urllib.parse.urlencode({"action": "query", "prop": "extracts", "exintro": 1, "explaintext": 1, "exlimit": 20, "titles": "|".join(tit[i:i+20]), "format": "json", "redirects": 1}))
    for p in d.get("query", {}).get("pages", {}).values(): wp[p.get("title")] = p.get("extract")
    time.sleep(1)
with gzip.open(f"base/bruto/wikidata-{hoje}.json.gz", "wt", encoding="utf-8") as g: json.dump({"fonte": "wikidata.org (CC0)", "recolhido": hoje, "entidades": ents}, g, ensure_ascii=False)
with gzip.open(f"base/bruto/wikipedia-pt-{hoje}.json.gz", "wt", encoding="utf-8") as g: json.dump({"fonte": "pt.wikipedia.org (CC BY-SA 4.0)", "recolhido": hoje, "extractos": wp}, g, ensure_ascii=False)
print(len(ents), "entidades;", len(wp), "extractos")
