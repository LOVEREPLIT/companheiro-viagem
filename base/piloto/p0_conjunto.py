"""Piloto F1.0 — constrói o conjunto de 20 entidades: perguntas cegas (sem verdade) e verdade (separada)."""
import gzip, json, glob, re
from datetime import datetime, timezone
FAMOSAS = [742, 4390, 3503, 247, 808, 3289, 684, 2777, 3281, 3335]   # estrato A
HIPERLOCAIS = [463, 462, 74, 4524, 4195, 4197, 1191, 1491, 3362, 2657]  # estrato B
from datetime import timedelta
def ano_ms(ms): return (datetime(1970,1,1)+timedelta(milliseconds=ms)).year if ms is not None else None
verdade, cegas = [], []
for f in sorted(glob.glob("base/bruto/cml/toponimia-*.json.gz")):
    d = json.load(gzip.open(f, "rt", encoding="utf-8"))
    for x in d["features"]:
        a = x["attributes"]
        if a["TOP_ID"] in FAMOSAS + HIPERLOCAIS:
            anos = re.findall(r"\b(1[0-9]{3}|20[0-2][0-9])\b", a.get("LEGENDA") or "")
            verdade.append({"top_id": a["TOP_ID"], "estrato": "famosa" if a["TOP_ID"] in FAMOSAS else "hiperlocal",
                "designacao": a["DESIGNACAO"], "freguesia": d["freguesia"], "legenda": a.get("LEGENDA"),
                "anos_legenda": anos, "nome_anterior": a.get("DENOMINACOES_ANTERIORES"),
                "ano_edital": ano_ms(a.get("DATA_EDITAL")), "historial": a.get("HISTORIAL")})
            cegas.append({"top_id": a["TOP_ID"], "rua": a["DESIGNACAO"], "freguesia": d["freguesia"] + ", Lisboa"})
json.dump(verdade, open("base/piloto/verdade.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(cegas, open("base/piloto/perguntas_cegas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for v in verdade: print(v["top_id"], v["estrato"][:3], v["designacao"], "|", v["legenda"], "|", v["nome_anterior"], "|", v["ano_edital"])
