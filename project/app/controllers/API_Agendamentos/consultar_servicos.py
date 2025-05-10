from flask import Blueprint, request, jsonify

consultar_servicos_bp = Blueprint('consultar_servicos', __name__)

@consultar_servicos_bp.route('/consultar-servicos', methods=['POST'])
def consultar_servicos():
    # Lógica para tratar a requisição POST pode ser adicionada aqui
    return jsonify({"message": "Requisição bem sucedida"}), 200