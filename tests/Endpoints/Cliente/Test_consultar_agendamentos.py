import pytest
from unittest.mock import patch
from flask import Flask, json
from project.app.controllers.API_Agendamentos.consultar_agendamentos import consultar_agendamentos_bp

# filepath: /workspaces/Pass-Cut-Backend/tests/Endpoints/Agendamentos/Test_consultar_agendamentos.py

# Documentação: Testes para o endpoint de consulta de agendamentos
# Este arquivo contém testes que verificam o funcionamento do endpoint
# /api/consultar_agendamentos, cobrindo cenários de sucesso e falha.

@pytest.fixture
def app():
    """
    Fixture que cria uma instância da aplicação Flask para testes
    """
    app = Flask(__name__)
    app.register_blueprint(consultar_agendamentos_bp)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """
    Fixture que cria um cliente de teste para fazer requisições à aplicação
    """
    return app.test_client()

def test_consultar_agendamentos_sucesso(client):
    """
    Teste para o cenário de sucesso na consulta de agendamentos
    
    Verifica se o endpoint retorna os agendamentos corretamente quando
    todos os parâmetros são válidos e existem agendamentos para o usuário.
    """
    # Configura todos os mocks necessários para simular sucesso
    with patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.validar_token_consultar_agendamentos', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.validar_token_id_estabelecimento', return_value=(True, "123")), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.validar_token_id_user', return_value=(True, "456")), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.consultar_agendamentos_por_estabelecimento_cliente_status', 
               return_value=[{"id": 1, "data": "2023-06-01", "hora": "14:00", "servico": "Corte de Cabelo"}]):
        
        # Configura cabeçalhos e dados para a requisição
        headers = {
            'Authorization': 'token-fernet-valido',
            'token-estabelecimento': 'token-jwt-estabelecimento',
            'token-user': 'token-jwt-usuario'
        }
        data = {
            'type': 'ativos'
        }
        
        # Faz a requisição GET (que na verdade precisa de um body, então é meio híbrida)
        response = client.get('/api/consultar_agendamentos', 
                             headers=headers,
                             json=data)
        
        # Verifica a resposta
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["status"] == "success"
        assert response_data["message"] == "Consulta realizada com sucesso."
        assert isinstance(response_data["agendamentos"], list)
        assert len(response_data["agendamentos"]) == 1
        assert response_data["agendamentos"][0]["id"] == 1

def test_consultar_agendamentos_sem_resultados(client):
    """
    Teste para o cenário onde não há agendamentos para o usuário
    
    Verifica se o endpoint retorna uma mensagem adequada quando
    não existem agendamentos para o usuário com os parâmetros informados.
    """
    # Configura mocks para simular o caso de nenhum agendamento encontrado
    with patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.validar_token_consultar_agendamentos', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.validar_token_id_estabelecimento', return_value=(True, "123")), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.validar_token_id_user', return_value=(True, "456")), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.consultar_agendamentos_por_estabelecimento_cliente_status', 
               return_value=None):
        
        headers = {
            'Authorization': 'token-fernet-valido',
            'token-estabelecimento': 'token-jwt-estabelecimento',
            'token-user': 'token-jwt-usuario'
        }
        data = {
            'type': 'historico'
        }
        
        response = client.get('/api/consultar_agendamentos', 
                             headers=headers,
                             json=data)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["status"] == "success"
        assert response_data["message"] == "Nenhum agendamento encontrado para os dados informados."
        assert "agendamentos" not in response_data

def test_consultar_agendamentos_sem_headers(client):
    """
    Teste para o cenário onde os cabeçalhos de autorização estão ausentes
    
    Verifica se o endpoint rejeita a requisição quando não são fornecidos
    os cabeçalhos de autorização necessários.
    """
    # Teste sem enviar nenhum header
    response = client.get('/api/consultar_agendamentos')
    
    assert response.status_code == 401
    response_data = json.loads(response.data)
    assert response_data["status"] == "error"
    assert response_data["message"] == "Erro de autenticação"

def test_consultar_agendamentos_headers_incompletos(client):
    """
    Teste para o cenário onde alguns cabeçalhos de autorização estão ausentes
    
    Verifica se o endpoint rejeita a requisição quando apenas alguns dos
    cabeçalhos necessários são fornecidos.
    """
    # Teste enviando apenas o header Authorization
    headers = {
        'Authorization': 'token-fernet-valido'
    }
    response = client.get('/api/consultar_agendamentos', headers=headers)
    
    assert response.status_code == 401
    response_data = json.loads(response.data)
    assert response_data["status"] == "error"
    assert response_data["message"] == "Erro de autenticação"

def test_consultar_agendamentos_token_formato_invalido(client):
    """
    Teste para o cenário onde os tokens têm formato inválido
    
    Verifica se o endpoint rejeita a requisição quando os tokens
    fornecidos não têm o formato correto.
    """
    # Configura mock para simular token Fernet inválido
    with patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.verificar_token_fernet', return_value=False):
        headers = {
            'Authorization': 'token-fernet-invalido',
            'token-estabelecimento': 'token-jwt-estabelecimento',
            'token-user': 'token-jwt-usuario'
        }
        response = client.get('/api/consultar_agendamentos', headers=headers)
        
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data["status"] == "error"
        assert response_data["message"] == "Erro de autenticação"

    # Configura mock para simular token JWT inválido
    with patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.verificar_token_jwt', return_value=False):
        headers = {
            'Authorization': 'token-fernet-valido',
            'token-estabelecimento': 'token-jwt-invalido',
            'token-user': 'token-jwt-usuario'
        }
        response = client.get('/api/consultar_agendamentos', headers=headers)
        
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data["status"] == "error"
        assert response_data["message"] == "Erro de autenticação"

def test_consultar_agendamentos_token_autorizacao_invalido(client):
    """
    Teste para o cenário onde o token de autorização é inválido para consulta
    
    Verifica se o endpoint rejeita a requisição quando o token de autorização
    não é válido especificamente para consulta de agendamentos.
    """
    # Configura mocks para simular token de autorização inválido para consulta
    with patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.validar_token_consultar_agendamentos', return_value=False):
        
        headers = {
            'Authorization': 'token-fernet-valido-mas-nao-para-consulta',
            'token-estabelecimento': 'token-jwt-estabelecimento',
            'token-user': 'token-jwt-usuario'
        }
        response = client.get('/api/consultar_agendamentos', headers=headers)
        
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data["status"] == "error"
        assert response_data["message"] == "Erro de autenticação"

def test_consultar_agendamentos_token_estabelecimento_invalido(client):
    """
    Teste para o cenário onde o token do estabelecimento é inválido
    
    Verifica se o endpoint rejeita a requisição quando o token do
    estabelecimento não é válido.
    """
    # Configura mocks para simular token de estabelecimento inválido
    with patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.validar_token_consultar_agendamentos', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.validar_token_id_estabelecimento', return_value=False):
        
        headers = {
            'Authorization': 'token-fernet-valido',
            'token-estabelecimento': 'token-jwt-estabelecimento-invalido',
            'token-user': 'token-jwt-usuario'
        }
        response = client.get('/api/consultar_agendamentos', headers=headers)
        
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data["status"] == "error"
        assert response_data["message"] == "Erro de autenticação"

def test_consultar_agendamentos_token_usuario_invalido(client):
    """
    Teste para o cenário onde o token do usuário é inválido
    
    Verifica se o endpoint rejeita a requisição quando o token do
    usuário não é válido para o estabelecimento.
    """
    # Configura mocks para simular token de usuário inválido
    with patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.validar_token_consultar_agendamentos', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.validar_token_id_estabelecimento', return_value=(True, "123")), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.validar_token_id_user', return_value=False):
        
        headers = {
            'Authorization': 'token-fernet-valido',
            'token-estabelecimento': 'token-jwt-estabelecimento',
            'token-user': 'token-jwt-usuario-invalido'
        }
        response = client.get('/api/consultar_agendamentos', headers=headers)
        
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data["status"] == "error"
        assert response_data["message"] == "Erro de autenticação"

def test_consultar_agendamentos_sem_parametro_tipo(client):
    """
    Teste para o cenário onde o parâmetro de tipo está ausente
    
    Verifica se o endpoint rejeita a requisição quando o parâmetro
    'type' não é fornecido no corpo da requisição.
    """
    # Configura mocks para simular validação bem-sucedida até o ponto de verificar o parâmetro type
    with patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.validar_token_consultar_agendamentos', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.validar_token_id_estabelecimento', return_value=(True, "123")), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.validar_token_id_user', return_value=(True, "456")):
        
        headers = {
            'Authorization': 'token-fernet-valido',
            'token-estabelecimento': 'token-jwt-estabelecimento',
            'token-user': 'token-jwt-usuario'
        }
        # Não envia o parâmetro 'type'
        data = {}
        
        response = client.get('/api/consultar_agendamentos', 
                             headers=headers,
                             json=data)
        
        assert response.status_code == 411
        response_data = json.loads(response.data)
        assert response_data["status"] == "error"
        assert response_data["message"] == "Erro de dados insuficientes"

def test_consultar_agendamentos_tipo_invalido(client):
    """
    Teste para o cenário onde o parâmetro de tipo tem valor inválido
    
    Verifica se o endpoint rejeita a requisição quando o valor
    do parâmetro 'type' não é 'ativos' nem 'historico'.
    """
    # Configura mocks para simular validação bem-sucedida até o ponto de verificar o valor do parâmetro type
    with patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.validar_token_consultar_agendamentos', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.validar_token_id_estabelecimento', return_value=(True, "123")), \
         patch('project.app.controllers.API_Agendamentos.consultar_agendamentos.validar_token_id_user', return_value=(True, "456")):
        
        headers = {
            'Authorization': 'token-fernet-valido',
            'token-estabelecimento': 'token-jwt-estabelecimento',
            'token-user': 'token-jwt-usuario'
        }
        # Envia um tipo inválido
        data = {
            'type': 'invalido'
        }
        
        response = client.get('/api/consultar_agendamentos', 
                             headers=headers,
                             json=data)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data["status"] == "error"
        assert response_data["message"] == "Dados invalidos"