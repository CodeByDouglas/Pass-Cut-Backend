from flask import Blueprint, request, jsonify
from ...services.Services_Agendamentos.Validar_Tokens.Validar_Token_Inicial import validar_token_inicial
from ...services.Services_Agendamentos.Verificacao_Dados.Verificacao_IDBase import verificar_id_base
from ...services.Services_Agendamentos.Verificacao_Dados.Verificacao_Nome_Estabelecimento import verificar_nome_estabelecimento

redirecionamento_bp = Blueprint('redirecionamento_inicial', __name__, url_prefix='/api/redirecionamento_inicial')

@redirecionamento_bp.route('', methods=['POST'])
def redirecionamento_inicial():
    token = request.headers.get('Authorization')
    if token:
        if validar_token_inicial(token):
            # Extrai dados do corpo da requisição (JSON)
            data = request.get_json() or {}
            nome = data.get("nome")
            id_base = data.get("ID base")
            
            # Verifica se ambos os dados estão presentes e não são nulos
            if nome is not None and id_base is not None:
                # Valida os dados usando as funções correspondentes
                if verificar_id_base(id_base) and verificar_nome_estabelecimento(nome):
                    return jsonify({
                        "status": "success",
                        "message": "Token e dados recebidos com sucesso.",
                        "nome": nome,
                        "ID base": id_base
                    }), 200
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