"""C0: descarrega a toponímia CML (Lumiar, Benfica) para base/bruto/cml/ (gz).
Casa a freguesia por token exacto (Benfica != São Domingos de Benfica)."""
import gzip, json, re, sys, datetime, urllib.parse, urllib.request
U = "https://services.arcgis.com/1dSrzEWVQn5kHHyK/arcgis/rest/services/Cultura_Toponimia/FeatureServer/0/query"
FREG = {"lumiar": "Lumiar", "benfica": "Benfica"}

def pagina(where, off):
    q = {"where": where, "outFields": "*", "returnGeometry": "true", "outSR": "4326",
         "resultOffset": off, "resultRecordCount": 1000, "f": "json"}
    with urllib.request.urlopen(U + "?" + urllib.parse.urlencode(q), timeout=60) as r:
        return json.load(r)

def main():
    hoje = datetime.date.today().isoformat()
    for slug, nome in FREG.items():
        feats, off = [], 0
        while True:
            d = pagina(f"FREGUESIAS LIKE '%{nome}%'", off)
            feats += d.get("features", [])
            if not d.get("exceededTransferLimit"): break
            off += 1000
        tok = lambda s: nome in [re.sub(r"\s*\(.*?\)", "", t).strip() for t in re.split(r"[;,]", s or "")]
        feats = [f for f in feats if tok(f["attributes"].get("FREGUESIAS"))]
        out = f"base/bruto/cml/toponimia-{slug}-{hoje}.json.gz"
        with gzip.open(out, "wt", encoding="utf-8") as g:
            json.dump({"fonte": U, "recolhido": hoje, "freguesia": nome, "features": feats}, g, ensure_ascii=False)
        print(slug, len(feats), out)
main()
