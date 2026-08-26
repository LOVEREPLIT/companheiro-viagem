# Companheiro de Viagem — protótipos

Três programas, três perguntas:

1. **`factos.py`** — há factos verificáveis suficientes, de graça? (Sim: 94%.)
2. **`companheiro.py`** — funciona como companheiro contínuo, sem destino, com voz? (Sim.)
3. **`webapp/`** — corre num smartphone, sem loja de apps? (Sim — ver abaixo.)

## Fase 6 do PLANO-EXECUCAO.md — concluída (agosto 2026)

Pré-viagem com destino real: escreves para onde vais, ele conta o que há pelo
caminho antes de partires.

- **UI**: "Simulação (teste no PC)" passou a "Pré-viagem 🛋 (ouve o caminho
  antes de o fazeres)". Novos campos "Destino" e "Partida" (Partida vazio =
  GPS actual); as rotas de teste antigas continuam disponíveis por baixo,
  para quem não escrever destino — nada do que já existia foi removido.
- **Geocodificação e percurso**: Nominatim `/search?countrycodes=pt` resolve
  o texto em coordenadas (testei "Évora" → a 50 metros do centro real). O
  percurso é RECTO, por interpolação linear entre partida e destino (8
  pontos) — a UI diz sempre "percurso aproximado em linha recta", sem
  fingir que há estradas reais. Velocidade: 25 m/s (carro) se a distância
  em linha recta for >15 km, 1,4 m/s (a pé) se for mais curta.
- **A regra de ouro, testada a sério**: corri Lisboa→Évora completo (turbo
  200×) e confirmei `M.ditos` com 0 chaves novas no fim — nada do que se
  disse na pré-viagem ficou na memória real. A seguir simulei um anúncio a
  sério no mesmo sítio (Évora) e os mesmos temas puderam ser contados de
  novo (5 factos novos em `M.ditos`, desta vez a sério). Também tratei
  `M.visitas`, `M.colecoes`, `M.freguesias`, `M.stats` e `M.pesos` da mesma
  forma — nenhum escreve durante uma pré-viagem (o plano só falava
  explicitamente de `M.ditos`, mas a Fase 3 acrescentou estas outras
  memórias depois de o plano estar escrito; alarguei a regra a todas por
  a mesma razão de fundo: uma pré-viagem não é uma visita).
- **Bug real encontrado e corrigido**: a primeira versão restaurava
  `S.fonte`/`M` reais assim que a última posição simulada era processada —
  mas um `anunciar()` ainda a meio de uma pesquisa assíncrona (por exemplo
  a nova pesquisa à Wikisource, que pode fazer até 10 pedidos em série)
  podia terminar DEPOIS dessa restauração e escrever na memória real na
  mesma. Confirmei o bug (2 chaves a vazar para `M.ditos` num teste real)
  e corrigi fazendo a restauração esperar por `S.anunciando===false` — a
  mesma bandeira que já existia para o watchdog de segurança.
- Testado: F6.1 (geocodificação), F6.2 (a regra de ouro, com o bug acima),
  F6.3 (UI) — todos com dados e chamadas reais, não simulados.

## Fase 5 do PLANO-EXECUCAO.md — concluída, com fontes descartadas (agosto 2026)

Por ordem do plano — cada fonte só entrou depois de um `fetch()` real
provar que existe e devolve o que promete (secção 7 do plano).

### 6.1 Literatura geolocalizada — Wikisource (integrado)
Excertos REAIS de obras em domínio público que mencionam o lugar, ditos
como "Escreveu {autor}, em {obra}: «...»" dentro do canal HISTÓRIA. A
pesquisa de texto integral (`pt.wikisource.org`, API igual à da
Wikipédia) apanha muito lixo por si só: testei ao vivo com 11 termos reais
e, sem filtros, "Leiria" devolvia uma lei municipal de São Paulo e "Braga"
um catálogo tabular de cantigas medievais — nenhum dos dois é literatura.
Os filtros que ficaram, todos genéricos (não por nome de obra):
- excluir títulos que começam por "Lei", "Hino", "Decreto", "Resolução",
  "Portaria" e páginas de sistema;
- exigir uma ligação real a `Autor:` (rejeita "Vários"/"Anónimo") — é o
  sinal estrutural que separa literatura de documento administrativo;
- rejeitar excertos com muitos números/parênteses/"Capítulo" (cheiram a
  índice, não a prosa);
- rejeitar uma ocorrência do nome do lugar se a palavra anterior for
  maiúscula e não for uma preposição de lugar (apanha "Delfim Guimarães"
  ou "Pereira de Faro" — apelidos que por acaso são topónimos).
Com estes filtros, 6 de 7 termos "difíceis" testados (Leiria, Sintra,
Óbidos, Coimbra, Évora, mais tarde Guimarães e Porto) deram um excerto
real e bem atribuído — Eça de Queirós sobre Leiria, Álvaro de Campos "Ao
Volante" sobre Sintra, Florbela Espanca sobre Évora e Coimbra. **Limite
conhecido e aceite**: "Braga" continua a devolver por vezes um índice de
capítulos disfarçado — nomes de terra que são também apelidos portugueses
comuns (Braga, Faro, Porto, Guimarães) continuam a ser um risco residual
sem uma solução NLP mais pesada, que não se justifica para esta fase.
Nunca inventa — nada encontrado de jeito devolve `null` e o canal
simplesmente segue sem literatura nesse anúncio. Uma pesquisa por nome de
lugar só é tentada UMA vez por sessão (mesmo mecanismo do `S.ditos`).

### 6.2 SIPA (integrado, retomado depois de descartado) / MatrizPCI (descartado)
Numa primeira ronda descartei o SIPA por não ter API de pesquisa por
localização — só um formulário HTML. Depois de o utilizador pedir para
retomar, inspeccionei o HTML real do formulário (`pesquisa.php`, via
corsproxy.io directo — a versão em Markdown do `textoViaProxy` não mostra
os `<option>` do `<select>`) e descobri que **é submetível por concelho**:
`POST resultado.php` com um `concelho=<id numérico>`, onde o `id` de cada
concelho só existe dentro das opções desse `<select>` — não há tabela
nenhuma disto documentada, teve de ser extraída ao vivo. Testado de ponta
a ponta com concelhos reais:
- Palmela → id 2813 → 15 fichas reais, incluindo "Grutas da Quinta do
  Anjo" (sítio arqueológico, Neolítico Final/Calcolítico).
- Tavira → "Capela ou Ermida de São Sebastião, com todo o seu recheio",
  com nota histórico-artística real.
A extracção de título+nota (a mesma usada nas 4 fichas já validadas
antes) mantém-se fiável. Cada concelho só é pesquisado UMA vez por sessão
(mesmo mecanismo do `S.ditos` que a Wikisource usa) — o formulário custa
uma pesquisa + até 3 fichas por concelho, por isso não vale a pena
repetir. Domínio real: `imovel.patrimoniocultural.gov.pt` (não
`sipa.dgpc.pt`, como o plano supunha).

**MatrizPCI continua descartado.** Existe a sério
(`matrizpci.patrimoniocultural.gov.pt`, não `matrizpci.dgpc.pt`), mas não
voltei a investigar se tem o mesmo tipo de formulário submetível por
concelho — fica como próximo passo se algum dia valer a pena (patrimonio
imaterial: lendas, festas, artes populares).

### 6.3 Mais câmaras com dados abertos
- **Porto — integrado.** `opendata.porto.digital` (portal CKAN, não
  ArcGIS Hub — mas serve o mesmo propósito) tem um CSV real de 61
  monumentos com descrição em português, testado ao vivo: 49 monumentos
  reais devolvidos num raio de 2 km da Torre dos Clérigos, incluindo a
  própria Torre, o Arco de Sant'Ana, os Pilares da Ponte Pênsil. O CSV vem
  num dialecto próprio (aspas simples, campos de texto em formato de
  dicionário Python) — escrevi um parser dedicado para isto, testado
  contra 7 registos reais antes de confiar nele.
- **Coimbra, Braga, Guimarães, Évora, Faro — descartados.** Nenhum tem um
  catálogo de dados abertos real com património ou toponímia. Guimarães
  tem um portal de dados abertos real (`sig.cm-guimaraes.pt/dadosabertos`)
  mas as suas 13 categorias são todas de equipamentos/administração, nada
  de património. Braga só tem um visualizador de mapas, não um catálogo.
  Évora tem uma referência a um serviço ArcGIS de terceiros que já não
  existe (404 confirmado). Nenhum hub inventado — tudo verificado ao vivo
  antes de descartar.

### 6.4 Desemprego por concelho (IEFP) — descartado
O catálogo `dados.gov.pt` só tem 2 conjuntos de dados ligados ao IEFP, sem
nenhum ficheiro anexado (0% preenchido) e sem quebra por concelho — só
agregados nacionais. Existem relatórios mensais reais em PDF directamente
em iefp.pt, mas cada mês tem um URL com um identificador interno
imprevisível (não é um padrão fixo que se possa construir), por isso não
dá uma fonte estável para a app consultar sozinha. Descartado, como o
plano permite quando a cadeia não fecha num dia de trabalho.

## Fase 3 do PLANO-EXECUCAO.md — concluída (agosto 2026)

Interesses declarados, passaporte de território, colecções verificáveis,
estatísticas de viagem, e um briefing de chegada para a primeira vez que
se visita um concelho.

- **Interesses declarados**: seis temas (azulejos, castelos e fortalezas,
  igrejas e conventos, arte urbana, vinho e gastronomia, natureza e
  miradouros) activáveis em ⚙ ou por voz («interessa-me X» / «deixou de
  me interessar X»). Um interesse activo soma +30 à pontuação de um
  artigo em `pontua()`, tem prioridade no "olhar em volta" e no radar de
  desvios (testei: um castelo mais distante venceu um miradouro mais
  perto só por ter o interesse activo). "Arte urbana" é uma simplificação
  honesta: em vez de uma consulta Overpass dedicada a `tourism=artwork`,
  usa o mesmo casamento de texto que os outros temas — a app já cobre
  esse tag no canal de POIs, mas não priorizava por ele antes desta fase.
  "Vinho e gastronomia" não tem regex — activa-lo dá um reforço único
  (×1,5) ao peso do canal SABORES.
- **Passaporte de território**: na primeira visita de sempre a um
  concelho, o anúncio inclui "É o teu N.º concelho — ainda te faltam
  308-N." `M.freguesias` regista as freguesias visitadas (sem anúncio de
  voz próprio — seria repetitivo de mais). Comando «passaporte».
- **Colecções verificáveis**: pré-requisito cumprido primeiro — validei
  ao vivo por SPARQL no Wikidata os QIDs de 5 tipos de monumento
  classificado em Portugal com coordenadas. Descobri que o próprio plano
  tinha adivinhado errado 3 dos 5 QIDs (comparado com o real, via
  `rdfs:label`):

  | Colecção | QID usado (o do plano, se diferente) | Instâncias em PT com coordenadas |
  |---|---|---|
  | pelourinho | Q241212 (plano tinha Q1782709, errado) | 402 |
  | castelo | Q23413 (correcto) | 195 |
  | farol | Q39715 (correcto) | 84 |
  | moinho de vento | Q38720 (plano tinha Q42517, errado) | 62 |
  | aqueduto | Q474 (plano tinha Q474764, errado) | 41 |

  Quando um item de história falado tem QID do Wikidata e esse QID
  pertence a uma destas classes (`P31`), o anúncio ganha "É o N.º
  pelourinho da tua colecção — de 402 classificados em Portugal." Testado
  ao vivo com um pelourinho real (Q11789, Couto de Esteves): primeira vez
  → frase completa; segunda vez com o mesmo QID → sem repetir. Comando
  «colecções».
- **Estatísticas de viagem**: `M.stats` acumula metros por modo (pé,
  corrida, bicicleta, carro) a cada posição nova, e factos ouvidos até ao
  fim (o mesmo sinal que já reforçava pesos). Concelhos novos este mês
  derivam de `M.visitas` (primeira visita de cada concelho cai ou não no
  mês corrente) — não há contador à parte para não duplicar a fonte de
  verdade. Comando «quanto andei» ou «estatísticas de viagem» (tive de
  evitar a palavra "estatísticas" sozinha, que já mudava para o canal
  Números).
- **Briefing de chegada**: na primeira visita de sempre a um concelho,
  em vez do fluxo normal, monta-se um único texto mais longo (identidade
  + 1 facto de história + 1 sabor + números do INE, já com a comparação a
  Lisboa que o canal Números já fazia) — testado ao vivo em Sintra, com
  dados reais: identidade, a Estação Ferroviária de Sintra, os
  travesseiros da Casa Piriquita, e 385606 habitantes segundo o INE.
  Como este texto é deliberadamente mais longo (~60s) do que o limite
  normal do modo actual, `paraVoz()` ganhou um segundo parâmetro
  opcional (o limite de corte) só para este caso — sem ele, o corte por
  comprimento do modo a pé (750 caracteres) cortava o briefing a meio e
  engolia o fecho "Boa descoberta, diz conta mais" (confirmei o bug antes
  de o corrigir: sem o parâmetro, um briefing real de 811 caracteres
  ficava cortado a 611).
- **Bug de colisão de comandos encontrado e corrigido**: "interessa-me
  vinho e gastronomia" era apanhado pelo comando de troca de canal
  SABORES (que testa a palavra "gastronomia"), porque os comandos de
  canal vinham antes na lista. Os novos comandos (interesses, passaporte,
  colecções, estatísticas) tiveram de passar para o TOPO da lista de
  comandos de voz — confirmado com teste ao vivo antes e depois da
  correcção.
- Testado: os 5 critérios de aceitação da Fase 3 (F3.1–F3.5) com dados
  reais (Wikidata, Wikipédia, INE) — nenhum simulado; regressão
  amostrada nas funções tocadas (pontua, olharEmVolta, narrar, paraVoz,
  dedupe persistente, respeito por canais desligados) sem quebras.

## Fase 4 do PLANO-EXECUCAO.md — concluída (agosto 2026)

Rádio e podcasts a tocar dentro da própria app, com *ducking* automático
quando o companheiro fala, controlos no ecrã de bloqueio, e uma oferta
proactiva quando não há novidades. Honestidade primeiro: uma webapp não
consegue controlar o Spotify de outra app nem navegar lá dentro — por
isso o caminho principal é tocar tudo cá dentro, não "ligar-se" a apps
externas.

- **Rádio**: directório aberto `radio-browser.info` (363 estações
  portuguesas, testado ao vivo) — filtra automaticamente os streams
  `.m3u8`/HLS que o Chrome não toca sem biblioteca extra. Testei 5
  estações reais: RFM, Rádio Observador e Rádio Renascença tocam de
  imediato; Antena 1 (só tinha stream `.m3u8`) foi correctamente excluída.
- **Podcasts**: guarda-se os teus feeds RSS em ⚙. Testei com um feed real
  — *Extremamente Desagradável*, o podcast mais ouvido de Portugal — e
  confirmei que o áudio toca directamente, sem proxy (só a leitura do
  texto do feed passa pelas mesmas regras de CORS do resto da app; o
  próprio ficheiro de áudio não). A posição fica guardada e retoma entre
  sessões — testei a sério: gravei aos 42s, recarreguei a página, retomou
  aos 43,7s.
- **Ducking real**: toquei uma rádio a sério e confirmei o volume a descer
  de 1 para 0,15 quando o companheiro fala, e a voltar a 1 no fim.
- **Oferta proactiva**: ao fim de 2 anúncios seguidos sem nada de novo (e
  sem áudio já a tocar), pergunta se queres rádio ou podcast — no máximo
  uma vez por hora. Ao testar apanhei uma supressão a funcionar
  correctamente que pareceu à primeira vista uma falha: a segunda
  tentativa de teste, na mesma hora real, ficou muda de propósito.
- **Handoff Spotify**: avisa sempre por voz antes de tentar abrir o
  Spotify, com 2,5s de intervalo para o aviso ser mesmo ouvido antes de
  sair da app — testado a confirmar a ordem exacta dos eventos.
- Testado: 13/14 da regressão (1 inconclusivo, mesma causa externa já
  documentada na Fase 2) e 5/5 dos critérios de aceitação, com rádio e
  podcast reais a tocar durante os testes — não simulado.

## Fase 2 do PLANO-EXECUCAO.md — concluída (agosto 2026)

Modo corrida (jogging), bicicleta, percursos pedestres/ciclovias do OSM, e
radar de desvio para monumentos classificados fora do caminho.

- **Jogging como modo próprio**, pedido pelo João a meio da execução — o
  plano original só previa pé/bicicleta/carro. Corrida (1,8–3,3 m/s,
  ≈6,5–12 km/h) trata-se como "a pé" para a rua/bairro e o olhar em volta
  (é gente a pé, só mais depressa), mas com cadência e gancho próprios
  (1 frase, 550 caracteres — mais curto que a pé, porque a respirar fundo
  não se processa tanta informação de uma vez).
- Detecção por velocidade com **histerese real** (`S.modo`, actualizado em
  `novaPosicao`): só muda de modo ao fim de ~20s estável no novo
  intervalo, para não oscilar num semáforo entre carro e bicicleta.
- **Percursos** (PR/GR, ecopistas): consulta nova ao Overpass
  (`route=hiking|foot|bicycle`), testada ao vivo antes de integrar — a
  Serra de Sintra devolveu o PR2SNT e o PR3SNT reais, com nome, referência
  e distância. "Estás a cruzar o PR2SNT — Pena, um percurso circular de
  4,5 quilómetros." Nunca de carro.
- **Radar de desvio**: quando há um Monumento Nacional/Imóvel de Interesse
  Público perto mas fora do caminho, sugere um pequeno desvio com o lado
  certo ("à tua esquerda, a 300 metros…"), calculado pelo rumo real, não
  adivinhado. Nunca de carro; um só por anúncio.
- **Bug real apanhado a testar**: a primeira versão do desvio prefixava o
  texto da rua (que pode ser longo) ao texto do desvio, e o corte por
  comprimento do modo corrida (550 caracteres) comia o próprio desvio
  antes de lá chegar — calando exactamente a única coisa que importava
  dizer. Corrigido para o desvio nunca depender do que vier antes.
- Testado: 14/14 da regressão (2 momentaneamente inconclusivos por
  bloqueio temporário do `r.jina.ai` ao `news.google.com`, causado pelo
  volume de testes de hoje — confirmado pelo próprio erro da fonte, não
  pelo código) e 6/6 dos critérios de aceitação da Fase 2, incluindo o
  modo corrida de ponta a ponta.

## Fase 1 do PLANO-EXECUCAO.md — concluída (agosto 2026)

Gancho curto + «conta mais»/«conta menos» + duração adaptativa ao modo +
pré-carregamento em segundo plano. Detalhe completo no commit; resumo:

- Cada anúncio fala só o gancho (1-2 frases, conforme o modo); o resto
  fica disponível a pedido — «conta mais» (ou botão ⏵ novo na barra de
  ícones) fala-o e reforça o interesse nesse canal; «conta menos» encurta
  e desce o detalhe, sem contar como salto (não dispara a auto-troca de
  canal que o «salta» dispara).
- A pé fala-se mais (750 caracteres, 2 frases); de carro, menos (450, 1
  frase) — `limitesFala()`, consultado por `paraVoz()` e por `narrar()`.
- Testado: **14/14 da bateria de regressão** (`PLANO-TESTES.md`, secção
  R) e **7/7 dos critérios de aceitação da Fase 1** (T-F1).
- **Limitação pré-existente descoberta a testar** (não introduzida agora):
  a tabela `COMANDOS` dá prioridade aos gatilhos de troca de canal
  (`/historia/`, `/economia/`, …) sobre qualquer comando mais recente na
  lista — uma frase como "conta mais sobre esta história" é apanhada por
  engano pelo comando que muda para o canal HISTÓRIA, porque "história"
  bate certo com esse padrão e esse comando está mais acima na tabela.
  «desenvolve» e «continua essa» (sem mais nada a seguir) funcionam bem.
  Fica para uma fase futura arrumar a prioridade da tabela de comandos.
- Confirmado também: o ambiente de teste (Browser pane em 2.º plano) pode
  atrasar uma única chamada de rede em dezenas de segundos — não é bug
  da app, é o browser a poupar recursos com o separador sem foco.

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

## 4 indicadores INE, sempre comparados com Lisboa (agosto 2026, 4.ª ronda)

Pedido do João: descobrir os códigos e integrar poder de compra,
envelhecimento, desemprego e "todos os indicadores interessantes",
comparando sempre com a capital. Métodos dos códigos: pesquisa dirigida
por indicador, depois confirmação real de cada `varcd` (nome, último ano,
e se a dimensão geográfica desce a `categ_nivel:"5"` = concelho).

**4 indicadores confirmados e integrados**, cada um testado com dados reais
antes de entrar no código:

| Indicador | varcd | Canal | Testado com |
|---|---|---|---|
| População residente | `0008273` | NÚMEROS | Lisboa 655 542 (2023) |
| Índice de envelhecimento | `0008258` | NÚMEROS | Reguengos 204 vs Lisboa 169 idosos/100 jovens |
| Poder de compra per capita | `0008614` | ECONOMIA | Reguengos 90,9 vs Lisboa 186,3 (país=100) |
| Ganho médio mensal | `0012653` | ECONOMIA | Reguengos 1237€ vs Lisboa 2121€ (2024) |

Todos comparam sempre com Lisboa (excepto quando já se está em Lisboa).
Testados e descartados por não descerem a concelho (só distrito ou país):
`0001272` (envelhecimento por sexo, sem geografia fina), `0010704` (taxa
de desemprego, só distrito), `0010697` (rendimento médio, só distrito).

**Desemprego por concelho: não existe no INE.** O Inquérito ao Emprego é
uma sondagem por amostragem, sem escala estatística para 308 municípios —
só desce a distrito. A alternativa real é o IEFP (desempregados inscritos
nos centros de emprego, dados mensais por concelho, publicados no
dados.gov.pt), mas o portal bloqueia CORS mesmo via proxy nesta ronda —
fica documentado para uma futura tentativa, não implementado.

Um bug real apanhado a testar: o nome do artigo da Wikipédia às vezes é
"X (freguesia)" quando existe também uma freguesia-sede com o mesmo nome
do concelho — isso não batia certo com o nome que o INE usa. Corrigido ao
usar sempre `f.local.concelho` (limpo) para os pedidos ao INE, nunca o
título do artigo da Wikipédia.

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
