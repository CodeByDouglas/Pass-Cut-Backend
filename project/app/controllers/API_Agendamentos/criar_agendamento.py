from flask import Blueprint, request, jsonify
from ...services.Services_Agendamentos.Verificacao_Dados.Verificar_Token_Fernet import verificar_token_fernet
from ...services.Services_Agendamentos.Verificacao_Dados.Verificar_Token_JWT import verificar_token_jwt
from ...services.Services_Agendamentos.Autenticacao_Tokens.Validar_Token_criar_agendamento import validar_token_consultar_servico
from ...services.Services_Agendamentos.Autenticacao_Tokens.Validar_Token_ID_estebelecimento import validar_token_id_estabelecimento
from ...services.Services_Agendamentos.Autenticacao_Tokens.Validar_Token_ID_user import validar_token_id_user

criar_agendamento_bp = Blueprint('criar_agendamento', __name__)

@criar_agendamento_bp.route('/criar-agendamento', methods=['POST'])
def criar_agendamento():
    auth = request.headers.get('auth')
    token_estabelecimento = request.headers.get('token-estabelecimento')
    token_user = request.headers.get('token-user')

    if auth and token_estabelecimento and token_user:
        if (verificar_token_fernet(auth) and 
            verificar_token_jwt(token_user) and 
            verificar_token_jwt(token_estabelecimento)):
            
            if validar_token_consultar_servico(auth):
                resultado_est = validar_token_id_estabelecimento(token_estabelecimento)
                if isinstance(resultado_est, tuple) and resultado_est[0]:
                    _, estabelecimento_id = resultado_est
                    resultado_user = validar_token_id_user(estabelecimento_id, token_user)
                    if isinstance(resultado_user, tuple) and resultado_user[0]:
                        _, user_id = resultado_user
                        return jsonify({
                            "message": "Agendamento criado com sucesso",
                            "estabelecimento_id": estabelecimento_id,
                            "user_id": user_id
                        }), 200
                    else:
                        return jsonify({"erro": "Erro de autenticação"}), 401
                else:
                    return jsonify({"erro": "Erro de autenticação"}), 401
            else:
                return jsonify({"erro": "Erro de autenticação"}), 401
        else:
            return jsonify({"erro": "Erro de autenticação"}), 401
    else:
        return jsonify({"erro": "Erro de autenticação"}), 401