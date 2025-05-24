from flask import Blueprint, request, jsonify
from ....services.Services_Agendamentos.Verificacao_Dados.sanitizar_token_fernet import verificar_token_fernet
from ....services.Services_Agendamentos.Verificacao_Dados.sanitizar_token_jwt import verificar_token_jwt
from ....services.Services_Agendamentos.Autenticacao_Tokens.Validar_Token_cancelar_agendamento import validar_token_cancelar_agendamento
from ....services.Services_Agendamentos.Autenticacao_Tokens.Validar_Token_ID_estebelecimento import validar_token_id_estabelecimento
from ....services.Services_Agendamentos.Autenticacao_Tokens.Validar_Token_ID_user import validar_token_id_user
from ....services.Services_Agendamentos.Verificacao_Dados.sanitizar_id_agendamento import verificar_id_agendamento
from ....services.Services_Agendamentos.Consulta_DataBase.Cancelar_agendamento import cancelar_agendamento_db

cancelar_agendamento_bp = Blueprint('cancelar_agendamento', __name__)

@cancelar_agendamento_bp.route('/cancelar-agendamento', methods=['POST'])
def cancelar_agendamento():
    auth = request.headers.get('auth')
    token_estabelecimento = request.headers.get('token-estabelecimento')
    token_user = request.headers.get('token-user')
    
    if auth and token_estabelecimento and token_user:
        if (verificar_token_fernet(auth) and 
            verificar_token_jwt(token_estabelecimento) and 
            verificar_token_jwt(token_user)):
            if validar_token_cancelar_agendamento(auth):
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
                        
                        # Verifica se o corpo da requisição contém o parâmetro "agendamento_id"
                        req_data = request.get_json()
                        if req_data and isinstance(req_data, dict):
                            agendamento_id = req_data.get('agendamento_id')
                            if agendamento_id:
                                # Verifica se o agendamento_id segue o padrão esperado
                                if verificar_id_agendamento(agendamento_id):
                                    if cancelar_agendamento_db(agendamento_id, estabelecimento_id, user_id):
                                        return jsonify({"message": "Agendamento cancelado com sucesso"}), 200
                                    else:
                                        return jsonify({
                                            "status": "error",
                                            "message": "Erro interno"
                                        }), 500
                                else:
                                    return jsonify({
                                        "status": "error",
                                        "message": "Dados inválidos"
                                    }), 400
                            else:
                                return jsonify({
                                    "status": "error",
                                    "message": "Dados Insuficientes"
                                    
                                    }), 400
                        else:
                            return jsonify({
                                "status": "error",
                                "message": "Dados insuficientes"
                            }), 400
                    else:
                        return jsonify({
                            "status": "error",
                            "message": "Autenticação Falhou - erro no user"
                        }), 401
    return jsonify({
        "status": "error",
        "message": "Autenticação Falhou"
    }), 401