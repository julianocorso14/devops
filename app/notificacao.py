from fastapi import FastAPI
from datetime import datetime

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
    print(mensagem_padrao)
    return mensagem_padrao
