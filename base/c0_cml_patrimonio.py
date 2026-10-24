"""C0: património CML (camadas 11 e 12) e casas religiosas, Lisboa inteira (pequeno); filtragem por freguesia em C1 (polígono)."""
import gzip, json, datetime, urllib.parse, urllib.request
B = "https://services.arcgis.com/1dSrzEWVQn5kHHyK/arcgis/rest/services/"
CAM = {"patrimonio11": B + "Patrimonio/FeatureServer/11", "patrimonio12": B + "Patrimonio/FeatureServer/12", "casas_religiosas": B + "Cultura_CasasReligiosas/FeatureServer/0"}
hoje = datetime.date.today().isoformat()
for nome, u in CAM.items():
    q = urllib.parse.urlencode({"where": "1=1", "outFields": "*", "returnGeometry": "true", "outSR": "4326", "resultRecordCount": 2000, "f": "json"})
    d = json.load(urllib.request.urlopen(u + "/query?" + q, timeout=90))
    with gzip.open(f"base/bruto/cml/{nome}-{hoje}.json.gz", "wt", encoding="utf-8") as g:
        json.dump({"fonte": u, "recolhido": hoje, "features": d["features"], "campos": [f["name"] for f in d.get("fields", [])]}, g, ensure_ascii=False)
    print(nome, len(d["features"]), [f["name"] for f in d.get("fields", [])][:14])
