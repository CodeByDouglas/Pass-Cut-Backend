from flask import Blueprint, request, jsonify
from ....services.Cliente.Sanetizar_dados.sanitizar_token_fernet import verificar_token_fernet
from ....services.Cliente.Sanetizar_dados.sanitizar_token_jwt import verificar_token_jwt
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_cancelar_agendamento import validar_token_cancelar_agendamento
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_ID_estabelecimento import validar_token_id_estabelecimento
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_ID_user import validar_token_id_user
from ....services.Cliente.Sanetizar_dados.sanitizar_id_agendamento import verificar_id_agendamento
from ....services.Cliente.Consulta_DataBase.Cancelar_agendamento import cancelar_agendamento_db

cancelar_agendamento_bp = Blueprint('cancelar_agendamento', __name__)

@cancelar_agendamento_bp.route('/cancelar-agendamento', methods=['POST'])
def cancelar_agendamento():
    """
    Endpoint para cancelamento de agendamento do cliente.

    Espera receber:
    - Header 'Authorization' com token Fernet válido.
    - Cookies 'token_estabelecimento' e 'token_user' com JWTs válidos.
    - JSON no corpo com 'agendamento_id'.

    Fluxo:
    1. Valida presença dos dados obrigatórios.
    2. Valida tokens.
    3. Valida credenciais do usuário e do estabelecimento.
    4. Valida o formato do agendamento_id.
    5. Cancela o agendamento no banco.

    Returns:
        200: Cancelamento bem-sucedido.
        400: Dados insuficientes ou inválidos.
        401: Falha de autenticação.
        500: Erro interno ao cancelar.
    """
    auth = request.headers.get('Authorization')
    token_estabelecimento = request.cookies.get('token_estabelecimento')
    token_user = request.cookies.get('token_user')

    if not (auth and token_estabelecimento and token_user):
        return jsonify({"erro": "Autenticação falhou"}), 401

    if not (verificar_token_fernet(auth) and verificar_token_jwt(token_estabelecimento) and verificar_token_jwt(token_user)):
        return jsonify({"erro": "Autenticação falhou"}), 401

    if not validar_token_cancelar_agendamento(auth):
        return jsonify({"erro": "Autenticação falhou"}), 401

    result_est = validar_token_id_estabelecimento(token_estabelecimento)
    if isinstance(result_est, tuple):
        valid_est, estabelecimento_id = result_est
    else:
        valid_est = result_est
        estabelecimento_id = None

    if not (valid_est and estabelecimento_id):
        return jsonify({"erro": "Autenticação falhou"}), 401

    valid_user = validar_token_id_user(estabelecimento_id, token_user)
    if not (isinstance(valid_user, tuple) and valid_user[0]):
        return jsonify({"erro": "Autenticação falhou - erro no user"}), 401

    _, user_id = valid_user

    req_data = request.get_json(silent=True) or {}
    if not (req_data and isinstance(req_data, dict)):
        return jsonify({"erro": "Dados insuficientes"}), 411

    agendamento_id = req_data.get('agendamento_id')
    if not agendamento_id:
        return jsonify({"erro": "Dados insuficientes"}), 411

    if not verificar_id_agendamento(agendamento_id):
        return jsonify({"erro": "Dados invalidos: agendamento_id inválido"}), 400

    if cancelar_agendamento_db(agendamento_id, estabelecimento_id, user_id):
        return jsonify({"message": "Agendamento cancelado com sucesso"}), 200
    else:
        return jsonify({"erro": "Não foi possível cancelar o agendamento. Erro interno."}), 500