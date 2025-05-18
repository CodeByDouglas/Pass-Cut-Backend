import pytest
from unittest.mock import patch
from flask import Flask, json
from project.app.controllers.API_Agendamentos.criar_agendamento import criar_agendamento_bp

# filepath: project/app/controllers/API_Agendamentos/test_criar_agendamento.py

# Importa o blueprint do controller que será testado

@pytest.fixture
def app():
    """
    Fixture que cria e configura uma instância da aplicação Flask para os testes.
    Registra o blueprint 'criar_agendamento_bp' e ativa o modo de teste.
    """
    app = Flask(__name__)
    app.register_blueprint(criar_agendamento_bp) # Rota base definida no blueprint
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

# --- Testes para o endpoint /criar-agendamento ---

def test_criar_agendamento_sucesso(client):
    """
    Testa a criação de agendamento bem-sucedida.
    Todos os tokens são válidos, dados do payload são válidos,
    e a função 'agendar' retorna True.
    Espera-se uma resposta 200 OK.
    """
    with patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_token_fernet', return_value=True) as mock_v_fernet, \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_token_jwt', return_value=True) as mock_v_jwt, \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.validar_token_consultar_servico', return_value=True) as mock_v_token_serv, \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.validar_token_id_estabelecimento', return_value=(True, "est_id_1")) as mock_v_id_est, \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.validar_token_id_user', return_value=(True, "user_id_1")) as mock_v_id_user, \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_id_colaborador', return_value=True) as mock_v_id_colab, \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_horario_valido', return_value=True) as mock_v_horario, \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_data', return_value=True) as mock_v_data, \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_ids_servicos', return_value=True) as mock_v_ids_serv, \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.agendar', return_value=True) as mock_agendar:

        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token'
        }
        payload = {
            'colaborador_id': 'colab_123',
            'horario': '10:00',
            'data': '2024-07-20',
            'servicos': ['serv_A', 'serv_B']
        }
        response = client.post('/criar-agendamento', headers=headers, json=payload)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == "Agendamento criado com sucesso"
        assert data['estabelecimento_id'] == "est_id_1"
        assert data['user_id'] == "user_id_1"

        # Verifica chamadas dos mocks
        mock_v_fernet.assert_called_once_with('valid-fernet-token')
        assert mock_v_jwt.call_count == 2 # Para token_user e token_estabelecimento
        mock_v_token_serv.assert_called_once_with('valid-fernet-token') # Note: usando validar_token_consultar_servico conforme o código
        mock_v_id_est.assert_called_once_with('valid-jwt-est-token')
        mock_v_id_user.assert_called_once_with("est_id_1", 'valid-jwt-user-token')
        mock_v_id_colab.assert_called_once_with('colab_123')
        mock_v_horario.assert_called_once_with('10:00')
        mock_v_data.assert_called_once_with('2024-07-20')
        mock_v_ids_serv.assert_called_once_with(['serv_A', 'serv_B'])
        mock_agendar.assert_called_once_with("est_id_1", "user_id_1", ['serv_A', 'serv_B'], 'colab_123', '2024-07-20', '10:00')

@pytest.mark.parametrize("missing_header", ["auth", "token-estabelecimento", "token-user"])
def test_criar_agendamento_cabecalho_ausente(client, missing_header):
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
    payload = {'colaborador_id': 'c1', 'horario': 'h1', 'data': 'd1', 'servicos': ['s1']}

    response = client.post('/criar-agendamento', headers=headers, json=payload)
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['erro'] == "Erro de autenticação" # Mensagem genérica do último else

@pytest.mark.parametrize("mock_config", [
    {'target': 'project.app.controllers.API_Agendamentos.criar_agendamento.verificar_token_fernet', 'return_value': False},
    {'target': 'project.app.controllers.API_Agendamentos.criar_agendamento.verificar_token_jwt', 'side_effect': [False, True]}, # token_user falha
    {'target': 'project.app.controllers.API_Agendamentos.criar_agendamento.verificar_token_jwt', 'side_effect': [True, False]}, # token_estabelecimento falha
])
def test_criar_agendamento_falha_verificacao_token_inicial(client, mock_config):
    """
    Testa a falha quando a verificação inicial de um dos tokens (Fernet ou JWT) falha.
    Espera-se uma resposta 401 Unauthorized.
    """
    with patch(mock_config['target'], **{key: val for key, val in mock_config.items() if key != 'target'}):
        # Se verificar_token_jwt for mockado com side_effect, precisamos garantir que o outro mock de verificar_token_fernet ainda funcione
        # ou que o side_effect cubra todas as chamadas de verificar_token_jwt.
        # Para simplificar, se o target é verificar_token_jwt, o verificar_token_fernet é True.
        # Se o target é verificar_token_fernet, o verificar_token_jwt é True (ou não é chamado).
        patch_fernet = patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_token_fernet', return_value=True)
        patch_jwt = patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_token_jwt', return_value=True)

        if mock_config['target'] == 'project.app.controllers.API_Agendamentos.criar_agendamento.verificar_token_fernet':
            patch_jwt.start()
        else: # mock_config['target'] is verificar_token_jwt
            patch_fernet.start()


        headers = {'auth': 't1', 'token-estabelecimento': 't2', 'token-user': 't3'}
        payload = {'colaborador_id': 'c1', 'horario': 'h1', 'data': 'd1', 'servicos': ['s1']}
        response = client.post('/criar-agendamento', headers=headers, json=payload)
        
        if mock_config['target'] == 'project.app.controllers.API_Agendamentos.criar_agendamento.verificar_token_fernet':
            patch_jwt.stop()
        else:
            patch_fernet.stop()

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Erro de autenticação"


def test_criar_agendamento_falha_validar_token_servico(client):
    """
    Testa a falha quando validar_token_consultar_servico (token de API) retorna False.
    Espera-se uma resposta 401 Unauthorized.
    """
    with patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.validar_token_consultar_servico', return_value=False):
        headers = {'auth': 't1', 'token-estabelecimento': 't2', 'token-user': 't3'}
        payload = {'colaborador_id': 'c1', 'horario': 'h1', 'data': 'd1', 'servicos': ['s1']}
        response = client.post('/criar-agendamento', headers=headers, json=payload)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Erro de autenticação"

@pytest.mark.parametrize("id_est_return_val", [False, (False, None), ("not_a_tuple")])
def test_criar_agendamento_falha_validar_token_id_estabelecimento(client, id_est_return_val):
    """
    Testa a falha quando validar_token_id_estabelecimento retorna um valor inválido.
    Espera-se uma resposta 401 Unauthorized.
    """
    with patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.validar_token_consultar_servico', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.validar_token_id_estabelecimento', return_value=id_est_return_val):
        headers = {'auth': 't1', 'token-estabelecimento': 't2', 'token-user': 't3'}
        payload = {'colaborador_id': 'c1', 'horario': 'h1', 'data': 'd1', 'servicos': ['s1']}
        response = client.post('/criar-agendamento', headers=headers, json=payload)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Erro de autenticação"

@pytest.mark.parametrize("id_user_return_val", [False, (False, None), ("not_a_tuple")])
def test_criar_agendamento_falha_validar_token_id_user(client, id_user_return_val):
    """
    Testa a falha quando validar_token_id_user retorna um valor inválido.
    Espera-se uma resposta 401 Unauthorized.
    """
    with patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.validar_token_consultar_servico', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.validar_token_id_estabelecimento', return_value=(True, "est_id")), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.validar_token_id_user', return_value=id_user_return_val):
        headers = {'auth': 't1', 'token-estabelecimento': 't2', 'token-user': 't3'}
        payload = {'colaborador_id': 'c1', 'horario': 'h1', 'data': 'd1', 'servicos': ['s1']}
        response = client.post('/criar-agendamento', headers=headers, json=payload)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Erro de autenticação"

@pytest.mark.parametrize("bad_payload", [
    None, # Sem JSON
    {},   # JSON vazio
    {'horario': 'h1', 'data': 'd1', 'servicos': ['s1']}, # Falta colaborador_id
    {'colaborador_id': 'c1', 'data': 'd1', 'servicos': ['s1']}, # Falta horario
    {'colaborador_id': 'c1', 'horario': 'h1', 'servicos': ['s1']}, # Falta data
    {'colaborador_id': 'c1', 'horario': 'h1', 'data': 'd1'}, # Falta servicos
    {'colaborador_id': 'c1', 'horario': 'h1', 'data': 'd1', 'servicos': "nao_lista"}, # servicos não é lista
    {'colaborador_id': 'c1', 'horario': 'h1', 'data': 'd1', 'servicos': []}, # servicos lista vazia
])
def test_criar_agendamento_dados_insuficientes_payload(client, bad_payload):
    """
    Testa a falha quando o payload JSON é inválido ou dados obrigatórios estão ausentes.
    Espera-se uma resposta 400 com "Dados insuficientes para a consulta".
    """
    with patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.validar_token_consultar_servico', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.validar_token_id_estabelecimento', return_value=(True, "est_id")), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.validar_token_id_user', return_value=(True, "user_id")):
        headers = {'auth': 't1', 'token-estabelecimento': 't2', 'token-user': 't3'}
        
        if bad_payload is None:
            # Envia a string JSON "null" para simular um payload JSON nulo
            response = client.post('/criar-agendamento', headers=headers, data='null', content_type='application/json')
        else:
            response = client.post('/criar-agendamento', headers=headers, json=bad_payload)
            
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['erro'] == "Dados insuficientes para a consulta"

@pytest.mark.parametrize("validation_function_to_fail", [
    'project.app.controllers.API_Agendamentos.criar_agendamento.verificar_id_colaborador',
    'project.app.controllers.API_Agendamentos.criar_agendamento.verificar_horario_valido',
    'project.app.controllers.API_Agendamentos.criar_agendamento.verificar_data',
    'project.app.controllers.API_Agendamentos.criar_agendamento.verificar_ids_servicos',
])
def test_criar_agendamento_falha_validacao_dados(client, validation_function_to_fail):
    """
    Testa a falha quando uma das funções de validação de dados (colaborador, horario, data, servicos) retorna False.
    Espera-se uma resposta 400 com "Dados invalidos".
    """
    with patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.validar_token_consultar_servico', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.validar_token_id_estabelecimento', return_value=(True, "est_id")), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.validar_token_id_user', return_value=(True, "user_id")), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_id_colaborador', return_value=validation_function_to_fail != 'project.app.controllers.API_Agendamentos.criar_agendamento.verificar_id_colaborador'), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_horario_valido', return_value=validation_function_to_fail != 'project.app.controllers.API_Agendamentos.criar_agendamento.verificar_horario_valido'), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_data', return_value=validation_function_to_fail != 'project.app.controllers.API_Agendamentos.criar_agendamento.verificar_data'), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_ids_servicos', return_value=validation_function_to_fail != 'project.app.controllers.API_Agendamentos.criar_agendamento.verificar_ids_servicos'):

        # Garante que a função específica que está sendo testada para falhar retorne False
        patch(validation_function_to_fail, return_value=False).start()

        headers = {'auth': 't1', 'token-estabelecimento': 't2', 'token-user': 't3'}
        payload = {'colaborador_id': 'c1', 'horario': 'h1', 'data': 'd1', 'servicos': ['s1']}
        response = client.post('/criar-agendamento', headers=headers, json=payload)
        
        patch.stopall() # Para garantir que o patch específico seja parado

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['erro'] == "Dados invalidos"

@pytest.mark.parametrize("agendar_return, expected_status, expected_json", [
    ((False, "Erro interno"), 500, {"erro": "Erro interno ao processar o agendamento"}),
    ((False, "Horário indisponível"), 204, {"message": "Infelizmente o horário solicitado acabou de ser preenchido e não está mais disponível."}),
    ((False, "Outro erro especifico"), 400, {"erro": "Outro erro especifico"}),
    (None, 500, {"erro": "Erro desconhecido"}), # Caso de retorno não esperado (não é True nem tupla (False, msg))
    (False, 500, {"erro": "Erro desconhecido"}), # Caso de retorno não esperado
])
def test_criar_agendamento_falhas_funcao_agendar(client, agendar_return, expected_status, expected_json):
    """
    Testa diferentes cenários de falha da função 'agendar'.
    """
    with patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.validar_token_consultar_servico', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.validar_token_id_estabelecimento', return_value=(True, "est_id")), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.validar_token_id_user', return_value=(True, "user_id")), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_id_colaborador', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_horario_valido', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_data', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.verificar_ids_servicos', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.criar_agendamento.agendar', return_value=agendar_return):

        headers = {'auth': 't1', 'token-estabelecimento': 't2', 'token-user': 't3'}
        payload = {'colaborador_id': 'c1', 'horario': 'h1', 'data': 'd1', 'servicos': ['s1']}
        response = client.post('/criar-agendamento', headers=headers, json=payload)

        assert response.status_code == expected_status
        # Para 204, não há corpo JSON, então response.data será b''
        if expected_status == 204:
            assert not response.data # Verifica se o corpo está vazio
        else:
            data = json.loads(response.data)
            assert data == expected_json