from flask import Blueprint, request, jsonify
from ...services.Services_Agendamentos.Autenticacao_Tokens.Validar_Token_Inicial import validar_token_redirecionamento_inicial
from ...services.Services_Agendamentos.Verificacao_Dados.Verificar_Token_Fernet import verificar_token_fernet
from ...services.Services_Agendamentos.Verificacao_Dados.Verificacao_IDBase import verificar_id_base
from ...services.Services_Agendamentos.Verificacao_Dados.Verificacao_Nome_Estabelecimento import verificar_nome_estabelecimento
from ...services.Services_Agendamentos.Consulta_DataBase.Consulta_ID_Estabelecimento import consultar_estabelecimento
from ...services.Services_Agendamentos.Gerar_Token_JWT.Gerar_JWT_IDEstabelecimento import gerar_jwt_id_estabelecimento

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
                id_base = data.get("ID base")
                
                # Verifica se ambos os dados estão presentes e não são nulos
                if nome is not None and id_base is not None:
                    # Valida os dados usando as funções correspondentes
                    if verificar_id_base(id_base) and verificar_nome_estabelecimento(nome):
                        resultado = consultar_estabelecimento(nome, id_base)
                        if resultado is not False:
                            sucesso, estabelecimento_id = resultado
                            jwt_token = gerar_jwt_id_estabelecimento(estabelecimento_id)
                            return jsonify({
                                "status": "success",
                                "message": "Base autenticada",
                                "Token": jwt_token
                            }), 200
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