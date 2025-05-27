from flask import Blueprint, request, jsonify
from ....services.Cliente.Sanetizar_dados.sanitizar_token_fernet import verificar_token_fernet
from ....services.Cliente.Sanetizar_dados.sanitizar_token_jwt import verificar_token_jwt
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_consulta_agendamentos import validar_token_consultar_agendamentos
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_ID_estabelecimento import validar_token_id_estabelecimento
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_ID_user import validar_token_id_user
from ....services.Cliente.Consulta_DataBase.Consultar_agendamentos_no_DB import consultar_agendamentos_por_estabelecimento_cliente_status

consultar_agendamentos_bp = Blueprint('consultar_agendamentos', __name__, url_prefix='/api/consultar_agendamentos')

@consultar_agendamentos_bp.route('', methods=['POST'])
def consultar_agendamentos():
    """
    Endpoint para consulta de agendamentos do cliente.

    Espera receber:
    - Header 'Authorization' com token Fernet válido.
    - Cookies 'token_estabelecimento' e 'token_user' com JWTs válidos.
    - JSON no corpo com 'type' ("ativos" ou "historico").

    Fluxo:
    1. Valida presença dos dados obrigatórios.
    2. Valida tokens.
    3. Valida tipo de consulta.
    4. Consulta agendamentos no banco.

    Returns:
        200: Consulta realizada com sucesso ou nenhum agendamento encontrado.
        400: Dados inválidos.
        401: Falha de autenticação.
        411: Dados insuficientes.
    """
    auth = request.headers.get('Authorization')
    token_estabelecimento = request.cookies.get('token_estabelecimento')
    token_user = request.cookies.get('token_user')

    if not (auth and token_estabelecimento and token_user):
        return jsonify({"status": "error", "message": "Erro de autenticação"}), 401

    if not (verificar_token_fernet(auth) and verificar_token_jwt(token_estabelecimento) and verificar_token_jwt(token_user)):
        return jsonify({"status": "error", "message": "Erro de autenticação"}), 401

    if not validar_token_consultar_agendamentos(auth):
        return jsonify({"status": "error", "message": "Erro de autenticação"}), 401

    resultado = validar_token_id_estabelecimento(token_estabelecimento)
    if resultado is False:
        return jsonify({"status": "error", "message": "Erro de autenticação"}), 401
    _, estabelecimento_id = resultado

    valid_user = validar_token_id_user(estabelecimento_id, token_user)
    if valid_user is False:
        return jsonify({"status": "error", "message": "Erro de autenticação"}), 401
    _, user_id = valid_user

    data = request.get_json(silent=True) or {}
    type_param = data.get("type")
    if not type_param:
        return jsonify({"status": "error", "message": "Erro de dados insuficientes"}), 411

    if type_param not in ["ativos", "historico"]:
        return jsonify({"status": "error", "message": "Dados invalidos"}), 400

    agendamentos = consultar_agendamentos_por_estabelecimento_cliente_status(estabelecimento_id, user_id, type_param)
    if agendamentos is not None:
        return jsonify({
            "status": "success",
            "message": "Consulta realizada com sucesso.",
            "agendamentos": agendamentos
        }), 200
    else:
        return jsonify({
            "status": "success",
            "message": "Nenhum agendamento encontrado para os dados informados."
        }), 200