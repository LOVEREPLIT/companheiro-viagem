# Companheiro de Viagem

Webapp de áudio mãos-livres para quem viaja em Portugal (a pé, de bicicleta, de carro): conta a história, a gente, os sabores e o que está a acontecer à volta, pela voz, conforme a posição. Ficheiro único `docs/index.html`, vanilla JS, sem compilação, publicado em GitHub Pages: https://lovereplit.github.io/companheiro-viagem/

**Custo zero em funcionamento**: só fontes gratuitas, sem chaves de API.

## Correr localmente

```
python -m http.server 8124 --bind 127.0.0.1   (na pasta docs/)
```
Abrir http://127.0.0.1:8124/ (a porta 8123 costuma estar ocupada por outra aplicação).

## Mapa dos documentos

| Ficheiro | Para quê | Quando ler |
|---|---|---|
| `HANDOVER.md` | Estado actual, decisões, próximos passos | **Sempre primeiro** |
| `CLAUDE.md` | Regras do projecto (curto) | Automático |
| `DESENHO-BASE-CONHECIMENTO.md` | Desenho da base de conhecimento geo (Lumiar e Benfica primeiro) | Ao desenvolver a base |
| `projecto/PLANO-TESTES.md` | Bateria de regressão R1–R14 (§R, linhas 39–112) e aceitação por fase | Antes de cada push |
| `projecto/PLANO-EXECUCAO.md` | Plano das 6 fases (concluído) e princípios §0 | Só para consultar princípios |
| `projecto/historico-fases.md` | Registo detalhado de tudo o que se fez e testou, fase a fase | Só para investigar uma decisão passada |
| `companheiro.py`, `factos.py`, `servir.py`, `voz.ps1` | Protótipos antigos em Python (já não são o produto) | Ignorar |
