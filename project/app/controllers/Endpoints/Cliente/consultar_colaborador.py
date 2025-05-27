from flask import Blueprint, request, jsonify
from ....services.Cliente.Sanetizar_dados.sanitizar_token_fernet import verificar_token_fernet
from ....services.Cliente.Sanetizar_dados.sanitizar_token_jwt import verificar_token_jwt
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_consultar_colaboradores import validar_token_consultar_colaborador
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_ID_estabelecimento import validar_token_id_estabelecimento
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_ID_user import validar_token_id_user
from ....services.Cliente.Consulta_DataBase.Consulta_colaboradores import consultar_colaboradores_por_estabelecimento

consultar_colaborador_bp = Blueprint('consultar_colaborador', __name__)

@consultar_colaborador_bp.route('/consultar-colaborador', methods=['POST'])
def consultar_colaborador():
    """
    Endpoint para consulta de colaboradores do estabelecimento.

    Espera receber:
    - Header 'Authorization' com token Fernet válido.
    - Cookies 'token_estabelecimento' e 'token_user' com JWTs válidos.

    Fluxo:
    1. Valida presença dos dados obrigatórios.
    2. Valida tokens.
    3. Valida credenciais do usuário e do estabelecimento.
    4. Consulta colaboradores no banco.

    Returns:
        200: Consulta realizada com sucesso.
        401: Falha de autenticação.
        404: Não foi possível localizar os dados.
    """
    auth = request.headers.get('Authorization')
    token_estabelecimento = request.cookies.get('token_estabelecimento')
    token_user = request.cookies.get('token_user')

    if not (auth and token_estabelecimento and token_user):
        return jsonify({"erro": "Autenticação falhou"}), 401

    if not (verificar_token_fernet(auth) and verificar_token_jwt(token_estabelecimento) and verificar_token_jwt(token_user)):
        return jsonify({"erro": "Autenticação falhou"}), 401

    if not validar_token_consultar_colaborador(auth):
        return jsonify({"erro": "Autenticação falhou"}), 401

    result_est = validar_token_id_estabelecimento(token_estabelecimento)
    if isinstance(result_est, tuple):
        valid_est, estabelecimento_id = result_est
    else:
        valid_est = result_est
        estabelecimento_id = None

    if not (valid_est and estabelecimento_id):
        return jsonify({"erro": "Autenticação falhou"}), 401

    result_user = validar_token_id_user(estabelecimento_id, token_user)
    if not isinstance(result_user, tuple):
        return jsonify({"erro": "Autenticação falhou"}), 401
    _, user_id = result_user

    result = consultar_colaboradores_por_estabelecimento(estabelecimento_id)
    if result:
        success, servicos_array = result
        if success:
            return jsonify({
                "message": "Requisição bem sucedida",
                "estabelecimento_id": estabelecimento_id,
                "user_id": user_id,
                "servicos": servicos_array
            }), 200
    return jsonify({
        "erro": "Não foi possível localizar os dados"
    }), 404