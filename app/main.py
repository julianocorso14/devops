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
    # Lista tarefas (somente id e titulo)
    if len(LISTA_TAREFAS) == 0:
        LOGGER.info("Lista de tarefas vazia")
        return LISTA_TAREFAS

    tarefas = []
    LOGGER.info("Criando a lista de tarefas para ser retornada")
    for tarefa in LISTA_TAREFAS:
        info = {"id": tarefa['id'], "titulo": tarefa['titulo']}
        LOGGER.debug(str(info))
        tarefas.append(info)
        LOGGER.debug("Tarefa adicionada a lista")

    LOGGER.info("Retornando a lista de tarefas")
    LOGGER.debug(str(LISTA_TAREFAS))
    return tarefas

@APP.get("/tarefas/{id}", summary="Listar tarefa específica", description="Lista uma tarefa específica pelo ID", tags=["Tarefas"])
def listar_tarefa_especifica(id: int):
    mensagem_padrao = {"mensagem": "Não existe nenhuma tarefa"}
    if len(LISTA_TAREFAS) == 0:
        LOGGER.error("Não existe nenhuma tarefa, retornando mensagem padrão")
        return mensagem_padrao
    
    # ID da tarefa é o índice na lista
    if id >= 0 and id < len(LISTA_TAREFAS):
        LOGGER.debug(str(LISTA_TAREFAS[id]))
        LOGGER.info("Retornando tarefa encontrada")
        return LISTA_TAREFAS[id]

    LOGGER.error("Não existe nenhuma tarefa, retornando mensagem padrão")
    return mensagem_padrao

@APP.post("/tarefas", summary="Inserir tarefa", description="Insere uma nova tarefa", tags=["Tarefas"], status_code=201)
def inserir_tarefa(tarefa: Tarefa):
    mensagem_padrao = {"mensagem": "OK"}
    novo_id = len(LISTA_TAREFAS)
    LOGGER.debug(f"Verificando o tamanho da lista: {novo_id}")
    nova = nova_tarefa(novo_id, tarefa.titulo, tarefa.descricao)
    LOGGER.debug(str(nova))
    LISTA_TAREFAS.append(nova)
    LOGGER.info(f"Nova tarefa inserida com sucesso, {str(mensagem_padrao)}")
    qtd_tarefas += 1 
    return mensagem_padrao

@APP.put("/tarefas/{id}", summary="Atualizar tarefa", description="Atualiza uma tarefa específica pelo ID", tags=["Tarefas"])
def atualizar_tarefa(id: int, tarefa: Tarefa):
    mensagem_padrao = {"mensagem": "OK"}
    if id < 0 or id >= len(LISTA_TAREFAS):
        LOGGER.error("TAREFA NÃO EXISTE, criando exception")
        raise HTTPException(status_code=404, detail="TAREFA NÃO EXISTE")
    
    LISTA_TAREFAS[id]["titulo"] = tarefa.titulo
    LISTA_TAREFAS[id]["descricao"] = tarefa.descricao
    LISTA_TAREFAS[id]["concluido"] = tarefa.concluido
    if tarefa.concluido == True:
        LOGGER.info("Tarefa concluida, enviando notificação")
        qtd_tarefas_concluida += 1
        qtd_tarefas_pendentes -= 1
        requests.post(f"http://notificacoes:8000/notificar?titulo={tarefa.titulo}&data_finalizacao={datetime.now()}", timeout=100)
    LOGGER.info(str(mensagem_padrao))
    return mensagem_padrao


@APP.delete("/tarefas/{id}", summary="Deletar tarefa", description="Deleta uma tarefa específica pelo ID", tags=["Tarefas"])
def deletar_tarefa(id: int):
    mensagem_padrao = {"mensagem": "OK"}
    if id < 0 or id >= len(LISTA_TAREFAS):
        LOGGER.error("TAREFA NÃO EXISTE, criando exception")
        raise HTTPException(status_code=404, detail="TAREFA NÃO EXISTE")
    
    LOGGER.debug(f"Apagando a tarefa: {id}, {str(LISTA_TAREFAS[id])}")
    LISTA_TAREFAS.pop(id)
    qtd_tarefas_removidas += 1
    LOGGER.info("Tarefa deletada com sucesso")
    return mensagem_padrao

@APP.get('/metricas', summary="Metricas", description="Retona metricas de tarefas", tags=["Tarefas"],
response_model=Metricas)
def metricas():
    tempo_medio_total = 0
    metricas = Metricas()
    metricas.qtd_tarefas = len(LISTA_TAREFAS)
    metricas.qtd_tarefas_pendentes = qtd_tarefas_pendentes
    metricas.qtd_tarefas_concluida = qtd_tarefas_concluida
    metricas.qtd_tarefas_atualizadas = qtd_tarefas_atualizadas
    metricas.qtd_tarefas_removidas = qtd_tarefas_removidas
    if tempo_medio == 0:
        metricas.tempo_medio = 0
    else:
        metricas.tempo_medio = tempo_medio_total / len(LISTA_TAREFAS)
    LOGGER.info("Retornando metricas")
    LOGGER.debug(str(metricas))

    return metricas