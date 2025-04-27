from flask import Blueprint, request, jsonify
from ...services.Services_Agendamentos.Validar_Tokens.Validar_Token_Inicial import validar_token_inicial

redirecionamento_bp = Blueprint('redirecionamento_inicial', __name__, url_prefix='/api/redirecionamento_inicial')

@redirecionamento_bp.route('', methods=['POST'])
def redirecionamento_inicial():
    token = request.headers.get('Authorization')
    if token:
        # Chama a função que valida o token recebido
        if validar_token_inicial(token):
            
            return jsonify({
                "status": "success",
                "message": "Token recebido com sucesso.",
                "token": token
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