#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serve a webapp do Companheiro de Viagem na rede local, para abrir no telemóvel.

No teu PC, PowerShell, nesta pasta:

    python servir.py

Depois, no telemóvel (na MESMA rede Wi-Fi), abre no Chrome o endereço que
este script imprime.

Nota sobre o GPS: o Chrome só dá acesso ao GPS em páginas seguras (HTTPS).
Numa rede local sem certificado há duas saídas:
  a) usar o modo "Simulação" da app (não precisa de GPS) — imediato;
  b) no Chrome do telemóvel, abrir chrome://flags/#unsafely-treat-insecure-origin-as-secure,
     escrever aí o endereço impresso abaixo e reiniciar o Chrome — uma vez só.
A voz e o microfone funcionam sem nada disto.
"""
import http.server
import socket
import socketserver
from pathlib import Path

PORTA = 8123
PASTA = Path(__file__).resolve().parent / "docs"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(PASTA), **kw)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


if __name__ == "__main__":
    ip = ip_local()
    print("Companheiro de Viagem — servidor local")
    print(f"  Neste PC:      http://localhost:{PORTA}")
    print(f"  No telemóvel:  http://{ip}:{PORTA}   (mesma rede Wi-Fi)")
    print("Ctrl+C para parar.\n")
    with socketserver.ThreadingTCPServer(("", PORTA), Handler) as srv:
        srv.serve_forever()
