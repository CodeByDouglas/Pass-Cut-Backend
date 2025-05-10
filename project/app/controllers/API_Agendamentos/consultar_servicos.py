from flask import Blueprint, request, jsonify
from ...services.Services_Agendamentos.Verificacao_Dados.Verificar_Token_Fernet import verificar_token_fernet
from ...services.Services_Agendamentos.Verificacao_Dados.Verificar_Token_JWT import verificar_token_jwt
from ...services.Services_Agendamentos.Autenticacao_Tokens.Validar_Token_consultar_servicos import validar_token_consultar_servico
from ...services.Services_Agendamentos.Autenticacao_Tokens.Validar_Token_ID_estebelecimento import validar_token_id_estabelecimento
from ...services.Services_Agendamentos.Autenticacao_Tokens.Validar_Token_ID_user import validar_token_id_user

consultar_servicos_bp = Blueprint('consultar_servicos', __name__)

@consultar_servicos_bp.route('/consultar-servicos', methods=['POST'])
def consultar_servicos():
    auth = request.headers.get('auth')
    token_estabelecimento = request.headers.get('token-estabelecimento')
    token_user = request.headers.get('token-user')
    
    if auth and token_estabelecimento and token_user:
        if (verificar_token_fernet(auth) and 
            verificar_token_jwt(token_estabelecimento) and 
            verificar_token_jwt(token_user)):
            # Chama as funções de validação adicionais
            if validar_token_consultar_servico(auth):
                valid_est, estabelecimento_id = validar_token_id_estabelecimento(token_estabelecimento)
                if valid_est:
                    valid_user = validar_token_id_user(estabelecimento_id, token_user)
                    if valid_user:
                        _, user_id = valid_user
                        return jsonify({
                            "message": "Requisição bem sucedida",
                            "estabelecimento_id": estabelecimento_id,
                            "user_id": user_id
                        }), 200
                    else:
                        return jsonify({"erro": "Autenticação falhou"}), 401
                    
    return jsonify({"erro": "Autenticação falhou"}), 401