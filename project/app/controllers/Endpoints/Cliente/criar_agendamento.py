from flask import Blueprint, request, jsonify
from ....services.Cliente.Sanetizar_dados.sanitizar_token_fernet import verificar_token_fernet
from ....services.Cliente.Sanetizar_dados.sanitizar_token_jwt import verificar_token_jwt
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_criar_agendamento import validar_token_consultar_servico
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_ID_estabelecimento import validar_token_id_estabelecimento
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_ID_user import validar_token_id_user
from ....services.Cliente.Sanetizar_dados.sanitizar_colaborador_id import verificar_id_colaborador
from ....services.Cliente.Sanetizar_dados.sanitizar_horarios import verificar_horario_valido
from ....services.Cliente.Sanetizar_dados.sanitizar_data import verificar_data
from ....services.Cliente.Sanetizar_dados.sanitizar_id_servico import verificar_ids_servicos
from ....services.Cliente.Consulta_DataBase.Criar_agendamento import agendar

criar_agendamento_bp = Blueprint('criar_agendamento', __name__)

@criar_agendamento_bp.route('/criar-agendamento', methods=['POST'])
def criar_agendamento():
    """
    Endpoint para criação de agendamento do cliente.

    Espera receber:
    - Header 'Authorization' com token Fernet válido.
    - Cookies 'token_estabelecimento' e 'token_user' com JWTs válidos.
    - JSON no corpo com:
        - 'colaborador_id': ID do colaborador
        - 'horario': horário do agendamento
        - 'data': data do agendamento
        - 'servicos': lista de IDs de serviços

    Fluxo:
    1. Valida presença dos dados obrigatórios.
    2. Valida tokens.
    3. Valida credenciais do usuário e do estabelecimento.
    4. Valida formato dos dados.
    5. Cria o agendamento no banco.

    Returns:
        200: Agendamento criado com sucesso.
        204: Horário indisponível.
        400: Dados insuficientes ou inválidos.
        401: Falha de autenticação.
        500: Erro interno ao criar agendamento.
    """
    auth = request.headers.get('Authorization')
    token_estabelecimento = request.cookies.get('token_estabelecimento')
    token_user = request.cookies.get('token_user')

    if not (auth and token_estabelecimento and token_user):
        return jsonify({"erro": "Erro de autenticação"}), 401

    if not (verificar_token_fernet(auth) and verificar_token_jwt(token_user) and verificar_token_jwt(token_estabelecimento)):
        return jsonify({"erro": "Erro de autenticação"}), 401

    if not validar_token_consultar_servico(auth):
        return jsonify({"erro": "Erro de autenticação"}), 401

    resultado_est = validar_token_id_estabelecimento(token_estabelecimento)
    if not (isinstance(resultado_est, tuple) and resultado_est[0]):
        return jsonify({"erro": "Erro de autenticação"}), 401
    _, estabelecimento_id = resultado_est

    resultado_user = validar_token_id_user(estabelecimento_id, token_user)
    if not (isinstance(resultado_user, tuple) and resultado_user[0]):
        return jsonify({"erro": "Erro de autenticação"}), 401
    _, user_id = resultado_user

    dados = request.get_json(silent=True) or {}
    colaborador_id = dados.get('colaborador_id')
    horario = dados.get('horario')
    data = dados.get('data')
    servicos = dados.get('servicos')

    if not (colaborador_id and horario and data and servicos and isinstance(servicos, list) and len(servicos) > 0):
        return jsonify({"erro": "Dados insuficientes para a consulta"}), 400

    if not (verificar_id_colaborador(colaborador_id)
            and verificar_horario_valido(horario)
            and verificar_data(data)
            and verificar_ids_servicos(servicos)):
        return jsonify({"erro": "Dados invalidos"}), 400

    resultado = agendar(estabelecimento_id, user_id, servicos, colaborador_id, data, horario)
    if resultado is True:
        return jsonify({
            "message": "Agendamento criado com sucesso",
            "estabelecimento_id": estabelecimento_id,
            "user_id": user_id
        }), 200
    elif isinstance(resultado, tuple) and resultado[0] is False:
        mensagem = resultado[1]
        if mensagem == "Erro interno":
            return jsonify({"erro": "Erro interno ao processar o agendamento"}), 500
        elif mensagem == "Horário indisponível":
            return '', 204
        else:
            return jsonify({"erro": mensagem}), 400

    return jsonify({"erro": "Erro desconhecido"}), 500