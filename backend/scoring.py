WEIGHTS = {
    "estrutura_codigo": 0.10,
    "metricas_qualidade": 0.15,
    "detalhes_implementacao": 0.10,
    "elementos_arquiteturais": 0.15,
    "debito_tecnico": 0.10,
    "seguranca": 0.15,
    "performance": 0.15,
    "testes": 0.10
}

def calculate_sqc(subnotes: dict) -> float:
    score = 0
    for k, w in WEIGHTS.items():
        score += w * subnotes.get(k, {}).get("nota", 0)
    return round(score, 2)
