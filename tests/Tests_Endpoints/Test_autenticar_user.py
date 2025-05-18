import pytest
from unittest.mock import patch
from flask import Flask, json
from project.app.controllers.API_Agendamentos.autenticar_user import autenticar_user_bp

# Arquivo de testes para o endpoint de autenticação de usuários

@pytest.fixture
def app():
    """
    Fixture que cria uma instância da aplicação Flask para testes
    Registra o blueprint de autenticação e configura o modo de teste
    """
    app = Flask(__name__)
    app.register_blueprint(autenticar_user_bp)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """
    Fixture que cria um cliente de teste para fazer requisições HTTP
    Usa a aplicação criada pela fixture 'app'
    """
    return app.test_client()

def test_autenticar_user_success(client):
    """
    Teste do cenário de sucesso na autenticação com credenciais válidas
    
    Este teste simula uma autenticação bem-sucedida, onde:
    - Os tokens de autorização são válidos
    - As credenciais do usuário são válidas
    - O usuário existe no banco de dados
    - A senha está correta
    - Um token JWT é gerado corretamente
    """
    # Configura todos os mocks necessários para simular um fluxo de autenticação bem-sucedido
    with patch('project.app.controllers.API_Agendamentos.autenticar_user.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.validar_token_autenticar_user', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.validar_token_id_estabelecimento', return_value=(True, "123")), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.verificar_email', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.verificar_senha', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.consultar_id_user', return_value=(True, "456")), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.autenticar_senha', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.gerar_jwt_id_estabelecimento', return_value="mock-jwt-token"):
        
        # Prepara os dados para o teste: cabeçalhos com tokens válidos
        headers = {
            'Authorization': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-token'
        }
        # Prepara os dados de login e senha
        data = {
            'login': 'test@example.com',
            'senha': 'Valid123!'
        }
        
        # Faz a requisição POST ao endpoint de autenticação
        response = client.post('/api/autenticar_user', 
                              headers=headers,
                              json=data)
        
        # Verifica se a resposta tem status 200 (sucesso) e contém os dados esperados
        assert response.status_code == 200
        assert json.loads(response.data) == {
            "status": "success",
            "message": "User autenticado",
            "token": "mock-jwt-token"
        }

def test_autenticar_user_missing_headers(client):
    """
    Teste de falha na autenticação quando os cabeçalhos estão ausentes
    
    Verifica se o endpoint rejeita a requisição quando não são fornecidos
    os cabeçalhos de autorização necessários
    """
    # Faz uma requisição sem fornecer os cabeçalhos de autorização
    response = client.post('/api/autenticar_user')
    
    # Verifica se a resposta tem status 401 (não autorizado) e a mensagem de erro esperada
    assert response.status_code == 401
    assert json.loads(response.data) == {
        "status": "error",
        "message": "Erro de autenticação"
    }

def test_autenticar_user_invalid_tokens(client):
    """
    Teste de falha na autenticação quando os tokens são inválidos
    
    Simula um cenário onde o token Fernet fornecido é inválido,
    verificando se o endpoint rejeita corretamente a requisição
    """
    # Simula a verificação do token Fernet retornando falso (token inválido)
    with patch('project.app.controllers.API_Agendamentos.autenticar_user.verificar_token_fernet', return_value=False):
        headers = {
            'Authorization': 'invalid-token',
            'token-estabelecimento': 'some-token'
        }
        # Faz a requisição com um token inválido
        response = client.post('/api/autenticar_user', headers=headers)
        
        # Verifica se a resposta tem status 401 (não autorizado)
        assert response.status_code == 401

def test_autenticar_user_missing_credentials(client):
    """
    Teste de falha na autenticação quando as credenciais estão ausentes
    
    Verifica se o endpoint rejeita a requisição quando o corpo da mensagem
    não contém os campos de login e senha necessários
    """
    # Configura os mocks para simular tokens válidos
    with patch('project.app.controllers.API_Agendamentos.autenticar_user.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.validar_token_autenticar_user', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.validar_token_id_estabelecimento', return_value=(True, "123")):
        
        # Prepara cabeçalhos válidos
        headers = {
            'Authorization': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-token'
        }
        # Envia um JSON vazio (sem credenciais)
        response = client.post('/api/autenticar_user', headers=headers, json={})
        
        # Verifica se a resposta tem status 411 (comprimento necessário) e a mensagem de erro esperada
        assert response.status_code == 411
        assert json.loads(response.data) == {
            "status": "error",
            "message": "Erro dados insuficientes"
        }

def test_autenticar_user_invalid_email(client):
    """
    Teste de falha na autenticação com formato de email inválido
    
    Verifica se o endpoint rejeita a requisição quando o email
    fornecido tem um formato inválido
    """
    # Configura os mocks para simular tokens válidos, mas email inválido
    with patch('project.app.controllers.API_Agendamentos.autenticar_user.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.validar_token_autenticar_user', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.validar_token_id_estabelecimento', return_value=(True, "123")), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.verificar_email', return_value=False):
        
        # Prepara cabeçalhos válidos
        headers = {
            'Authorization': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-token'
        }
        # Dados com email em formato inválido
        data = {
            'login': 'invalid-email',
            'senha': 'Password123'
        }
        # Faz a requisição
        response = client.post('/api/autenticar_user', headers=headers, json=data)
        
        # Verifica se a resposta tem status 400 (requisição inválida) e a mensagem de erro esperada
        assert response.status_code == 400
        assert json.loads(response.data) == {
            "status": "error",
            "message": "Erro dados invalidos"
        }

def test_autenticar_user_user_not_found(client):
    """
    Teste de falha na autenticação quando o usuário não é encontrado
    
    Verifica se o endpoint retorna erro quando o usuário não existe
    no banco de dados, mesmo com email e senha em formato válido
    """
    # Configura os mocks para simular usuário não encontrado
    with patch('project.app.controllers.API_Agendamentos.autenticar_user.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.validar_token_autenticar_user', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.validar_token_id_estabelecimento', return_value=(True, "123")), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.verificar_email', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.verificar_senha', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.consultar_id_user', return_value=False):
        
        # Prepara cabeçalhos válidos
        headers = {
            'Authorization': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-token'
        }
        # Dados de um usuário que não existe
        data = {
            'login': 'nonexistent@example.com',
            'senha': 'Password123'
        }
        # Faz a requisição
        response = client.post('/api/autenticar_user', headers=headers, json=data)
        
        # Verifica se a resposta tem status 401 (não autorizado) e a mensagem específica
        assert response.status_code == 401
        assert json.loads(response.data) == {
            "status": "error",
            "message": "Usuário não encontrado"
        }

def test_autenticar_user_wrong_password(client):
    """
    Teste de falha na autenticação com senha incorreta
    
    Verifica se o endpoint retorna erro quando o usuário existe
    mas a senha fornecida não corresponde à senha armazenada
    """
    # Configura os mocks para simular senha incorreta
    with patch('project.app.controllers.API_Agendamentos.autenticar_user.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.validar_token_autenticar_user', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.validar_token_id_estabelecimento', return_value=(True, "123")), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.verificar_email', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.verificar_senha', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.consultar_id_user', return_value=(True, "456")), \
         patch('project.app.controllers.API_Agendamentos.autenticar_user.autenticar_senha', return_value=False):
        
        # Prepara cabeçalhos válidos
        headers = {
            'Authorization': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-token'
        }
        # Dados com senha incorreta
        data = {
            'login': 'test@example.com',
            'senha': 'WrongPassword'
        }
        # Faz a requisição
        response = client.post('/api/autenticar_user', headers=headers, json=data)
        
        # Verifica se a resposta tem status 401 (não autorizado) e a mensagem específica
        assert response.status_code == 401
        assert json.loads(response.data) == {
            "status": "error",
            "message": "Erro ao autenticar user"
        }