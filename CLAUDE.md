# Companheiro de Viagem — regras do projecto

- Falar com o João por **tu**, em **PT-PT**. Ler `HANDOVER.md` primeiro; actualizá-lo no fim de cada tarefa.
- **Custo zero em funcionamento, sem chaves de API.** Modelos (Claude, Ollama) só ao construir dados, nunca em runtime.
- **Toda a fonte nova é verificada ao vivo** (`fetch` real) antes de integrar. Nunca inventar URLs ou dados; um LLM não é fonte de factos, só editor de texto recolhido (com fonte citada).
- Pré-viagem (`S.fonte==="sim"`) **nunca** escreve em `M` (memória real). Qualquer função nova que escreva em `M` tem de ter esse portão.
- Proxies CORS: só `r.jina.ai` funciona (corsproxy.io exige chave; allorigins em baixo; s.jina.ai pede chave).
- Testar no browser em http://127.0.0.1:8124/ (python http.server em `docs/`), com os testes mudos (`speechSynthesis.speak=()=>{}; window.diz=()=>{}`). Recarregar com `?v=N` para evitar cache.
- Antes de cada push correr a bateria R1–R14 (`projecto/PLANO-TESTES.md`, §R).
- Commits terminam com `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Backup = GitHub (`LOVEREPLIT/companheiro-viagem`) + OneDrive.
- Modelos: Opus só para arquitectura e verificação final; Haiku para trabalho bem definido e verificável; modelos locais (Ollama) só com a GPU livre e OK do João.
