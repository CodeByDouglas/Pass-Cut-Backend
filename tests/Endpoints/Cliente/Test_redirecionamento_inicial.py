import pytest
from unittest.mock import patch
from flask import Flask, json
from project.app.controllers.API_Agendamentos.redirecionamento_inicial import redirecionamento_bp

# filepath: /workspaces/Pass-Cut-Backend/tests/Tests_Endpoints/test_redirecionamento_inicial.py

# Arquivo de testes para o endpoint de redirecionamento inicial

@pytest.fixture
def app():
    """
    Fixture que cria uma instância da aplicação Flask para testes
    Registra o blueprint de redirecionamento e configura o modo de teste
    """
    app = Flask(__name__)
    app.register_blueprint(redirecionamento_bp)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """
    Fixture que cria um cliente de teste para fazer requisições HTTP
    Usa a aplicação criada pela fixture 'app'
    """
    return app.test_client()

def test_redirecionamento_inicial_success(client):
    """
    Teste do cenário de sucesso no redirecionamento inicial
    
    Este teste simula um redirecionamento bem-sucedido, onde:
    - O token de autorização é válido
    - Os dados de nome e ID base são válidos
    - O estabelecimento é encontrado no banco de dados
    - Um token JWT é gerado corretamente
    """
    # Configura todos os mocks necessários para simular um fluxo de redirecionamento bem-sucedido
    with patch('project.app.controllers.API_Agendamentos.redirecionamento_inicial.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.redirecionamento_inicial.validar_token_redirecionamento_inicial', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.redirecionamento_inicial.verificar_id_base', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.redirecionamento_inicial.verificar_nome_estabelecimento', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.redirecionamento_inicial.consultar_estabelecimento', return_value=(True, "123")), \
         patch('project.app.controllers.API_Agendamentos.redirecionamento_inicial.gerar_jwt_id_estabelecimento', return_value="mock-jwt-token"):
        
        # Prepara os dados para o teste: cabeçalho com token válido
        headers = {
            'Authorization': 'valid-fernet-token'
        }
        # Prepara os dados de nome e ID base
        data = {
            'nome': 'Estabelecimento Teste',
            'ID base': '12345'
        }
        
        # Faz a requisição POST ao endpoint de redirecionamento
        response = client.post('/api/redirecionamento_inicial', 
                              headers=headers,
                              json=data)
        
        # Verifica se a resposta tem status 200 (sucesso) e contém os dados esperados
        assert response.status_code == 200
        assert json.loads(response.data) == {
            "status": "success",
            "message": "Base autenticada",
            "Token": "mock-jwt-token"
        }

def test_redirecionamento_inicial_missing_auth_header(client):
    """
    Teste de falha no redirecionamento quando o cabeçalho de autorização está ausente
    
    Verifica se o endpoint rejeita a requisição quando não é fornecido
    o cabeçalho de autorização necessário
    """
    # Faz uma requisição sem fornecer o cabeçalho de autorização
    response = client.post('/api/redirecionamento_inicial')
    
    # Verifica se a resposta tem status 401 (não autorizado) e a mensagem de erro esperada
    assert response.status_code == 401
    assert json.loads(response.data) == {
        "status": "error",
        "message": "Erro de autenticação"
    }

def test_redirecionamento_inicial_invalid_fernet_token(client):
    """
    Teste de falha no redirecionamento quando o token Fernet é inválido
    
    Verifica se o endpoint rejeita a requisição quando o token
    fornecido não é um token Fernet válido
    """
    # Simula a verificação do token Fernet retornando falso (token inválido)
    with patch('project.app.controllers.API_Agendamentos.redirecionamento_inicial.verificar_token_fernet', return_value=False):
        headers = {
            'Authorization': 'invalid-token'
        }
        # Faz a requisição com um token inválido
        response = client.post('/api/redirecionamento_inicial', headers=headers)
        
        # Verifica se a resposta tem status 401 (não autorizado)
        assert response.status_code == 401
        assert json.loads(response.data) == {
            "status": "error",
            "message": "Erro de autenticação"
        }

def test_redirecionamento_inicial_invalid_redirection_token(client):
    """
    Teste de falha no redirecionamento quando o token é válido como Fernet
    mas inválido para o redirecionamento específico
    
    Verifica se o endpoint rejeita a requisição quando o token
    não é válido para o propósito específico de redirecionamento
    """
    # Simula um token Fernet válido, mas inválido para redirecionamento
    with patch('project.app.controllers.API_Agendamentos.redirecionamento_inicial.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.redirecionamento_inicial.validar_token_redirecionamento_inicial', return_value=False):
        
        headers = {
            'Authorization': 'valid-fernet-but-invalid-redirect-token'
        }
        # Faz a requisição com um token inválido para redirecionamento
        response = client.post('/api/redirecionamento_inicial', headers=headers)
        
        # Verifica se a resposta tem status 401 (não autorizado)
        assert response.status_code == 401
        assert json.loads(response.data) == {
            "status": "error",
            "message": "Erro de autenticação"
        }

def test_redirecionamento_inicial_missing_json(client):
    """
    Teste de falha no redirecionamento quando os dados JSON estão ausentes
    
    Verifica se o endpoint rejeita a requisição quando não são fornecidos
    os dados necessários no corpo da requisição
    """
    # Configura os mocks para simular token válido
    with patch('project.app.controllers.API_Agendamentos.redirecionamento_inicial.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.redirecionamento_inicial.validar_token_redirecionamento_inicial', return_value=True):
    
        # Prepara cabeçalho válido
        headers = {
            'Authorization': 'valid-fernet-token'
        }
        # Envia a requisição com JSON vazio em vez de sem JSON
        response = client.post('/api/redirecionamento_inicial', headers=headers, json={})
    
        # Verifica se a resposta tem status 400 (requisição inválida) e a mensagem de erro esperada
        assert response.status_code == 400
        assert json.loads(response.data) == {
            "status": "error",
            "message": "Dados insuficientes"
        }

def test_redirecionamento_inicial_incomplete_data(client):
    """
    Teste de falha no redirecionamento quando os dados JSON estão incompletos
    
    Verifica se o endpoint rejeita a requisição quando falta algum
    dos campos necessários nos dados fornecidos
    """
    # Configura os mocks para simular token válido
    with patch('project.app.controllers.API_Agendamentos.redirecionamento_inicial.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.redirecionamento_inicial.validar_token_redirecionamento_inicial', return_value=True):
        
        # Prepara cabeçalho válido
        headers = {
            'Authorization': 'valid-fernet-token'
        }
        # Dados incompletos (falta o ID base)
        data = {
            'nome': 'Estabelecimento Teste'
            # ID base está faltando
        }
        # Faz a requisição com dados incompletos
        response = client.post('/api/redirecionamento_inicial', headers=headers, json=data)
        
        # Verifica se a resposta tem status 400 (requisição inválida) e a mensagem de erro esperada
        assert response.status_code == 400
        assert json.loads(response.data) == {
            "status": "error",
            "message": "Dados insuficientes"
        }

def test_redirecionamento_inicial_invalid_data_format(client):
    """
    Teste de falha no redirecionamento quando o formato dos dados é inválido
    
    Verifica se o endpoint rejeita a requisição quando o formato
    do ID base ou do nome do estabelecimento é inválido
    """
    # Configura os mocks para simular token válido mas dados com formato inválido
    with patch('project.app.controllers.API_Agendamentos.redirecionamento_inicial.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.redirecionamento_inicial.validar_token_redirecionamento_inicial', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.redirecionamento_inicial.verificar_id_base', return_value=False):
        
        # Prepara cabeçalho válido
        headers = {
            'Authorization': 'valid-fernet-token'
        }
        # Dados com formato inválido
        data = {
            'nome': 'Estabelecimento Teste',
            'ID base': 'formato-invalido'
        }
        # Faz a requisição com dados de formato inválido
        response = client.post('/api/redirecionamento_inicial', headers=headers, json=data)
        
        # Verifica se a resposta tem status 400 (requisição inválida) e a mensagem de erro esperada
        assert response.status_code == 400
        assert json.loads(response.data) == {
            "status": "error",
            "message": "Dados invalidos"
        }

def test_redirecionamento_inicial_establishment_not_found(client):
    """
    Teste de falha no redirecionamento quando o estabelecimento não é encontrado
    
    Verifica se o endpoint retorna o erro correto quando os dados são válidos
    mas o estabelecimento não existe no banco de dados
    """
    # Configura os mocks para simular estabelecimento não encontrado
    with patch('project.app.controllers.API_Agendamentos.redirecionamento_inicial.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.redirecionamento_inicial.validar_token_redirecionamento_inicial', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.redirecionamento_inicial.verificar_id_base', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.redirecionamento_inicial.verificar_nome_estabelecimento', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.redirecionamento_inicial.consultar_estabelecimento', return_value=False):
        
        # Prepara cabeçalho válido
        headers = {
            'Authorization': 'valid-fernet-token'
        }
        # Dados com formato válido, mas estabelecimento inexistente
        data = {
            'nome': 'Estabelecimento Inexistente',
            'ID base': '12345'
        }
        # Faz a requisição
        response = client.post('/api/redirecionamento_inicial', headers=headers, json=data)
        
        # Verifica se a resposta tem status 404 (não encontrado) e a mensagem de erro esperada
        assert response.status_code == 404
        assert json.loads(response.data) == {
            "status": "error",
            "message": "Estabelecimento não encontrado."
        }