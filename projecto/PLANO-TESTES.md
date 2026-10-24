# Companheiro de Viagem — Plano de Testes (executável pelo Sonnet 5)

Testes específicos e aprofundados de tudo o que está implementado, mais os
critérios de aceitação das fases do `PLANO-EXECUCAO.md`. Escrito para ser
executado por um modelo com acesso ao browser de teste (Browser pane) e ao
PowerShell do PC.

## Ambiente e método

- Servidor local: `preview_start` com o nome `companheiro` (launch.json em
  `.claude/` aponta para `servir.py`, porta 8123). Abrir `http://localhost:8123`.
- Produção: `https://lovereplit.github.io/companheiro-viagem/` — os testes
  de fontes correm melhor aqui (origem HTTPS real).
- Método principal: `javascript_tool` na consola da página. TODAS as funções
  internas são globais (não há módulos) — chamam-se directamente.
- Entre execuções que dependem de estado limpo:
  `localStorage.removeItem("cv-mem"); localStorage.removeItem("cv-prefs"); location.reload();`
- O botão «Ligar companheiro» exige gesto: usa
  `document.querySelector("#ligar").click()` via javascript_tool.
- ATENÇÃO ao ambiente: o Browser pane em segundo plano TRAVA `setInterval`
  — a simulação pára entre chamadas. Para testar o fluxo de anúncios chama
  `anunciar(lat,lon)` directamente em vez de esperar pelo timer. Não é um
  bug da app (no telemóvel com ecrã ligado funciona) — documentado.
- Latência: primeira chamada a uma zona ~5–15 s (rede fria); repetida <2 s
  (cache). Timeouts nos testes: 20 s.
- O que NÃO é testável neste ambiente (verificar apenas que não rebenta e
  que o fallback actua): áudio audível do TTS, reconhecimento de voz por
  microfone, GPS real, wake lock físico, descarga do modelo WebLLM (~1 GB —
  NUNCA a inicies num teste). Estes só no Pixel do João.

## Formato do relatório final

Para cada teste: `ID | PASSOU/FALHOU/INCONCLUSIVO | evidência (1 linha)`.
Um FALHOU numa regressão (secção R) bloqueia o push. INCONCLUSIVO exige
explicação (ex.: fonte externa em baixo no momento — repetir mais tarde).

---

## R. BATERIA DE REGRESSÃO (correr antes de cada push)

Cada uma destas foi um bug real corrigido; o teste garante que não volta.

**R1 — Regex de povoação com acentos.** Em JS, `\b` falha antes de "é".
`RE_POVOACAO.test("évora é a cidade portuguesa...")` → `true`. E
`artigosLocalidade({freguesia:"Meadela",concelho:"Viana do Castelo"},41.694,-8.833,"pt")`
devolve lista que inclui "Viana do Castelo".

**R2 — Inglês nunca sai sem tentativa de tradução.**
`escolher(38.7702,-9.1713,"pe")` → `lang==="pt"` e todos os
`escolhidos[].lang` são `"pt"` (zona do Lumiar tem cobertura PT).
E `traduzParaPT({titulo:"Telheiras Station",texto:"x",lang:"en"})` →
`titulo==="Estação Telheiras"`, `lang==="pt"`.

**R3 — Toponímia CML: abreviaturas e homónimos.**
`toponimiaCML("Praça Dom Pedro IV",38.7139,-9.1394)` →
`DESIGNACAO==="Praça D. Pedro IV"` (não "Rua Pedro Ivo").
`toponimiaCML("Avenida da Liberdade",38.7180,-9.1430)` →
`DESIGNACAO==="Avenida da Liberdade"` (não "Escadinhas da Liberdade").

**R4 — Pessoa da rua: correspondência exacta vence fama.**
`(async()=>{for(const c of candidatosPessoaDaRua("Rua Padre Cruz")){const p=await pessoaPorNome(c); if(p) return p.titulo;}})()`
→ `"Padre Cruz"` (não "Padre Pio"). E `candidatosPessoaDaRua("Rua Augusta")`
→ `[]` (não é pessoa); `candidatosPessoaDaRua("Rua Professor Aires de Sousa")`
→ `["Aires de Sousa"]`.

**R5 — Corte de frases protege abreviaturas.**
`frases("O templo do séc. XVI foi restaurado. Tem azulejos de Sto. António no interior. Fim.",1)`
→ contém "séc. XVI foi restaurado." completo (não corta em "séc.").

**R6 — INE usa o concelho limpo, não o título da Wikipédia.**
`(async()=>{const f={local:{concelho:"Reguengos de Monsaraz"},base:[],escolhidos:[]}; return await ineComLisboa("PODER_COMPRA","Reguengos de Monsaraz");})()`
→ `aqui.valor` ≈ 90.9 e `lisboa.valor` ≈ 186.3. (Os valores exactos podem
mudar com actualizações do INE — aceitar aqui∈[60,120], lisboa∈[150,220].)

**R7 — Notícias sem duplicação de fonte e com escalada.**
`noticias({concelho:"Lisboa",freguesia:"Lumiar"})` → ≥1 item; nenhum
`titulo` termina com " - " + o próprio `fonte`.
`noticias({concelho:"Reguengos de Monsaraz",freguesia:"Monsaraz"})` → ≥1
item (escalou até encontrar).

**R8 — Jornal regional tem prioridade onde existe.**
`noticias({concelho:"Sintra",freguesia:"Sintra"})` → primeiro item com
`fonte==="Sintra Notícias"`. Idem Coimbra→"Diário As Beiras",
Ponta Delgada→"Diário dos Açores", Funchal→"Funchal Notícias".

**R9 — Sectores direccionais rodam com o rumo.**
`olharEmVolta(38.7702,-9.1713,90,[])` e o mesmo com rumo 270: o MESMO
título aparece com lados opostos ("esquerda" num, "direita" no outro).

**R10 — Watchdog e travão de anúncio.** `S.anunciando=true;
S.inicioAnuncio=Date.now()-30000;` esperar 6 s após o arranque do intervalo
(o intervalo só existe depois de «Ligar») → `S.anunciando===false`.

**R11 — narraIA em passthrough quando desligada.**
`await narraIA("Texto de teste.")` → exactamente `"Texto de teste."`
(sem motor carregado). NUNCA ligar `#chkIA` num teste.

**R12 — Dedupe persistente.** `marcaDito("teste:x")` →
`S.ditos.has("teste:x")===true`; após `location.reload()` (sem limpar
storage) continua `true` e `M.ditos["teste:x"]` é um timestamp.

**R13 — Canais respeitam o desligar.** Com
`S.ativos.DEMOGRAFIA=false`, `narrar(f,…)` nunca devolve `canal==="DEMOGRAFIA"`
(verificar com um `f` de Évora, 5 chamadas seguidas).

**R14 — Sem regressão de arranque.** Recarregar a página → zero erros novos
na consola além dos conhecidos (403/503 de corsproxy/allorigins — a cadeia
de proxies tenta-os e falha por design; e 429 esporádicos do Overpass).
Qualquer `ReferenceError`/`SyntaxError` = FALHOU.

---

## T-EXIST. Aprofundamento do já implementado

**E1 — Localizações de referência** (para cada uma: `anunciar(lat,lon)`
directo, depois `get_page_text`; verificar que o texto é português,
coerente com o local, sem "undefined"/"null"/"[object"):
- Lisboa histórica: 38.7098,-9.1330 (Sé)
- Lisboa residencial: 38.7702,-9.1713 (Lumiar)
- Cidade média: 40.2033,-8.4103 (Coimbra centro)
- Vila: 38.4430,-7.3810 (Monsaraz)
- Rural profundo: 37.96,-7.98 (Beja interior)
- Ilha: 37.7412,-25.6756 (Ponta Delgada)
- Fronteira de cobertura: 41.8,-6.75 (Trás-os-Montes raiano)

**E2 — Memória entre "viagens".** Limpar storage; `anunciar` em Monsaraz;
guardar `S.ditos.size`; recarregar SEM limpar; `anunciar` no mesmo ponto →
nenhum item repetido (comparar textos registados) e `saudacaoRegresso`
só dispara se a visita anterior tiver >20 h (forçar:
`M.visitas["Reguengos de Monsaraz"]=[Date.now()-90*24*3600e3]` → prefixo
"Já por aqui tinhas passado em maio").

**E3 — Pesos e auto-mudança.** Estado limpo; `S.canal="ECONOMIA"`;
simular 3 `salta()` com `falaCanal="ECONOMIA"` forçado → `S.canal` mudou
e o registo "Noto que tens saltado economia" apareceu no log. `M.pesos.ECONOMIA<1`.

**E4 — Ligações entre terras.**
`M.entidades["Vasco da Gama"]={onde:"Sines",quando:Date.now()-3600e3};`
`ligaEntreTerras({chave:"x",texto:"...Vasco da Gama..."},"Vidigueira")` →
string com "Sines". Com `onde:"Vidigueira"` (mesmo concelho) → `""`.

**E5 — Sazonalidade e efemérides.** `festasDoMes` com base=artigo de Viana
do Castelo → texto com "Romaria" e mês corrente ou seguinte (em agosto).
`efemeride` com `f.todos` de 39.599,-8.874 (campo de Aljubarrota) → dispara
apenas se a data corrente estiver a ±3 dias de 14 de agosto — se estiver
fora da janela, o resultado esperado é `null` (anotar a data do teste).

**E6 — IPMA/fogos degradam com elegância.** `avisosIPMA("Évora")` →
array (possivelmente vazio — sem avisos activos não é falha);
`fogosPerto(38.5,-8.0)` → array; nenhum lança excepção não-capturada.

**E7 — Robustez a falha de fonte.** Substituir temporariamente
`window.fetch` por uma versão que rejeita para `*.wikipedia.org` (guardar a
original e repor no fim!); `anunciar(38.57,-7.907)` → não lança, e ou fala
de outra fonte ou fica silencioso — mas `S.anunciando` volta a `false`.

**E8 — paraVoz.** `paraVoz("A densidade é 45 hab./km² a 100 m — ver https://x.pt")`
→ sem URL, "habitantes por quilómetro quadrado", "100 metros".
`paraVoz("545 796 habitantes")` → "545796 habitantes".

---

## T-F1. Aceitação da Fase 1 (conversa)

**F1.1** `narrar` devolve `{gancho,resto}`; `gancho` tem ≤2 frases
(contar por `split(/(?<=[.!?])\s/)`) para um artigo longo (Sé de Évora).
**F1.2** `comando("conta mais")` após um anúncio com resto → o resto é
registado/falado; com resto vazio → "Não tenho mais sobre isto.".
**F1.3** `comando("conta menos")` → `S.detalhe[canal]` desceu 1 (não abaixo
de 1); `S.saltos[canal]` NÃO incrementou; peso desceu (`M.pesos`).
**F1.4** «conta mais» sobe o peso: `M.pesos[canal]` maior que antes.
**F1.5** Limites por modo: com `S.veloc=1` (pé) vs `S.veloc=25` (carro),
o texto final registado é visivelmente mais longo a pé (comprimento >1.4×).
**F1.6** Pré-carregamento: após `anunciar`, verificar que a cache de
`busca` contém entradas para a posição seguinte (inspeccionar `cache`
— é um Map global) sem segunda chamada explícita.
**F1.7** Regressão R completa.

## T-F2. Aceitação da Fase 2 (movimento)

**F2.1** Histerese de modo: sequência de `novaPosicao` com velocidades
1.5→5→5→5 m/s em <20 s → modo ainda "pe"; mantendo 5 m/s >20 s → "bicicleta";
chip 🚴.
**F2.2** Percursos: em zona com PR conhecida (ex. Sintra serra 38.787,-9.39
— confirmar com Overpass primeiro qual existe ali), item "Estás a cruzar a
PR…" dito uma única vez (`marcaDito`).
**F2.3** Desvio sugerido: construir cenário com `f.todos` contendo artigo
com "Monumento Nacional" a ~300 m fora do sector frontal → anúncio com
lado correcto (validar com rumo invertido, lado troca — como R9).
De carro (`S.veloc=25`) → NUNCA sugere desvio.
**F2.4** Overpass 429: forçar 3 chamadas seguidas; a app não rebenta e
regista aviso (`console.warn`), anúncio segue sem POIs.

## T-F3. Aceitação da Fase 3 (interesses/colecções)

**F3.1** Interesse "azulejos" activo → `pontua()` de um artigo cujo
extracto contém "azulejos" sobe ≥30 vs. mesmo artigo sem o interesse.
**F3.2** Passaporte: estado limpo; primeira visita a concelho → anúncio
com "É o teu 1.º concelho"; `M.visitas` tem 1 chave; comando «passaporte»
responde com a contagem.
**F3.3** Colecções: ANTES de tudo, validar a consulta SPARQL de pelourinhos
com contagem real (>30 com coordenadas; senão a colecção não entra).
Depois: item de HISTÓRIA com QID de pelourinho → `M.colecoes.pelourinhos.vistos`
ganha a entrada e o anúncio inclui "da tua colecção".
**F3.4** Estatísticas: após simular 2 km a pé, comando «estatísticas» →
resposta inclui os km (±10%).
**F3.5** Briefing de chegada: concelho nunca visto → briefing (verificar
presença de: identidade + história + sabor + números INE); segunda visita
→ fluxo normal, sem briefing.

## T-F4. Aceitação da Fase 4 (áudio contínuo)

**F4.1** Directório de rádios: o endpoint radio-browser devolve estações
PT com `url_resolved`; escolher 3, criar `new Audio(url)` e verificar
evento `canplay` em ≤10 s para pelo menos 2 (streams caem — 2/3 chega,
documentar as que falham).
**F4.2** Ducking: com rádio a tocar (`audio.volume===1`), disparar
`diz("teste",null)` → `volume` desce ≤0.2 durante a fala e repõe depois
(no ambiente de teste o TTS pode ser instantâneo — validar pela sequência
de eventos, não por tempo real).
**F4.3** Podcast: feed RSS de teste com `<enclosure>`; «podcast» toca;
recarregar página → «podcast» retoma posição (±30 s) de `M.podcast`.
**F4.4** Oferta proactiva: forçar `narrar` a devolver null 2× (zona já
toda dita) → oferta aparece UMA vez; repetir → não repete na mesma hora.
**F4.5** Handoff Spotify: comando dispara o aviso por voz ANTES de
qualquer `window.open` (verificar ordem no log).

## T-F5. Aceitação da Fase 5 (fontes novas)

**F5.1** Cada fonte nova tem no README a amostra real que provou (conferir
que a amostra existe e corresponde ao endpoint).
**F5.2** Wikisource: pesquisa "Leiria" devolve obras; o excerto escolhido
contém "Leiria" por extenso, tem 200–600 caracteres, começa e termina em
fronteira de frase, e o texto falado inclui autor+obra.
**F5.3** SIPA/MatrizPCI (se integrados): 5 fichas de 5 distritos diferentes
extraem título+época sem lixo HTML; se <5 passarem, a fonte NÃO entra.
**F5.4** Câmaras ArcGIS novas: para cada uma, consulta espacial real com
2 coordenadas diferentes da cidade → features coerentes; org-ID confirmado
a partir do catálogo dcat da própria câmara (NUNCA de memória do modelo).
**F5.5** Fontes descartadas: verificar que o README documenta cada
descartada com a razão real do descarte.

## T-F6. Aceitação da Fase 6 (pré-viagem)

**F6.1** Geocodificação: destino "Évora" resolve para coordenadas ±20 km
do centro de Évora.
**F6.2** A REGRA DE OURO: correr uma pré-viagem completa (Lisboa→Évora,
turbo 200); no fim `M.ditos` NÃO contém as chaves dos itens falados na
pré-viagem (comparar snapshot antes/depois); iniciar depois modo GPS
simulando o mesmo trajecto → os mesmos temas voltam a poder ser ditos.
**F6.3** A UI declara "percurso aproximado em linha recta".

---

## Notas finais para o executor dos testes

- Testa SEMPRE em produção (GitHub Pages) além do localhost quando o teste
  envolve fontes externas — o comportamento de CORS pode diferir de origem
  para origem.
- Fontes externas oscilam (429/503 do Overpass e dos proxies são normais).
  Distingue "a fonte está em baixo agora" (INCONCLUSIVO, repetir) de "o
  código está errado" (FALHOU). Em dúvida, repete o teste 10 minutos depois.
- Regista os tempos: um `anunciar` frio >20 s é um problema de desempenho
  a reportar mesmo que o conteúdo esteja certo.
- No fim de cada sessão de testes: repor `window.fetch` se o alteraste,
  limpar `cv-mem`/`cv-prefs` de teste, e NUNCA deixar o `#chkIA` ligado.
