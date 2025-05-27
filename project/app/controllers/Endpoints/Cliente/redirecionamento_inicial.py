from flask import Blueprint, request, jsonify
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_Inicial import validar_token_redirecionamento_inicial
from ....services.Cliente.Sanetizar_dados.sanitizar_token_fernet import verificar_token_fernet
from ....services.Cliente.Sanetizar_dados.sanitizar_id_base import verificar_id_base
from ....services.Cliente.Sanetizar_dados.sanitizar_nome_estabelecimento import verificar_nome_estabelecimento
from ....services.Cliente.Consulta_DataBase.Consulta_ID_Estabelecimento import consultar_estabelecimento
from ....services.Cliente.Gerar_Token_JWT.Gerar_JWT_IDEstabelecimento import gerar_jwt_id_estabelecimento

redirecionamento_bp = Blueprint('redirecionamento_inicial', __name__, url_prefix='/api/redirecionamento_inicial')

@redirecionamento_bp.route('', methods=['POST'])
def redirecionamento_inicial():
    """
    Endpoint para redirecionamento inicial do cliente.

    Espera receber:
    - Header 'Authorization' com token Fernet válido.
    - JSON no corpo com:
        - 'nome': nome do estabelecimento
        - 'IDbase': identificador base do estabelecimento

    Fluxo:
    1. Valida presença do token e dos dados obrigatórios.
    2. Valida o token Fernet e o token de redirecionamento.
    3. Valida o formato dos dados.
    4. Consulta o estabelecimento no banco.
    5. Gera e retorna o JWT do estabelecimento em cookie httpOnly.

    Returns:
        200: Redirecionamento bem-sucedido, retorna token em cookie.
        400: Dados insuficientes ou inválidos.
        401: Falha de autenticação.
        404: Estabelecimento não encontrado.
    """
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"status": "error", "message": "Erro de autenticação"}), 401

    if not verificar_token_fernet(token):
        return jsonify({"status": "error", "message": "Erro de autenticação"}), 401

    if not validar_token_redirecionamento_inicial(token):
        return jsonify({"status": "error", "message": "Erro de autenticação"}), 401

    data = request.get_json(silent=True) or {}
    nome = data.get("nome")
    id_base = data.get("IDbase")

    if nome is None or id_base is None:
        return jsonify({"status": "error", "message": "Dados insuficientes"}), 400

    if not (verificar_id_base(id_base) and verificar_nome_estabelecimento(nome)):
        return jsonify({"status": "error", "message": "Dados invalidos"}), 400

    resultado = consultar_estabelecimento(nome, id_base)
    if resultado is False:
        return jsonify({"status": "error", "message": "Estabelecimento não encontrado."}), 404

    _, estabelecimento_id = resultado
    jwt_token = gerar_jwt_id_estabelecimento(estabelecimento_id)
    resposta = jsonify({
        "status": "success",
        "message": "Base autenticada",
        "Token": jwt_token
    })
    resposta.set_cookie(
        "token_estabelecimento",
        jwt_token,
        httponly=True,
        secure=True,
        samesite='None',
        max_age=3600,
        path='/'
    )
    return resposta, 200