from fastapi import FastAPI
from datetime import datetime
import logging

APP_NOTIFICACAO = FastAPI()

# Criar uma rota para receber tarefa finalizada
# APP_NOTIFICACAO.post("/notificar")
# Entrada:
#   - Recebe título da tarefa e data de finalização da tarefa
# Saída:
#   - print no terminal
@APP_NOTIFICACAO.post("/notificar")
def inserir_notificacao(titulo: str, data: datetime):
    mensagem_padrao = {"mensagem": f"A tarefa {titulo} foi concluida em: {data}"}
    LOGGER.info(str(mensagem_padrao))
    return mensagem_padrao
