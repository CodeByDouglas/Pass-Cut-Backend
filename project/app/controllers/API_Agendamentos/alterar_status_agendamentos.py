from flask import Blueprint, request, jsonify
from ...services.Services_Agendamentos.Verificacao_Dados.Verificar_Token_Fernet import verificar_token_fernet
from ...services.Services_Agendamentos.Verificacao_Dados.Verificar_Token_JWT import verificar_token_jwt
from ...services.Services_Agendamentos.Autenticacao_Tokens.Validar_Token_alterar_status_agendamento import validar_token_alterar_status_agendamento
from ...services.Services_Agendamentos.Autenticacao_Tokens.Validar_Token_ID_estebelecimento import validar_token_id_estabelecimento
from ...services.Services_Agendamentos.Autenticacao_Tokens.Validar_Token_ID_user import validar_token_id_user

alterar_status_agendamentos_bp = Blueprint('alterar_status_agendamentos', __name__)

@alterar_status_agendamentos_bp.route('/alterar-status-agendamentos', methods=['POST'])
def alterar_status_agendamentos():
    auth = request.headers.get('auth')
    token_estabelecimento = request.headers.get('token-estabelecimento')
    token_user = request.headers.get('token-user')
    
    if auth and token_estabelecimento and token_user:
        if (verificar_token_fernet(auth) and 
            verificar_token_jwt(token_estabelecimento) and 
            verificar_token_jwt(token_user)):
            if validar_token_alterar_status_agendamento(auth):
                result_est = validar_token_id_estabelecimento(token_estabelecimento)
                if isinstance(result_est, tuple):
                    valid_est, estabelecimento_id = result_est
                else:
                    valid_est = result_est
                    estabelecimento_id = None
                    
                if valid_est and estabelecimento_id:
                    valid_user = validar_token_id_user(estabelecimento_id, token_user)
                    if isinstance(valid_user, tuple):
                        _, user_id = valid_user
                        
                        # Verifica se o corpo da requisição contém os parâmetros "agendamento_id" e "status"
                        req_data = request.get_json()
                        if req_data and isinstance(req_data, dict):
                            agendamento_id = req_data.get('agendamento_id')
                            status = req_data.get('status')
                            if agendamento_id and status:
                                return jsonify({"message": "Requisição bem sucedida"}), 200
                            else:
                                return jsonify({"erro": "Dados insuficientes"}), 411
                        else:
                            return jsonify({"erro": "Dados insuficientes"}), 411
                    else:
                        return jsonify({"erro": "Autenticação falhou - erro no user"}), 401
    return jsonify({"erro": "Autenticação falhou"}), 401