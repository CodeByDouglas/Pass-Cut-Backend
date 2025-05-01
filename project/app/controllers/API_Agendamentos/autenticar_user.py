from flask import Blueprint, request, jsonify
from ...services.Services_Agendamentos.Verificacao_Dados.Verificar_Token_Fernet import verificar_token_fernet
from ...services.Services_Agendamentos.Verificacao_Dados.Verificar_Token_JWT import verificar_token_jwt
from ...services.Services_Agendamentos.Validar_Tokens.Validar_Token_autenticar_user import validar_token_autenticar_user
from ...services.Services_Agendamentos.Validar_Tokens.Validar_Token_ID_estebelecimento import validar_token_id_estabelecimento

autenticar_user_bp = Blueprint('autenticar_user', __name__, url_prefix='/api/autenticar_user')

@autenticar_user_bp.route('', methods=['POST'])
def autenticar_user():
    # Recupera os parâmetros do cabeçalho
    authorization = request.headers.get('Authorization')
    token_estabelecimento = request.headers.get('token-estabelecimento')
    
    # Verifica se ambos os parâmetros estão presentes e não são vazios
    if authorization and token_estabelecimento:
        # Primeiro, realiza as verificações estruturais dos tokens
        if verificar_token_fernet(authorization) and verificar_token_jwt(token_estabelecimento):
            # Valida os tokens com as funções específicas
            if validar_token_autenticar_user(authorization):
                resultado = validar_token_id_estabelecimento(token_estabelecimento)
                if resultado is not False:
                    # Desempacota o resultado para obter o ID do estabelecimento
                    _, estabelecimento_id = resultado
                    
                    # Recupera dados do corpo da requisição utilizando silent=True para evitar 400 Bad Request
                    data = request.get_json(silent=True) or {}
                    login = data.get("login")
                    senha = data.get("senha")
                    
                    # Verifica se "login" e "senha" estão presentes e não vazios
                    if login and senha:
                        return jsonify({
                            "status": "success",
                            "message": "Requisição POST recebida com sucesso.",
                            "estabelecimento_id": estabelecimento_id
                        }), 200
                    else:
                        return jsonify({
                            "status": "error",
                            "message": "Erro de dados insuficientes"
                        }), 411
                return jsonify({
                    "status": "error",
                    "message": "Erro de autenticação - token id"
                }), 401
            return jsonify({
                "status": "error",
                "message": "Erro de autenticação - token aut"
            }), 401
    return jsonify({
        "status": "error",
        "message": "Erro de autenticação - formatos inválidos"
    }), 401