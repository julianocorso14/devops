from fastapi import FastAPI
from datetime import datetime
import logging

LOGGER = logging.getLogger("devops")
LOGGER.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
file_handler   = logging.FileHandler(f"{LOGGER.name}.log", encoding='utf-8')
formatador     = logging.Formatter(fmt="%(name)s | %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(message)s")

stream_handler.setFormatter(formatador)
file_handler.setFormatter(formatador)

LOGGER.addHandler(stream_handler)
LOGGER.addHandler(file_handler)


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
