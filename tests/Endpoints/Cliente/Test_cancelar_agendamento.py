import pytest
from unittest.mock import patch
from flask import Flask, json
from project.app.controllers.API_Agendamentos.cancelar_agendamento import cancelar_agendamento_bp

# filepath: project/app/controllers/API_Agendamentos/test_cancelar_agendamento.py

# Importa o blueprint do controller que será testado

@pytest.fixture
def app():
    """
    Fixture que cria e configura uma instância da aplicação Flask para os testes.
    Registra o blueprint 'cancelar_agendamento_bp' e ativa o modo de teste.
    """
    app = Flask(__name__)
    app.register_blueprint(cancelar_agendamento_bp) # Rota base definida no blueprint
    app.config['TESTING'] = True
    app.config['DEBUG'] = False # Desabilitar debug para não interferir nos testes de erro
    return app

@pytest.fixture
def client(app):
    """
    Fixture que cria um cliente de teste para fazer requisições HTTP à aplicação.
    Utiliza a aplicação Flask configurada pela fixture 'app'.
    """
    return app.test_client()

# --- Testes para o endpoint /cancelar-agendamento ---

def test_cancelar_agendamento_sucesso(client):
    """
    Testa o cancelamento de agendamento bem-sucedido.
    Todos os tokens são válidos, 'agendamento_id' é fornecido e válido,
    e o cancelamento no banco de dados ocorre com sucesso.
    Espera-se uma resposta 200 OK.
    """
    with patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.verificar_token_fernet', return_value=True) as mock_ver_fernet, \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.verificar_token_jwt', return_value=True) as mock_ver_jwt, \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.validar_token_cancelar_agendamento', return_value=True) as mock_val_token_cancel, \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.validar_token_id_estabelecimento', return_value=(True, "est_id_123")) as mock_val_id_est, \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.validar_token_id_user', return_value=(True, "user_id_456")) as mock_val_id_user, \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.verificar_id_agendamento', return_value=True) as mock_ver_id_ag, \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.cancelar_agendamento_db', return_value=True) as mock_cancel_db:

        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token'
        }
        payload = {'agendamento_id': 'ag_12345'}
        response = client.post('/cancelar-agendamento', headers=headers, json=payload)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == "Agendamento cancelado com sucesso"

        # Verifica se os mocks foram chamados
        mock_ver_fernet.assert_called_once_with('valid-fernet-token')
        assert mock_ver_jwt.call_count == 2
        mock_val_token_cancel.assert_called_once_with('valid-fernet-token')
        mock_val_id_est.assert_called_once_with('valid-jwt-est-token')
        mock_val_id_user.assert_called_once_with("est_id_123", 'valid-jwt-user-token')
        mock_ver_id_ag.assert_called_once_with('ag_12345')
        mock_cancel_db.assert_called_once_with('ag_12345', "est_id_123", "user_id_456")

@pytest.mark.parametrize("missing_header", ["auth", "token-estabelecimento", "token-user"])
def test_cancelar_agendamento_cabecalho_ausente(client, missing_header):
    """
    Testa a falha quando um dos cabeçalhos obrigatórios está ausente.
    Espera-se uma resposta 401 Unauthorized.
    """
    headers = {
        'auth': 'valid-fernet-token',
        'token-estabelecimento': 'valid-jwt-est-token',
        'token-user': 'valid-jwt-user-token'
    }
    del headers[missing_header]
    payload = {'agendamento_id': 'ag_12345'}

    response = client.post('/cancelar-agendamento', headers=headers, json=payload)
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['erro'] == "Autenticação falhou"

def test_cancelar_agendamento_token_fernet_invalido(client):
    """
    Testa a falha quando o token Fernet ('auth') é inválido.
    Espera-se uma resposta 401 Unauthorized.
    """
    with patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.verificar_token_fernet', return_value=False):
        headers = {
            'auth': 'invalid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token'
        }
        payload = {'agendamento_id': 'ag_12345'}
        response = client.post('/cancelar-agendamento', headers=headers, json=payload)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou"

@pytest.mark.parametrize("jwt_est_valid, jwt_user_valid", [(False, True), (True, False)])
def test_cancelar_agendamento_token_jwt_invalido(client, jwt_est_valid, jwt_user_valid):
    """
    Testa a falha quando um dos tokens JWT é inválido.
    Espera-se uma resposta 401 Unauthorized.
    """
    with patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.verificar_token_jwt', side_effect=[jwt_est_valid, jwt_user_valid]):
        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'jwt-est-token',
            'token-user': 'jwt-user-token'
        }
        payload = {'agendamento_id': 'ag_12345'}
        response = client.post('/cancelar-agendamento', headers=headers, json=payload)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou"

def test_cancelar_agendamento_token_auth_nao_valido_para_cancelar(client):
    """
    Testa a falha quando o token 'auth' não é válido para cancelamento.
    Espera-se uma resposta 401 Unauthorized.
    """
    with patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.validar_token_cancelar_agendamento', return_value=False):
        headers = {
            'auth': 'valid-fernet-token-but-not-for-cancel',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token'
        }
        payload = {'agendamento_id': 'ag_12345'}
        response = client.post('/cancelar-agendamento', headers=headers, json=payload)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou"

@pytest.mark.parametrize("id_est_return_val", [False, (True, None), (False, None)])
def test_cancelar_agendamento_token_id_estabelecimento_invalido(client, id_est_return_val):
    """
    Testa a falha quando a validação do token do estabelecimento falha.
    Casos: retorna False, (True, None), (False, None).
    Espera-se uma resposta 401 Unauthorized.
    """
    with patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.validar_token_cancelar_agendamento', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.validar_token_id_estabelecimento', return_value=id_est_return_val):
        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token-invalid-id',
            'token-user': 'valid-jwt-user-token'
        }
        payload = {'agendamento_id': 'ag_12345'}
        response = client.post('/cancelar-agendamento', headers=headers, json=payload)
        assert response.status_code == 401 # O endpoint retorna 401 genérico aqui, não o "erro no user"
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou"


def test_cancelar_agendamento_token_id_user_invalido(client):
    """
    Testa a falha quando a validação do token do usuário falha (não retorna tupla).
    Espera-se uma resposta 401 Unauthorized com mensagem específica "erro no user".
    """
    with patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.validar_token_cancelar_agendamento', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.validar_token_id_estabelecimento', return_value=(True, "est_id_123")), \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.validar_token_id_user', return_value=False): # Falha na validação do user
        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token-invalid-id'
        }
        payload = {'agendamento_id': 'ag_12345'}
        response = client.post('/cancelar-agendamento', headers=headers, json=payload)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou - erro no user"

@pytest.mark.parametrize("bad_payload", [None, [], {}, {"other_key": "value"}, {"agendamento_id": None}, {"agendamento_id": ""}])
def test_cancelar_agendamento_dados_insuficientes_ou_invalidos_payload(client, bad_payload):
        """
        Testa a falha quando o payload JSON é inválido, não é um dicionário,
        ou 'agendamento_id' está ausente/vazio.
        Espera-se uma resposta 411 "Dados insuficientes".
        """
        with patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.verificar_token_fernet', return_value=True), \
             patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.verificar_token_jwt', return_value=True), \
             patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.validar_token_cancelar_agendamento', return_value=True), \
             patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.validar_token_id_estabelecimento', return_value=(True, "est_id_123")), \
             patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.validar_token_id_user', return_value=(True, "user_id_456")):
            headers = {
                'auth': 'valid-fernet-token',
                'token-estabelecimento': 'valid-jwt-est-token',
                'token-user': 'valid-jwt-user-token'
            }
            if bad_payload is None:
                # Envia a string JSON "null" para simular um payload JSON nulo
                response = client.post('/cancelar-agendamento', headers=headers, data='null', content_type='application/json')
            else:
                response = client.post('/cancelar-agendamento', headers=headers, json=bad_payload)
            
            assert response.status_code == 411
            data = json.loads(response.data)
            assert data['erro'] == "Dados insuficientes"

def test_cancelar_agendamento_id_agendamento_formato_invalido(client):
    """
    Testa a falha quando 'agendamento_id' tem um formato inválido.
    Espera-se uma resposta 400 "Dados invalidos: agendamento_id inválido".
    """
    with patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.validar_token_cancelar_agendamento', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.validar_token_id_estabelecimento', return_value=(True, "est_id_123")), \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.validar_token_id_user', return_value=(True, "user_id_456")), \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.verificar_id_agendamento', return_value=False): # Formato inválido
        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token'
        }
        payload = {'agendamento_id': 'formato_invalido_id'}
        response = client.post('/cancelar-agendamento', headers=headers, json=payload)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['erro'] == "Dados invalidos: agendamento_id inválido"

def test_cancelar_agendamento_falha_no_banco(client):
    """
    Testa a falha quando o cancelamento no banco de dados (cancelar_agendamento_db) retorna False.
    Espera-se uma resposta 500 "Erro interno".
    """
    with patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.validar_token_cancelar_agendamento', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.validar_token_id_estabelecimento', return_value=(True, "est_id_123")), \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.validar_token_id_user', return_value=(True, "user_id_456")), \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.verificar_id_agendamento', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.cancelar_agendamento.cancelar_agendamento_db', return_value=False): # Falha no DB
        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token'
        }
        payload = {'agendamento_id': 'ag_12345_db_fail'}
        response = client.post('/cancelar-agendamento', headers=headers, json=payload)
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['erro'] == "Não foi possível cancelar o agendamento. Erro interno."