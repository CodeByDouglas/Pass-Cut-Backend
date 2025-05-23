from flask import Blueprint, request, jsonify
from ....services.Cliente.Sanetizar_dados.sanitizar_token_fernet import verificar_token_fernet
from ....services.Cliente.Sanetizar_dados.sanitizar_token_jwt import verificar_token_jwt
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_criar_agendamento import validar_token_consultar_servico
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_ID_estabelecimento import validar_token_id_estabelecimento
from ....services.Cliente.Autenticacao_Tokens.Validar_Token_ID_user import validar_token_id_user
from ....services.Cliente.Sanetizar_dados.sanitizar_colaborador_id import verificar_id_colaborador
from ....services.Cliente.Sanetizar_dados.sanitizar_horarios import verificar_horario_valido
from ....services.Cliente.Sanetizar_dados.sanitizar_data import verificar_data
from ....services.Cliente.Sanetizar_dados.sanitizar_id_servico import verificar_ids_servicos
from ....services.Cliente.Consulta_DataBase.Criar_agendamento import agendar

criar_agendamento_bp = Blueprint('criar_agendamento', __name__)

@criar_agendamento_bp.route('/criar-agendamento', methods=['POST'])
def criar_agendamento():
    auth = request.headers.get('auth')
    token_estabelecimento = request.cookies.get('token_estabelecimento')  # Busca do cookie
    token_user = request.cookies.get('token_user')  # Busca do cookie

    if auth and token_estabelecimento and token_user:
        if (verificar_token_fernet(auth) and 
            verificar_token_jwt(token_user) and 
            verificar_token_jwt(token_estabelecimento)):
            
            if validar_token_consultar_servico(auth):
                resultado_est = validar_token_id_estabelecimento(token_estabelecimento)
                if isinstance(resultado_est, tuple) and resultado_est[0]:
                    _, estabelecimento_id = resultado_est
                    resultado_user = validar_token_id_user(estabelecimento_id, token_user)
                    if isinstance(resultado_user, tuple) and resultado_user[0]:
                        _, user_id = resultado_user

                        # Verificação dos dados no corpo da requisição
                        dados = request.get_json()
                        colaborador_id = dados.get('colaborador_id') if dados else None
                        horario = dados.get('horario') if dados else None
                        data = dados.get('data') if dados else None
                        servicos = dados.get('servicos') if dados else None

                        if colaborador_id and horario and data and servicos and isinstance(servicos, list) and len(servicos) > 0:
                            if (
                                verificar_id_colaborador(colaborador_id)
                                and verificar_horario_valido(horario)
                                and verificar_data(data)
                                and verificar_ids_servicos(servicos)
                            ):
                                resultado = agendar(estabelecimento_id, user_id, servicos, colaborador_id, data, horario)
                                if resultado is True:
                                    return jsonify({
                                        "message": "Agendamento criado com sucesso",
                                        "estabelecimento_id": estabelecimento_id,
                                        "user_id": user_id
                                    }), 200
                                elif isinstance(resultado, tuple) and resultado[0] is False:
                                    mensagem = resultado[1]
                                    if mensagem == "Erro interno":
                                        return jsonify({
                                            "status":"error",
                                            "message": "Erro interno ao processar o agendamento"
                                        }), 500
                                    elif mensagem == "Horário indisponível":
                                        return jsonify({
                                            "status": "error",
                                            "message": "Infelizmente o horário solicitado acabou de ser preenchido e não está mais disponível."
                                        }), 204
                                    else:
                                        return jsonify({"erro": mensagem}), 400
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