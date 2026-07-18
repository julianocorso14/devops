"""Módulo principal da aplicação de tarefas."""

from datetime import datetime
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

LOGGER = logging.getLogger("devops")
LOGGER.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler(f"{LOGGER.name}.log", encoding="utf-8")
formatador = logging.Formatter(
    fmt="%(name)s | %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(message)s"
)

stream_handler.setFormatter(formatador)
file_handler.setFormatter(formatador)

LOGGER.addHandler(stream_handler)
LOGGER.addHandler(file_handler)


class Tarefa(BaseModel):
    """Modelo de dados para representar uma tarefa."""
    titulo: str
    descricao: str
    concluido: bool = False


class Metricas(BaseModel):
    """Modelo de dados para representar métricas das tarefas."""
    qtd_tarefas: int
    qtd_tarefas_pendentes: int
    qtd_tarefas_concluida: int
    qtd_tarefas_atualizadas: int
    qtd_tarefas_removidas: int
    tempo_medio: float


LISTA_TAREFAS = []
QTD_TAREFAS = 0
QTD_TAREFAS_PENDENTES = 0
QTD_TAREFAS_CONCLUIDA = 0
QTD_TAREFAS_ATUALIZADAS = 0
QTD_TAREFAS_REMOVIDAS = 0
TEMPO_MEDIO = 0

APP = FastAPI()


def nova_tarefa(tarefa_id: int, titulo: str, descricao: str):
    """Cria uma nova tarefa como dicionário."""
    return {
        "id": tarefa_id,
        "titulo": titulo,
        "descricao": descricao,
        "concluido": False,
        "criado_em": datetime.now()
    }


@APP.get("/", summary="Página inicial", description="Página inicial da API", tags=["Home"])
def index():
    """Endpoint inicial da API."""
    LOGGER.info("Acesso a HomePage")
    return "Olá, DevOps!"


@APP.get("/health", summary="Health", description="Retorna Health da API", tags=["Health"])
def health():
    """Endpoint de verificação de saúde da API."""
    LOGGER.info("Health - OK")
    return {"status": "OK"}


@APP.get("/tarefas", summary="Listar tarefas", description="Lista todas as tarefas cadastradas",
 tags=["Tarefas"])
def listar_tarefas():
    """Lista todas as tarefas cadastradas (somente id e título)."""
    if not LISTA_TAREFAS:
        LOGGER.info("Lista de tarefas vazia")
        return LISTA_TAREFAS
    return [{"id": tarefa["id"], "titulo": tarefa["titulo"]} for tarefa in LISTA_TAREFAS]


@APP.get("/tarefas/{tarefa_id}", summary="Listar tarefa específica",
description="Lista uma tarefa pelo ID", tags=["Tarefas"])
def listar_tarefa_especifica(tarefa_id: int):
    """Lista uma tarefa específica pelo ID."""
    mensagem_padrao = {"mensagem": "Não existe nenhuma tarefa"}
    if not LISTA_TAREFAS or tarefa_id < 0 or tarefa_id >= len(LISTA_TAREFAS):
        LOGGER.error("Tarefa não encontrada")
        return mensagem_padrao
    return LISTA_TAREFAS[tarefa_id]


@APP.post("/tarefas", summary="Inserir tarefa", description="Insere uma nova tarefa",
tags=["Tarefas"], status_code=201)
def inserir_tarefa(tarefa: Tarefa):
    """Insere uma nova tarefa na lista."""
    global QTD_TAREFAS, QTD_TAREFAS_PENDENTES
    novo_id = len(LISTA_TAREFAS)
    nova = nova_tarefa(novo_id, tarefa.titulo, tarefa.descricao)
    LISTA_TAREFAS.append(nova)
    QTD_TAREFAS += 1
    QTD_TAREFAS_PENDENTES += 1
    return {"mensagem": "OK"}


@APP.put("/tarefas/{tarefa_id}", summary="Atualizar tarefa",
description="Atualiza uma tarefa pelo ID", tags=["Tarefas"])
def atualizar_tarefa(tarefa_id: int, tarefa: Tarefa):
    """Atualiza uma tarefa existente."""
    global QTD_TAREFAS_CONCLUIDA, QTD_TAREFAS_PENDENTES, QTD_TAREFAS_ATUALIZADAS
    if tarefa_id < 0 or tarefa_id >= len(LISTA_TAREFAS):
        raise HTTPException(status_code=404, detail="TAREFA NÃO EXISTE")

    LISTA_TAREFAS[tarefa_id].update({
        "titulo": tarefa.titulo,
        "descricao": tarefa.descricao,
        "concluido": tarefa.concluido
    })
    QTD_TAREFAS_ATUALIZADAS += 1

    if tarefa.concluido:
        QTD_TAREFAS_CONCLUIDA += 1
        QTD_TAREFAS_PENDENTES -= 1
        try:
            requests.post(
                f"http://notificacoes:8000/notificar?titulo={tarefa.titulo}&"
                f"data_finalizacao={datetime.now()}",
                timeout=5
            )
        except requests.RequestException:
            LOGGER.warning("Falha ao enviar notificação")

    return {"mensagem": "OK"}


@APP.delete("/tarefas/{tarefa_id}", summary="Deletar tarefa",
description="Deleta uma tarefa pelo ID", tags=["Tarefas"])
def deletar_tarefa(tarefa_id: int):
    """Remove uma tarefa da lista."""
    global QTD_TAREFAS_REMOVIDAS, QTD_TAREFAS_PENDENTES
    if tarefa_id < 0 or tarefa_id >= len(LISTA_TAREFAS):
        raise HTTPException(status_code=404, detail="TAREFA NÃO EXISTE")

    tarefa_removida = LISTA_TAREFAS.pop(tarefa_id)
    QTD_TAREFAS_REMOVIDAS += 1
    if not tarefa_removida["concluido"]:
        QTD_TAREFAS_PENDENTES -= 1
    return {"mensagem": "OK"}


@APP.get("/metricas", summary="Metricas", description="Retorna métricas de tarefas",
tags=["Tarefas"], response_model=Metricas)
def metricas():
    """Retorna métricas das tarefas cadastradas."""
    tempo_medio_total = 0
    return Metricas(
        qtd_tarefas=len(LISTA_TAREFAS),
        qtd_tarefas_pendentes=QTD_TAREFAS_PENDENTES,
        qtd_tarefas_concluida=QTD_TAREFAS_CONCLUIDA,
        qtd_tarefas_atualizadas=QTD_TAREFAS_ATUALIZADAS,
        qtd_tarefas_removidas=QTD_TAREFAS_REMOVIDAS,
        tempo_medio=0.0 if TEMPO_MEDIO == 0 else tempo_medio_total / len(LISTA_TAREFAS)
    )
