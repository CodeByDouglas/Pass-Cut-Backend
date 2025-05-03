from flask import Blueprint, request, jsonify
from ...services.Services_Agendamentos.Verificacao_Dados.Verificar_Token_Fernet import verificar_token_fernet
from ...services.Services_Agendamentos.Verificacao_Dados.Verificar_Token_JWT import verificar_token_jwt

consultar_agendamentos_bp = Blueprint('consultar_agendamentos', __name__, url_prefix='/api/consultar_agendamentos')

@consultar_agendamentos_bp.route('', methods=['GET'])
def consultar_agendamentos():
    auth = request.headers.get('Authorization')
    token_estabelecimento = request.headers.get('token-estabelecimento')
    token_user = request.headers.get('token-user')
    
    if auth and token_estabelecimento and token_user:
        if (verificar_token_fernet(auth) and verificar_token_jwt(token_estabelecimento) and verificar_token_jwt(token_user)):
            return jsonify({
                "status": "success",
                "message": "Consulta realizada com sucesso."
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