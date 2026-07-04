def soma(a, b):
    return a + b

def test_soma_positivos():
    assert soma(4, 4) == 8

def test_soma_errada():
    assert soma(3, 7) == 10