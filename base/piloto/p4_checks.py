"""Checks automáticos (§5.3): números, anos e nomes próprios do facto têm de existir nas frases-âncora."""
import json, re, sys, unicodedata
def n(s): return unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()
F = {o["top_id"]: o for o in json.load(open("base/piloto/fonte_editor.json", encoding="utf-8"))}
def tokens(s):
    nums = re.findall(r"\d+", s)
    props = [w for m in re.finditer(r"(?<![.!?]\s)(?<!^)\b([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]{2,})", s) for w in [m.group(1)]]
    return nums, props
def verifica(f):
    o = F[f["top_id"]]
    fr = " ".join([o["legenda"]] + [o["frases"].get(str(a), "") for a in f.get("ancoras", [])])
    nf = n(fr); falhas = []
    nums, props = tokens(f["texto"] + " " + f.get("gancho", ""))
    for t in nums:
        if t not in fr: falhas.append("num:" + t)
    for t in props:
        if n(t) not in nf: falhas.append("nome:" + t)
    if not f.get("ancoras"): falhas.append("sem_ancora")
    return falhas
if __name__ == "__main__":
    fs = json.load(open(sys.argv[1], encoding="utf-8")); mal = 0
    for i, f in enumerate(fs):
        x = verifica(f); f["auto"] = x; mal += bool(x)
    json.dump(fs, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(fs), "factos;", mal, "reprovados nos checks automáticos")
