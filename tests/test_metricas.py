import pytest
from fastapi.testclient import TestClient
import app.main as main

CLIENT = TestClient(main.APP)

@pytest.fixture(autouse=True)
def reset_state():
    main.LISTA_TAREFAS.clear()
    main.QTD_TAREFAS = 0
    main.QTD_TAREFAS_PENDENTES = 0
    main.QTD_TAREFAS_CONCLUIDA = 0
    main.QTD_TAREFAS_ATUALIZADAS = 0
    main.QTD_TAREFAS_REMOVIDAS = 0
    main.TEMPO_MEDIO = 0


def test_metricas_tarefa():
    CLIENT.post("/tarefas", json={"titulo": "Teste", "descricao": "Desc"})
    requisicao = CLIENT.get("/metricas")
    assert requisicao.status_code == 200
    assert requisicao.json() == {
        "qtd_tarefas": 1,
        "qtd_tarefas_pendentes": 1,
        "qtd_tarefas_concluida": 0,
        "qtd_tarefas_atualizadas": 0,
        "qtd_tarefas_removidas": 0,
        "tempo_medio": 0.0
    }


def test_metricas_concluir_tarefa():
    CLIENT.post("/tarefas", json={"titulo": "Finalizar", "descricao": "Teste"})
    CLIENT.put("/tarefas/0", json={"titulo": "Finalizar", "descricao": "Teste", "concluido": True})
    requisicao = CLIENT.get("/metricas")
    assert requisicao.status_code == 200
    assert requisicao.json()["qtd_tarefas_concluida"] == 1
    assert requisicao.json()["qtd_tarefas_pendentes"] == 0


def test_metricas_remover_tarefa():
    CLIENT.post("/tarefas", json={"titulo": "Apagar", "descricao": "Teste"})
    CLIENT.delete("/tarefas/0")
    requisicao = CLIENT.get("/metricas")
    assert requisicao.status_code == 200
    assert requisicao.json()["qtd_tarefas_removidas"] == 1
    assert requisicao.json()["qtd_tarefas"] == 0
