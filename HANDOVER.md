# HANDOVER — Companheiro de Viagem

Actualizado: 24/10/2026. Último commit de código: `30ad811`.

## Estado
- Plano das 6 fases **concluído**, testado e publicado (interesses, passaporte, colecções, estatísticas, rádio/podcast, pré-viagem, Wikisource, Porto/Cascais/Sesimbra).
- Ronda de desempenho feita: cache persistente (`cv-cache`, localStorage, TTL por host), coordenadas arredondadas (`q3`/`q4`), fontes opcionais em paralelo com prazo (`comPrazo`). Execução fria medida ~6 s (**uma só medição**; antes 18–45 s).
- Corrigido Cascais (agora via r.jina.ai). **SIPA partido** (precisa de POST; corsproxy.io exige chave) — sem substituto gratuito.

## Pendente / por verificar
1. Teste em telemóvel real (GPS, voz, ecrã bloqueado) — nunca feito.
2. Repetir a bateria R1–R14 após as alterações de desempenho — não repetida.
3. Documentar no `projecto/historico-fases.md` a ronda de desempenho e a retirada dos proxies mortos.
4. Fontes novas verificadas a 08/10/2026 mas **não integradas**: etimologia de ruas (Overpass `name:etymology:wikidata` + Wikidata), placas/inscrições (Overpass `historic~memorial|plaque`, `inscription`), Commons geosearch, AgendaLX (`/wp-json/agendalx/v1/events`), alertas Carris (`api.carrismetropolitana.pt/v1/alerts`), Open-Meteo (ar/mar), IPMA (UV/sismos), Arquivo.pt (`siteSearch`), Europeana (chave demo), pesquisa web `r.jina.ai/https://html.duckduckgo.com/html/?q=`. Overpass dá 504 com frequência.

## Próximo grande passo: Base de Conhecimento Geo
Ideia do João: base que cresce com o uso, consultada antes da Internet, com backup, pesquisa geo, pré-carregamento antes da viagem, facetas para não repetir. **Primeiro caso: freguesias Lumiar e Benfica (Lisboa)**; Alfama/Baixa só depois e se não forem grandes demais.
Decisões já tomadas:
- Modelos como **editores** de texto recolhido (com fonte citada), nunca como fonte de factos (H2). Ingestão determinística primeiro (OSM, Wikidata, Wikipédia, CML, Commons).
- Empresas: só comércio histórico/marcos. Pessoas: só falecidas/públicas via Wikidata. Guardar fonte e licença por facto.
- Um só utilizador por agora; sem servidor.
- Desenvolvimento numa **janela nova**, depois da avaliação do Opus (arquitectura) e do Haiku (contagens).
Em curso a 24/10: Opus escreve `DESENHO-BASE-CONHECIMENTO.md`; Haiku escreve `saida/contagens_lisboa.md` (pasta `saida/` não vai para o git — copiar para `projecto/dados/` quando pronto).

## Decisões acrescentadas a 24/10 (pipeline de conhecimento)
- Desenho do Opus em `DESENHO-BASE-CONHECIMENTO.md` (lido e aceite; relações OSM Lumiar 6384124 / Benfica 6385130 confirmadas; toponímia CML = dataset aberto **CC0** em dados.gov.pt). Esqueleto do marco 1 = toponímia CML (Lumiar 253, Benfica 182 topónimos), não a Wikipédia (pobre nestas freguesias). A etapa de entrevista (§4.1) e o piloto medível (F1.0) já estão no desenho.
- Entrevista entre modelos: Haiku-entrevista-Haiku só vale como auto-consistência (5 tentativas, ficam as estáveis); concordância entre o mesmo modelo NÃO prova nada. Sonnet valida **contra texto de fonte** (a frase sustenta a afirmação? cita-a), nunca de memória. Opus audita 100 factos por marco. Locais (Ollama) = segunda voz independente, só com OK do João e VRAM livre medida.
- **Primeira tarefa da construção = piloto medível**: ~20 entidades de Lumiar/Benfica com verdade conhecida; comparar Haiku sozinho vs Haiku+Sonnet validador vs consenso entre modelos diferentes; decidir por taxa de acerto.
- Decisões do João ainda abertas (recomendações no desenho): base pública sob ODbL+CC BY-SA; editor do marco 1 = Haiku (~0,60 $); texto web só depois de verificado; exportação manual de `M` com lembrete mensal.
- Contagens do Haiku entregues e guardadas em `projecto/dados/contagens_lisboa.md`: batem com as do Opus (Wikidata Lisboa 2 167 entidades, 899 com artigo PT; OSM wikidata 2 028; Lumiar 46 e Benfica 28 entidades no Wikidata). Diferença só de unidade (5 213 segmentos de via com etimologia vs 911 nomes únicos). Novo facto: **"Lojas com História" NÃO existe como dataset aberto** em dados.gov.pt (0 resultados) — riscar do desenho como candidata. Overpass de Lumiar/Benfica medido depois (admin_level 8): historic 48/46, museus 2/0, culto 10/10, wikidata 49/63 — igual ao desenho.

## Decisões do João (24/10, respondidas)
1. Base **pública** (ODbL + CC BY-SA, ecrã «Fontes»). 2. Locais Ollama **autorizados** com portão de VRAM; Haiku editor do marco 1. 3. Texto web da lista branca **só depois de verificado**. 4. **Backup de M automático**, com pop-up de autorização que diz o que vai ser guardado, e o João dá OK (não exportação manual). Nota técnica: app estática não escreve no OneDrive sozinha; desenho proposto = agendar sozinho (semanal/mensal), mostrar o pop-up «Guardar cópia de segurança? (N ditos, sem localização)» e, no OK, `showSaveFilePicker`/Web Share/download para uma pasta do OneDrive; confirmar com o João o mecanismo exacto antes de implementar (F2).

## Piloto F1.0 FEITO (24/10) — ver `base/piloto/RELATORIO.md`
- Entrevista de memória: hiperlocais → Haiku/Sonnet 0 % de cobertura, Opus 10 %, qwen3:30b inventa (88 % erro confiante). Critério não cumprido → modo «descobrir lacunas»; entrevista nunca cria factos. gemma4/gpt-oss não corridos (VRAM 3,5 GB livres; não alteram a decisão).
- Editor Haiku sobre texto CML: 58/60 ok, 2 distorções, 0 invenções; checks automáticos e Sonnet validador apanharam 0 das 2 distorções; só o Opus as apanhou. Decisão: Haiku editor + checks automáticos + auditoria Opus; sem validador Sonnet. Regra para o brief do editor: preservar ressalvas («pode ser considerado») e não trocar obra adaptada por obra original.
- Feito também: `base/c0_cml_toponimia.py` e `base/bruto/cml/toponimia-{lumiar,benfica}-2026-10-24.json.gz` (253 + 182, bate com o desenho). Pasta `base/` ainda não commitada.

## C0 FEITO (24/10)
`base/bruto/`: cml (toponímia Lumiar 253 / Benfica 182, património 11+12, casas religiosas), osm (Lumiar+Benfica, polígono + elementos: ~1135 em Benfica), wikidata (157 QIDs), wikipedia-pt (133 extractos). Scripts `base/c0_*.py`. Cartão de sessão nova «Marco 1 geo» proposto (task_0e8f7418) para C1→publicar. Falta o geosearch Wikipédia (opcional) e o Commons (só metadados).

## Próximo passo (por ordem)
C0 restante (OSM por Overpass relações 6384124/6385130 a 15 s entre pedidos, património CML camadas 11+12, Wikidata, Wikipédia geosearch) → C1 fusão → C2 Haiku editor (lotes de 10, âncoras = números de frases, checks de `p4_checks.py`) → C3 auditoria Opus de 100 factos → tiles geohash-6 + `baseAqui` no `docs/index.html` → testes F1 em http://127.0.0.1:8124/ → publicar. Depois F2 (escrita de volta + backup com pop-up).

## Como começar a próxima janela
Ler este ficheiro e `DESENHO-BASE-CONHECIMENTO.md`; não ler `projecto/` salvo necessidade. Decidir com o João as "Decisões que só ele pode tomar" do desenho antes de construir.
