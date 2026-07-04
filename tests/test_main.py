from fastapi.testclient import TestClient
from app import APP

CLIENT = TestClient(APP)

def test_index():
    requisicao = CLIENT.get("/")

    assert requisicao.status_code == 200
    assert requisicao.json() == "Olá, DevOps!"

def test_inserir_tarefa():
    tarefa = {
        "titulo": "str",
        "descricao": "str"
    }

    requisicao = CLIENT.post(url="/tarefas", json=tarefa)
    assert requisicao.status_code == 201
    assert requisicao.json() == {"mensagem": "OK"}
