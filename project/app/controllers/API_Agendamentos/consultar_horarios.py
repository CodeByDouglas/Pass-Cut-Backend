from flask import Blueprint, request, jsonify
from ...services.Services_Agendamentos.Verificacao_Dados.Verificar_Token_Fernet import verificar_token_fernet
from ...services.Services_Agendamentos.Verificacao_Dados.Verificar_Token_JWT import verificar_token_jwt
from ...services.Services_Agendamentos.Autenticacao_Tokens.Validar_Token_consultar_horarios import validar_token_consultar_horarios
from ...services.Services_Agendamentos.Autenticacao_Tokens.Validar_Token_ID_estebelecimento import validar_token_id_estabelecimento
from ...services.Services_Agendamentos.Autenticacao_Tokens.Validar_Token_ID_user import validar_token_id_user

consultar_horarios_bp = Blueprint('consultar_horarios', __name__)

@consultar_horarios_bp.route('/consultar-horarios', methods=['POST'])
def consultar_horarios():
    auth = request.headers.get('auth')
    token_estabelecimento = request.headers.get('token-estabelecimento')
    token_user = request.headers.get('token-user')
    print(auth)
    
    if auth and token_estabelecimento and token_user:
        if (verificar_token_fernet(auth) and 
            verificar_token_jwt(token_estabelecimento) and 
            verificar_token_jwt(token_user)):
            # Chama as funções de validação adicionais
            if validar_token_consultar_horarios(auth):
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
                        return jsonify({"erro": "Autenticação falhou erro no user"}), 401
                else:
                    return jsonify({"erro": "Autenticação falhou erro ao validar token estabelecinento "}), 401
            else: 
                return jsonify({"erro": "Autenticação falhou erro no user validando token da api"}), 401
        else: 
            return jsonify({"erro": "Autenticação falhou erro no user  verificando se são tokens"}), 401
    else:
        return jsonify({"erro": "Autenticação falhou erro no user não foram nem encontrados"}), 401