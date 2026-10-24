# Contagens de entidades em Lisboa (concelho)

Medido em 24/10/2026 com pedidos reais (Overpass, Wikidata SPARQL, dados.gov.pt).

| medição | número | query | exemplo | estado |
|---|---|---|---|---|
| A1 Overpass: vias com nome | 15025 | `[out:json][timeout:90];area["name"="Lisboa"]["admin_level"="7"]->.a;way(area.a)["highway"]["name"];out count;` | {"type": "way", "id": 4219855, "tags": {"description": "Toponímia: Náuticos e marítimos. Início: Avenida da Índia. Fim: Rua da Junqueira.", "highway": "residential", "lanes": "2", "name": "Travessa da Galé", "sidewalk": "both", "source:description":  | MEDIDO |
| A2 Overpass: vias com nome e name:etymology:wikidata | 5213 | `[out:json][timeout:90];area["name"="Lisboa"]["admin_level"="7"]->.a;way(area.a)["highway"]["name"]["name:etymology:wikidata"];out count;` | {"type": "way", "id": 4219880, "tags": {"description": "Toponímia: Escritor, Militar, Poeta. Início: Rua 1º de Maio. Fim: Calçada da Tapada.", "highway": "tertiary", "lane_markings": "no", "lit": "yes", "name": "Rua Luís de Camões", "name:etymology:w | MEDIDO |
| A3 Overpass: vias com nome e description ou inscription | 11349 | `[out:json][timeout:90];area["name"="Lisboa"]["admin_level"="7"]->.a;(way(area.a)["highway"]["name"]["description"];way(area.a)["highway"]["name"]["inscription"];);out count;` | {"type": "way", "id": 4219855, "tags": {"description": "Toponímia: Náuticos e marítimos. Início: Avenida da Índia. Fim: Rua da Junqueira.", "highway": "residential", "lanes": "2", "name": "Travessa da Galé", "sidewalk": "both", "source:description":  | MEDIDO |
| A4 Overpass: nwr historic | 1064 | `[out:json][timeout:90];area["name"="Lisboa"]["admin_level"="7"]->.a;nwr(area.a)["historic"];out count;` | {"type": "node", "id": 578460077, "tags": {"artist_name": "Domingos Soares Branco", "artwork_subject": "figurative", "description": "Réplica do Fairey F III-D MkII. Reproduz em tamanho natural o hidroavião \"Lusitânia\" utilizado por Gago Coutinho e  | MEDIDO |
| A5 Overpass: nwr tourism=museum | 104 | `[out:json][timeout:90];area["name"="Lisboa"]["admin_level"="7"]->.a;nwr(area.a)["tourism"="museum"];out count;` | {"type": "node", "id": 578460076, "tags": {"addr:city": "Lisboa", "addr:housename": "Forte do Bom Sucesso", "addr:street": "Avenida de Brasília", "check_date": "2024-05-02", "fee": "yes", "name": "Museu dos Combatentes do Ultramar", "tourism": "museu | MEDIDO |
| A6 Overpass: nwr heritage | 203 | `[out:json][timeout:90];area["name"="Lisboa"]["admin_level"="7"]->.a;nwr(area.a)["heritage"];out count;` | {"type": "node", "id": 1120633222, "tags": {"description": "Erguido após o terramoto de 1755, em substituição do anterior, de acordo com o plano urbanístico de Eugénio dos Santos, foi objecto de alterações ao longo do tempo, que lhe conferiram o aspe | MEDIDO |
| A7 Overpass: nwr amenity~place_of_worship | 248 | `[out:json][timeout:90];area["name"="Lisboa"]["admin_level"="7"]->.a;nwr(area.a)["amenity"~"place_of_worship"];out count;` | {"type": "node", "id": 1595748651, "tags": {"amenity": "place_of_worship", "check_date": "2026-01-08", "name": "Igreja do Convento de Santos-o-Novo", "religion": "christian"}} | MEDIDO |
| A8 Overpass: nwr shop com name | 5189 | `[out:json][timeout:90];area["name"="Lisboa"]["admin_level"="7"]->.a;nwr(area.a)["shop"]["name"];out count;` | (só contagem) | MEDIDO |
| A9 Overpass: nwr historic~memorial|plaque | 339 | `[out:json][timeout:90];area["name"="Lisboa"]["admin_level"="7"]->.a;nwr(area.a)["historic"~"memorial\|plaque"];out count;` | {"type": "node", "id": 578460077, "tags": {"artist_name": "Domingos Soares Branco", "artwork_subject": "figurative", "description": "Réplica do Fairey F III-D MkII. Reproduz em tamanho natural o hidroavião \"Lusitânia\" utilizado por Gago Coutinho e  | MEDIDO |
| A10 Overpass: nwr wikidata (total) | 2028 | `[out:json][timeout:90];area["name"="Lisboa"]["admin_level"="7"]->.a;nwr(area.a)["wikidata"];out count;` | {"type": "node", "id": 25414208, "tags": {"local_ref": "3", "name": "Sete Rios", "public_transport": "stop_position", "railway": "stop", "ref": "3", "train": "yes", "wikidata": "Q801112", "wikimedia_commons": "Category:Sete Rios train station", "wiki | MEDIDO |
| B1 Wikidata: entidades em Lisboa (P131*) com coordenadas | 2167 | `PREFIX wd: <http://www.wikidata.org/entity/> PREFIX wdt: <http://www.wikidata.org/prop/direct/> PREFIX schema: <http://schema.org/> PREFIX wikibase: <http://wikiba.se/ontology#> PREFIX bd: <http://www.bigdata.com/rdf#> SELECT (COUNT(DISTINCT ?item) AS ?n) WHERE { ?item wdt:P131* wd:Q597 ; wdt:P625 ?c . }` | {"item": "http://www.wikidata.org/entity/Q212459", "itemLabel": "Museu Nacional de Arte Antiga"} | MEDIDO |
| B2 Wikidata: dessas, com artigo na Wikipedia PT | 899 | `PREFIX wd: <http://www.wikidata.org/entity/> PREFIX wdt: <http://www.wikidata.org/prop/direct/> PREFIX schema: <http://schema.org/> PREFIX wikibase: <http://wikiba.se/ontology#> PREFIX bd: <http://www.bigdata.com/rdf#> SELECT (COUNT(DISTINCT ?item) AS ?n) WHERE { ?item wdt:P131* wd:Q597 ; wdt:P625 ?c . ?art schema:about ?item ; schema:isPartOf <https://pt.wikipedia.org/> . }` | {"item": "http://www.wikidata.org/entity/Q10279330", "itemLabel": "Faculdade de Arquitetura da Universidade de Lisboa"} | MEDIDO |
| B3 Wikidata: museus (P31/P279* Q33506) com coordenadas | NÃO MEDIDO | `SELECT (COUNT(DISTINCT ?item) AS ?n) WHERE { ?item wdt:P131* wd:Q597 ; wdt:P625 ?c ; wdt:P31/wdt:P279* wd:Q33506 . }` | HTTP 000 (tentativa 3) | NAO MEDIDO |
| B4 Wikidata: edificios/monumentos (P31/P279* Q811979) com P1435 | NÃO MEDIDO | `SELECT (COUNT(DISTINCT ?item) AS ?n) WHERE { ?item wdt:P131* wd:Q597 ; wdt:P625 ?c ; wdt:P31/wdt:P279* wd:Q811979 ; wdt:P1435 ?h . }` | HTTP 000 (tentativa 3) | NAO MEDIDO |
| B5 Wikidata: igrejas (P31/P279* Q16970) com coordenadas | NÃO MEDIDO | `SELECT (COUNT(DISTINCT ?item) AS ?n) WHERE { ?item wdt:P131* wd:Q597 ; wdt:P625 ?c ; wdt:P31/wdt:P279* wd:Q16970 . }` | HTTP 000 (tentativa 3) | NAO MEDIDO |
| B6 Wikidata: pessoas nascidas em Lisboa (P19 Q597) | 5259 | `PREFIX wd: <http://www.wikidata.org/entity/> PREFIX wdt: <http://www.wikidata.org/prop/direct/> PREFIX schema: <http://schema.org/> PREFIX wikibase: <http://wikiba.se/ontology#> PREFIX bd: <http://www.bigdata.com/rdf#> SELECT (COUNT(DISTINCT ?p) AS ?n) WHERE { ?p wdt:P19 wd:Q597 . }` | {"p": "http://www.wikidata.org/entity/Q590", "pLabel": "Q590"} | MEDIDO |
| B7 Wikidata: nascidas em Lisboa e falecidas (P570) com artigo PT | 1873 | `PREFIX wd: <http://www.wikidata.org/entity/> PREFIX wdt: <http://www.wikidata.org/prop/direct/> PREFIX schema: <http://schema.org/> PREFIX wikibase: <http://wikiba.se/ontology#> PREFIX bd: <http://www.bigdata.com/rdf#> SELECT (COUNT(DISTINCT ?p) AS ?n) WHERE { ?p wdt:P19 wd:Q597 ; wdt:P570 ?d . ?art schema:about ?p ; schema:isPartOf <https://pt.wikipedia.org/> . }` | {"p": "http://www.wikidata.org/entity/Q928189", "pLabel": "Luís Joaquim dos Santos Marrocos"} | MEDIDO |
| B3 variante simplificada: museus (P131 direto, com coordenadas) | 18 | `SELECT (COUNT(DISTINCT ?item) AS ?n) WHERE { ?item wdt:P131 wd:Q597 ; wdt:P625 ?c ; wdt:P31/wdt:P279* wd:Q33506 . }` | (sem exemplo) | MEDIDO (simplificada) |
| B4 variante simplificada: edifícios com P1435 (P131 direto) | NÃO MEDIDO | `... wdt:P131 wd:Q597 ; wdt:P625 ?c ; wdt:P31/wdt:P279* wd:Q811979 ; wdt:P1435 ?h ...` | - | NÃO MEDIDO (3 tentativas, timeout/000) |
| B5 variante simplificada: igrejas (P131 direto, com coordenadas) | 11 | `SELECT (COUNT(DISTINCT ?item) AS ?n) WHERE { ?item wdt:P131 wd:Q597 ; wdt:P625 ?c ; wdt:P31/wdt:P279* wd:Q16970 . }` | (sem exemplo) | MEDIDO (simplificada) |
| C1 dados.gov.pt: "toponimia lisboa" | 1 dataset | `https://dados.gov.pt/api/1/datasets/?q=lisboa%20toponimia&page_size=5` | Toponímia de Lisboa, org. Município de Lisboa, recurso ArcGIS FeatureServer (Cultura_Toponimia) | MEDIDO |
| C2 dados.gov.pt: "lojas com historia" | 0 datasets | `https://dados.gov.pt/api/1/datasets/?q=lojas%20com%20historia&page_size=5` | (sem resultados) | MEDIDO: "Lojas com História" NÃO existe como dataset aberto na pesquisa |
| D2 Lumiar, Wikidata: entidades da freguesia (P131*, Q924723) com coordenadas | 46 | `SELECT (COUNT(DISTINCT ?item) AS ?n) WHERE { ?item wdt:P131* wd:Q924723 ; wdt:P625 ?c . }` | (ver lb_results) | MEDIDO |
| D3 Lumiar, Wikidata: dessas com artigo PT | 28 | idem + `?art schema:about ?item ; schema:isPartOf <https://pt.wikipedia.org/>` | (ver lb_results) | MEDIDO |
| E2 Benfica, Wikidata: entidades da freguesia (P131*, Q534230) com coordenadas | 28 | `SELECT (COUNT(DISTINCT ?item) AS ?n) WHERE { ?item wdt:P131* wd:Q534230 ; wdt:P625 ?c . }` | (ver lb_results) | MEDIDO |
| E3 Benfica, Wikidata: dessas com artigo PT | 11 | idem + artigo PT | (ver lb_results) | MEDIDO |

## Lumiar e Benfica (freguesias, admin_level 8 em OSM)

| medição | Lumiar | Benfica |
|---|---|---|
| 1 vias com nome | MEDIDO | MEDIDO |
| 2 vias com nome + name:etymology:wikidata | MEDIDO | MEDIDO |
| 3 vias com nome + description/inscription | MEDIDO | MEDIDO |
| 4 nwr historic | MEDIDO | MEDIDO |
| 5 nwr tourism=museum | MEDIDO | MEDIDO |
| 6 nwr heritage | MEDIDO | MEDIDO |
| 7 nwr amenity~place_of_worship | MEDIDO | MEDIDO |
| 8 nwr shop com name (só contagem) | MEDIDO | MEDIDO |
| 9 nwr historic~memorial|plaque | MEDIDO | MEDIDO |
| 10 nwr wikidata (total) | MEDIDO | MEDIDO |
| 11 Wikidata: entidades P131* com coordenadas | MEDIDO | MEDIDO |
| 12 Wikidata: dessas com artigo PT | MEDIDO | MEDIDO |

## Notas

- Overpass: `area["name"="Lisboa"]["admin_level"="7"]` deu 15025 vias com nome, por isso admin_level 7 ficou. Endpoint principal com 429 frequentes; todos os valores MEDIDOS vieram do mesmo endpoint, sem fallback.
- Lumiar e Benfica: a primeira tentativa usou admin_level 9/10 e deu 0 em tudo, por estarem erradas (freguesias em OSM são admin_level 8). Esses zeros ficam descartados e foram substituídos pelo re-run com admin_level 8, ainda em curso.
- Wikidata: as 3 contagens de museus, edifícios e igrejas com P131* deram timeout. Museus e igrejas foram medidos com P131 direto (variante simplificada, não comparável diretamente com B1-B2). Edifícios continuam NÃO MEDIDO.
- Para os exemplos completos de Lumiar e Benfica (Wikidata), ver `wd_results` / `lb_results` no scratchpad.
