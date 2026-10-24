Tarefa de memória (sem ferramentas de pesquisa, sem ler outros ficheiros). Para cada rua da lista (ficheiro indicado), de Lisboa, diz o que SABES de memória sobre o homenageado do nome da rua. Responde em PT-PT.

Para cada rua devolve um objecto com:
- top_id (copiado)
- profissao: profissão/actividade principal do homenageado, em 1-4 palavras, ou null
- nascimento: ano (número) ou null
- morte: ano (número) ou null
- ano_atribuicao: ano em que a Câmara de Lisboa atribuiu o nome à rua (número) ou null
- facto: UM facto marcante sobre o homenageado, numa frase, ou null

Regras: "não sei" (null) é uma resposta valorizada; uma resposta errada e confiante é pior do que null. Só afirmes o que tens por certo. Não adivinhes anos. Não uses ferramentas de pesquisa nem leias ficheiros além do indicado.
Escreve o resultado como um array JSON válido no ficheiro de saída indicado (ferramenta Write) e responde apenas "feito".
