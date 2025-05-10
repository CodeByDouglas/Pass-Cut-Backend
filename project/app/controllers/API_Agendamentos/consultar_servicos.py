from flask import Blueprint, request, jsonify

consultar_servicos_bp = Blueprint('consultar_servicos', __name__)

@consultar_servicos_bp.route('/consultar-servicos', methods=['POST'])
def consultar_servicos():
    auth = request.headers.get('auth')
    token_estabelecimento = request.headers.get('token-estabelecimento')
    token_user = request.headers.get('token-user')
    
    if not auth or not token_estabelecimento or not token_user:
        return jsonify({"erro": "Autenticação falhou"}), 401
    
    return jsonify({"message": "Requisição bem sucedida"}), 200