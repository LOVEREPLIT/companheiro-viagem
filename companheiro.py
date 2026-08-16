#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Companheiro de Viagem — modo contínuo (protótipo de PC).

Não há destino. Liga-se, e ele fala sobre onde estás e o que vem a seguir:

  · deduz a VELOCIDADE e o RUMO da tua posição (carro vs. a pé, automático);
  · PREVÊ onde vais estar daqui a uns minutos — projecta a posição ao longo
    do rumo actual — e vai buscar factos desse ponto ANTES de lá chegares;
  · lê tudo EM VOZ ALTA (voz portuguesa do Windows, via voz.ps1);
  · aceita "steering" de canal a qualquer momento, por teclas — que no
    telemóvel serão palavras ditas:

        1 história   2 economia   3 demografia   4 actualidade
        s silêncio (liga/desliga)   q sair

A rota/GPX aqui NÃO é um destino: é o GPS simulado, porque um PC não anda.
A lógica nunca olha para o fim da rota — só para a posição, velocidade e
rumo actuais, exactamente como fará no telemóvel com GPS real.

Uso (no teu PC, PowerShell, nesta pasta):

    python companheiro.py --rota a1 --turbo 60
    python companheiro.py --rota baixa-lisboa --turbo 20
    python companheiro.py --gpx viagem.gpx --turbo 30
    python companheiro.py --sem-voz --rota alentejo --turbo 200   # só texto

--turbo N acelera o tempo N vezes (60 = uma hora de viagem em um minuto).
"""

import argparse
import queue
import re
import subprocess
import sys
import tempfile
import threading
import time
from bisect import bisect_right
from math import asin, atan2, cos, degrees, radians, sin
from pathlib import Path
import xml.etree.ElementTree as ET

import factos

BASE = Path(__file__).resolve().parent
CANAIS = ("HISTORIA", "ECONOMIA", "DEMOGRAFIA", "ACTUALIDADE")
TECLA_CANAL = {"1": "HISTORIA", "2": "ECONOMIA", "3": "DEMOGRAFIA", "4": "ACTUALIDADE"}

INTRO = {
    "HISTORIA": "Mais à frente, perto de {nome}.",
    "ECONOMIA": "Sobre a economia de {nome}.",
    "DEMOGRAFIA": "Alguns números sobre {nome}.",
    "ACTUALIDADE": "Notícias de {nome}.",
}

# ───────────────────────────────────────────────────────────── geometria ──

def rumo_graus(la1, lo1, la2, lo2):
    la1, la2 = radians(la1), radians(la2)
    dlo = radians(lo2 - lo1)
    x = sin(dlo) * cos(la2)
    y = cos(la1) * sin(la2) - sin(la1) * cos(la2) * cos(dlo)
    return (degrees(atan2(x, y)) + 360) % 360


def avanca(lat, lon, rumo, dist_m):
    """Ponto a dist_m na direcção do rumo — a previsão 'o que vem a seguir'."""
    R = 6371000.0
    d, th = dist_m / R, radians(rumo)
    la1, lo1 = radians(lat), radians(lon)
    la2 = asin(sin(la1) * cos(d) + cos(la1) * sin(d) * cos(th))
    lo2 = lo1 + atan2(sin(th) * sin(d) * cos(la1), cos(d) - sin(la1) * sin(la2))
    return degrees(la2), degrees(lo2)


class Percurso:
    """Polilinha com interpolação por distância — faz de GPS."""

    def __init__(self, pontos):
        self.p = pontos
        self.acum = [0.0]
        for i in range(1, len(pontos)):
            d = factos._dist_km(*pontos[i - 1], *pontos[i]) * 1000
            self.acum.append(self.acum[-1] + d)
        self.total = self.acum[-1]

    def em(self, d):
        if d >= self.total:
            a, b = self.p[-2], self.p[-1]
            return b[0], b[1], rumo_graus(*a, *b)
        i = min(bisect_right(self.acum, d) - 1, len(self.p) - 2)
        a, b = self.p[i], self.p[i + 1]
        seg = (self.acum[i + 1] - self.acum[i]) or 1.0
        f = (d - self.acum[i]) / seg
        return (a[0] + (b[0] - a[0]) * f,
                a[1] + (b[1] - a[1]) * f,
                rumo_graus(*a, *b))


def gpx_todos_pontos(caminho):
    """Todos os trkpt do GPX + velocidade média real, se houver <time>."""
    raiz = ET.parse(caminho).getroot()
    ns = {"g": raiz.tag.split("}")[0].strip("{")} if "}" in raiz.tag else {}
    tp = raiz.findall(".//g:trkpt", ns) if ns else raiz.findall(".//trkpt")
    pontos, tempos = [], []
    for p in tp:
        pontos.append((float(p.get("lat")), float(p.get("lon"))))
        t = p.findtext("g:time", default="", namespaces=ns) if ns else p.findtext("time", "")
        tempos.append(t)
    veloc = None
    if len(pontos) > 1 and tempos[0] and tempos[-1]:
        try:
            from datetime import datetime
            fmt = "%Y-%m-%dT%H:%M:%S"
            t0 = datetime.strptime(tempos[0][:19], fmt)
            t1 = datetime.strptime(tempos[-1][:19], fmt)
            dur = (t1 - t0).total_seconds()
            if dur > 0:
                perc = Percurso(pontos)
                veloc = perc.total / dur
        except ValueError:
            pass
    return pontos, veloc


# ──────────────────────────────────────────────────────────────────── voz ──

class Voz:
    """Fila de fala com um lugar de espera. Se entretanto chegou um facto
    mais novo, o que estava à espera é descartado — já é passado."""

    def __init__(self, lingua="pt-PT", ativa=True):
        self.lingua, self.ativa = lingua, ativa
        self.fila = queue.Queue(maxsize=1)
        self.a_falar = threading.Event()
        if ativa:
            threading.Thread(target=self._trabalho, daemon=True).start()

    def diz(self, texto):
        if not self.ativa:
            return
        try:
            self.fila.put_nowait(texto)
        except queue.Full:
            try:
                self.fila.get_nowait()      # descarta o que envelheceu na fila
            except queue.Empty:
                pass
            self.fila.put_nowait(texto)

    def _trabalho(self):
        while True:
            texto = self.fila.get()
            self.a_falar.set()
            try:
                f = Path(tempfile.gettempdir()) / "companheiro-fala.txt"
                f.write_text(texto, encoding="utf-8")
                subprocess.run(
                    ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
                     "-File", str(BASE / "voz.ps1"),
                     "-Ficheiro", str(f), "-Lingua", self.lingua],
                    capture_output=True, timeout=120)
            except (OSError, subprocess.SubprocessError):
                pass
            finally:
                self.a_falar.clear()

    def espera_fim(self, max_s=90):
        fim = time.time() + max_s
        while (self.a_falar.is_set() or not self.fila.empty()) and time.time() < fim:
            time.sleep(0.3)


def para_voz(t):
    """Texto escrito → texto que soa bem dito."""
    t = re.sub(r"https?://\S+", "", t)
    t = re.sub(r"\d{1,3}(?: \d{3})+", lambda m: m.group(0).replace(" ", ""), t)
    t = re.sub(r"hab\.?\s*/\s*km²", "habitantes por quilómetro quadrado", t)
    t = t.replace("km²", "quilómetros quadrados")
    t = re.sub(r"\b(\d+) m\b", r"\1 metros", t)
    t = re.sub(r"\bkm/h\b", "quilómetros por hora", t)
    t = t.replace("·", ", ").replace("—", ", ").replace("↳", "")
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) > 550:                       # ~35 s de fala; corta em frase
        corte = t[:550]
        t = corte[:corte.rfind(".") + 1] or corte
    return t


# ─────────────────────────────────────────────────────────────── narração ──

def narra(r, canal, ditos):
    """Escolhe o próximo facto ainda não dito, começando pelo canal actual."""
    nome = factos.nome_para_noticias(r["local"]) or r["local"]["linha"]
    for c in [canal] + [x for x in CANAIS if x != canal]:
        for it in r["canais"][c]["itens"]:
            if c == "HISTORIA":
                chave, corpo = it["titulo"], f"{it['titulo']}. {it['texto']}"
            else:
                chave, corpo = str(it)[:120], str(it)
            if chave in ditos:
                continue
            ditos.add(chave)
            return c, f"{INTRO[c].format(nome=nome)} {corpo}"
    return None, None


def tecla():
    if not sys.stdin.isatty():
        return None
    try:
        import msvcrt
        if msvcrt.kbhit():
            return msvcrt.getwch().lower()
    except ImportError:
        pass
    return None


# ─────────────────────────────────────────────────────────────────── main ──

def main():
    ap = argparse.ArgumentParser(description="Companheiro de Viagem — modo contínuo")
    ap.add_argument("--rota", help=f"GPS simulado: {', '.join(factos.ROTAS)}")
    ap.add_argument("--gpx", help="GPS simulado a partir de um .gpx real")
    ap.add_argument("--turbo", type=float, default=1.0, help="acelerar o tempo N×")
    ap.add_argument("--lingua", default="pt-PT")
    ap.add_argument("--canal", default="HISTORIA", choices=CANAIS)
    ap.add_argument("--sem-voz", action="store_true", help="só texto, sem áudio")
    ap.add_argument("--max-anuncios", type=int, default=0, help="0 = sem limite")
    a = ap.parse_args()

    if a.gpx:
        pontos, v_gpx = gpx_todos_pontos(a.gpx)
        if len(pontos) < 2:
            sys.exit("esse GPX não tem pontos de trilho suficientes.")
        veloc = v_gpx or 25.0
    elif a.rota:
        if a.rota not in factos.ROTAS:
            sys.exit(f"rota desconhecida. Disponíveis: {', '.join(factos.ROTAS)}")
        modo_r, wpts = factos.ROTAS[a.rota]
        pontos = [(la, lo) for la, lo, _ in wpts]
        veloc = 1.4 if modo_r == "pe" else 25.0        # 5 km/h ou 90 km/h
    else:
        ap.print_help()
        return

    perc = Percurso(pontos)

    # A velocidade decide tudo — como no GPS real:
    modo = "pe" if veloc < 3.0 else "carro"
    horizonte = 60 if modo == "pe" else 240            # segundos de antecipação
    passo = 250 if modo == "pe" else 4000              # metros entre anúncios

    voz = Voz(a.lingua, ativa=not a.sem_voz)
    canal = a.canal
    ditos, silencio = set(), False
    d, ultimo_anuncio, ultimo_concelho, feitos = 0.0, -passo, None, 0

    print(f"Companheiro ligado · {perc.total/1000:.1f} km de percurso simulado · "
          f"{veloc*3.6:.0f} km/h → modo {modo} · antecipação {horizonte}s · turbo {a.turbo:g}×")
    print("Teclas: 1 história  2 economia  3 demografia  4 actualidade  s silêncio  q sair\n")

    dt_real = 0.1
    try:
        while d < perc.total:
            lat, lon, rb = perc.em(d)

            t = tecla()
            if t == "q":
                break
            if t == "s":
                silencio = not silencio
                print(f"   ── silêncio {'LIGADO' if silencio else 'desligado'} ──")
            if t in TECLA_CANAL:
                canal = TECLA_CANAL[t]
                print(f"   ── canal → {canal} ──")

            if not silencio and d - ultimo_anuncio >= passo:
                # prever onde vamos estar, seguindo o rumo actual
                ahead = veloc * horizonte
                pla, plo = avanca(lat, lon, rb, ahead) if ahead > 150 else (lat, lon)
                r = factos.analisa(pla, plo, modo)

                concelho = r["local"].get("concelho")
                prefixo = ""
                if concelho and concelho != ultimo_concelho:
                    prefixo = (f"Estamos a chegar ao concelho de {concelho}. "
                               if ultimo_concelho else
                               f"Estás perto de {r['local']['linha']}. ")
                    ultimo_concelho = concelho

                c_usado, texto = narra(r, canal, ditos)
                if texto or prefixo:
                    final = para_voz((prefixo or "") + (texto or ""))
                    etiqueta = c_usado or "LOCAL"
                    print(f"[{d/1000:6.1f} km · {etiqueta}] {final}\n")
                    voz.diz(final)
                    feitos += 1
                ultimo_anuncio = d
                if a.max_anuncios and feitos >= a.max_anuncios:
                    break

            time.sleep(dt_real)
            d += veloc * dt_real * a.turbo
    except KeyboardInterrupt:
        pass

    voz.espera_fim()
    print(f"\nFim: {min(d, perc.total)/1000:.1f} km percorridos, {feitos} anúncios, "
          f"{len(ditos)} factos contados.")


if __name__ == "__main__":
    main()
