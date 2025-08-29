import os, requests, json, logging, re
from prompts.commit_eval import COMMIT_PROMPT
from prompts.system import SYSTEM_PROMPT

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def call_llm(repo, commit_sha, author, language, files, diff):
    """
    Envia o diff e metadados do commit para a LLM
    e retorna a avaliação em JSON.
    """

    # Calcula métricas auxiliares
    changed_files = ", ".join([f["filename"] for f in files])
    loc_add = sum(f.get("additions", 0) for f in files)
    loc_del = sum(f.get("deletions", 0) for f in files)

    # Preenche o template do prompt
    prompt = COMMIT_PROMPT.format(
        repo=repo,
        commit_sha=commit_sha,
        author=author,
        language=language,
        changed_files=changed_files,
        loc_add=loc_add,
        loc_del=loc_del,
        unified_diff=diff
    )

    #logging.info(f"SYSTEM_PROMPT: {SYSTEM_PROMPT}")
    #logging.info(f"User prompt: {prompt}")
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        }
    )
    data = resp.json()
    #logging.info(f"Resposta OpenAI: {json.dumps(data)[:1000]}")
    try:
        content = data["choices"][0]["message"]["content"]
        # Remove blocos markdown tipo ```json ... ```

        content = re.sub(r"^```(?:json)?\s*", "", content.strip())
        content = re.sub(r"```\s*$", "", content.strip())
        #logging.info(f"Conteudo a ser parseado: [{content[:400]}]")
        if not content.strip():
            raise ValueError("Resposta da LLM vazia após limpeza de markdown!")
        return json.loads(content)

    except Exception as e:
        logging.error(f"Erro parsing LLM: {e}")
        logging.error(f"Resposta OpenAI bruta: {json.dumps(data)[:2000]}")
        return {
            "scores": {},
            "rationale": f"Erro parsing LLM: {e}",
            "sqc_final": 0
        }