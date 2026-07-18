from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import requests
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


class Tarefa(BaseModel):
    titulo: str
    descricao: str
    concluido: bool = False

class Metricas(BaseModel):
    qtd_tarefas: int
    qtd_tarefas_pendentes: int
    qtd_tarefas_concluida: int
    qtd_tarefas_atualizadas: int
    qtd_tarefas_removidas: int
    tempo_medio: float

LISTA_TAREFAS = []
qtd_tarefas: int = 0
qtd_tarefas_pendentes: int = 0
qtd_tarefas_concluida: int = 0
qtd_tarefas_atualizadas: int = 0
qtd_tarefas_removidas: int = 0
tempo_medio: int = 0

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
    LOGGER.info("Acesso a HomePage")
    return "Olá, DevOps!"

@APP.get("/health", summary="Health", description="Retorna Health da API", tags=["Health"])
def health():
    LOGGER.info("Health - OK")
    return {"status": "OK"}

@APP.get("/tarefas", summary="Listar tarefas", description="Lista todas as tarefas cadastradas (somente id e titulo)", tags=["Tarefas"])
def listar_tarefas():
    if len(LISTA_TAREFAS) == 0:
        LOGGER.info("Lista de tarefas vazia")
        return LISTA_TAREFAS

    tarefas = [{"id": tarefa['id'], "titulo": tarefa['titulo']} for tarefa in LISTA_TAREFAS]
    LOGGER.info("Retornando a lista de tarefas")
    return tarefas

@APP.get("/tarefas/{id}", summary="Listar tarefa específica", description="Lista uma tarefa específica pelo ID", tags=["Tarefas"])
def listar_tarefa_especifica(id: int):
    mensagem_padrao = {"mensagem": "Não existe nenhuma tarefa"}
    if len(LISTA_TAREFAS) == 0 or id < 0 or id >= len(LISTA_TAREFAS):
        LOGGER.error("Não existe nenhuma tarefa, retornando mensagem padrão")
        return mensagem_padrao
    
    LOGGER.info("Retornando tarefa encontrada")
    return LISTA_TAREFAS[id]

@APP.post("/tarefas", summary="Inserir tarefa", description="Insere uma nova tarefa", tags=["Tarefas"], status_code=201)
def inserir_tarefa(tarefa: Tarefa):
    global qtd_tarefas, qtd_tarefas_pendentes
    mensagem_padrao = {"mensagem": "OK"}
    novo_id = len(LISTA_TAREFAS)
    nova = nova_tarefa(novo_id, tarefa.titulo, tarefa.descricao)
    LISTA_TAREFAS.append(nova)
    qtd_tarefas += 1
    qtd_tarefas_pendentes += 1
    LOGGER.info("Nova tarefa inserida com sucesso")
    return mensagem_padrao

@APP.put("/tarefas/{id}", summary="Atualizar tarefa", description="Atualiza uma tarefa específica pelo ID", tags=["Tarefas"])
def atualizar_tarefa(id: int, tarefa: Tarefa):
    global qtd_tarefas_concluida, qtd_tarefas_pendentes, qtd_tarefas_atualizadas
    mensagem_padrao = {"mensagem": "OK"}
    if id < 0 or id >= len(LISTA_TAREFAS):
        raise HTTPException(status_code=404, detail="TAREFA NÃO EXISTE")
    
    LISTA_TAREFAS[id]["titulo"] = tarefa.titulo
    LISTA_TAREFAS[id]["descricao"] = tarefa.descricao
    LISTA_TAREFAS[id]["concluido"] = tarefa.concluido
    qtd_tarefas_atualizadas += 1

    if tarefa.concluido:
        qtd_tarefas_concluida += 1
        qtd_tarefas_pendentes -= 1
        requests.post(f"http://notificacoes:8000/notificar?titulo={tarefa.titulo}&data_finalizacao={datetime.now()}", timeout=100)
    
    return mensagem_padrao

@APP.delete("/tarefas/{id}", summary="Deletar tarefa", description="Deleta uma tarefa específica pelo ID", tags=["Tarefas"])
def deletar_tarefa(id: int):
    global qtd_tarefas_removidas, qtd_tarefas_pendentes
    mensagem_padrao = {"mensagem": "OK"}
    if id < 0 or id >= len(LISTA_TAREFAS):
        raise HTTPException(status_code=404, detail="TAREFA NÃO EXISTE")
    
    tarefa_removida = LISTA_TAREFAS.pop(id)
    qtd_tarefas_removidas += 1
    if not tarefa_removida["concluido"]:
        qtd_tarefas_pendentes -= 1
    return mensagem_padrao

@APP.get('/metricas', summary="Metricas", description="Retona metricas de tarefas", tags=["Tarefas"], response_model=Metricas)
def metricas():
    tempo_medio_total = 0
    metricas = Metricas(
        qtd_tarefas=len(LISTA_TAREFAS),
        qtd_tarefas_pendentes=qtd_tarefas_pendentes,
        qtd_tarefas_concluida=qtd_tarefas_concluida,
        qtd_tarefas_atualizadas=qtd_tarefas_atualizadas,
        qtd_tarefas_removidas=qtd_tarefas_removidas,
        tempo_medio=0 if tempo_medio == 0 else tempo_medio_total / len(LISTA_TAREFAS)
    )
    return metricas
