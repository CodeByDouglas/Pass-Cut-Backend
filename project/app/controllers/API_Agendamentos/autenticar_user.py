from flask import Blueprint, request, jsonify
from ...services.Services_Agendamentos.Validar_Tokens.Verificar_Token_Fernet import verificar_token_fernet
from ...services.Services_Agendamentos.Validar_Tokens.Verificar_Token_JWT import verificar_token_jwt

autenticar_user_bp = Blueprint('autenticar_user', __name__, url_prefix='/api/autenticar_user')

@autenticar_user_bp.route('', methods=['POST'])
def autenticar_user():
    # Recupera os parâmetros do cabeçalho
    authorization = request.headers.get('Authorization')
    token_estabelecimento = request.headers.get('token-estabelecimento')
    
    # Verifica se ambos os parâmetros estão presentes e não são vazios
    if authorization and token_estabelecimento:
        if verificar_token_fernet(authorization) and verificar_token_jwt(token_estabelecimento):
            return jsonify({
                "status": "success",
                "message": "Requisição POST recebida com sucesso 3."
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Erro de autenticação"
            }), 401
    else:
        return jsonify({
            "status": "error",
            "message": "Erro de autenticação"
        }), 401