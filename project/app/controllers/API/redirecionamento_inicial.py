from flask import Blueprint, request, jsonify

redirecionamento_bp = Blueprint('redirecionamento_inicial', __name__, url_prefix='/api/redirecionamento_inicial')

@redirecionamento_bp.route('', methods=['POST'])
def redirecionamento_inicial():
    data = request.get_json() or {}
    # Coloque aqui a lógica necessária para o redirecionamento
    return jsonify({
        "status": "success",
        "message": "Rota POST 'redirecionamento_inicial' chamada com sucesso.",
        "data": data
    }), 200