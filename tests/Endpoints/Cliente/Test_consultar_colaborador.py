import pytest
from unittest.mock import patch
from flask import Flask, json
from project.app.controllers.API_Agendamentos.consultar_colaborador import consultar_colaborador_bp

# filepath: project/app/controllers/API_Agendamentos/test_consultar_colaborador.py

# Importa o blueprint do controller que será testado
# Usando import absoluto conforme a estrutura do projeto e as diretrizes

@pytest.fixture
def app():
    """
    Fixture que cria e configura uma instância da aplicação Flask para os testes.
    Registra o blueprint 'consultar_colaborador_bp' e ativa o modo de teste.
    """
    app = Flask(__name__)
    app.register_blueprint(consultar_colaborador_bp) # O endpoint está em /consultar-colaborador
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

# --- Testes para o endpoint /consultar-colaborador ---

def test_consultar_colaborador_sucesso_com_colaboradores(client):
    """
    Testa o cenário de sucesso onde todos os tokens são válidos,
    o usuário é autenticado e colaboradores são encontrados para o estabelecimento.
    Espera-se uma resposta 200 OK com a lista de colaboradores.
    """
    # Mock das funções de serviço para simular um cenário de sucesso
    with patch('project.app.controllers.API_Agendamentos.consultar_colaborador.verificar_token_fernet', return_value=True) as mock_ver_fernet, \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.verificar_token_jwt', return_value=True) as mock_ver_jwt, \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.validar_token_consultar_colaborador', return_value=True) as mock_val_token_colab, \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.validar_token_id_estabelecimento', return_value=(True, "est_id_789")) as mock_val_id_est, \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.validar_token_id_user', return_value=(True, "user_id_101")) as mock_val_id_user, \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.consultar_colaboradores_por_estabelecimento', return_value=(True, [{"id": 1, "nome": "Colaborador Alfa"}, {"id": 2, "nome": "Colaborador Beta"}])) as mock_cons_colab:

        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token'
        }
        # O endpoint é POST, mas não espera um corpo JSON para esta lógica específica
        response = client.post('/consultar-colaborador', headers=headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == "Requisição bem sucedida"
        assert data['estabelecimento_id'] == "est_id_789"
        assert data['user_id'] == "user_id_101"
        # A chave no JSON de resposta é 'servicos' conforme o código do endpoint,
        # mesmo que estejamos consultando 'colaboradores'. Isso pode ser um bug ou intencional.
        # Se for um bug, o teste falhará aqui e o código do endpoint precisará ser corrigido para 'colaboradores'.
        # Assumindo que a chave 'servicos' é intencional por ora, conforme o código fornecido.
        assert "servicos" in data # Verificando a chave conforme o código do endpoint
        assert len(data['servicos']) == 2
        assert data['servicos'][0]['nome'] == "Colaborador Alfa"


        # Verifica se os mocks foram chamados como esperado
        mock_ver_fernet.assert_called_once_with('valid-fernet-token')
        assert mock_ver_jwt.call_count == 2 # Chamado para token-estabelecimento e token-user
        mock_val_token_colab.assert_called_once_with('valid-fernet-token')
        mock_val_id_est.assert_called_once_with('valid-jwt-est-token')
        mock_val_id_user.assert_called_once_with("est_id_789", 'valid-jwt-user-token')
        mock_cons_colab.assert_called_once_with("est_id_789")

def test_consultar_colaborador_sucesso_sem_colaboradores_cadastrados(client):
    """
    Testa o cenário de sucesso onde todos os tokens são válidos,
    mas o estabelecimento não possui colaboradores cadastrados (lista vazia).
    Espera-se uma resposta 200 OK com uma lista de 'servicos' (colaboradores) vazia.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_colaborador.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.validar_token_consultar_colaborador', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.validar_token_id_estabelecimento', return_value=(True, "est_id_789")), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.validar_token_id_user', return_value=(True, "user_id_101")), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.consultar_colaboradores_por_estabelecimento', return_value=(True, [])): # Lista de colaboradores vazia

        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token'
        }
        response = client.post('/consultar-colaborador', headers=headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == "Requisição bem sucedida"
        assert data['estabelecimento_id'] == "est_id_789"
        assert data['user_id'] == "user_id_101"
        assert data['servicos'] == [] # Chave 'servicos' conforme o código

def test_consultar_colaborador_falha_consulta_db(client):
    """
    Testa o cenário onde a consulta ao banco de dados por colaboradores falha
    (retorna (False, ...)).
    Espera-se uma resposta 404 Not Found.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_colaborador.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.validar_token_consultar_colaborador', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.validar_token_id_estabelecimento', return_value=(True, "est_id_789")), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.validar_token_id_user', return_value=(True, "user_id_101")), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.consultar_colaboradores_por_estabelecimento', return_value=(False, [])): # Falha na consulta

        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token'
        }
        response = client.post('/consultar-colaborador', headers=headers)

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['erro'] == "não foi possível localizar os dados"

def test_consultar_colaborador_falha_consulta_db_retorna_none(client):
    """
    Testa o cenário onde a consulta ao banco de dados por colaboradores retorna None.
    Espera-se uma resposta 404 Not Found.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_colaborador.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.validar_token_consultar_colaborador', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.validar_token_id_estabelecimento', return_value=(True, "est_id_789")), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.validar_token_id_user', return_value=(True, "user_id_101")), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.consultar_colaboradores_por_estabelecimento', return_value=None): # Consulta retorna None

        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token'
        }
        response = client.post('/consultar-colaborador', headers=headers)

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['erro'] == "não foi possível localizar os dados"


@pytest.mark.parametrize("missing_header", ["auth", "token-estabelecimento", "token-user"])
def test_consultar_colaborador_cabecalho_ausente(client, missing_header):
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

    response = client.post('/consultar-colaborador', headers=headers)
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['erro'] == "Autenticação falhou"

def test_consultar_colaborador_token_fernet_invalido(client):
    """
    Testa a falha quando o token Fernet ('auth') é inválido.
    Espera-se uma resposta 401 Unauthorized.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_colaborador.verificar_token_fernet', return_value=False):
        headers = {
            'auth': 'invalid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token'
        }
        response = client.post('/consultar-colaborador', headers=headers)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou"

def test_consultar_colaborador_token_jwt_estabelecimento_invalido(client):
    """
    Testa a falha quando o token JWT do estabelecimento é inválido.
    Espera-se uma resposta 401 Unauthorized.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_colaborador.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.verificar_token_jwt', side_effect=[False, True]): # Primeiro JWT (est) é inválido
        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'invalid-jwt-est-token',
            'token-user': 'valid-jwt-user-token'
        }
        response = client.post('/consultar-colaborador', headers=headers)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou"

def test_consultar_colaborador_token_jwt_user_invalido(client):
    """
    Testa a falha quando o token JWT do usuário é inválido.
    Espera-se uma resposta 401 Unauthorized.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_colaborador.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.verificar_token_jwt', side_effect=[True, False]): # Segundo JWT (user) é inválido
        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'invalid-jwt-user-token'
        }
        response = client.post('/consultar-colaborador', headers=headers)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou"

def test_consultar_colaborador_token_auth_nao_valido_para_colaborador(client):
    """
    Testa a falha quando o token 'auth' não é válido para a consulta de colaboradores.
    Espera-se uma resposta 401 Unauthorized.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_colaborador.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.validar_token_consultar_colaborador', return_value=False): # Token auth inválido para colaborador
        headers = {
            'auth': 'valid-fernet-token-but-not-for-colab',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token'
        }
        response = client.post('/consultar-colaborador', headers=headers)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou"

@pytest.mark.parametrize("id_est_return_val", [False, (True, None), (False, None)])
def test_consultar_colaborador_token_id_estabelecimento_invalido(client, id_est_return_val):
    """
    Testa a falha quando a validação do token do estabelecimento falha
    (validar_token_id_estabelecimento retorna False, (True, None) ou (False, None)).
    Espera-se uma resposta 401 Unauthorized.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_colaborador.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.validar_token_consultar_colaborador', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.validar_token_id_estabelecimento', return_value=id_est_return_val): # Validação do ID do estabelecimento falha
        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token-invalid-id',
            'token-user': 'valid-jwt-user-token'
        }
        response = client.post('/consultar-colaborador', headers=headers)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou"


def test_consultar_colaborador_token_id_user_invalido_nao_tupla(client):
    """
    Testa a falha quando a validação do token do usuário falha
    (validar_token_id_user retorna um valor que não é uma tupla, ex: False).
    Espera-se uma resposta 401 Unauthorized.
    """
    with patch('project.app.controllers.API_Agendamentos.consultar_colaborador.verificar_token_fernet', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.verificar_token_jwt', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.validar_token_consultar_colaborador', return_value=True), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.validar_token_id_estabelecimento', return_value=(True, "est_id_789")), \
         patch('project.app.controllers.API_Agendamentos.consultar_colaborador.validar_token_id_user', return_value=False): # Validação do ID do usuário falha (não é tupla)
        headers = {
            'auth': 'valid-fernet-token',
            'token-estabelecimento': 'valid-jwt-est-token',
            'token-user': 'valid-jwt-user-token-invalid-id'
        }
        response = client.post('/consultar-colaborador', headers=headers)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['erro'] == "Autenticação falhou"