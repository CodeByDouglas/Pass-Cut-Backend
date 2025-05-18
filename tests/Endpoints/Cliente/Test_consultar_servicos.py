import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, json
from project.app.controllers.API_Agendamentos.consultar_servicos import consultar_servicos_bp

# filepath: project/app/controllers/API_Agendamentos/test_consultar_servicos.py

# Importa o blueprint do controller que será testado
# Usando import absoluto conforme a estrutura do projeto e as diretrizes

@pytest.fixture
def app():
    """
    Fixture que cria e configura uma instância da aplicação Flask para os testes.
    Registra o blueprint 'consultar_servicos_bp' e ativa o modo de teste.
    """
    app = Flask(__name__)
    app.register_blueprint(consultar_servicos_bp) # O endpoint está em /consultar-servicos
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """
    Fixture que cria um cliente de teste para fazer requisições HTTP à aplicação.
    Utiliza a aplicação Flask configurada pela fixture 'app'.
    """
    return app.test_client()

# --- Testes para o endpoint /consultar-servicos ---

def test_consultar_servicos_sucesso_com_servicos(client):
    """
    Testa o cenário de sucesso onde todos os tokens são válidos,
    o usuário é autenticado e serviços são encontrados para o estabelecimento.
    Espera-se uma resposta 200 OK com a lista de serviços.
    """
    # Mock das funções de serviço para simular um cenário de sucesso
    with patch('project.app.controllers.API_Agendamentos.consultar_servicos.verificar_token_fernet', return_value=True) as mock_ver_fernet, \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.verificar_token_jwt', return_value=True) as mock_ver_jwt, \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.validar_token_consultar_servico', return_value=True) as mock_val_token_serv, \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.validar_token_id_estabelecimento', return_value=(True, "est_id_123")) as mock_val_id_est, \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.validar_token_id_user', return_value=(True, "user_id_456")) as mock_val_id_user, \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.consultar_servicos_por_estabelecimento', return_value=(True, [{"id": 1, "nome": "Corte"}, {"id": 2, "nome": "Barba"}])) as mock_cons_serv:

        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token'
        }
        response = client.post('/consultar-servicos', headers=headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == "Requisição bem sucedida"
        assert data['estabelecimento_id'] == "est_id_123"
        assert data['user_id'] == "user_id_456"
        assert len(data['servicos']) == 2
        assert data['servicos'][0]['nome'] == "Corte"

        # Verifica se os mocks foram chamados como esperado
        mock_ver_fernet.assert_called_once_with('valid-fernet-token')
        assert mock_ver_jwt.call_count == 2 # Chamado para token-estabelecimento e token-user
        mock_val_token_serv.assert_called_once_with('valid-fernet-token')
        mock_val_id_est.assert_called_once_with('valid-jwt-est-token')
        mock_val_id_user.assert_called_once_with("est_id_123", 'valid-jwt-user-token')
        mock_cons_serv.assert_called_once_with("est_id_123")

def test_consultar_servicos_sucesso_sem_servicos_cadastrados(client):
    """
    Testa o cenário de sucesso onde todos os tokens são válidos,
    mas o estabelecimento não possui serviços cadastrados (lista vazia).
    Espera-se uma resposta 200 OK com uma lista de serviços vazia.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_servicos.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.validar_token_consultar_servico', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.validar_token_id_estabelecimento', return_value=(True, "est_id_123")), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.validar_token_id_user', return_value=(True, "user_id_456")), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.consultar_servicos_por_estabelecimento', return_value=(True, [])): # Lista de serviços vazia

        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token'
        }
        response = client.post('/consultar-servicos', headers=headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == "Requisição bem sucedida"
        assert data['estabelecimento_id'] == "est_id_123"
        assert data['user_id'] == "user_id_456"
        assert data['servicos'] == []

def test_consultar_servicos_falha_consulta_db(client):
    """
    Testa o cenário onde a consulta ao banco de dados por serviços falha
    (retorna (False, ...)).
    Espera-se uma resposta 404 Not Found.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_servicos.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.validar_token_consultar_servico', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.validar_token_id_estabelecimento', return_value=(True, "est_id_123")), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.validar_token_id_user', return_value=(True, "user_id_456")), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.consultar_servicos_por_estabelecimento', return_value=(False, [])): # Falha na consulta

        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token'
        }
        response = client.post('/consultar-servicos', headers=headers)

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['erro'] == "não foi possível localizar os dados"

def test_consultar_servicos_falha_consulta_db_retorna_none(client):
    """
    Testa o cenário onde a consulta ao banco de dados por serviços retorna None.
    Espera-se uma resposta 404 Not Found.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_servicos.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.validar_token_consultar_servico', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.validar_token_id_estabelecimento', return_value=(True, "est_id_123")), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.validar_token_id_user', return_value=(True, "user_id_456")), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.consultar_servicos_por_estabelecimento', return_value=None): # Consulta retorna None

        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token'
        }
        response = client.post('/consultar-servicos', headers=headers)

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['erro'] == "não foi possível localizar os dados"


@pytest.mark.parametrize("missing_header", ["auth", "token-estabelecimento", "token-user"])
def test_consultar_servicos_cabecalho_ausente(client, missing_header):
    """
    Testa a falha quando um dos cabeçalhos obrigatórios ('auth', 
    'token-estabelecimento', 'token-user') está ausente.
    Espera-se uma resposta 401 Unauthorized.
    """
    headers = {
        'auth': 'valid-fernet-token',
        'token-estabelecimento': 'valid-jwt-est-token',
        'token-user': 'valid-jwt-user-token'
    }
    del headers[missing_header] # Remove o cabeçalho parametrizado

    response = client.post('/consultar-servicos', headers=headers)
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['erro'] == "Autenticação falhou"

def test_consultar_servicos_token_fernet_invalido(client):
    """
    Testa a falha quando o token Fernet ('auth') é inválido.
    Espera-se uma resposta 401 Unauthorized.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_servicos.verificar_token_fernet', return_value=False):
        headers = {
            'auth': 'invalid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token'
        }
        response = client.post('/consultar-servicos', headers=headers)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou"

def test_consultar_servicos_token_jwt_estabelecimento_invalido(client):
    """
    Testa a falha quando o token JWT do estabelecimento é inválido.
    Espera-se uma resposta 401 Unauthorized.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_servicos.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.verificar_token_jwt', side_effect=[False, True]): # Primeiro JWT (est) é inválido
        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'invalid-jwt-est-token',
            'token-user': 'valid-jwt-user-token'
        }
        response = client.post('/consultar-servicos', headers=headers)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou"

def test_consultar_servicos_token_jwt_user_invalido(client):
    """
    Testa a falha quando o token JWT do usuário é inválido.
    Espera-se uma resposta 401 Unauthorized.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_servicos.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.verificar_token_jwt', side_effect=[True, False]): # Segundo JWT (user) é inválido
        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'invalid-jwt-user-token'
        }
        response = client.post('/consultar-servicos', headers=headers)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou"

def test_consultar_servicos_token_auth_nao_valido_para_servico(client):
    """
    Testa a falha quando o token 'auth' não é válido para a consulta de serviços.
    Espera-se uma resposta 401 Unauthorized.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_servicos.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.validar_token_consultar_servico', return_value=False): # Token auth inválido para serviço
        headers = {
            'auth': 'valid-fernet-token-but-not-for-service',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token'
        }
        response = client.post('/consultar-servicos', headers=headers)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou"

def test_consultar_servicos_token_id_estabelecimento_invalido(client):
    """
    Testa a falha quando a validação do token do estabelecimento falha
    (validar_token_id_estabelecimento retorna False ou (False, ...)).
    Espera-se uma resposta 401 Unauthorized.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_servicos.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.validar_token_consultar_servico', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.validar_token_id_estabelecimento', return_value=False): # Validação do ID do estabelecimento falha
        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token-invalid-id',
            'token-user': 'valid-jwt-user-token'
        }
        response = client.post('/consultar-servicos', headers=headers)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou"

def test_consultar_servicos_token_id_estabelecimento_retorna_true_none(client):
    """
    Testa a falha quando validar_token_id_estabelecimento retorna (True, None),
    o que invalida a condição 'if valid_est and estabelecimento_id'.
    Espera-se uma resposta 401 Unauthorized.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_servicos.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.validar_token_consultar_servico', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.validar_token_id_estabelecimento', return_value=(True, None)): # ID do estabelecimento é None
        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token-id-none',
            'token-user': 'valid-jwt-user-token'
        }
        response = client.post('/consultar-servicos', headers=headers)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou"

def test_consultar_servicos_token_id_user_invalido_nao_tupla(client):
    """
    Testa a falha quando a validação do token do usuário falha
    (validar_token_id_user retorna um valor que não é uma tupla, ex: False).
    Espera-se uma resposta 401 Unauthorized.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_servicos.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.validar_token_consultar_servico', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.validar_token_id_estabelecimento', return_value=(True, "est_id_123")), \
         patch('project.app.controllers.API_Agendamentos.consultar_servicos.validar_token_id_user', return_value=False): # Validação do ID do usuário falha (não é tupla)
        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token-invalid-id'
        }
        response = client.post('/consultar-servicos', headers=headers)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou"