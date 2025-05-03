from flask import Blueprint, jsonify

consultar_agendamentos_bp = Blueprint('consultar_agendamentos', __name__, url_prefix='/api/consultar_agendamentos')

@consultar_agendamentos_bp.route('', methods=['GET'])
def consultar_agendamentos():
    return jsonify({
        "status": "success",
        "message": "Consulta realizada com sucesso."
    }), 200