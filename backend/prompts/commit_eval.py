# prompts/commit_eval.py
COMMIT_PROMPT = """
Analise o seguinte commit.

Contexto:
- Repositório: {repo}
- Commit: {commit_sha}
- Autor: {author}
- Linguagem principal: {language}
- Arquivos modificados: {changed_files}
- Linhas adicionadas/removidas: {loc_add} / {loc_del}

Diff do commit:
{unified_diff}

Tarefa:
Avalie este commit em cada uma das dimensões de qualidade abaixo, atribuindo notas de 0 a 100 (quanto maior, melhor).
Justifique brevemente cada nota em até 2 frases.
Não utilize criatividade, apenas siga critérios objetivos.

Dimensões:
1. Estrutura do Código: clareza e organização de classes, interfaces e métodos.
2. Métricas de Qualidade: coesão, complexidade e acoplamento.
3. Detalhes de Implementação: uso de estruturas de dados, dependências e injeção de dependência.
4. Elementos Arquiteturais: aplicação de padrões, camadas de persistência e consumo de APIs.
5. Débito Técnico: se o commit introduz ou reduz dívida técnica.
6. Riscos de Segurança: possíveis vulnerabilidades ou más práticas de segurança.
7. Implicações de Performance: riscos ou melhorias de eficiência no runtime.
8. Qualidade dos Testes: presença, abrangência e relevância dos testes.

Responda exclusivamente no formato JSON, obedecendo aos seguintes critérios:
- Não altere a ordem dos campos no JSON
- Use sempre o mesmo padrão de texto para justificativas semelhantes
- Não use caracteres especiais ou emojis

{{
  "scores": {{
    "estrutura_codigo": {{"nota": <0-100>, "justificativa": "<texto>"}},
    "metricas_qualidade": {{"nota": <0-100>, "justificativa": "<texto>"}},
    "detalhes_implementacao": {{"nota": <0-100>, "justificativa": "<texto>"}},
    "elementos_arquiteturais": {{"nota": <0-100>, "justificativa": "<texto>"}},
    "debito_tecnico": {{"nota": <0-100>, "justificativa": "<texto>"}},
    "seguranca": {{"nota": <0-100>, "justificativa": "<texto>"}},
    "performance": {{"nota": <0-100>, "justificativa": "<texto>"}},
    "testes": {{"nota": <0-100>, "justificativa": "<texto>"}}
  }},
  "riscos_detectados": ["..."],
  "sugestoes": ["..."],
  "sqc_final": <0-100>  // média ponderada das notas acima
}}
"""
