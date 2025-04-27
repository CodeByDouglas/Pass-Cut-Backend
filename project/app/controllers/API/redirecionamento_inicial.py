from flask import Blueprint, request, jsonify

redirecionamento_bp = Blueprint('redirecionamento_inicial', __name__, url_prefix='/api/redirecionamento_inicial')

@redirecionamento_bp.route('', methods=['POST'])
def redirecionamento_inicial():
    token = request.headers.get('Authorization')
    if token:
        print(token)
        return jsonify({
            "status": "success",
            "message": "Token recebido com sucesso.",
            "token": token
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "Erro de autenticação"
        }), 401