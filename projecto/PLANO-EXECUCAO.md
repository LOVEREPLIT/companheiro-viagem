# Companheiro de Viagem — Plano de Execução (para o modelo executor)

Este documento é a especificação de trabalho para a próxima grande evolução
da app. Foi escrito para ser executado por um modelo de IA com acesso ao
repositório, a um browser de teste e ao PowerShell do PC do João. Lê TUDO
antes de tocar em código. O plano de testes correspondente está em
`PLANO-TESTES.md` — cada fase só se considera terminada depois dos testes
dessa fase passarem.

---

## 0. Princípios inegociáveis (violar qualquer um = trabalho rejeitado)

1. **Áudio-primeiro, presença no momento.** O utilizador está a olhar para o
   mundo, não para o telemóvel. NENHUMA funcionalidade nova pode exigir olhar
   para o ecrã durante o passeio. O ecrã existe para configurar antes e
   consultar depois. (Por esta razão, a ideia de "fotos históricas no ecrã"
   foi explicitamente EXCLUÍDA pelo João — não a implementes.)
2. **Custo zero em funcionamento.** Só fontes gratuitas, sem chaves de API.
   O único intermediário aceite é o proxy de leitura `r.jina.ai` (com
   `corsproxy.io` e `allorigins` como reservas).
3. **Nunca integrar uma fonte sem a testar com um `fetch()` real** no browser
   de teste, com amostra da resposta verificada. Nesta base de código já
   foram apanhadas fontes externas com URLs e dados completamente inventados
   por modelos de pesquisa. A regra é absoluta. O protocolo está na
   secção 7.
4. **A app nunca inventa factos.** Tudo o que é dito vem de uma fonte com
   URL. O modelo de IA local (WebLLM), quando activo, só REESCREVE texto
   recebido — nunca acrescenta informação.
5. **Fallback sempre.** Cada fonte nova falha silenciosamente para o
   comportamento anterior. A app nunca fica muda nem pendurada por causa de
   uma fonte avariada.
6. **Um único ficheiro** (`docs/index.html`), JavaScript puro, sem build,
   sem dependências npm. Publica-se com `git push` (GitHub Pages, pasta
   `/docs`). Os protótipos Python na raiz são história — não lhes toques.
7. **Português de Portugal** em tudo o que o utilizador ouve e lê.
8. Depois de cada fase: commit com mensagem descritiva honesta (incluindo o
   que falhou e foi descartado), push, e registo no `README.md`.

---

## 1. Arquitectura actual (mapa para te orientares no código)

Tudo vive em `docs/index.html` (~1600 linhas). Blocos principais, pelos
nomes reais das funções:

- **Estado**: `S` (sessão: canal, veloc, rumo, ditos, pesos de saltos…),
  `M` (memória persistente em localStorage `cv-mem`: ditos com timestamp,
  visitas por concelho, entidades ouvidas, pesos por canal),
  `guardaPrefs()`/`lePrefs()` (localStorage `cv-prefs`).
- **Rede**: `busca(url, tipo)` — fetch com cache de sessão e throttle por
  host; `textoViaProxy()`/`jsonViaProxy()` — cadeia r.jina.ai → corsproxy →
  allorigins; o formato do r.jina.ai embrulha tudo num cabeçalho
  `"Markdown Content:\n"` que é preciso descartar.
- **Fontes**: `nominatim()` (localização), `wikiGeo()`/`wikiPaginas()`
  (Wikipédia), `wikidata()`/`filhosDaTerra()` (SPARQL), `overpass()` (POIs),
  `avisosIPMA()`, `fogosPerto()`, `tempoAgora()` (geoapi.pt),
  `toponimiaCML()`/`patrimonioCML()` (ArcGIS da CML — só Lisboa),
  `ineCatalogo()`/`ineValor()`/`ineComLisboa()` (INE, 4 indicadores),
  `noticias()`/`jornalRegional()` (Google News + 13 jornais regionais),
  `eventoLisboaPorContar()` (agendalx).
- **Motor**: `escolher()` (geosearch com pontuação `pontua()`, recuo
  para inglês só se PT vazio, tradução via `traduzParaPT()`),
  `artigosLocalidade()` (artigo da freguesia/concelho), `narrar()` (ordem de
  canais por peso aprendido, dedupe por `S.ditos`/`marcaDito()`,
  `ligaEntreTerras()`), canais em `CONSTRUTOR`: `canalHistoria` (inclui
  `olharEmVolta()` direccional e património CML), `canalSabores`,
  `canalEconomia`, `canalDemografia`, `canalActualidade`.
- **Contexto**: `detalheRua()` (rua/bairro + pessoa homenageada via
  `candidatosPessoaDaRua()`/`pessoaPorNome()` + toponímia oficial CML),
  `festasDoMes()`, `efemeride()`, `saudacaoRegresso()`, `avisosZona()`.
- **Voz**: `diz(texto,canal)` (fila de 1, descarta o que envelhece),
  `dizJa()` (imediato, para confirmações), `salta()` (penaliza peso do
  canal via `reforca()`, auto-muda de canal após 3 saltos), `_falaAgora()`
  (reforço positivo ao ouvir até ao fim), `paraVoz()` (texto→fala),
  `frases()` (corte por frases com protecção de abreviaturas `RE_ABREV`).
- **Ouvido**: `iniciaOuvido()` (webkitSpeechRecognition contínuo, pausado
  durante a fala para não se ouvir a si próprio), `comando()` com a tabela
  `COMANDOS` (regex → acção).
- **Loop**: `novaPosicao()` (velocidade suavizada, rumo, passo por modo),
  `anunciar()` (posição prevista por `avanca()`, monta `f`, avisos →
  tempo → festas/efemérides → rua → `narrar()` → `narraIA()` → `diz()`),
  watchdog que destrava `S.anunciando` ao fim de 25 s, `seguraEcraLigado()`
  + vídeo-canvas anti-suspensão, `iniciaGPS()`/`iniciaSim()` (a simulação
  reproduz rotas embutidas em `ROTAS` com relógio acelerado).
- **IA local**: `ligaIA()`/`narraIA()` — WebLLM (Qwen2.5-1.5B) por WebGPU,
  opt-in, timeout 30 s, passthrough garantido quando desligada/indisponível.

Modos: `modoAtual()` devolve `"pe"` (<3 m/s) ou `"carro"`; raio de pesquisa,
horizonte de antecipação e passo entre anúncios dependem do modo.

---

## 2. FASE 1 — Conversa: gancho, «conta mais», «conta menos»

**Objectivo.** Acabar com o monólogo. Cada anúncio passa a ter dois níveis:
um *gancho* curto (1–2 frases, dito sempre) e um *desenvolvimento* (dito só
a pedido). E o utilizador pode encurtar em qualquer sentido.

**Desenho.**
- `narrar()` e os canais passam a devolver `{canal, gancho, resto}` em vez
  de um texto único. Regra de corte: o gancho são as primeiras 1–2 frases
  (usa `frases(texto, 2)`); o resto é o que sobra. Se o texto todo couber
  em 2 frases, `resto` é vazio.
- Guarda o último anúncio completo em `S.ultimoAnuncio={canal,gancho,resto}`.
- Comando de voz **«conta mais»** (e botão ⏵ na fila de ícones): fala
  `S.ultimoAnuncio.resto` (se vazio: "Não tenho mais sobre isto."). Sinal
  positivo forte: `reforca(canal, 1.08)`.
- Comando de voz **«conta menos»**: (a) interrompe a fala actual como
  `salta()` mas SEM contar para o auto-switch de canal; (b) baixa o nível
  de detalhe do canal actual em 1 (mínimo 1), como o «menos detalhe» actual;
  (c) sinal `reforca(canal, 0.92)`. Confirmação curta: "Vou ser mais breve."
- **Duração adaptativa à velocidade**: o número de frases do gancho e o
  tamanho máximo de `paraVoz()` passam a depender do modo — a pé 2 frases
  de gancho e limite 750; de carro 1 frase e limite 450; bicicleta (Fase 2)
  intermédio. Implementa como função `limitesFala()` consultada por
  `narrar()` e `paraVoz()`.
- **Pré-carregamento**: no fim de `anunciar()`, se `aFalar===true`, dispara
  em background (sem `await` no caminho principal, com try/catch) o
  `nominatim`+`escolher` da PRÓXIMA posição prevista (posição actual +
  `avanca(rumo, passo())`). O resultado aquece a cache de `busca()` — não
  cries um segundo mecanismo de cache.

**Comandos novos na tabela `COMANDOS`**: `/conta mais|desenvolve|continua essa/`,
`/conta menos|mais curto|abrevia/`. Actualiza o texto da «ajuda».

**Aceitação**: ver PLANO-TESTES T-F1.

---

## 3. FASE 2 — Movimento: bicicleta, percursos, desvios

### 3.1 Modo bicicleta
- `modoAtual()` passa a devolver `"pe"` (<2.2 m/s), `"bicicleta"`
  (2.2–8 m/s ≈ 8–29 km/h), `"carro"` (>8 m/s). Usa histerese simples (só
  muda de modo após 20 s estável no novo intervalo) para não oscilar em
  semáforos.
- Parâmetros: bicicleta → raio de pesquisa 2000 m, horizonte 90 s, passo
  600 m, gancho de 1–2 frases. Chip do modo: 🚴.
- Tudo o que hoje testa `modo==="pe"` deve ser revisto caso a caso:
  `detalheRua` e `olharEmVolta` ficam só a pé; POIs Overpass também a
  bicicleta (raio maior).

### 3.2 Percursos pedestres e ecopistas (OSM/Overpass)
- Fonte já usada (`overpass()`), nova consulta: relações
  `route=hiking|foot|bicycle` num raio de ~300 m da posição actual
  (`relation(around:...)["route"~"^(hiking|foot|bicycle)$"];out tags;`).
  Testa a consulta primeiro no browser (protocolo da secção 7) — o Overpass
  é o serviço mais frágil que usamos (429 frequentes); mantém o throttle e
  a tolerância a falha.
- Quando o utilizador está a pé/bicicleta e cruza um percurso ainda não
  anunciado (`marcaDito("rota:"+nome)`), anúncio prioritário curto:
  "Estás a cruzar a PR5 — Rota das Levadas, um percurso circular de 7
  quilómetros." Usa os tags `name`, `ref`, `distance`, `from`/`to` quando
  existirem; nunca inventes o que não estiver nos tags.

### 3.3 Radar de raridades + desvio sugerido (por voz)
- Novo passo em `anunciar()` (a pé e bicicleta apenas): entre os artigos de
  `f.todos`, procura um com classificação de relevo — heurística: o extracto
  contém /monumento nacional|im[óo]vel de interesse p[úu]blico|patrim[óo]nio
  mundial/i — que esteja a 100–500 m, FORA do sector frontal (o frontal já
  é coberto pelo fluxo normal), e ainda não dito.
- Se existir, anúncio de desvio com direcção relativa calculada por
  `rumoG`/`anguloEntre` (já existem): "Vale um desvio: à tua esquerda, a
  300 metros, está o Pelourinho de X, Monumento Nacional. Dois minutos a
  pé." `marcaDito`. Máximo UM desvio sugerido por anúncio, e nunca de carro.
- Sinal de interesse: se o utilizador disser «conta mais» ao desvio,
  `reforca("HISTORIA", 1.08)`.

**Aceitação**: PLANO-TESTES T-F2.

---

## 4. FASE 3 — Interesses declarados, colecções e passaporte

### 4.1 Interesses declarados
- Novo bloco em ⚙ "Os meus interesses": lista de temas com checkbox.
  Temas iniciais e o seu mapeamento (guarda em `S.interesses`, persistido):
  - azulejos → regex /azulej/i nos extractos
  - castelos e fortalezas → /castelo|forte|fortaleza|muralha/i
  - igrejas e conventos → /igreja|convento|mosteiro|capela|s[ée]/i
  - arte urbana → Overpass `tourism=artwork`
  - vinho e gastronomia → reforço automático do canal SABORES (peso ×1.5)
  - natureza e miradouros → /miradouro|serra|rio|cascata|parque natural/i
    + Overpass `tourism=viewpoint`
- Efeito no motor: em `pontua()`, bónus de +30 quando o título ou o início
  do extracto casa com um interesse activo. Em `olharEmVolta()` e no radar
  de raridades, os interesses activos têm prioridade sobre a pontuação base.
- Comandos de voz: «interessa-me X» / «deixou de me interessar X» com os
  nomes dos temas. Confirmação curta.

### 4.2 Passaporte de território (áudio-primeiro)
- `M.visitas` já regista concelhos. Acrescenta `M.freguesias` (mesmo
  padrão, chave "concelho/freguesia").
- Na primeira visita de sempre a um concelho, o anúncio de entrada inclui:
  "É o teu 47.º concelho — ainda te faltam 261." (308 no total; conta
  `Object.keys(M.visitas).length`.)
- Painel ⚙ → "O teu passaporte": contagem de concelhos e freguesias,
  lista dos últimos 10. SEM mapa nesta fase (mapa = ecrã durante o uso;
  pode vir mais tarde como consulta em casa).
- Comando de voz «passaporte»: diz a contagem em voz.

### 4.3 Colecções verificáveis
- PRÉ-REQUISITO: validar as listas no Wikidata via SPARQL (protocolo da
  secção 7). Consultas a testar (uma a uma, com contagem real):
  - Pelourinhos de Portugal: instâncias de pelourinho (Q1782709 —
    CONFIRMA o QID antes de usar) com coordenadas em Portugal.
  - Castelos em Portugal (Q23413 castle, country Q45, com coordenadas).
  - Moinhos de vento, faróis, aquedutos — mesmo padrão, só integrar os
    que devolverem listas com >30 itens georreferenciados.
- Estrutura: `M.colecoes = {pelourinhos:{vistos:{qid:timestamp}, total:N}}`.
  O total vem da contagem SPARQL, obtida uma vez e guardada com a data.
- Detecção: quando um item de HISTÓRIA dito tem QID que pertence a uma
  colecção (verifica o P31 do QID — já existe `wikidata()`/`claim()`),
  regista e anuncia: "É o 12.º pelourinho da tua colecção — de 154
  classificados em Portugal."
- Comando «colecções»: resumo por voz.

### 4.4 Estatísticas de viagem
- Acumula em `M.stats`: metros percorridos por modo (a partir de
  `novaPosicao`, só com o companheiro ligado), n.º de factos ouvidos até ao
  fim, concelhos novos por mês (deriva de `M.visitas`).
- Comando «estatísticas»/«quanto andei»: resposta por voz ("Este mês:
  34 quilómetros a pé, 3 concelhos novos, 87 histórias ouvidas.").
  Painel ⚙ com o mesmo resumo em texto.

### 4.5 Briefing de chegada
- Na primeira visita de sempre a um concelho (`saudacaoRegresso` já detecta
  visitas; acrescenta o caso "nunca visto"), em vez do fluxo normal, monta
  um briefing de ~60 s: 1 frase de identidade (intro do artigo do concelho),
  1 facto de história, 1 prato/sabor, os números INE com comparação a
  Lisboa (já existem), e festas do mês se houver. Tudo com material já
  disponível nos canais — o briefing é um ORQUESTRADOR, não uma fonte nova.
- Termina com: "Boa descoberta. Diz «conta mais» sobre qualquer tema."

**Aceitação**: PLANO-TESTES T-F3.

---

## 5. FASE 4 — Áudio contínuo: rádio e podcasts com ducking

**Pedido do João**: quando o companheiro já não tem nada de relevante a
dizer, pergunta se o utilizador quer rádio, música ou podcast, e passa a
esse áudio SEM o utilizador olhar para o telemóvel — e o companheiro
continua a poder intervir.

**Realidade técnica a respeitar (sê honesto na implementação e no README):**
uma webapp NÃO pode controlar o Spotify/YouTube Music/apps de podcasts de
outra aplicação, nem navegar nelas. O que uma webapp PODE fazer, e é o que
se vai construir:

### 5.1 Rádio interna (o caminho principal)
- Player `<audio>` dentro da app com estações de rádio portuguesas por
  stream directo. PRÉ-REQUISITO: descobrir e testar os URLs de stream reais
  (protocolo da secção 7 — um stream é testável criando um `Audio(url)` e
  verificando o evento `canplay` no browser de teste; radio-browser.info
  (`https://de1.api.radio-browser.info/json/stations/bycountry/portugal`)
  é um directório aberto com CORS para descobrir streams — testa-o).
- Comandos: «rádio» (retoma a última ou a primeira da lista), «outra
  estação», «pára a rádio». Selecção inicial das estações em ⚙.
- **Ducking**: quando `anunciar()` tem algo a dizer, baixa `audio.volume`
  para 0.15 durante a fala (eventos `onstart`/`onend` da utterance já
  existem em `_falaAgora`) e repõe no fim. O companheiro NUNCA deixa de
  vigiar a viagem — a rádio é fundo, não substituição.
- Media Session API (`navigator.mediaSession`): metadados e controlos no
  ecrã de bloqueio/auscultadores (play/pause/next → outra estação). É isto
  que permite controlar sem olhar.

### 5.2 Podcasts internos
- Em ⚙, o utilizador cola URLs de feeds RSS dos seus podcasts (ou escolhe
  de uma lista inicial de podcasts portugueses — testa os feeds antes de
  os listar). Parser RSS já existe em espírito (`parseNoticiasXML`) — os
  feeds de podcast têm `<enclosure url>` com o áudio; muitos feeds têm
  CORS aberto, os que não tiverem NÃO funcionam (o áudio não passa por
  proxy de texto) — documenta os que falharem.
- Comandos: «podcast» (retoma onde ficou — guarda posição em `M.podcast`),
  «próximo episódio», «pára o podcast». Mesmo ducking da rádio.

### 5.3 Handoff externo (fallback honesto)
- Comando «abre o Spotify»: tenta `window.open("spotify:")` e, se falhar,
  `https://open.spotify.com`. AVISA por voz antes: "Vou abrir o Spotify —
  a partir daí deixo de poder falar contigo; volta à app para me ouvires."
  Não prometas mais do que isto.

### 5.4 Oferta proactiva
- Gatilho: 2 anúncios consecutivos sem nada novo para dizer (`narrar()`
  devolveu null 2×) E nenhum áudio de fundo activo → UMA vez por hora no
  máximo: "Por aqui está sossegado. Queres rádio ou um podcast? Diz
  «rádio» ou «podcast»." `marcaDito` com chave horária para não repetir.

**Aceitação**: PLANO-TESTES T-F4.

---

## 6. FASE 5 — Fontes novas de conteúdo (protocolo apertado)

Por ordem de valor esperado. NENHUMA entra sem passar o protocolo da
secção 7.

### 6.1 Literatura geolocalizada (domínio público)
- Conceito: excertos de escritores portugueses no domínio público
  (morte < 1955: Eça, Camilo, Ramalho, Oliveira Martins, Fialho…) ligados
  aos lugares que descrevem, LIDOS EM VOZ — canal HISTÓRIA ou novo tipo de
  item "LEITURA".
- Caminho técnico a validar: API da Wikisource PT
  (`pt.wikisource.org/w/api.php`, mesmo formato da Wikipédia, `origin=*`
  deve funcionar — TESTA). Estratégia: pesquisa full-text do nome da
  localidade nas obras, extrai parágrafos (200–600 caracteres) que
  mencionem o lugar, com autor+obra sempre citados na fala ("Escreveu Eça
  de Queirós, em A Cidade e as Serras: …").
- Curadoria mínima: só aceitar parágrafos onde o nome do lugar aparece por
  extenso; nunca cortar a meio de uma frase; `marcaDito` por obra+parágrafo.
- Se a pesquisa full-text da Wikisource se revelar fraca (risco real),
  recuo aceitável: tabela curada no código com ~30 pares lugar→obra→capítulo
  para as ligações mais famosas, construída manualmente com verificação.

### 6.2 SIPA/DGPC e MatrizPCI
- SIPA (inventário arquitectónico, cobre freguesias rurais): descobrir o
  formato de pesquisa do sítio, testar via proxy, extrair ficha (época,
  estilo, história). Só integrar se a extracção for estável em ≥5 fichas
  de teste de zonas diferentes.
- MatrizPCI (património imaterial: lendas, romarias, artes): mesmo processo.
  Destino: canal SABORES (tradições) e HISTÓRIA (lendas).
- Se qualquer um se revelar não-extraível de forma fiável, DOCUMENTA no
  README e segue em frente — não forçar.

### 6.3 Mais câmaras em ArcGIS Hub
- Método validado com Lisboa. Para cada cidade-alvo (Porto, Coimbra, Braga,
  Guimarães, Évora, Faro): procurar o hub real (`site:hub.arcgis.com` +
  nome, ou o catálogo `/api/feed/dcat-us/1.1.json` de candidatos),
  confirmar org-ID real, procurar camadas de toponímia/património, testar
  uma consulta espacial real. ATENÇÃO: uma ronda anterior "encontrou" hubs
  de Porto/Coimbra/Braga que NÃO EXISTEM (domínios inventados por um modelo
  de pesquisa). Parte do zero, confirma tudo.
- Estrutura no código: generalizar `ehLisboa()`/`toponimiaCML()` para um
  registo `CAMARAS_ARCGIS = {lisboa:{toponimia:URL, patrimonio:[URLs]}, …}`
  em que Lisboa é a primeira entrada.

### 6.4 Desemprego por concelho (IEFP) — tentativa única
- O INE não tem (confirmado — só distrito). O IEFP publica ficheiros
  mensais por concelho em dados.gov.pt. Tenta UMA via: o catálogo
  `dados.gov.pt/api/1/` via proxy → URL do recurso (xlsx/csv) → o CSV, se
  existir, pode ser lido via proxy. Se a cadeia não fechar num dia de
  trabalho, pára e documenta.

**Aceitação**: PLANO-TESTES T-F5.

---

## 7. Protocolo de validação de fontes (obrigatório, sem excepções)

Para CADA endpoint novo, no browser de teste (página da app aberta):

1. `fetch()` directo com timeout 10 s → regista status e primeiros 300
   caracteres REAIS da resposta.
2. Se falhar: mesma coisa via `https://r.jina.ai/<url>`.
3. Asserção de conteúdo: a resposta contém MESMO o que se espera (um campo
   concreto, um nome de terra real)? Um 200 com HTML de erro não conta.
4. Teste com um segundo caso diferente do primeiro (outra terra, outro id).
5. Só depois: integrar, sempre dentro de try/catch com fallback.
6. Registar no README: URL, o que dá, cobertura, directo ou proxy, e a
   amostra que provou.

Fontes que falharem ficam documentadas no README na secção de investigação
(o que se tentou e porquê falhou) — isso poupa rondas futuras.

---

## 8. FASE 6 — Pré-viagem como produto

- Renomear na UI: "Simulação (teste no PC)" → "Pré-viagem 🛋 (ouve o
  caminho antes de o fazeres)".
- Acrescentar ao arranque um campo de destino por texto: geocodifica com
  o Nominatim (`/search?q=...&countrycodes=pt`), gera uma rota RECTA por
  interpolação entre a posição actual (ou um ponto de partida escrito) e o
  destino — sem API de rotas nesta fase; a linha recta com amostragem de
  ~8 pontos chega para "ouvir o que há pelo caminho". Sê transparente na
  UI: "percurso aproximado em linha recta".
- No fim da pré-viagem: "Boa viagem a sério. Quando fores, eu vou contigo."
  E o material dito NÃO entra em `M.ditos` (senão a viagem real fica muda!)
  — usa um Set de sessão separado quando `fonte==="sim"`. ESTA É A REGRA
  MAIS IMPORTANTE DA FASE.

**Aceitação**: PLANO-TESTES T-F6.

---

## 9. Ordem de execução e dependências

1. Fase 1 (conversa) — melhora tudo o resto; sem dependências.
2. Fase 2 (movimento) — depende dos limites de fala da Fase 1.
3. Fase 4 (áudio contínuo) — independente; alto valor para o João; pode
   trocar com a 3 se a validação de streams correr bem.
4. Fase 3 (colecções) — depende da validação SPARQL prévia.
5. Fase 5 (fontes novas) — investigação com risco; intercalar com as outras.
6. Fase 6 (pré-viagem) — rápida; bom fecho.

Depois de CADA fase: correr a bateria de regressão (PLANO-TESTES secção R)
antes do push. O histórico deste projecto mostra que quase todas as rondas
partiram alguma coisa subtil — a bateria R existe por experiência própria.
