"""Piloto: corre as perguntas cegas num modelo Ollama, com portão de VRAM.
uso: python p2_local.py <modelo> <GB_necessários> <saida.json>
Se o modelo já está carregado (ollama ps) não pede VRAM extra. Aborta se a VRAM livre cair abaixo de 1,5 GB."""
import json, subprocess, sys, time, urllib.request
modelo, gb, saida = sys.argv[1], float(sys.argv[2]), sys.argv[3]
livre = lambda: int(subprocess.check_output(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"]).split()[0]) / 1024
carregado = modelo in subprocess.check_output(["ollama", "ps"], text=True)
if not carregado and livre() < gb + 2:
    sys.exit(f"PORTÃO: VRAM livre {livre():.1f} GB < {gb+2:.1f} GB; não corro {modelo}")
ruas = json.load(open("base/piloto/perguntas_cegas.json", encoding="utf-8"))
P = ("Responde de memória, sem pesquisar. Rua de Lisboa: {rua} ({freguesia}). Sobre o homenageado do nome da rua, devolve só JSON com as chaves: "
     "profissao (1-4 palavras ou null), nascimento (ano ou null), morte (ano ou null), ano_atribuicao (ano em que a Câmara de Lisboa deu o nome à rua, ou null), "
     "facto (uma frase com um facto marcante, ou null). 'Não sei' (null) é valorizado; uma resposta errada e confiante é pior. Não adivinhes. PT-PT.")
out = []
for r in ruas:
    if livre() < 1.5 and not carregado: sys.exit("ABORTA: VRAM livre caiu")
    body = {"model": modelo, "prompt": P.format(**r), "stream": False, "format": "json", "think": False,
            "options": {"temperature": 0, "num_ctx": 4096}, "keep_alive": "2m"}
    req = urllib.request.Request("http://127.0.0.1:11434/api/generate", json.dumps(body).encode(), {"Content-Type": "application/json"})
    try:
        txt = json.load(urllib.request.urlopen(req, timeout=300))["response"]
        d = json.loads(txt)
    except Exception as e:
        d = {"erro": str(e)[:80]}
    d["top_id"] = r["top_id"]; out.append(d); time.sleep(1)
json.dump(out, open(saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", len(out))
