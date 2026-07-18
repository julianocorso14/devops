from datetime import datetime
from fastapi import FastAPI

APP_NOTIFICACAO = FastAPI()


@APP_NOTIFICACAO.post("/notificar")
def inserir_notificacao(titulo: str, data: datetime):
    """Endpoint para registrar notificação de conclusão de tarefa."""
    return {"mensagem": f"A tarefa {titulo} foi concluída em: {data}"}
