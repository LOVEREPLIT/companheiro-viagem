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

## Como começar a próxima janela
Ler este ficheiro e `DESENHO-BASE-CONHECIMENTO.md`; não ler `projecto/` salvo necessidade. Decidir com o João as "Decisões que só ele pode tomar" do desenho antes de construir.
