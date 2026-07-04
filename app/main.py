from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import requests


class Tarefa(BaseModel):
    titulo: str
    descricao: str
    concluido: bool = False

LISTA_TAREFAS = []
APP = FastAPI()

def nova_tarefa(id: int, titulo: str, descricao: str):
    """Função auxiliar para criar uma tarefa usando dicionário (`dict`)"""
    return {
        "id": id,
        "titulo": titulo,
        "descricao": descricao,
        "concluido": False,
        "criado_em": datetime.now()
    }

@APP.get("/", summary="Página inicial", description="Página inicial da API", tags=["Home"])
def index():
    return "Olá, DevOps!"

@APP.get("/tarefas", summary="Listar tarefas", description="Lista todas as tarefas cadastradas (somente id e titulo)", tags=["Tarefas"])
def listar_tarefas():
    # Lista tarefas (somente id e titulo)
    if len(LISTA_TAREFAS) == 0:
        return LISTA_TAREFAS

    tarefas = []
    
    for tarefa in LISTA_TAREFAS:
        info = {"id": tarefa['id'], "titulo": tarefa['titulo']}
        tarefas.append(info)

    return tarefas

@APP.get("/tarefas/{id}", summary="Listar tarefa específica", description="Lista uma tarefa específica pelo ID", tags=["Tarefas"])
def listar_tarefa_especifica(id: int):
    mensagem_padrao = {"mensagem": "Não existe nenhuma tarefa"}
    if len(LISTA_TAREFAS) == 0:
        return mensagem_padrao
    
    # ID da tarefa é o índice na lista
    if id >= 0 and id < len(LISTA_TAREFAS):
        return LISTA_TAREFAS[id]
    
    return mensagem_padrao

@APP.post("/tarefas", summary="Inserir tarefa", description="Insere uma nova tarefa", tags=["Tarefas"], status_code=201)
def inserir_tarefa(tarefa: Tarefa):
    mensagem_padrao = {"mensagem": "OK"}
    novo_id = len(LISTA_TAREFAS)
    nova = nova_tarefa(novo_id, tarefa.titulo, tarefa.descricao)
    LISTA_TAREFAS.append(nova)
    return mensagem_padrao

@APP.put("/tarefas/{id}", summary="Atualizar tarefa", description="Atualiza uma tarefa específica pelo ID", tags=["Tarefas"])
def atualizar_tarefa(id: int, tarefa: Tarefa):
    mensagem_padrao = {"mensagem": "OK"}
    if id < 0 or id >= len(LISTA_TAREFAS):
        raise HTTPException(status_code=404, detail="TAREFA NÃO EXISTE")
    
    LISTA_TAREFAS[id]["titulo"] = tarefa.titulo
    LISTA_TAREFAS[id]["descricao"] = tarefa.descricao
    LISTA_TAREFAS[id]["concluido"] = tarefa.concluido
    if tarefa.concluido == True:
        requests.post(f"http://localhost:8002/notificar?titulo{tarefa.titulo}&data{datetime.now()}")

    return mensagem_padrao


@APP.delete("/tarefas/{id}", summary="Deletar tarefa", description="Deleta uma tarefa específica pelo ID", tags=["Tarefas"])
def deletar_tarefa(id: int):
    mensagem_padrao = {"mensagem": "OK"}
    if id < 0 or id >= len(LISTA_TAREFAS):
        raise HTTPException(status_code=404, detail="TAREFA NÃO EXISTE")
    
    LISTA_TAREFAS.pop(id)
    return mensagem_padrao