from flask import Blueprint, request, jsonify
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_Inicial import validar_token_redirecionamento_inicial
from ....services.Cliente.Sanetizar_dados.sanitizar_token_fernet import verificar_token_fernet
from ....services.Cliente.Sanetizar_dados.sanitizar_id_base import verificar_id_base
from ....services.Cliente.Sanetizar_dados.sanitizar_nome_estabelecimento import verificar_nome_estabelecimento
from ....services.Cliente.Consulta_DataBase.Consulta_ID_Estabelecimento import consultar_estabelecimento
from ....services.Cliente.Gerar_Token_JWT.Gerar_JWT_IDEstabelecimento import gerar_jwt_id_estabelecimento

redirecionamento_bp = Blueprint('redirecionamento_inicial', __name__, url_prefix='/api/redirecionamento_inicial')

@redirecionamento_bp.route('', methods=['POST'])
def redirecionamento_inicial():
    token = request.headers.get('Authorization')
    if token:
        # Primeiramente, verifica se o token é um token Fernet válido
        if verificar_token_fernet(token):
            # Se o token é Fernet, prossegue com a validação inicial
            if validar_token_redirecionamento_inicial(token):
                # Extrai dados do corpo da requisição (JSON)
                data = request.get_json() or {}
                nome = data.get("nome")
                id_base = data.get("IDbase")
                
                # Verifica se ambos os dados estão presentes e não são nulos
                if nome is not None and id_base is not None:
                    # Valida os dados usando as funções correspondentes
                    if verificar_id_base(id_base) and verificar_nome_estabelecimento(nome):
                        resultado = consultar_estabelecimento(nome, id_base)
                        if resultado is not False:
                            sucesso, estabelecimento_id = resultado
                            jwt_token = gerar_jwt_id_estabelecimento(estabelecimento_id)
                            resposta = jsonify({
                                "status": "success",
                                "message": "Base autenticada"
                                
                            })
                            resposta.set_cookie(
                                "token_estabelecimento",   # Corrigido o nome do cookie
                                jwt_token,                # valor do JWT
                                httponly=True,            # inacessível via JavaScript
                                secure=True,             # em DEV; em produção **deve** ser True
                                samesite='None',          # permite cross-site
                                max_age=3600,             # 60 minutos em segundos
                                path='/'                  # escopo global no domínio
                                # domain='seu-backend.com' # opcional: restrinja ao seu domínio
                            )
                            return resposta, 200
                        else:
                            return jsonify({
                                "status": "error",
                                "message": "Estabelecimento não encontrado."
                            }), 404
                    else:
                        return jsonify({
                            "status": "error",
                            "message": "Dados invalidos"
                        }), 400
                else:
                    return jsonify({
                        "status": "error",
                        "message": "Dados insuficientes"
                    }), 400
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