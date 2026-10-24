# Piloto F1.0 — relatório (24/10/2026)

Conjunto: 20 ruas (10 famosas, 10 hiperlocais) de Lumiar e Benfica; verdade = campos CML (`LEGENDA`, `DATA_EDITAL`).
Scripts: `p0_conjunto.py`, `p2_local.py`, `p3_pontuar.py`, `p4_checks.py`. Respostas em `respostas/`.

## A. Entrevista de memória (campos fechados: profissão, nascimento, morte, ano de atribuição)
| Modelo | Estrato | Perguntadas | Afirmadas | Certas | Precisão | Cobertura | Erro confiante |
|---|---|---|---|---|---|---|---|
| Haiku | famosa | 40 | 30 | 28 | 93 % | 75 % | 5 % |
| Sonnet | famosa | 40 | 30 | 27 | 90 % | 75 % | 8 % |
| Opus | famosa | 40 | 30 | 28 | 93 % | 75 % | 5 % |
| qwen3:30b-a3b | famosa | 40 | 40 | 17 | 42 % | 100 % | 57 % |
| Haiku | hiperlocal | 40 | 0 | 0 | — | 0 % | 0 % |
| Sonnet | hiperlocal | 40 | 0 | 0 | — | 0 % | 0 % |
| Opus | hiperlocal | 40 | 4 | 3 | 75 % | 10 % | 2 % |
| qwen3:30b-a3b | hiperlocal | 40 | 36 | 1 | 3 % | 90 % | 88 % |

Decisão (critério do desenho: precisão ≥ 90 %, erro confiante ≤ 5 %, cobertura ≥ 30 % no estrato hiperlocal):
a cobertura do consenso é limitada pelo modelo que menos afirma (0–10 %), logo **não cumpre**. Modo = **«descobrir lacunas»**:
a entrevista não gera candidatas; só serve para perguntas/termos de pesquisa de C2b. Os modelos Anthropic dizem «não sei» (comportamento correcto);
o qwen3 inventa quase tudo no hiperlocal (88 % de erro confiante) — **proibido como fonte ou voto**.
Não corridos: gemma4:31b e gpt-oss:20b (portão de VRAM: 3,5 GB livres de 24, outro processo tem qwen3:30b carregado). Não alteram a decisão (o limite superior da cobertura já falha).
Nota: pontuação de profissão por radical de palavra; facto livre não pontuado (irrelevante dado o resultado).

## B. Editor Haiku sobre texto CML (60 factos, 20 ruas, âncoras = números de frases)
| Camada | Resultado |
|---|---|
| Haiku sozinho (auditoria Opus como referência) | 58 ok, 2 distorcidos (3,3 %), 0 inventados |
| + checks automáticos (números/nomes nas âncoras) | 1 reprovação, falso positivo; **apanhou 0 das 2 distorções** |
| + Sonnet validador contra fonte | 60 «ok»; **apanhou 0 das 2 distorções** |
| Opus auditor | apanhou as 2 (afirmação perdeu a ressalva «pode ser considerado»; livro vs filme adaptado) |

Decisão: Haiku como editor é aceitável (0 invenções), mas as **distorções subtis só o Opus apanha**; o Sonnet validador não acrescenta nada mensurável
(n pequeno: 2 erros). Mantém-se: Haiku editor + checks automáticos (apanham invenções de números/nomes) + **auditoria Opus** por amostra (100 factos),
sem validador Sonnet em todos os factos. Regra de edição acrescentada: preservar ressalvas («pode ser considerado», «segundo») e não converter obra adaptada em obra original.
Limite: 1 amostra, 2 erros; o Opus também é um modelo (referência, não verdade absoluta).
