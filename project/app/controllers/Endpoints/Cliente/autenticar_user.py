from flask import Blueprint, request, jsonify
from ....services.Cliente.Sanetizar_dados.sanitizar_token_fernet import verificar_token_fernet
from ....services.Cliente.Sanetizar_dados.sanitizar_token_jwt import verificar_token_jwt
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_autenticar_user import validar_token_autenticar_user
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_ID_estabelecimento import validar_token_id_estabelecimento
from ....services.Cliente.Sanetizar_dados.sanitizar_email import verificar_email
from ....services.Cliente.Sanetizar_dados.sanitizar_senha import verificar_senha
from ....services.Cliente.Consulta_DataBase.Consultar_ID_User import consultar_id_user
from ....services.Cliente.Hashe_senha.Autendicar_senha import autenticar_senha
from ....services.Cliente.Gerar_Token_JWT.Gerar_JWT_IDUser import gerar_jwt_id_estabelecimento

autenticar_user_bp = Blueprint('autenticar_user', __name__, url_prefix='/api/autenticar_user')

@autenticar_user_bp.route('', methods=['POST'])
def autenticar_user():
    """
    Endpoint para autenticação de usuário do cliente.

    Espera receber:
    - Header 'Authorization' com token Fernet válido.
    - Cookie 'token_estabelecimento' com JWT do estabelecimento.
    - JSON no corpo com 'login' (email) e 'senha'.

    Fluxo:
    1. Valida presença dos dados obrigatórios.
    2. Valida tokens.
    3. Valida credenciais do usuário.
    4. Gera JWT do usuário autenticado e retorna em cookie httpOnly.

    Returns:
        200: Autenticação bem-sucedida, retorna token em cookie e no corpo.
        400: Dados inválidos.
        401: Falha de autenticação.
        411: Dados insuficientes.
    """
    authorization = request.headers.get('Authorization')
    token_estabelecimento = request.cookies.get('token_estabelecimento')

    if not (authorization and token_estabelecimento):
        return jsonify({
            "status": "error",
            "message": "Erro de autenticação"
        }), 401

    if not (verificar_token_fernet(authorization) and verificar_token_jwt(token_estabelecimento)):
        return jsonify({
            "status": "error",
            "message": "Erro de autenticação"
        }), 401

    if not validar_token_autenticar_user(authorization):
        return jsonify({
            "status": "error",
            "message": "Erro de autenticação"
        }), 401

    resultado = validar_token_id_estabelecimento(token_estabelecimento)
    if resultado is False:
        return jsonify({
            "status": "error",
            "message": "Erro de autenticação"
        }), 401

    _, estabelecimento_id = resultado
    data = request.get_json(silent=True) or {}
    login = data.get("login")
    senha = data.get("senha")

    if not (login and senha):
        return jsonify({
            "status": "error",
            "message": "Erro dados insuficientes"
        }), 411

    if not (verificar_email(login) and verificar_senha(senha)):
        return jsonify({
            "status": "error",
            "message": "Erro dados invalidos"
        }), 400

    consulta = consultar_id_user(estabelecimento_id, login)
    if consulta is False:
        return jsonify({
            "status": "error",
            "message": "Usuário não encontrado"
        }), 401

    _, user_id = consulta
    if not autenticar_senha(estabelecimento_id, user_id, senha):
        return jsonify({
            "status": "error",
            "message": "Erro ao autenticar user"
        }), 401

    jwt_token = gerar_jwt_id_estabelecimento(user_id)
    resposta = jsonify({
        "status": "success",
        "message": "User autenticado",
        "token": jwt_token
    })
    resposta.set_cookie(
        "token_user",
        jwt_token,
        httponly=True,
        secure=True,
        samesite="None",
        max_age=3600
    )
    return resposta, 200