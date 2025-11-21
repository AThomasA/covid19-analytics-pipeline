from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_api_online():
    """Testa se a API liga e responde na raiz"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"
    
def test_listar_paises():
    """Testa se a a lista de países retorna dados"""
    response = client.get("/paises")
    assert response.status_code == 200
    assert "total" in response.json()
    assert len(response.json()["paises"]) > 0

def test_dados_brasil():
    """Testa se a busca pelo Brasil funciona e traz as chaves corretas"""
    response = client.get("/dados/Brazil")
    assert response.status_code == 200
    data = response.json()
    assert data["pais"] == "Brazil"
    assert "taxa_letalidade" in data
    assert "casos_acumulados" in data
 
def test_pais_inexistente():
    """Testa se a API retorna 404 para país inventado"""
    response = client.get("/dados/Narnia")
    assert response.status_code == 404
    assert response.json()["detail"] == "País não encontrado"
 
