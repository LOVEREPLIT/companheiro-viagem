#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor de factos — protótipo do Companheiro de Viagem.

Dada uma coordenada, devolve factos VERIFICÁVEIS sobre o local, em 4 canais:
    HISTÓRIA · ECONOMIA · DEMOGRAFIA · ACTUALIDADE

Fontes (todas gratuitas, sem chave de API):
    · Wikipédia PT/EN   — artigos por geolocalização
    · Wikidata          — população, área, altitude, fundação
    · Nominatim (OSM)   — freguesia / concelho / distrito
    · Overpass (OSM)    — pontos de interesse próximos (modo a pé)
    · Google News RSS   — notícias recentes da localidade

Não há modelo de linguagem aqui. De propósito: este protótipo serve para
verificar se as FONTES chegam. A narração vem depois.

Uso:
    python factos.py --coord 38.7075,-9.1364 --modo pe
    python factos.py --rota baixa-lisboa
    python factos.py --rota a1 --modo carro
    python factos.py --gpx viagem.gpx --pontos 8
    python factos.py --listar-rotas
"""

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).resolve().parent
CACHE = BASE / ".cache"
SAIDA = BASE / "saida"
UA = "companheiro-viagem-prototipo/0.1 (uso pessoal; contacto via GitHub)"

# Intervalo mínimo entre pedidos, por servidor (política de uso do OSM: 1 req/s)
THROTTLE = {"nominatim.openstreetmap.org": 1.2, "overpass-api.de": 1.5}
_ultimo = {}


# ─────────────────────────────────────────────────────────── HTTP + cache ──

def _http(url, data=None, ttl=86400 * 7):
    """GET/POST com cache em disco. `data` (str) transforma em POST."""
    chave = hashlib.sha256((url + "|" + (data or "")).encode()).hexdigest()[:32]
    fich = CACHE / f"{chave}.txt"
    if fich.exists() and (time.time() - fich.stat().st_mtime) < ttl:
        return fich.read_text(encoding="utf-8")

    host = urllib.parse.urlparse(url).netloc
    espera = THROTTLE.get(host, 0.15)
    decorrido = time.time() - _ultimo.get(host, 0)
    if decorrido < espera:
        time.sleep(espera - decorrido)
    _ultimo[host] = time.time()

    pedido = urllib.request.Request(
        url,
        data=data.encode("utf-8") if data else None,
        headers={"User-Agent": UA, "Accept": "application/json, text/xml, */*"},
    )
    try:
        with urllib.request.urlopen(pedido, timeout=30) as r:
            corpo = r.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"   [aviso] falhou {host}: {e}", file=sys.stderr)
        return ""

    CACHE.mkdir(exist_ok=True)
    fich.write_text(corpo, encoding="utf-8")
    return corpo


def _json(url, data=None, ttl=86400 * 7):
    bruto = _http(url, data, ttl)
    if not bruto:
        return {}
    try:
        return json.loads(bruto)
    except json.JSONDecodeError:
        return {}


# ──────────────────────────────────────────────────────────────── fontes ──

def nominatim(lat, lon, zoom=14):
    """Onde estamos, em termos administrativos."""
    url = (f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}"
           f"&format=jsonv2&zoom={zoom}&addressdetails=1&accept-language=pt")
    return _json(url)


def wiki_geosearch(lat, lon, lang="pt", raio=10000, limite=30):
    """Artigos da Wikipédia com coordenadas dentro do raio (metros)."""
    url = (f"https://{lang}.wikipedia.org/w/api.php?action=query&format=json"
           f"&formatversion=2&list=geosearch&gscoord={lat}%7C{lon}"
           f"&gsradius={min(raio, 10000)}&gslimit={limite}")
    return _json(url).get("query", {}).get("geosearch", [])


def wiki_paginas(pageids, lang="pt", so_intro=True):
    """Introdução (ou texto completo), URL e Q-id do Wikidata."""
    res = {}
    for i in range(0, len(pageids), 20):
        lote = pageids[i:i + 20]
        url = (f"https://{lang}.wikipedia.org/w/api.php?action=query&format=json"
               f"&formatversion=2&prop=extracts%7Cpageprops%7Cinfo"
               f"&explaintext=1&exlimit=20&inprop=url&ppprop=wikibase_item"
               f"{'&exintro=1' if so_intro else ''}"
               f"&pageids={'%7C'.join(str(p) for p in lote)}")
        for p in _json(url).get("query", {}).get("pages", []):
            res[p["pageid"]] = p
    return res


def wikidata(qids):
    """Afirmações estruturadas para os Q-ids indicados."""
    if not qids:
        return {}
    url = ("https://www.wikidata.org/w/api.php?action=wbgetentities&format=json"
           f"&ids={'%7C'.join(qids)}&props=claims&languages=pt%7Cen")
    return _json(url).get("entities", {})


def overpass(lat, lon, raio=400):
    """Pontos de interesse concretos à volta — o que se vê a pé."""
    q = (f"[out:json][timeout:25];("
         f'node(around:{raio},{lat},{lon})["historic"];'
         f'way(around:{raio},{lat},{lon})["historic"];'
         f'node(around:{raio},{lat},{lon})["tourism"~"^(attraction|museum|artwork|viewpoint|gallery)$"];'
         f'way(around:{raio},{lat},{lon})["tourism"~"^(attraction|museum|artwork|viewpoint|gallery)$"];'
         f");out center tags 60;")
    d = _json("https://overpass-api.de/api/interpreter",
              data=urllib.parse.urlencode({"data": q}))
    return d.get("elements", [])


def noticias(nome, limite=4):
    """Notícias recentes que mencionem a localidade."""
    q = urllib.parse.quote(f'"{nome}" when:120d')
    url = f"https://news.google.com/rss/search?q={q}&hl=pt-PT&gl=PT&ceid=PT:pt-150"
    bruto = _http(url, ttl=3600 * 6)          # notícias: cache curta
    if not bruto:
        return []
    try:
        raiz = ET.fromstring(bruto)
    except ET.ParseError:
        return []
    saida = []
    for item in list(raiz.iterfind(".//item"))[:limite]:
        fonte = item.find("source")
        saida.append({
            "titulo": (item.findtext("title") or "").strip(),
            "link": (item.findtext("link") or "").strip(),
            "data": (item.findtext("pubDate") or "").strip(),
            "fonte": (fonte.text if fonte is not None else "") or "",
        })
    return saida


# ─────────────────────────────────────────────────────────────── selecção ──

BONUS = ("castelo", "igreja", "mosteiro", "convento", "palácio", "ponte",
         "forte", "fortaleza", "museu", "aqueduto", "ruínas", "solar",
         "capela", "torre", "teatro", "sé de", "praça", "miradouro",
         "santuário", "estação", "farol", "moinho", "pelourinho")

VETO = ("lista de", "anexo:", "desambiguação", "categoria:", "(álbum)",
        "(filme)", "(banda)", "campeonato", "temporada de")

# "é uma cidade", "é a cidade", "é o bairro", "is a town"… — tudo conta
RE_POVOACAO = re.compile(
    r"\b(é|foi)\s+(uma?|a|o)\s+(antiga\s+|pequena\s+|grande\s+)?"
    r"(cidade|vila|freguesia|aldeia|munic[íi]pio|concelho|bairro|localidade|"
    r"capital|povoa[çc][ãa]o|distrito)"
    r"|\bis\s+(a|the)\s+(former\s+)?(town|city|village|civil parish|"
    r"municipality|parish|district)\b", re.I)

EXTINTA = ("foi uma freguesia", "antiga freguesia", "foi extinta",
           "era uma freguesia", "former civil parish", "extinta em")

# Secções da Wikipédia que são economia a sério, não história económica
SECCAO_ECONOMIA = ("economia", "atividade económica", "actividade económica",
                   "economia e demografia", "sectores de atividade",
                   "setores de atividade", "agricultura e economia")

ECONOMIA_FORTE = ("economia", "económic", "indústria", "industrial",
                  "agricultura", "turismo", "comércio", "pesca", "vinho",
                  "produção", "fábrica", "empresas", "emprego", "exporta",
                  "minas", "pecuária", "cortiça", "olival")

ECONOMIA_KW = ECONOMIA_FORTE + ("produz", "empresa", "porto", "cooperativa",
                                "mercado", "artesanato", "cultivo", "sector",
                                "rendimento", "trabalhadores")


def _limpa(txt):
    txt = re.sub(r"={2,}[^=\n]{0,80}={2,}", " ", txt or "")   # títulos de secção
    txt = re.sub(r"\s+", " ", txt).strip()
    return re.sub(r"\(\s*\)", "", txt)


def _seccoes(txt):
    """Parte o texto simples da Wikipédia em {título de secção: corpo}."""
    partes = re.split(r"\n=+\s*([^=\n]{1,80}?)\s*=+\n", "\n" + (txt or ""))
    fora = {"": partes[0]}
    for i in range(1, len(partes) - 1, 2):
        fora[partes[i].strip().lower()] = partes[i + 1]
    return fora


def _frases(txt, n=3):
    partes = re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Þ0-9])", _limpa(txt))
    return " ".join(partes[:n])


def pontua(art, pagina, modo):
    titulo = (art.get("title") or "").lower()
    extracto = pagina.get("extract") or ""
    dist = art.get("dist", 0)

    if any(v in titulo for v in VETO):
        return -999

    s = 0.0
    s -= dist / (120 if modo == "carro" else 12)   # a pé, longe pesa muito mais

    n = len(extracto)
    if n > 700:
        s += 30
    elif n > 350:
        s += 20
    elif n > 150:
        s += 8
    else:
        s -= 45                                    # esboço: não vale contar

    cabeca = extracto[:400].lower()
    if any(b in titulo for b in BONUS):
        s += 22
    if RE_POVOACAO.search(cabeca):
        s += (25 if modo == "carro" else 5)        # de carro, interessa a terra
    if any(x in cabeca for x in EXTINTA):
        s -= 55                                    # freguesia extinta em 2013
    return s


def escolhe(lat, lon, modo, quantos=3):
    """Devolve os melhores artigos para este ponto, já com texto."""
    raio = 9000 if modo == "carro" else 700
    artigos = wiki_geosearch(lat, lon, "pt", raio)
    lang = "pt"
    if len(artigos) < 2:                            # zona sem cobertura em PT
        alt = wiki_geosearch(lat, lon, "en", raio)
        if len(alt) > len(artigos):
            artigos, lang = alt, "en"
    if not artigos:
        return [], lang

    paginas = wiki_paginas([a["pageid"] for a in artigos], lang)

    marcados = []
    for a in artigos:
        p = paginas.get(a["pageid"], {})
        marcados.append((pontua(a, p, modo), a, p))
    marcados.sort(key=lambda t: -t[0])

    escolhidos, vistos = [], []
    for s, a, p in marcados:
        if s < -100:
            continue
        t = a["title"].lower()
        if any(t in v or v in t for v in vistos):    # evita repetir o mesmo tema
            continue
        vistos.append(t)
        escolhidos.append({
            "titulo": a["title"],
            "dist_m": round(a.get("dist", 0)),
            "pontos": round(s, 1),
            "texto": _frases(p.get("extract", ""), 3),
            "fonte": p.get("fullurl", ""),
            "qid": (p.get("pageprops") or {}).get("wikibase_item"),
            "extracto_completo": p.get("extract", ""),
            "pageid": a["pageid"],
        })
        if len(escolhidos) >= quantos:
            break
    return escolhidos, lang


# ──────────────────────────────────────────────────────── canais temáticos ──

def _claim(ent, prop):
    """Melhor valor de uma propriedade Wikidata (o mais recente, se datado)."""
    cs = (ent.get("claims") or {}).get(prop) or []
    melhor, melhor_data = None, None
    for c in cs:
        dv = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if dv is None:
            continue
        val = dv.get("amount", dv.get("time", dv)) if isinstance(dv, dict) else dv
        quando = None
        for q in (c.get("qualifiers") or {}).get("P585", []):
            quando = ((q.get("datavalue") or {}).get("value") or {}).get("time")
        # o valor datado mais recente ganha; um valor sem data nunca
        # substitui um datado (senão atribuímos-lhe o ano errado)
        if melhor is None or (quando and (melhor_data is None or quando > melhor_data)):
            melhor, melhor_data = val, quando
    return melhor, melhor_data or ""


def _num(v):
    try:
        return float(str(v).lstrip("+"))
    except (TypeError, ValueError):
        return None


def canal_demografia(candidatos):
    """População/área/altitude — da LOCALIDADE, não dos monumentos ao lado."""
    qids = [e["qid"] for e in candidatos if e.get("qid")][:4]
    ents = wikidata(qids)
    linhas, fontes = [], []
    for e in candidatos:
        ent = ents.get(e.get("qid") or "")
        if not ent:
            continue
        pop, ano = _claim(ent, "P1082")
        area, _ = _claim(ent, "P2046")
        alt, _ = _claim(ent, "P2044")
        pop, area, alt = _num(pop), _num(area), _num(alt)
        if pop is None and alt is None:
            continue
        bits = []
        if pop:
            a = f" (censos de {ano[1:5]})" if ano else ""
            bits.append(f"{int(pop):,} habitantes{a}".replace(",", " "))
        if pop and area:
            bits.append(f"{pop / area:.0f} hab/km² em {area:.0f} km²")
        elif area:
            bits.append(f"{area:.0f} km²")
        if alt:
            bits.append(f"{alt:.0f} m de altitude")
        if bits:
            linhas.append(f"{e['titulo']}: " + "; ".join(bits))
            fontes.append(f"https://www.wikidata.org/wiki/{e['qid']}")
    return linhas, fontes


def canal_economia(candidatos, lang):
    """Frases do artigo COMPLETO da localidade que falem de economia.
    Heurística por palavras-chave — é o canal mais fraco, ver README."""
    alvos = [e for e in candidatos if e.get("pageid")][:2]
    if not alvos:
        return [], []
    completos = wiki_paginas([e["pageid"] for e in alvos], lang, so_intro=False)
    linhas, fontes = [], []
    for e in alvos:
        txt = (completos.get(e["pageid"], {}) or {}).get("extract", "")

        # 1.ª escolha: a secção "Economia" do artigo. É o que descreve o presente.
        secs = _seccoes(txt)
        alvo = next((v for k, v in secs.items()
                     if any(k.startswith(s) for s in SECCAO_ECONOMIA)), None)
        if alvo and len(_limpa(alvo)) > 80:
            linhas.append(f"{e['titulo']}: {_frases(alvo, 3)}")
            fontes.append(e["fonte"])
            continue

        # 2.ª escolha: pescar frases por palavras-chave em todo o artigo.
        frases = re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Þ0-9])", _limpa(txt))
        bons = []
        for f in frases:
            if len(f) < 60 or len(f) > 400:
                continue
            fl = f.lower()
            forca = sum(k in fl for k in ECONOMIA_FORTE)
            if not forca:
                continue
            peso = forca + sum(k in fl for k in ECONOMIA_KW)
            if re.search(r"século|\b1[0-9]{3}\b", fl):
                peso -= 5          # isto é história, não é economia de hoje
            if re.search(r"principa|actualmente|atualmente|hoje|concentra|"
                         r"emprega|baseia-se|assenta|predomina|sedeada", fl):
                peso += 3          # afirmação sobre o presente
            bons.append((peso, f))
        bons.sort(key=lambda t: -t[0])
        for _, f in bons[:2]:
            linha = f"{e['titulo']}: {f}"
            if linha not in linhas:
                linhas.append(linha)
        if bons:
            fontes.append(e["fonte"])
    return linhas, fontes


def artigos_localidade(local, lat, lon, lang="pt"):
    """Encontra o artigo da freguesia/concelho onde estamos — a base de
    demografia e economia. Confirma pelas coordenadas para não apanhar
    homónimos noutro ponto do país."""
    nomes, vistos = [], set()
    for n in (local.get("freguesia"), local.get("concelho"), local.get("distrito")):
        if n and n.lower() not in vistos:
            vistos.add(n.lower())
            nomes.append(n)
    if not nomes:
        return []

    concelho = (local.get("concelho") or "").lower()
    candidatos, ids = [], set()
    for nome in nomes[:3]:
        url = (f"https://{lang}.wikipedia.org/w/api.php?action=query&format=json"
               f"&formatversion=2&generator=search&gsrsearch="
               f"{urllib.parse.quote(nome)}&gsrlimit=6"
               f"&prop=extracts%7Cpageprops%7Cinfo%7Ccoordinates"
               f"&exintro=1&explaintext=1&exlimit=6&inprop=url&ppprop=wikibase_item")
        for p in _json(url).get("query", {}).get("pages", []):
            co = (p.get("coordinates") or [{}])[0]
            if not co.get("lat") or p["pageid"] in ids:
                continue
            if _dist_km(lat, lon, co["lat"], co["lon"]) > 60:
                continue                      # homónimo noutro ponto do país
            ext = p.get("extract") or ""
            cabeca = ext[:400].lower()
            if not RE_POVOACAO.search(cabeca):
                continue                      # não é uma povoação

            s = len(ext) / 250
            if p["title"].lower() == concelho:
                s += 50                       # é mesmo a terra onde estamos
            if re.search(r"\bé\s+(uma?|a|o)\s+(cidade|vila|munic[íi]pio)", cabeca):
                s += 25
            if any(x in cabeca for x in EXTINTA):
                s -= 70                       # freguesia extinta: não descreve hoje
            ids.add(p["pageid"])
            candidatos.append((s, {
                "titulo": p["title"], "pageid": p["pageid"],
                "fonte": p.get("fullurl", ""),
                "qid": (p.get("pageprops") or {}).get("wikibase_item"),
            }))

    candidatos.sort(key=lambda t: -t[0])
    return [c for s, c in candidatos if s > -40][:2]


def nome_para_noticias(local):
    """O concelho dá muito melhores notícias do que o nome oficial da união
    de freguesias. 'Évora (São Mamede, Sé, ...)' → 'Évora'."""
    for n in (local.get("concelho"), local.get("freguesia"), local.get("distrito")):
        if not n:
            continue
        n = re.sub(r"\s*\(.*?\)\s*$", "", n)                        # tira parênteses
        n = re.sub(r"^(União (das|de) Freguesias de|Uni[aã]o de)\s+", "", n, flags=re.I)
        n = re.split(r"\s+e\s+", n)[0] if n.count(" e ") else n     # 1.º nome da união
        n = n.strip()
        if len(n) > 2:
            return n
    return ""


def _dist_km(la1, lo1, la2, lo2):
    from math import radians, sin, cos, asin, sqrt
    la1, lo1, la2, lo2 = map(radians, (la1, lo1, la2, lo2))
    h = sin((la2 - la1) / 2) ** 2 + cos(la1) * cos(la2) * sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * asin(sqrt(h))


def canal_actualidade(local, escolhidos):
    nome = nome_para_noticias(local) or (escolhidos[0]["titulo"] if escolhidos else "")
    if not nome:
        return [], []
    itens = noticias(nome)
    linhas = [f"{i['titulo']}  —  {i['fonte']}" for i in itens]
    return linhas, [i["link"] for i in itens]


# ───────────────────────────────────────────────────────────────── ponto ──

def onde_estou(lat, lon):
    n = nominatim(lat, lon)
    a = n.get("address", {}) or {}
    freguesia = a.get("suburb") or a.get("village") or a.get("town") or a.get("city_district") or a.get("parish")
    concelho = a.get("municipality") or a.get("city") or a.get("town") or a.get("county")
    distrito = a.get("district") or a.get("state") or a.get("region")
    curto = freguesia or concelho or distrito or ""
    return {
        "freguesia": freguesia, "concelho": concelho, "distrito": distrito,
        "pais": a.get("country"), "nome_curto": curto,
        "linha": " · ".join(x for x in (freguesia, concelho, distrito) if x) or (n.get("display_name") or "—"),
    }


def analisa(lat, lon, modo="carro"):
    local = onde_estou(lat, lon)
    escolhidos, lang = escolhe(lat, lon, modo)

    historia = [{"texto": e["texto"], "fonte": e["fonte"],
                 "titulo": e["titulo"], "dist_m": e["dist_m"]} for e in escolhidos]

    # Demografia e economia descrevem a TERRA onde estamos; se não houver
    # artigo da localidade, recorre-se ao que foi encontrado por perto.
    base = artigos_localidade(local, lat, lon, lang) or escolhidos
    demo, demo_f = canal_demografia(base)
    econ, econ_f = canal_economia(base, lang)
    news, news_f = canal_actualidade(local, escolhidos)

    poi = []
    if modo == "pe":
        for el in overpass(lat, lon)[:12]:
            t = el.get("tags", {}) or {}
            nome = t.get("name") or t.get("name:pt")
            if not nome:
                continue
            tipo = t.get("historic") or t.get("tourism") or ""
            if tipo in ("toilets", "yes", ""):
                continue
            poi.append(f"{nome} ({tipo})")

    return {
        "coord": [lat, lon], "modo": modo, "lingua_wiki": lang,
        "local": local,
        "canais": {
            "HISTORIA": {"itens": historia, "fontes": [h["fonte"] for h in historia]},
            "ECONOMIA": {"itens": econ, "fontes": econ_f},
            "DEMOGRAFIA": {"itens": demo, "fontes": demo_f},
            "ACTUALIDADE": {"itens": news, "fontes": news_f},
        },
        "poi_visiveis": poi,
    }


# ─────────────────────────────────────────────────────────────── relatório ──

def mostra(r):
    lat, lon = r["coord"]
    print("\n" + "═" * 78)
    print(f" {r['local']['linha']}")
    print(f" {lat:.5f}, {lon:.5f}   ·   modo: {r['modo']}   ·   wiki: {r['lingua_wiki']}")
    print("═" * 78)

    h = r["canais"]["HISTORIA"]["itens"]
    print(f"\n▸ HISTÓRIA  ({len(h)})")
    if not h:
        print("   — nada encontrado —")
    for i in h:
        print(f"\n   [{i['dist_m']} m] {i['titulo']}")
        for linha in _quebra(i["texto"]):
            print(f"   {linha}")
        print(f"   ↳ {i['fonte']}")

    for nome in ("DEMOGRAFIA", "ECONOMIA", "ACTUALIDADE"):
        c = r["canais"][nome]
        print(f"\n▸ {nome}  ({len(c['itens'])})")
        if not c["itens"]:
            print("   — nada encontrado —")
        for it in c["itens"]:
            for linha in _quebra(it):
                print(f"   {linha}")
            print()
        if c["fontes"]:
            print(f"   ↳ {c['fontes'][0]}")

    if r["poi_visiveis"]:
        print(f"\n▸ À VOLTA (OSM, 400 m)")
        print("   " + " · ".join(r["poi_visiveis"]))
    print()


def _quebra(txt, largura=72):
    palavras, linhas, atual = _limpa(txt).split(), [], ""
    for p in palavras:
        if len(atual) + len(p) + 1 > largura:
            linhas.append(atual)
            atual = p
        else:
            atual = f"{atual} {p}".strip()
    if atual:
        linhas.append(atual)
    return linhas or [""]


# ────────────────────────────────────────────────────────────────── rotas ──

ROTAS = {
    "baixa-lisboa": ("pe", [
        (38.7075, -9.1364, "Praça do Comércio"),
        (38.7104, -9.1385, "Rua Augusta"),
        (38.7139, -9.1394, "Rossio"),
        (38.7098, -9.1330, "Sé de Lisboa"),
        (38.7139, -9.1335, "Castelo de São Jorge"),
    ]),
    "a1": ("carro", [
        (38.7700, -9.1000, "saída de Lisboa"),
        (39.0300, -8.8400, "Azambuja"),
        (39.2400, -8.6900, "Santarém"),
        (39.7400, -8.8100, "Fátima / Leiria"),
        (40.2100, -8.4300, "Coimbra"),
        (40.6400, -8.6300, "Aveiro"),
        (41.1300, -8.6100, "Vila Nova de Gaia"),
    ]),
    "alentejo": ("carro", [
        (38.4430, -7.3810, "Monsaraz"),
        (38.5700, -7.9070, "Évora"),
        (38.2400, -7.5400, "Reguengos / interior"),
        (37.9600, -7.9800, "Beja"),
        (38.1100, -7.1600, "raia, perto de Barrancos"),
    ]),
    "douro": ("carro", [
        (41.1600, -7.7900, "Peso da Régua"),
        (41.1900, -7.5400, "Pinhão"),
        (41.2400, -7.4200, "Tua"),
    ]),
}


def le_gpx(caminho, n=6):
    raiz = ET.parse(caminho).getroot()
    ns = {"g": raiz.tag.split("}")[0].strip("{")} if "}" in raiz.tag else {}
    pontos = raiz.findall(".//g:trkpt", ns) if ns else raiz.findall(".//trkpt")
    if not pontos:
        pontos = raiz.findall(".//g:wpt", ns) if ns else raiz.findall(".//wpt")
    if not pontos:
        return []
    passo = max(1, len(pontos) // n)
    amostra = pontos[::passo][:n]
    return [(float(p.get("lat")), float(p.get("lon")), f"ponto {i+1}")
            for i, p in enumerate(amostra)]


# ─────────────────────────────────────────────────────────────────── main ──

def main():
    ap = argparse.ArgumentParser(description="Motor de factos — Companheiro de Viagem")
    ap.add_argument("--coord", help="lat,lon")
    ap.add_argument("--rota", help=f"rota de teste: {', '.join(ROTAS)}")
    ap.add_argument("--gpx", help="ficheiro .gpx de uma viagem real")
    ap.add_argument("--pontos", type=int, default=6, help="pontos a amostrar do GPX")
    ap.add_argument("--modo", choices=["carro", "pe"], help="sobrepõe o modo da rota")
    ap.add_argument("--listar-rotas", action="store_true")
    a = ap.parse_args()

    if a.listar_rotas:
        for nome, (modo, pts) in ROTAS.items():
            print(f"  {nome:16s} [{modo}]  {len(pts)} pontos — {pts[0][2]} → {pts[-1][2]}")
        return

    if a.coord:
        lat, lon = (float(x) for x in a.coord.replace(" ", "").split(","))
        pontos, modo = [(lat, lon, "ponto")], a.modo or "carro"
    elif a.rota:
        if a.rota not in ROTAS:
            sys.exit(f"rota desconhecida. Disponíveis: {', '.join(ROTAS)}")
        modo_r, pontos = ROTAS[a.rota]
        modo = a.modo or modo_r
    elif a.gpx:
        pontos, modo = le_gpx(a.gpx, a.pontos), a.modo or "carro"
        if not pontos:
            sys.exit("não encontrei pontos nesse GPX.")
    else:
        ap.print_help()
        return

    t0 = time.time()
    resultados = []
    for i, (lat, lon, etiqueta) in enumerate(pontos, 1):
        print(f"\n[{i}/{len(pontos)}] {etiqueta} …", flush=True)
        r = analisa(lat, lon, modo)
        r["etiqueta"] = etiqueta
        resultados.append(r)
        mostra(r)

    SAIDA.mkdir(exist_ok=True)
    nome = a.rota or (Path(a.gpx).stem if a.gpx else "ponto")
    dest = SAIDA / f"{nome}-{datetime.now():%Y%m%d-%H%M}.json"
    dest.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")

    vazios = sum(1 for r in resultados for c in r["canais"].values() if not c["itens"])
    total = len(resultados) * 4
    print("─" * 78)
    print(f"{len(pontos)} pontos em {time.time() - t0:.0f}s   ·   "
          f"canais com conteúdo: {total - vazios}/{total}")
    print(f"JSON: {dest}")


if __name__ == "__main__":
    main()
