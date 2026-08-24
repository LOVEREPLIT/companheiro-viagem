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

## Fontes locais oficiais (Lisboa) — investigação de agosto de 2026

A Wikipédia sozinha esgota-se depressa em zonas residenciais e por vezes
salta para um artigo nacional genérico por falta de alternativa. Investigação
a fundo a fontes portuguesas gratuitas encontrou uma excelente para Lisboa:

- **Câmara de Lisboa (ArcGIS Hub, `geodados-cml.hub.arcgis.com`)** — ao
  contrário da maioria das câmaras, responde directamente do browser, sem
  proxy. Duas camadas usadas:
  - `Cultura_Toponimia` — a justificação HISTÓRICA OFICIAL de cada nome de
    rua, escrita pela própria Câmara. Substitui a adivinhação via Wikipédia
    quando existe, com texto oficial e sem inventar nada.
  - `Patrimonio` (camadas 11 e 12) + `Cultura_CasasReligiosas` — inventário
    de monumentos classificados com descrições completas escritas por
    técnicos de património, muito mais ricas que o resumo da Wikipédia.
- **geoapi.pt** — serviço português gratuito e sem chave; devolve numa só
  chamada leve a localização oficial, temperatura/humidade em tempo real, e
  risco de incêndio/inundação **por ponto exacto** (não ao nível do distrito
  inteiro, como o IPMA). Conteúdo que muda sempre, nunca repete.
- **agendalx.pt** — agenda cultural oficial de Lisboa, eventos reais e a
  decorrer (sem coordenadas por evento — entra como "o que se passa na
  cidade", reforço da Actualidade).

**Porquê só Lisboa, por agora:** a plataforma técnica que cada câmara usa
decide se dá para aceder directo do browser. As que usam **ArcGIS Hub**
(Lisboa) respondem sem proxy. As que usam **CKAN** (Porto, Cascais,
Guimarães, Águeda — confirmado por teste directo) bloqueiam por CORS e
precisavam do mesmo proxy já usado nas notícias — mais lento e frágil, e
cada câmara guarda os dados de maneira diferente (não há um "nome da
camada" universal a copiar de Lisboa para as outras). Expandir para mais
câmaras é trabalho de descoberta uma a uma, não uma mudança de configuração.

## Verificação cruzada de 4 investigadores externos (agosto 2026, 3.ª ronda)

Pedi a 4 modelos de pesquisa diferentes para encontrarem mais fontes, com um
critério explícito: só aceitar o que fosse testado de facto com `fetch()`,
nunca com base em documentação. Resultado — **duas das quatro inventaram
URLs e dados por completo**, o que confirma que o critério era necessário:

- Uma fonte deu um "endpoint ArcGIS do Porto" com um ID de organização que
  a própria Esri rejeitou como inválido, e "endpoints" para Coimbra e Braga
  em domínios que **não existem** (erro "Domain record(s) not found").
- A mesma fonte deu uma amostra de JSON do INE para o indicador `0011186`
  como sendo "taxa de desemprego por concelho" — testei o indicador real e
  é sobre **serviços de associações patronais**, nada a ver. O JSON inteiro,
  incluindo os números "6.2%" e "7.1%", era inventado.
- Deu ainda uma fonte de gastronomia (`tradicao.ongd.pt`) cujo domínio nem
  sequer resolve.
- Outra fonte deu exemplos de código que faziam `fetch("https://jina.ai")`
  sozinho — sem endpoint nenhum atrás — como se fosse prova de teste.

As outras duas foram honestas sobre não terem conseguido testar (o ambiente
delas não corre JavaScript num browser), e uma delas deu pistas reais
(URLs de feeds concretos) que confirmei eu próprio a seguir.

**O que sobrou depois de testar tudo — real, confirmado, e agora em uso:**

- **INE, população oficial por concelho** — confirmado ponta-a-ponta.
  O indicador `0008273` desce a nível de concelho (344 municípios,
  `categ_nivel:"5"`); bloqueia CORS directo mas funciona via `r.jina.ai`.
  Testei com dados reais: Lisboa 655 542 habitantes (2023), Porto 267 236
  (2023) — agora usado no canal NÚMEROS, com "segundo o INE (ano)" em vez
  da estimativa da Wikidata quando há dados oficiais.
- **6 jornais regionais novos**, testados um a um, que fecham lacunas
  geográficas que ainda faltavam:

  | Jornal | Cobre |
  |---|---|
  | Diário As Beiras | Coimbra, Figueira da Foz, Cantanhede |
  | Diário dos Açores | Ponta Delgada, São Miguel, e geral dos Açores |
  | JM Madeira | Madeira geral |
  | Jornal da Madeira | Madeira (Funchal) |
  | Funchal Notícias | Funchal, Porto Santo |
  | Tribuna da Madeira | Madeira geral |

  Com isto, **Açores e Madeira deixam de estar sem cobertura** — eram as
  duas lacunas mais visíveis da ronda anterior.

**O que continua por fazer:** o INE só tem população integrada; poder de
compra, envelhecimento e desemprego exigem descobrir o `varcd` certo para
cada um (o catálogo é real e funciona — só falta o trabalho de encontrar
os códigos, indicador a indicador, cada um com dimensões diferentes).
Alentejo interior e Beira interior continuam sem jornal local confirmado.

## Imprensa regional (investigação de agosto de 2026, 2.ª ronda)

Pedido explícito do João: ir a fontes mais pequenas do que o Google News.
Investigação a fontes portuguesas de jornalismo local, testada uma a uma:

- **recortes.pt** agrega ~14 jornais regionais pequenos (Diário de Aveiro,
  Diário de Coimbra, Diário de Leiria, Diário de Viseu, Gazeta das Caldas,
  Jornal da Bairrada, Jornal da Beira, Cerveira Nova, Voz de Mira). A página
  em si bloqueia por CORS e não foi integrada — documentado, não implementado.
- **Olh'ó Regional** (`olho-regional.pages.dev`) — projeto sério e rigoroso:
  pediu à ERC a lista completa de publicações registadas (4679), filtrou
  para regionais com presença online (663), complementou com o projeto
  Memória da Imprensa Portuguesa (573 finais), e mapeou cobertura aos 308
  municípios, identificando 100 "desertos de notícias". A sua API
  (`/api/jornais`) esteve **confirmadamente avariada** durante o teste
  ("Worker threw exception", erro 500) — não deu para integrar ao vivo.
  Vale a pena revisitar; entretanto, serviu para identificar jornais reais.
- **Jornais integrados e testados um a um** (via `r.jina.ai`, o mesmo proxy
  já usado no Google News) — entram ANTES da pesquisa genérica quando o
  concelho bate certo, por serem jornalismo local editado, não agregação:

  | Jornal | Cobre |
  |---|---|
  | Sintra Notícias | Sintra, Cascais, Oeiras, Amadora, Mafra |
  | Pombal Jornal | Pombal |
  | Jornal de Albergaria | Albergaria-a-Velha, Águeda |
  | O Minho | Braga, Barcelos, Guimarães, Vila Verde, Esposende |
  | Jornal do Algarve | Loulé, Olhão, Faro, Portimão, Tavira, Albufeira, Lagos |
  | O Setubalense | Setúbal |
  | A Voz de Trás-os-Montes | Vila Real, Chaves, Bragança |

  Testados e descartados por não responderem/não terem feed válido:
  Algarve Primeiro, Setúbal Notícias, Diário de Trás-os-Montes, A Voz de
  Ermesinde (a URL de RSS encontrada era uma página de explicação, não o
  feed real). Continua a faltar: Alentejo interior, Coimbra cidade, Beira
  interior, Açores, Madeira — nenhum jornal local com feed válido encontrado
  ainda para essas zonas nesta ronda.

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
