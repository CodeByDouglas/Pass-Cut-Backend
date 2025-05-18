from flask import Blueprint, request, jsonify
from ....services.Services_Agendamentos.Verificacao_Dados.Verificar_Token_Fernet import verificar_token_fernet
from ....services.Services_Agendamentos.Verificacao_Dados.Verificar_Token_JWT import verificar_token_jwt
from ....services.Services_Agendamentos.Autenticacao_Tokens.Validar_Token_consultar_colaboradores import validar_token_consultar_colaborador
from ....services.Services_Agendamentos.Autenticacao_Tokens.Validar_Token_ID_estebelecimento import validar_token_id_estabelecimento
from ....services.Services_Agendamentos.Autenticacao_Tokens.Validar_Token_ID_user import validar_token_id_user
from ....services.Services_Agendamentos.Consulta_DataBase.Consulta_colaboradores import consultar_colaboradores_por_estabelecimento

consultar_colaborador_bp = Blueprint('consultar_colaborador', __name__)

@consultar_colaborador_bp.route('/consultar-colaborador', methods=['POST'])
def consultar_colaborador():
    auth = request.headers.get('auth')
    token_estabelecimento = request.headers.get('token-estabelecimento')
    token_user = request.headers.get('token-user')
    
    if auth and token_estabelecimento and token_user:
        if (verificar_token_fernet(auth) and 
            verificar_token_jwt(token_estabelecimento) and 
            verificar_token_jwt(token_user)):
            if validar_token_consultar_colaborador(auth):
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
                        return jsonify({"erro": "Autenticação falhou"}), 401

                    # Chama a função para consultar os serviços do estabelecimento
                    result = consultar_colaboradores_por_estabelecimento(estabelecimento_id)
                    if result:
                        success, servicos_array = result
                        if success:
                            return jsonify({
                                "message": "Requisição bem sucedida",
                                "estabelecimento_id": estabelecimento_id,
                                "user_id": user_id,
                                "servicos": servicos_array
                            }), 200
                    return jsonify({"erro": "não foi possível localizar os dados"}), 404
                else:
                    return jsonify({"erro": "Autenticação falhou"}), 401                    
    return jsonify({"erro": "Autenticação falhou"}), 401