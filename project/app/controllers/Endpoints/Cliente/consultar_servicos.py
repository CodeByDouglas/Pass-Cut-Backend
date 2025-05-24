from flask import Blueprint, request, jsonify
from ....services.Cliente.Sanetizar_dados.sanitizar_token_fernet import verificar_token_fernet
from ....services.Cliente.Sanetizar_dados.sanitizar_token_jwt import verificar_token_jwt
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_consultar_servicos import validar_token_consultar_servico
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_ID_estabelecimento import validar_token_id_estabelecimento
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_ID_user import validar_token_id_user
from ....services.Cliente.Consulta_DataBase.Consultar_servicos import consultar_servicos_por_estabelecimento

consultar_servicos_bp = Blueprint('consultar_servicos', __name__)

@consultar_servicos_bp.route('/consultar-servicos', methods=['POST'])
def consultar_servicos():
    auth = request.headers.get('auth')
    token_estabelecimento = request.cookies.get('token_estabelecimento')  # Busca do cookie
    token_user = request.cookies.get('token_user')  # Busca do cookie
    
    if auth and token_estabelecimento and token_user:
        if (verificar_token_fernet(auth) and 
            verificar_token_jwt(token_estabelecimento) and 
            verificar_token_jwt(token_user)):
            if validar_token_consultar_servico(auth):
                result_est = validar_token_id_estabelecimento(token_estabelecimento)
                # Verifica se o retorno é uma tupla antes de desempacotar
                if isinstance(result_est, tuple):
                    valid_est, estabelecimento_id = result_est
                else:
                    valid_est = result_est
                    estabelecimento_id = None
                    
                if valid_est and estabelecimento_id:
                    result_user = validar_token_id_user(estabelecimento_id, token_user)
                    if isinstance(result_user, tuple):
                        _, user_id = result_user
                    else:
                        return jsonify({
                            "status": "error",
                            "message": "Erro de Autenticação"
                        }), 401

                    # Chama a função para consultar os serviços do estabelecimento
                    result = consultar_servicos_por_estabelecimento(estabelecimento_id)
                    if result:
                        success, servicos_array = result
                        if success:
                            return jsonify({
                                "message": "Requisição bem sucedida",
                                "estabelecimento_id": estabelecimento_id,
                                "user_id": user_id,
                                "servicos": servicos_array
                            }), 200
                    return jsonify({
                        "status": "error",
                        "message": "não foi possível localizar os dados"
                        }), 404
                else:
                    return jsonify({
                        "status": "error",
                        "message": "Erro de Autentiicação"
                    }), 401                    
    return jsonify({
        "status":"error",
        "message": "Erro de Autenticação"
    }), 401