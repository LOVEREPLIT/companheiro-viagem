# Base de Conhecimento Geo — desenho (24/10/2026)

Desenho, não implementação. Medições de hoje, com pedidos reais (o Overpass deu 429 duas vezes e passou à terceira). `saida/contagens_lisboa.md` não existia.

## 0. Avaliação da visão

- (1) base primeiro: **sim**, só para conhecimento permanente; dados vivos (IPMA, fogos, agenda, Carris, meteorologia) sempre ao vivo.
- (2) guarda tudo: **não "tudo"**; só o permanente, citado e verificado; o que vem do telemóvel fica em quarentena.
- (3)(4)(5) geo, pré-viagem, só o novo: **sim**, com tiles geohash.
- (6) variedade: **sim**, com facetas por entidade (§8).
- (7) LLM: **editores e proponentes, nunca fonte** (H2 aceite, reforçada no §4).
- (8) Lisboa inteira: ruas, património, personalidades falecidas e economia por freguesia (INE), sim; empresas só comércio histórico com fonte verificada ao vivo.

**Crítica à H2:** tem uma falha de circularidade. Se o LLM propõe um facto e a confirmação vem do DuckDuckGo, a página pode ser gerada por IA. Só conta uma confirmação de domínio da lista branca (§4).

**Achado:** Lumiar e Benfica são pobres na Wikipédia e na etimologia OSM, mas ricos na toponímia CML (§1). O esqueleto da base é a toponímia CML.

## 1. Medições

**Lisboa (concelho, área OSM admin_level 7)**

| Universo | Contagem |
|---|---|
| Nomes de via únicos (OSM; 15 025 segmentos) | 4 412 |
| …com `name:etymology:wikidata` | 911 (843 QIDs distintos) |
| Topónimos CML (`Cultura_Toponimia`) | 3 671 |
| …texto `HISTORIAL` | 5,17 M caracteres; JSON 5,86 MB bruto / **2,03 MB gzip** |
| Património CML (camadas 11 + 12) / casas religiosas | 222 + 63 / 76 |
| OSM `historic` / museu+atracção+arte+miradouro / culto / `memorial` | 1 064 / 1 068 / 248 / 351 |
| OSM com `wikidata` | 2 028 |
| Wikidata com coordenadas (caixa) / `P131*` Lisboa / com artigo PT | 2 930 / 2 167 / 899 |
| Falecidos nascidos/mortos em Lisboa, com artigo PT | 3 633 |

**Marco 1 (relações OSM: Lumiar 6384124 e Benfica 6385130, admin_level 8)**

| | Lumiar | Benfica |
|---|---|---|
| Nomes de via únicos OSM | 298 | 304 |
| …com etimologia Wikidata | 56 | 27 |
| Topónimos CML (freguesia exacta) / com historial | 253 / 240 | 182 / 175 |
| Topónimos de pessoas (legenda com datas) | 191 | 116 |
| CML bruto / gzip | 522 / 182 KB | 306 / 104 KB |
| OSM historic / museu / atracção+arte+miradouro / culto / memorial | 48 / 2 / 23 / 10 / 14 | 46 / 0 / 15 / 10 / 6 |
| OSM com wikidata (sem vias) / Wikidata `P131+` freguesia | 49 / 45 | 63 / 27 |
| Wikipédia geosearch 1,5 km do centro | 14 | 17 |

Notas:

- O `P131` do Wikidata quase nunca aponta para a freguesia; a atribuição tem de ser pelo polígono OSM.
- `FREGUESIAS LIKE '%Benfica%'` apanha também São Domingos de Benfica; comparar por token exacto.
- Santa Maria Maior (Alfama/Baixa): 370 topónimos, 163 KB gzip. **Não é demasiado grande**; fica como marco 2, reaproveitando o já feito em Alfama.

**Não medi:** texto total da Wikipédia para Lisboa, área exacta das freguesias (estimo 6,6 e 8 km²), casamento geométrico CML↔OSM, licença da CML, tamanho real das facetas, fidelidade dos modelos locais.

**Estimativas:** marco 1 com facetas ≈ 1,5–2 MB bruto (0,6–0,8 MB gzip); Lisboa ≈ 15–25 MB bruto (5–9 MB gzip). Cabe com folga no GitHub Pages.

## 2. Esquema (decisão)

**Entidade** (`base/factos/entidades.jsonl`, uma por linha, ordenada por `id`, para diffs legíveis):

```json
{"id":"wd:Q123","aliases":["osm:w4567","cml:top:2240"],"tipo":"via|monumento|museu|edificio|pessoa|lugar|comercio_historico|freguesia",
 "nome":"Rua Virgínia Quaresma","geo":{"p":[38.70,-9.21],"bbox":[...],"tiles":["eycs0w","eycs0x"]},
 "freguesia":"Belém","homenageia":"wd:Q10379870","nomes_anteriores":["..."],
 "estado":"publicada|quarentena","esquema":1}
```

Id estável: `wd:QID`, senão `cml:top:TOP_ID`/`cml:pat:OBJECTID`, senão `osm:{n|w|r}ID`; os restantes ficam em `aliases`. Nunca se reutiliza um id.

**Facto** (`base/factos/factos.jsonl`):

```json
{"id":"f:<sha1(entidade|faceta|fonte.url|ancora)>[0:12]","entidade":"wd:Q123",
 "faceta":"nome|historia|gente|arquitectura|economia|curiosidade|literatura|antes",
 "gancho":"1 frase","texto":"2-4 frases","variantes":["outra formulação do MESMO facto"],
 "fonte":{"url":"...","titulo":"...","recolhido":"2026-10-24","ancoras":["frase literal do texto-fonte", "..."]},
 "licenca":"CML-?|CC-BY-SA-4.0|ODbL|CC0|PD","confianca":"A|B|C",
 "metodo":"det|llm:haiku-5.5|llm:qwen3-30b","verif":{"auto":"ok","auditado":"2026-11-02|null"},
 "chave_dito":"compatível com marcaDito()","validade":"permanente"}
```

- Níveis de confiança: **A** = institucional (CML, DGPC, INE); **B** = colaborativo (Wikipédia, Wikidata, OSM); **C** = web na lista branca.
- `ancoras` é obrigatório. Sem âncora literal na fonte guardada, o facto não existe.

## 3. Ficheiros e partição (decisão)

- **Tiles geohash-6** (≈1,2 × 0,6 km): Lisboa ≈ 140–160, marco 1 ≈ 20–25, 30–60 KB gzip cada.
- A entidade vive no tile do centróide; os outros tiles que uma via atravessa levam um "stub" `{id, pontos, tile_casa}`.
- `docs/base/indice.json` guarda o esquema, a versão, `{tile: {hash, n_factos, completo:{via,poi,pessoa}}}` e os polígonos simplificados das freguesias cobertas.
- `docs/base/t/<geohash>.json` são os tiles derivados, gerados a partir dos `.jsonl` e nunca editados à mão.
- `base/bruto/<fonte>/<freguesia>-<data>.json.gz` guarda os snapshots das respostas reais, em git. São a prova das âncoras: CML Lisboa ≈ 2 MB.
- `base/*.py`: scripts de construção. A app continua num ficheiro único.
- No telemóvel: IndexedDB `cv-base` (stores `tiles`, `novos` = quarentena, `meta`), nunca localStorage (tecto de cerca de 5 MB, já usado por `cv-cache`/`cv-mem`).

## 4. Pipeline de construção

**C0 — recolha determinística**, por freguesia: Overpass com `area(3600000000+id)` e 15 s entre pedidos (o 429 é real); CML (toponímia com geometria, património, casas religiosas); Wikidata (QIDs do OSM e da etimologia, pessoas com `P570`); extractos e geosearch da Wikipédia; Wikisource; Commons só metadados (nada para o ecrã, §0.1); INE. Tudo gravado em `base/bruto`.

**C1 — fusão determinística:** por QID, depois TOP_ID, depois nome normalizado e menos de 150 m entre a geometria CML e a OSM. Os ambíguos vão para `conflitos`, que o Sonnet resolve num lote. Freguesia pelo polígono.

**C2 — LLM editor:** recebe só os textos de C0, com frases numeradas, e devolve facetas em JSON; cada frase de saída cita as frases de origem ("não acrescentes nada").

**C2b — LLM proponente** (só zonas pobres): o Haiku propõe até 3 consultas por entidade fraca; um script corre-as por `r.jina.ai/https://html.duckduckgo.com/html/?q=` (≤1 pedido a cada 5 s, ≤200 por construção). Só contam páginas da lista branca (`*.gov.pt`, `cm-lisboa.pt`, juntas de freguesia, `arquivo.pt`, Wikipédia, jornais nacionais), cada domínio verificado ao vivo antes de entrar (§0.3). O texto volta a C0 e só depois passa por C2.

**C3 — verificação** (§5).

**Que modelo faz o quê** (marco 1, cerca de 600 entidades):

- **C2 editor:** Haiku 5.5, esforço alto, cerca de 5K de entrada e 1K de saída por entidade, lotes de 10 (menos de 60K por pedido). Custo ≈ **0,60 $**; Lisboa ≈ 6–8 $.
- **Conflitos de C1 e entidades ambíguas:** Sonnet 5.5, menos de 2 $.
- **Auditoria e verificação final:** Opus 5.5 (cerca de 30K), uma vez por marco.
- **Alternativa local ao C2:** qwen3:30b-a3b com `num_ctx` 16384 explícito; gemma4:31b-it-qat como segunda opinião. Custo 0 $.

**Modelos locais sem prejudicar o PC:** só com OK do João; antes de cada lote, o script mede a VRAM livre (`nvidia-smi`) e espera se for menor que o modelo + 2 GB; `OLLAMA_KEEP_ALIVE` curto, nunca `wsl --shutdown`; aborta se a VRAM livre cair (chamada). Um modelo local só substitui o Haiku se empatar na fidelidade, nas mesmas 30 entidades.

**C2c — entrevista entre modelos** (§4.1).

### 4.1 Entrevista entre modelos e piloto medível

**Mecânica.**

1. O entrevistador (Haiku) pergunta por entidade, com campos fechados (homenageado, profissão, nascimento e morte, nome anterior, ano de atribuição, facto marcante) e "não sei" explícito e valorizado.
2. Respondem, às cegas (sem as outras respostas nem os textos de C0), Haiku, Sonnet, Opus, gemma4:31b, qwen3.6:35b e gpt-oss:20b.
3. As respostas decompõem-se em **afirmações candidatas atómicas**; só passam as que têm consenso.
4. Cada candidata procura-se na Wikipédia/Wikidata, depois no Arquivo.pt, depois no DuckDuckGo via `r.jina.ai` (lista branca).
5. Só vira facto com âncora literal numa fonte (C3). Sem fonte fica `nao_verificada`, só em `base/candidatas.jsonl`, e **nunca é narrada**.

**Limites:**

- **Erros correlacionados:** os modelos aprenderam com os mesmos textos e herdam os mesmos erros; concordância não é prova.
- **Consenso por família, não por modelo:** Anthropic (Haiku, Sonnet e Opus = 1 voto), Google, Qwen (os dois = 1 voto), OpenAI. Passa com ≥ 3 de 4.
- **Hiperlocal:** a fiabilidade é mais baixa justamente nas ruas secundárias de Lumiar e Benfica; é lá que se mede.
- **Pesquisa enviesada:** não se pesquisa a frase da candidata (traria páginas que a repetem), mas o nome da entidade e o campo. A comparação faz-se depois.

**Piloto (primeira tarefa da construção, antes de C2 em escala).**

- **20 entidades em dois estratos de 10:** famosas (etimologia OSM/Wikidata e artigo na Wikipédia) e hiperlocais (só historial CML).
- **Verdade, escondida dos modelos:** `LEGENDA`, `HISTORIAL`, `DENOMINACOES_ANTERIORES` e `DATA_EDITAL` da CML, e `name:etymology:wikidata`.
- **Mede-se por modelo, por família e para o consenso, em cada estrato:** precisão (certas / afirmadas), cobertura (afirmadas / perguntadas) e erro confiante.
- **Correcção:** os campos fechados por script; o texto livre pelo Opus.
- **Esforço:** 20 × 6 perguntas × 7 modelos, cerca de 0,5 $ nos pagos; os locais com OK e portão de VRAM.

**Critério de decisão** (aplicado ao estrato hiperlocal, que é o que interessa):

- **"Fonte de candidatas"** (o consenso vai para verificação automática): precisão do consenso ≥ 90 %, erro confiante ≤ 5 % e cobertura ≥ 30 %.
- **"Descobrir lacunas"** abaixo disso: só se aproveitam perguntas e termos de pesquisa para C2b.
- Com cerca de 60 afirmações hiperlocais, 90 % observados têm limite inferior de cerca de 80 % (Wilson): entre 85 e 90 %, repete-se com mais 20 entidades.
- Em nenhum dos modos a entrevista cria factos; só a fonte os cria.

## 5. Protocolo de verificação

**Checks automáticos.** Todos bloqueiam a publicação.

1. A coordenada está dentro do polígono da freguesia (buffer de 50 m) e do concelho.
2. Cada frase de `texto` e `gancho` tem ≥1 âncora, e cada âncora existe literalmente no snapshot de `base/bruto`, depois de normalizar espaços e acentos.
3. Cada número, ano e nome próprio do facto aparece numa das âncoras. O teste faz-se por tokens, e é o que apanha as alucinações do editor.
4. As URLs respondem 200 (amostra de 20 %), os títulos da Wikipédia existem na API e o QID tem um rótulo coerente com o nome.
5. Datas plausíveis: ano ≤ 2026; nascimento < morte; idade < 110; edital posterior ao nascimento do homenageado.
6. Pessoas: `P570` presente; as vivas ficam reduzidas à legenda do topónimo.
7. As variantes têm os mesmos nomes e números que o original.
8. Na mesma entidade, factos com similaridade > 0,8 fundem-se.

**Auditoria por marco:** amostra estratificada de **100 factos** (por faceta, fonte e método), comparada com a fonte pelo Opus. **Aceitação:** 0 inventados, ≤ 3 distorções menores, 100 % nos checks automáticos (0 em 100 dá um limite superior de cerca de 3 % a 95 %). Uma invenção rejeita o lote desse método: corrige-se a causa e repete-se.

## 6. Runtime

**Ordem de consulta:** base (IndexedDB), depois `cv-cache` (localStorage), depois as fontes vivas.

**Novo `baseAqui(lat,lon,raio)`:** lê os tiles do ponto e vizinhos (< 50 ms); um tile do índice em falta busca-se à própria origem com `comPrazo(…,1500)` e grava-se. É a primeira fonte de `canalHistoria(f)` e `detalheRua()`; o resto fica como fallback (§0.5).

**Quando a base manda:** com `completo.via` no tile, `detalheRua` não chama a CML; com `completo.poi`, `canalHistoria` só faz geosearch quando a base em volta já está toda em `M.ditos`. Se a base e a fonte viva divergirem, fala-se a base e a divergência vai para `novos`. Dados vivos nunca vêm da base.

**Escrita de volta:** o permanente vindo de fontes vivas vai para `novos`, com proveniência e estado `quarentena`. Pode ser falado como hoje (já tem URL) e só entra no mestre por exportação e C3. Deduplicação por `id`; `chave_dito` mantém o formato de `marcaDito`, para `M.ditos` continuar válido.

**Falhas:** sem IndexedDB ou com esquema desconhecido, comportamento actual.

## 7. Pré-viagem

Em `iniciaPreViagem`:

1. Densificar a rota: um ponto a cada 300 m a pé, ou a cada 2 km de carro.
2. Calcular os geohash-6 num buffer de 200 m a pé, ou de 1 km de carro.
3. Descarregar os tiles do índice que faltam.
4. Fora da cobertura, aquecer o `cv-cache` com os buscadores actuais.
5. Zonas pobres (menos de 5 factos no tile) vão para `novos`, para C2b na construção seguinte. **Nada de DuckDuckGo em lote no runtime.**
6. No ecrã: "N de M zonas prontas para ouvir sem rede".

**Não poluir `M`:** o pré-carregamento escreve só em `cv-base` e `cv-cache`; os itens de `novos` levam `origem:"pre-viagem"`. Teste fixo: hash de `JSON.stringify(M)` igual antes e depois da pré-viagem, e depois o modo avião, para provar que se ouve sem rede.

## 8. Anti-repetição e variedade

- Até 8 facetas por entidade. Escolhe-se a faceta ainda não dita (`M.ditos`), pesada por `M.pesos` e pelos interesses: "nome" na primeira passagem, "gente", "antes", "arquitectura" e "curiosidade" nas seguintes.
- Com tudo dito, a entidade fica "esgotada" 90 dias e a voz passa à vizinha. Ao fim de 180 dias pode voltar, só com uma `variante` ("Lembras-te de…?").
- As `variantes` mudam a abordagem, nunca os factos.
- **Sinal de procura:** `M.procura[entidade]++` em cada «conta mais». Vai na exportação (sem localização nem horas) e dá prioridade a C2b nessas entidades.
- **Capacidade:** `M.ditos` corta para 2 000 chaves acima de 3 000 (≈150 h a pé). Chega por agora; migrar para IndexedDB na F5.

## 9. Backup, versões, fusão, migração

- **Mestre:** os `.jsonl` e `base/bruto` em git, que é o histórico. Os tiles reconstroem-se sempre.
- **Telemóvel:** "Exportar" em ⚙ gera `cv-novos-AAAAMMDD.json` (quarentena e `M.procura`) e `cv-memoria-AAAAMMDD.json` (o `M` completo); "Importar" restaura. Resolve também a perda de `M` se o browser limpar dados. **`M` nunca vai para o git** (dados pessoais).
- **Fusão (`base/funde.py`):** o ficheiro exportado entra em quarentena e passa por C3 antes de chegar aos `.jsonl`. Com ids iguais, ganha o de maior confiança; com textos diferentes da mesma fonte, o mais recente.
- **Migração:** campo `esquema` no índice e em cada linha; `base/migra_vN.py`; no cliente, `onupgradeneeded` redescarrega os tiles e migra só `novos`.

## 10. Fases e aceitação

**F1.0 — Piloto da entrevista (§4.1):** relatório de precisão, cobertura e erro confiante por modelo, por família e para o consenso, com o modo decidido pelo critério numérico.

**F1 — Marco 1: Lumiar + Benfica.**

- C0–C3 completos; ≥ 90 % dos topónimos CML com historial casados com a geometria OSM (≥ 374 de 415); todos os POIs `historic`, museu e memorial com entidade.
- Auditoria de 100 factos: 0 invenções, ≤ 3 distorções.
- Tiles publicados e `baseAqui` integrado.
- Simulação a pé, 2 percursos reais por freguesia: ≥ 90 % dos anúncios vindos da base; 0 chamadas à CML nos tiles `completo`; mediana até à fala < 300 ms; funciona em modo avião depois da pré-viagem; hash de `M` inalterado.
- Regressão R completa (`PLANO-TESTES.md`).

**F2 — Escrita de volta:** um facto de fonte viva chega ao mestre por exportar → fundir → C3; importar restaura `M` byte a byte.

**F3 — Variedade:** o mesmo percurso 3 vezes, como visita real: 0 factos repetidos e ≥ 70 % das entidades com faceta diferente em cada passagem.

**F4 — Santa Maria Maior** (reaproveita Alfama), com os critérios de F1. **F5 — Lisboa** em lotes de 4 freguesias, cada um com auditoria de 100 factos. **F6 — Pré-viagem fora de Lisboa:** cache e quarentena.

## 11. Riscos e o que NÃO fazer

- LLM como fonte (nem por consenso); factos sem âncora literal; páginas fora da lista branca.
- Dados vivos na base; base em localStorage; martelar Overpass, Nominatim ou DuckDuckGo.
- Comércio actual ou dados de pessoas vivas. "Lojas com História" (CML) é candidata **não verificada ao vivo**.
- Licenças: OSM → ODbL, Wikipédia → CC BY-SA; obrigam a atribuição (ecrã "Fontes" e `indice.json`) e partilha nos mesmos termos. A licença CML confirma-se antes de publicar.
- Pré-viagem a tocar em `M`; facetas publicadas sem auditoria; modelos locais sem OK e sem VRAM medida.

## Decisões que só o João pode tomar

1. **Base pública (GitHub Pages, ODbL + CC BY-SA, com atribuição) ou privada?** Privada exige um backend. **Recomendo pública**: só dados públicos.
2. **GPU para o piloto e para o editor local:** autorizas as 3 corridas locais do piloto (gemma4, qwen3.6, gpt-oss), com o portão de VRAM? **Recomendo sim**: sem os locais, o consenso fica com 1 família só. E o Haiku como editor do marco 1 (≈ 0,60 $).
3. **Texto da pesquisa web (lista branca): falar logo, citando o site, ou só depois de verificado na construção?** **Recomendo só depois**: algum silêncio em zonas pobres, sem risco ao §0.4.
4. **Backup de `M`: exportação manual com lembrete falado mensal?** **Recomendo que sim**: uma app estática não escreve no OneDrive sem autenticação.
