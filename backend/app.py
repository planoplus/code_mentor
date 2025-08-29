from fastapi import FastAPI, Request, Header, BackgroundTasks
import os, requests, json, logging
from llm_client import call_llm
from db import save_score

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

app = FastAPI()

@app.post("/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks, x_github_event: str = Header(None)):
    
    try:
        payload = await request.json()
        logging.info(f"Payload recebido: {json.dumps(payload)[:500]}")
    except Exception as e:
        logging.error(f"Erro ao ler payload JSON: {e}")
        raise
    logging.info(f"x_github_event: {x_github_event}")

    author = None
    diff_text = ""
    repo = None
    commit_sha = None
    sqc = 0
    subnotes = {}
    rationale = ""
    files = []  # <- inicializa aqui para evitar erro no fluxo PR

    # Fallback: tenta inferir o evento pelo payload
    if not x_github_event:
        if "pull_request" in payload:
            x_github_event = "pull_request"
        elif "pusher" in payload:
            x_github_event = "push"
        else:
            logging.warning("Evento GitHub não identificado no payload.")

    # PUSH
    if x_github_event == "push":
        if "pusher" in payload and "repository" in payload:
            commit_sha = payload.get("after")
            repo = payload["repository"].get("full_name", "unknown")
            author = payload["pusher"].get("name", "unknown")
            diff_url = f"https://api.github.com/repos/{repo}/commits/{commit_sha}"
            gh_resp = requests.get(diff_url, headers={"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"})
            files = gh_resp.json().get("files", [])
            diff_text = "\n".join([f["patch"] for f in files if "patch" in f])
        else:
            logging.warning("Payload push sem campos esperados.")
            return {"status": "ignored", "reason": "Payload push sem campos esperados"}

    # PULL REQUEST
    elif x_github_event == "pull_request":
        if "pull_request" in payload and "repository" in payload:
            repo = payload["repository"].get("full_name", "unknown")
            author = payload["pull_request"]["user"].get("login", "unknown")
            commit_sha = payload["pull_request"]["head"].get("sha", "unknown")
            
            # Pega arquivos modificados via API (mais rico que diff cru)
            pr_number = payload["pull_request"].get("number")
            files_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
            gh_resp = requests.get(files_url, headers={"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"})
            files = gh_resp.json()
            
            # Ainda pode capturar o diff cru para contexto adicional
            diff_url = payload["pull_request"].get("diff_url")
            diff_resp = requests.get(diff_url, headers={"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"})
            diff_text = diff_resp.text
        else:
            logging.warning("Payload pull_request sem campos esperados.")
            return {"status": "ignored", "reason": "Payload pull_request sem campos esperados"}

    else:
        logging.warning("Evento não suportado ou payload inesperado.")
        return {"status": "ignored", "reason": "Evento não suportado ou payload inesperado"}

    # Chamada da LLM e salvamento do score
    def process_llm_and_save():
        logging.info(f"Iniciando processamento LLM/background para commit {commit_sha}")
        
        try:
            result = call_llm(
                repo=repo,
                commit_sha=commit_sha,
                author=author,
                language="java",   # por enquanto fixo, depois pode detectar automaticamente
                files=files,
                diff=diff_text
            )
            logging.info(f"Result LLM: {json.dumps(result)[:1000]}")
    
            subnotes = result.get("scores", {})
            rationale = result.get("rationale", "")
            sqc = result.get("sqc_final", 0)

            # Salva o score no banco de dados
            save_score(commit_sha, repo, author, subnotes, rationale, sqc)
            logging.info(f"Score salvo com sucesso para commit {commit_sha}")

        except Exception as e:
            logging.error(f"Erro ao processar/salvar score do commit {commit_sha}: {e}")
            raise
        logging.info(f"Finalizado processamento background para commit {commit_sha}")

    # Dispara processamento em background
    background_tasks.add_task(process_llm_and_save)
    return {"status": "ok", "commit": commit_sha}
