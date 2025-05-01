from flask import Blueprint, request, jsonify

autenticar_user_bp = Blueprint('autenticar_user', __name__, url_prefix='/api/autenticar_user')

@autenticar_user_bp.route('', methods=['POST'])
def autenticar_user():
    # Você pode adicionar aqui a lógica de autenticação no futuro.
    return jsonify({
        "status": "success",
        "message": "Requisição POST recebida com sucesso."
    }), 200