# Companheiro de Viagem — protótipos

Três programas, três perguntas:

1. **`factos.py`** — há factos verificáveis suficientes, de graça? (Sim: 94%.)
2. **`companheiro.py`** — funciona como companheiro contínuo, sem destino, com voz? (Sim.)
3. **`webapp/`** — corre num smartphone, sem loja de apps? (Sim — ver abaixo.)

## webapp — a app para o telemóvel (sem loja de apps)

Um único ficheiro HTML que corre no Chrome do telemóvel. Para a usares:

```bash
python servir.py
```

e abre no telemóvel (mesma rede Wi-Fi) o endereço que o script imprime.
GPS: o Chrome exige HTTPS para dar a localização; numa rede local usa o modo
**Simulação** (imediato) ou ativa uma vez a flag indicada pelo `servir.py`.
No PC abre `http://localhost:8123` — funciona igual.

O que a webapp faz que os protótipos de linha de comandos não faziam:

- **5 canais**: história · **sabores e tradições** · economia · números · notícias;
- **menu falado a sério** (Chrome Android): «história», «gastronomia»,
  «mais detalhe», «menos detalhe», «sem densidade populacional», «silêncio»,
  «salta», «repete», «ajuda» — e botões equivalentes no ecrã;
- **preferências finas por canal**, à voz ou no painel ⚙: nível de detalhe
  (curto/normal/longo) e, nos números, ligar/desligar população, densidade,
  área e altitude — guardadas no telemóvel entre sessões;
- **avisos ao vivo**: avisos meteorológicos do IPMA para o distrito onde estás
  e incêndios ativos num raio de 40 km (Fogos.pt) — falados antes de tudo;
- **filhos da terra**: figuras ilustres nascidas no concelho (Wikidata);
- **pormenor de rua e bairro quando vais a pé** («Estás na Rua de Santa Justa,
  no bairro da Baixa…»), com o artigo da própria rua quando existe;
- **gastronomia em três níveis**: secções do artigo da terra → pratos da
  região (categorias da Wikipédia: açorda à alentejana, cataplana, sarrabulho…)
  → a mesa portuguesa em geral (o pão, o azeite, o vinho, a doçaria).

### O companheiro que te conhece (novidades desta versão)

- **Memória de viagens** (fica no telemóvel, em localStorage): nunca repete um
  facto entre sessões, e ao voltares a um concelho diz «Já por aqui tinhas
  passado em maio — desta vez conto-te coisas novas.»
- **Ligações entre terras**: se um facto mencionar alguém de quem já ouviste
  falar noutro sítio, acrescenta «Curiosamente, de Vasco da Gama já tinhas
  ouvido falar quando passaste por Sines, em agosto.»
- **Sazonalidade**: cruza o calendário com as festas da terra — «Por estes
  dias em Viana do Castelo: Romaria da Senhora d'Agonia…» (procura o mês no
  artigo da terra e, se preciso, no artigo da própria festa).
- **Efemérides locais**: «Efeméride: faz agora 641 anos. A Batalha de
  Aljubarrota decorreu no final da tarde de 14 de agosto de 1385…» — dispara
  quando passas a ±3 dias da data, no próprio lugar.
- **Perfil de interesses com pesos, não interruptores**: ouvir um canal até ao
  fim sobe o seu peso; «salta» desce-o. A ordem da mistura adapta-se; se
  saltares 3 vezes seguidas o mesmo canal, ele passa a dar prioridade ao teu
  favorito e avisa. O perfil vê-se (e apaga-se) no painel ⚙.

### Fontes usadas pela webapp (todas gratuitas, sem chave)

| Fonte | Dá | Acesso do browser |
|---|---|---|
| Wikipédia PT/EN | história, monumentos, secções de economia/gastronomia | direto |
| Wikidata + SPARQL | população, área, altitude; figuras ilustres | direto |
| Nominatim (OSM) | freguesia/concelho; rua e bairro (a pé) | direto |
| Overpass (OSM) | pontos de interesse à volta (a pé) | direto |
| IPMA open-data | avisos meteorológicos por distrito | direto |
| Fogos.pt | incêndios ativos em tempo real | via proxy CORS |
| Google News RSS | notícias da localidade | via proxy CORS |
| INE (API JSON) | estatísticas por concelho | **fase servidor** (sem CORS) |

O proxy (corsproxy.io) é o único elo não-institucional — na fase seguinte,
notícias e INE passam pelo pequeno servidor próprio e deixa de ser preciso.

## companheiro.py — o modo contínuo

Não se introduz destino nenhum. Liga-se e ele:

- deduz **velocidade e rumo** da posição (carro vs. a pé, automático);
- **prevê onde vais estar** daqui a 4 minutos (1 minuto a pé), projectando a
  posição ao longo do rumo, e vai buscar factos desse ponto *antes* de lá
  chegares — por isso um facto "atrasado" nunca acontece: são adiantados;
- **lê em voz alta** com a voz portuguesa do Windows (Microsoft Helia, via
  `voz.ps1` e o motor OneCore — o motor clássico não tem português);
- aceita **mudança de canal a qualquer momento** por teclas — o substituto de
  secretária das palavras ditas que o telemóvel reconhecerá:
  `1` história · `2` economia · `3` demografia · `4` actualidade ·
  `s` silêncio · `q` sair;
- se um facto envelhecer na fila de fala enquanto outro é dito, é
  **descartado** — falar do que já passou há 10 km não interessa.

A rota/GPX serve só de **GPS simulado** (um PC não anda). A lógica nunca olha
para o fim da rota — só para posição, velocidade e rumo, como fará no
telemóvel com GPS real.

No teu PC, PowerShell, nesta pasta:

```bash
python companheiro.py --rota a1 --turbo 60
```

```bash
python companheiro.py --gpx viagem.gpx --turbo 30
```

`--turbo 60` = uma hora de viagem num minuto. `--sem-voz` para só texto.
Com GPX com carimbos de tempo, a velocidade real da viagem é respeitada.

---

# factos.py — o motor de factos

Este protótipo responde a **uma só pergunta**: dada uma coordenada em Portugal,
é possível obter factos verificáveis e interessantes, de graça, sem chaves de API?

Não há aqui nenhum modelo de linguagem. É de propósito. Se as fontes não
chegarem, nenhum modelo salva a app — só a faria inventar com mais elegância.

## Como correr

Na tua máquina, PowerShell, a partir desta pasta:

```bash
python factos.py --rota alentejo
```

Outras formas:

```bash
python factos.py --coord 38.7098,-9.1330 --modo pe
```

```bash
python factos.py --gpx viagem.gpx --pontos 8
```

```bash
python factos.py --listar-rotas
```

Sem instalações. Só a biblioteca padrão do Python (3.8+).
Cada execução grava o resultado em `saida/*.json` e faz cache em `.cache/`
(a segunda corrida da mesma rota é instantânea e não incomoda os servidores).

## Os quatro canais

Correspondem ao "menu falado" que queres poder trocar por voz em andamento.

| Canal | Fonte | Estado |
|---|---|---|
| **HISTÓRIA** | Wikipédia PT (geo-pesquisa por coordenadas) | Sólido |
| **DEMOGRAFIA** | Wikidata (P1082 população, P2046 área, P2044 altitude) | Sólido |
| **ACTUALIDADE** | Google News RSS, filtrado pela localidade, 120 dias | Sólido |
| **ECONOMIA** | Secção "Economia" da Wikipédia + heurística por palavras-chave | **Fraco** |

Modo `carro`: raio de 9 km, dá prioridade a povoações e grandes marcos.
Modo `pe`: raio de 700 m, dá prioridade a monumentos concretos, e acrescenta
os pontos de interesse do OpenStreetMap num raio de 400 m.

## Resultado dos testes

20 pontos em 4 rotas — cidade a pé, auto-estrada, Alentejo rural e Douro:

```
baixa-lisboa    5 pontos    20/20 canais com conteúdo
a1              7 pontos    27/28
alentejo        5 pontos    18/20
douro           3 pontos    10/12
                            ─────
                            75/80  (94%)
```

**As 5 falhas são todas no mesmo canal: ECONOMIA.**
História, demografia e actualidade acertaram em 20 pontos de 20, incluindo
aldeias do interior. A cobertura da Wikipédia em português é melhor do que
eu esperava para o Portugal rural — em Monsaraz apanhou o castelo e dois
menires classificados como Monumento Nacional.

## O que ficou por resolver

1. **Economia é o canal fraco.** Concelhos pequenos não têm secção "Economia"
   na Wikipédia. Falhou em Azambuja, Monsaraz, Reguengos, Régua e Tua.
   Resolve-se com uma fonte a sério: API do INE, Eurostat a nível NUTS-3, ou
   PORDATA. Fica para a fase seguinte.

2. **Fronteiras administrativas confundem.** Uniões de freguesias criadas em
   2013 e extintas em 2025 aparecem como se descrevessem o presente. Já são
   penalizadas, mas ainda escapa alguma.

3. **Wikidata está desactualizada em sítios.** Alguns concelhos ainda têm
   censos de 2011. O valor mostrado indica sempre o ano — nunca apresentar
   um número sem a data.

4. **Zonas sem cobertura em português** caem para a Wikipédia inglesa
   (aconteceu no Alqueva). Num produto final é preciso traduzir localmente.

5. **Limites de utilização.** Nominatim e Overpass são gratuitos mas com
   limites rígidos: 1 pedido/s, e proibido uso intensivo. Para uso pessoal
   chega; para distribuir a app é preciso servidor próprio ou pré-carregar
   os dados por região.

## O passo seguinte

O pré-carregamento por rumo já está no `companheiro.py` (antecipação de
4 min). O que falta para o telemóvel:

1. reconhecimento de voz local para o menu falado (as teclas 1–4 de hoje);
2. o modelo local (1–2B) para reescrever os factos em narração natural —
   nunca para os inventar — e traduzir quando a fonte cair no inglês;
3. Android primeiro (background livre); no iOS será app de ecrã ligado.
