from flask import Blueprint, request, jsonify
from ....services.Cliente.Sanetizar_dados.sanitizar_token_fernet import verificar_token_fernet
from ....services.Cliente.Sanetizar_dados.sanitizar_token_jwt import verificar_token_jwt
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_consulta_agendamentos import validar_token_consultar_agendamentos
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_ID_estabelecimento import validar_token_id_estabelecimento
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_ID_user import validar_token_id_user
from ....services.Cliente.Consulta_DataBase.Consultar_agendamentos_no_DB import consultar_agendamentos_por_estabelecimento_cliente_status

consultar_agendamentos_bp = Blueprint('consultar_agendamentos', __name__, url_prefix='/api/consultar_agendamentos')

@consultar_agendamentos_bp.route('', methods=['GET'])
def consultar_agendamentos():
    auth = request.headers.get('Authorization')
    token_estabelecimento = request.cookies.get('token_estabelecimento')  # Agora busca do cookie
    token_user = request.cookies.get('token_user')  # Agora busca do cookie
    
    if auth and token_estabelecimento and token_user:
        if (verificar_token_fernet(auth) and 
            verificar_token_jwt(token_estabelecimento) and 
            verificar_token_jwt(token_user)):
            
            # Chama as funções de validação adicionais
            if validar_token_consultar_agendamentos(auth):
                resultado = validar_token_id_estabelecimento(token_estabelecimento)
                if resultado is not False:
                    _, estabelecimento_id = resultado
                    valid_user = validar_token_id_user(estabelecimento_id, token_user)
                    if valid_user is not False:
                        _, user_id = valid_user
                        data = request.get_json(silent=True) or {}
                        type_param = data.get("type")
                        if type_param:
                            if type_param in ["ativos", "historico"]:
                                agendamentos = consultar_agendamentos_por_estabelecimento_cliente_status(estabelecimento_id, user_id, type_param)
                                if agendamentos is not None:
                                    return jsonify({
                                        "status": "success",
                                        "message": "Consulta realizada com sucesso.",
                                        "agendamentos": agendamentos
                                    }), 200
                                else:
                                    return jsonify({
                                        "status": "success",
                                        "message": "Nenhum agendamento encontrado para os dados informados."
                                    }), 200
                            else:
                                return jsonify({
                                    "status": "error",
                                    "message": "Dados invalidos"
                                }), 400
                        else:
                            return jsonify({
                                "status": "error",
                                "message": "Erro de dados insuficientes"
                            }), 411
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
    else:
        return jsonify({
            "status": "error",
            "message": "Erro de autenticação"
        }), 401