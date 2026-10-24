"""Pontua campos fechados (profissao, nascimento, morte, ano_atribuicao) por modelo e estrato; consenso por família."""
import json, re, unicodedata, glob, os, collections
V = {v["top_id"]: v for v in json.load(open("base/piloto/verdade.json", encoding="utf-8"))}
def norm(s): return re.sub(r"[^a-z ]", "", unicodedata.normalize("NFD", (s or "").lower()).encode("ascii", "ignore").decode())
def verdade(v):
    a = v["anos_legenda"]
    return {"nascimento": int(a[0]) if len(a) >= 2 else None, "morte": int(a[1]) if len(a) >= 2 else None,
            "ano_atribuicao": v["ano_edital"], "profissao": v["legenda"]}
SIN = {"politico": "politic", "escritor": "escritor", "escritora": "escritor"}
def prof_ok(resp, leg):
    r = set(norm(resp).split()) - {"e", "de", "do", "da"}
    l = norm(leg)
    rad = lambda w: w[:5]
    return bool(r) and any(rad(w) in l for w in r if len(w) > 3)
def certo(c, resp, v):
    t = verdade(v)[c]
    if t is None: return None
    if c == "profissao": return prof_ok(str(resp), t)
    try: return int(resp) == t
    except: return False
FAM = {"haiku": "anthropic", "sonnet": "anthropic", "opus": "anthropic", "gemma4": "google", "qwen3-30b": "qwen", "qwen3.6": "qwen", "gpt-oss": "openai"}
CAMPOS = ["profissao", "nascimento", "morte", "ano_atribuicao"]
res = {}
for f in sorted(glob.glob("base/piloto/respostas/*.json")):
    m = os.path.basename(f)[:-5]
    if m not in FAM: continue
    R = {r["top_id"]: r for r in json.load(open(f, encoding="utf-8"))}
    for est in ("famosa", "hiperlocal"):
        n = af = ok = 0; per = 0
        for t, v in V.items():
            if v["estrato"] != est: continue
            for c in CAMPOS:
                if verdade(v)[c] is None: continue
                per += 1
                x = R.get(t, {}).get(c)
                if x in (None, "", "null"): continue
                af += 1; k = certo(c, x, v); ok += bool(k)
        res[(m, est)] = (per, af, ok)
        print(f"{m:10s} {est:10s} perguntadas={per} afirmadas={af} certas={ok} precisao={ok/af if af else 0:.0%} cobertura={af/per:.0%} erro_confiante={(af-ok)/per:.0%}")
