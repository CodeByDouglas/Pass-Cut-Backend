from flask import Blueprint, request, jsonify
from ....services.Cliente.Sanetizar_dados.sanitizar_token_fernet import verificar_token_fernet
from ....services.Cliente.Sanetizar_dados.sanitizar_token_jwt import verificar_token_jwt
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_autenticar_user import validar_token_autenticar_user
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_ID_estabelecimento import validar_token_id_estabelecimento
from ....services.Cliente.Sanetizar_dados.sanitizar_email import verificar_email
from ....services.Cliente.Sanetizar_dados.sanitizar_senha import verificar_senha
from ....services.Cliente.Consulta_DataBase.Consultar_ID_User import consultar_id_user
from ....services.Cliente.Hashe_senha.Autendicar_senha import autenticar_senha
from ....services.Cliente.Gerar_Token_JWT.Gerar_JWT_IDUser import gerar_jwt_id_estabelecimento

autenticar_user_bp = Blueprint('autenticar_user', __name__, url_prefix='/api/autenticar_user')

@autenticar_user_bp.route('', methods=['POST'])
def autenticar_user():
    # Recupera o token Fernet do cabeçalho e o token do estabelecimento do cookie
    authorization = request.headers.get('Authorization')
    token_estabelecimento = request.cookies.get('token_estabelecimento')  # Alterado para cookie

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
                    
                    # Verifica se "login" e "senha" estão presentes e não são vazios
                    if login and senha:
                        # Valida o email e a senha
                        if verificar_email(login) and verificar_senha(senha):
                            # Consulta o ID do user a partir do ID do estabelecimento e do email (login)
                            consulta = consultar_id_user(estabelecimento_id, login)
                            if consulta is not False:
                                # Desempacota o resultado para obter o ID do user
                                _, user_id = consulta
                                # Chama a função para autenticar a senha
                                if autenticar_senha(estabelecimento_id, user_id, senha):
                                    # Chama a função para gerar o JWT com o id do user
                                    jwt_token = gerar_jwt_id_estabelecimento(user_id)
                                    resposta =  jsonify({
                                        "status": "success",
                                        "message": "User autenticado",
                                        "token": jwt_token
                                    })
                                    resposta.set_cookie(
                                            "token_user",
                                            jwt_token,
                                            httponly=True,
                                            secure=False,      # Em produção, usar True
                                            samesite="None",   # Em produção, mantenha None se for cross-site
                                            max_age=60
                                    )
                                    return resposta, 200
                                else:
                                    return jsonify({
                                        "status": "error",
                                        "message": "Erro ao autenticar user"
                                    }), 401
                            else:
                                return jsonify({
                                    "status": "error",
                                    "message": "Usuário não encontrado"
                                }), 401
                        else:
                            return jsonify({
                                "status": "error",
                                "message": "Erro dados invalidos"
                            }), 400
                    else:
                        return jsonify({
                            "status": "error",
                            "message": "Erro dados insuficientes"
                        }), 411
                return jsonify({
                    "status": "error",
                    "message": "Erro de autenticação"
                }), 401
            return jsonify({
                "status": "error",
                "message": "Erro de autenticação"
            }), 401
    return jsonify({
        "status": "error",
        "message": "Erro de autenticação"
    }), 401