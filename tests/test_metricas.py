from fastapi.testclient import TestClient
from app import APP

CLIENT = TestClient(APP)

def test_inserir_tarefa():
    tarefa = {
        "titulo": "str",
        "descricao": "str"
    }

    requisicao = CLIENT.post(url="/tarefas", json=tarefa)
    assert requisicao.status_code == 201
    assert requisicao.json() == {"mensagem": "OK"}

def test_metricas_tarefa():

    requisicao = CLIENT.get(url="/metricas")
    assert requisicao.status_code == 200
    assert requisicao.json() == {
        qtd_tarefas: 1,
        qtd_tarefas_pendentes: 0,
        qtd_tarefas_concluida: 0,
        qtd_tarefas_atualizadas: 0,
        qtd_tarefas_removidas: 0
    }