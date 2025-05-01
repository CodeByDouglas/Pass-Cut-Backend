from flask import Blueprint, request, jsonify

autenticar_user_bp = Blueprint('autenticar_user', __name__, url_prefix='/api/autenticar_user')

@autenticar_user_bp.route('', methods=['POST'])
def autenticar_user():
    # Recupera os parâmetros do cabeçalho
    authorization = request.headers.get('Authorization')
    token_estabelecimento = request.headers.get('token-estabelecimento')
    
    # Verifica se ambos os parâmetros estão presentes e não são vazios
    if authorization and token_estabelecimento:
        return jsonify({
            "status": "success",
            "message": "Requisição POST recebida com sucesso 2."
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "Erro de autenticação"
        }), 401