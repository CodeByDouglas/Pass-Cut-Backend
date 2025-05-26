from flask import Blueprint, request, jsonify
from ....services.Cliente.Sanetizar_dados.sanitizar_token_fernet import verificar_token_fernet
from ....services.Cliente.Sanetizar_dados.sanitizar_token_jwt import verificar_token_jwt
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_consultar_horarios import validar_token_consultar_horarios
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_ID_estabelecimento import validar_token_id_estabelecimento
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_ID_user import validar_token_id_user
from ....services.Cliente.Sanetizar_dados.sanitizar_colaborador_id import verificar_id_colaborador
from ....services.Cliente.Sanetizar_dados.sanitizar_data import verificar_data
from ....services.Cliente.Sanetizar_dados.sanitizar_id_servico import verificar_ids_servicos
from ....services.Cliente.Consulta_DataBase.Consultar_horario import consultar_horarios_agendamento

consultar_horarios_bp = Blueprint('consultar_horarios', __name__)

@consultar_horarios_bp.route('/consultar-horarios', methods=['POST'])
def consultar_horarios():
    auth = request.headers.get('auth')
    token_estabelecimento = request.cookies.get('token_estabelecimento')
    token_user = request.cookies.get('token_user')

    if not (auth and token_estabelecimento and token_user):
        return jsonify({
            "status": "error",
            "message": "Autenticação falhou - cabeçalhos não encontrados"
        }), 401

    if not (verificar_token_fernet(auth) and verificar_token_jwt(token_estabelecimento) and verificar_token_jwt(token_user)):
        return jsonify({
            "status": "error",
            "message": "Autenticação falhou - erro na verificação dos tokens"
        }), 401

    if not validar_token_consultar_horarios(auth):
        return jsonify({
            "status": "error",
            "message": "Autenticação falhou - erro no token da API"
        }), 401

    result_est = validar_token_id_estabelecimento(token_estabelecimento)
    if isinstance(result_est, tuple):
        valid_est, estabelecimento_id = result_est
    else:
        valid_est = result_est
        estabelecimento_id = None

    if not (valid_est and estabelecimento_id):
        return jsonify({
            "status": "error",
            "message": "Autenticação falhou - erro ao validar token estabelecimento"
        }), 401

    valid_user = validar_token_id_user(estabelecimento_id, token_user)
    if not isinstance(valid_user, tuple):
        return jsonify({
            "status": "error",
            "message": "Autenticação falhou - erro no user"
        }), 401
    _, user_id = valid_user

    req_data = request.get_json()
    if not (req_data and isinstance(req_data, dict)):
        return jsonify({
            "status": "error",
            "message": "Dados Insuficientes"
        }), 400

    servicos = req_data.get('servicos')
    colaborador_id = req_data.get('colaborador-id')
    data_agendamento = req_data.get('data')

    if not (servicos and isinstance(servicos, list) and colaborador_id and data_agendamento):
        return jsonify({
            "status": "error",
            "message": "Dados Insuficientes"
        }), 400

    if not verificar_id_colaborador(colaborador_id):
        return jsonify({
            "status": "error",
            "message": "Dados invalidos: colaborador_id inválido"
        }), 400

    if not verificar_data(data_agendamento):
        return jsonify({
            "status": "error",
            "message": "Dados invalidos: data inválida"
        }), 400

    if not verificar_ids_servicos(servicos):
        return jsonify({
            "status": "error",
            "message": "Dados invalidos: ids de serviço inválidos"
        }), 400

    resultado = consultar_horarios_agendamento(estabelecimento_id, colaborador_id, data_agendamento, servicos)
    if resultado is False:
        return jsonify({
            "status": "error",
            "message": "Erro interno ao processar solicitação"
        }), 501

    success, horarios_array = resultado
    if horarios_array == [None]:
        return jsonify({"message": "Nenhum horário disponível para essa data."}), 200

    return jsonify({
        "message": "Requisição bem sucedida",
        "estabelecimento_id": estabelecimento_id,
        "user_id": user_id,
        "horarios": [slot.strftime("%H:%M:%S") for slot in horarios_array]
    }), 200