import pytest
from unittest.mock import patch
from flask import Flask, json
import datetime
from project.app.controllers.API_Agendamentos.consultar_horarios import consultar_horarios_bp

# filepath: project/app/controllers/API_Agendamentos/test_consultar_horarios.py

# Importa o blueprint do controller que será testado

@pytest.fixture
def app():
    """
    Fixture que cria e configura uma instância da aplicação Flask para os testes.
    Registra o blueprint 'consultar_horarios_bp' e ativa o modo de teste.
    """
    app = Flask(__name__)
    app.register_blueprint(consultar_horarios_bp) # Rota base definida no blueprint
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

# --- Testes para o endpoint /consultar-horarios ---

def test_consultar_horarios_sucesso_com_horarios(client):
    """
    Testa o cenário de sucesso onde todos os tokens e dados são válidos,
    e horários disponíveis são retornados.
    Espera-se uma resposta 200 OK com a lista de horários formatados.
    """
    horarios_mock = [datetime.time(9, 0), datetime.time(10, 30), datetime.time(14, 15)]
    with patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_fernet', return_value=True) as mock_v_fernet, \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_jwt', return_value=True) as mock_v_jwt, \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_consultar_horarios', return_value=True) as mock_v_token_hor, \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_id_estabelecimento', return_value=(True, "est_id_abc")) as mock_v_id_est, \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_id_user', return_value=(True, "user_id_xyz")) as mock_v_id_user, \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_id_colaborador', return_value=True) as mock_v_id_colab, \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_data', return_value=True) as mock_v_data, \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_ids_servicos', return_value=True) as mock_v_ids_serv, \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.consultar_horarios_agendamento', return_value=(True, horarios_mock)) as mock_cons_hor:

        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token'
        }
        payload = {
            'servicos': ["serv1", "serv2"],
            'colaborador-id': "colab_1",
            'data': "2024-01-10"
        }
        response = client.post('/consultar-horarios', headers=headers, json=payload)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == "Requisição bem sucedida"
        assert data['estabelecimento_id'] == "est_id_abc"
        assert data['user_id'] == "user_id_xyz"
        assert data['horarios'] == ["09:00:00", "10:30:00", "14:15:00"]

        # Verifica chamadas dos mocks
        mock_v_fernet.assert_called_once_with('valid-fernet-token')
        assert mock_v_jwt.call_count == 2
        mock_v_token_hor.assert_called_once_with('valid-fernet-token')
        mock_v_id_est.assert_called_once_with('valid-jwt-est-token')
        mock_v_id_user.assert_called_once_with("est_id_abc", 'valid-jwt-user-token')
        mock_v_id_colab.assert_called_once_with("colab_1")
        mock_v_data.assert_called_once_with("2024-01-10")
        mock_v_ids_serv.assert_called_once_with(["serv1", "serv2"])
        mock_cons_hor.assert_called_once_with("est_id_abc", "colab_1", "2024-01-10", ["serv1", "serv2"])

def test_consultar_horarios_sucesso_nenhum_horario_disponivel(client):
    """
    Testa o cenário de sucesso onde todos os tokens e dados são válidos,
    mas não há horários disponíveis (retorna [None]).
    Espera-se uma resposta 200 OK com a mensagem apropriada.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_consultar_horarios', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_id_estabelecimento', return_value=(True, "est_id_abc")), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_id_user', return_value=(True, "user_id_xyz")), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_id_colaborador', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_data', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_ids_servicos', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.consultar_horarios_agendamento', return_value=(True, [None])):

        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token'
        }
        payload = {
            'servicos': ["serv1"],
            'colaborador-id': "colab_1",
            'data': "2024-01-10"
        }
        response = client.post('/consultar-horarios', headers=headers, json=payload)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == "Nenhum horário disponível para essa data."

@pytest.mark.parametrize("missing_header", ["auth", "token-estabelecimento", "token-user"])
def test_consultar_horarios_cabecalhos_ausentes(client, missing_header):
    """
    Testa a falha quando um dos cabeçalhos obrigatórios está ausente.
    Espera-se uma resposta 401 com mensagem específica.
    """
    headers = {
        'auth': 'valid-fernet-token',
        'token-estabelecimento': 'valid-jwt-est-token',
        'token-user': 'valid-jwt-user-token'
    }
    del headers[missing_header]
    payload = {'servicos': ["s1"], 'colaborador-id': "c1", 'data': "d1"}

    response = client.post('/consultar-horarios', headers=headers, json=payload)
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['erro'] == "Autenticação falhou - cabeçalhos não encontrados"

def test_consultar_horarios_token_fernet_invalido(client):
    """
    Testa a falha quando o token Fernet ('auth') é inválido.
    Espera-se uma resposta 401 com mensagem específica.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_fernet', return_value=False):
        headers = {'auth': 'invalid', 'token-estabelecimento': 'valid', 'token-user': 'valid'}
        payload = {'servicos': ["s1"], 'colaborador-id': "c1", 'data': "d1"}
        response = client.post('/consultar-horarios', headers=headers, json=payload)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou - erro na verificação dos tokens"

@pytest.mark.parametrize("jwt_est_valid, jwt_user_valid", [(False, True), (True, False)])
def test_consultar_horarios_token_jwt_invalido(client, jwt_est_valid, jwt_user_valid):
    """
    Testa a falha quando um dos tokens JWT é inválido.
    Espera-se uma resposta 401 com mensagem específica.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_jwt', side_effect=[jwt_est_valid, jwt_user_valid]):
        headers = {'auth': 'valid', 'token-estabelecimento': 'jwt1', 'token-user': 'jwt2'}
        payload = {'servicos': ["s1"], 'colaborador-id': "c1", 'data': "d1"}
        response = client.post('/consultar-horarios', headers=headers, json=payload)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou - erro na verificação dos tokens"

def test_consultar_horarios_token_api_invalido(client):
    """
    Testa a falha quando o token 'auth' não é válido para consultar horários.
    Espera-se uma resposta 401 com mensagem específica.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_consultar_horarios', return_value=False):
        headers = {'auth': 'valid', 'token-estabelecimento': 'valid', 'token-user': 'valid'}
        payload = {'servicos': ["s1"], 'colaborador-id': "c1", 'data': "d1"}
        response = client.post('/consultar-horarios', headers=headers, json=payload)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou - erro no token da API"

@pytest.mark.parametrize("id_est_return_val", [False, (True, None), (False, "some_id")]) # (False, "some_id") para cobrir o 'else'
def test_consultar_horarios_token_id_estabelecimento_invalido(client, id_est_return_val):
    """
    Testa a falha quando a validação do token do estabelecimento falha.
    Espera-se uma resposta 401 com mensagem específica.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_consultar_horarios', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_id_estabelecimento', return_value=id_est_return_val):
        headers = {'auth': 'valid', 'token-estabelecimento': 'invalid_est_token', 'token-user': 'valid'}
        payload = {'servicos': ["s1"], 'colaborador-id': "c1", 'data': "d1"}
        response = client.post('/consultar-horarios', headers=headers, json=payload)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou - erro ao validar token estabelecimento"

def test_consultar_horarios_token_id_user_invalido(client):
    """
    Testa a falha quando a validação do token do usuário falha (não retorna tupla).
    Espera-se uma resposta 401 com mensagem específica.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_consultar_horarios', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_id_estabelecimento', return_value=(True, "est_id")), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_id_user', return_value=False): # Falha na validação do user
        headers = {'auth': 'valid', 'token-estabelecimento': 'valid', 'token-user': 'invalid_user_token'}
        payload = {'servicos': ["s1"], 'colaborador-id': "c1", 'data': "d1"}
        response = client.post('/consultar-horarios', headers=headers, json=payload)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou - erro no user"

@pytest.mark.parametrize("bad_payload, expected_status, expected_message", [
    (None, 400, "Dados insuficientes"), # JSON não enviado
    ([], 400, "Dados insuficientes"),   # JSON é lista, não dict
    ({}, 400, "Dados insuficientes"),   # JSON dict vazio
    ({'colaborador-id': "c1", 'data': "d1"}, 400, "Dados insuficientes"), # Falta 'servicos'
    ({'servicos': ["s1"], 'data': "d1"}, 400, "Dados insuficientes"),    # Falta 'colaborador-id'
    ({'servicos': ["s1"], 'colaborador-id': "c1"}, 400, "Dados insuficientes"), # Falta 'data'
    ({'servicos': "nao_lista", 'colaborador-id': "c1", 'data': "d1"}, 400, "Dados insuficientes"), # 'servicos' não é lista
])
def test_consultar_horarios_dados_insuficientes_payload(client, bad_payload, expected_status, expected_message):
    """
    Testa a falha quando o payload JSON é inválido ou dados obrigatórios estão ausentes.
    Espera-se uma resposta 400 com mensagem "Dados insuficientes".
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_consultar_horarios', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_id_estabelecimento', return_value=(True, "est_id")), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_id_user', return_value=(True, "user_id")):
        headers = {'auth': 'valid', 'token-estabelecimento': 'valid', 'token-user': 'valid'}
        
        if bad_payload is None:
            # Envia a string JSON "null" para simular um payload JSON nulo
            response = client.post('/consultar-horarios', headers=headers, data='null', content_type='application/json')
        else:
            response = client.post('/consultar-horarios', headers=headers, json=bad_payload)
        
        assert response.status_code == expected_status
        data = json.loads(response.data)
        assert data['erro'] == expected_message

def test_consultar_horarios_id_colaborador_invalido(client):
    """
    Testa a falha quando 'colaborador-id' é inválido.
    Espera-se uma resposta 400 com mensagem específica.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_consultar_horarios', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_id_estabelecimento', return_value=(True, "est_id")), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_id_user', return_value=(True, "user_id")), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_id_colaborador', return_value=False): # ID Colaborador inválido
        headers = {'auth': 'valid', 'token-estabelecimento': 'valid', 'token-user': 'valid'}
        payload = {'servicos': ["s1"], 'colaborador-id': "invalid_colab", 'data': "2024-01-01"}
        response = client.post('/consultar-horarios', headers=headers, json=payload)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['erro'] == "Dados invalidos: colaborador_id inválido"

def test_consultar_horarios_data_invalida(client):
    """
    Testa a falha quando 'data' é inválida.
    Espera-se uma resposta 400 com mensagem específica.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_consultar_horarios', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_id_estabelecimento', return_value=(True, "est_id")), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_id_user', return_value=(True, "user_id")), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_id_colaborador', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_data', return_value=False): # Data inválida
        headers = {'auth': 'valid', 'token-estabelecimento': 'valid', 'token-user': 'valid'}
        payload = {'servicos': ["s1"], 'colaborador-id': "c1", 'data': "invalid_date"}
        response = client.post('/consultar-horarios', headers=headers, json=payload)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['erro'] == "Dados invalidos: data inválida"

def test_consultar_horarios_ids_servicos_invalidos(client):
    """
    Testa a falha quando 'servicos' contém IDs inválidos.
    Espera-se uma resposta 400 com mensagem específica.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_consultar_horarios', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_id_estabelecimento', return_value=(True, "est_id")), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_id_user', return_value=(True, "user_id")), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_id_colaborador', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_data', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_ids_servicos', return_value=False): # IDs de serviço inválidos
        headers = {'auth': 'valid', 'token-estabelecimento': 'valid', 'token-user': 'valid'}
        payload = {'servicos': ["invalid_serv"], 'colaborador-id': "c1", 'data': "2024-01-01"}
        response = client.post('/consultar-horarios', headers=headers, json=payload)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['erro'] == "Dados invalidos: ids de serviço inválidos"

def test_consultar_horarios_erro_interno_consulta_db(client):
    """
    Testa a falha quando a consulta ao banco de dados (consultar_horarios_agendamento) retorna False.
    Espera-se uma resposta 501 com mensagem específica.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_consultar_horarios', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_id_estabelecimento', return_value=(True, "est_id")), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.validar_token_id_user', return_value=(True, "user_id")), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_id_colaborador', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_data', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.verificar_ids_servicos', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_horarios.consultar_horarios_agendamento', return_value=False): # Erro na consulta DB
        headers = {'auth': 'valid', 'token-estabelecimento': 'valid', 'token-user': 'valid'}
        payload = {'servicos': ["s1"], 'colaborador-id': "c1", 'data': "2024-01-01"}
        response = client.post('/consultar-horarios', headers=headers, json=payload)
        assert response.status_code == 501
        data = json.loads(response.data)
        assert data['erro'] == "Erro interno ao processar solicitação"