from app.models.models import Colaborador
from app.extensions import db

def consultar_colaboradores_por_estabelecimento(estabelecimento_id: str):
    """
    Recebe o ID de um estabelecimento e consulta o banco de dados por todos os colaboradores
    que possuem o estabelecimento referenciado.
    
    Para cada colaborador encontrado, extrai:
      - ID do colaborador
      - Nome do colaborador
      
    Organiza esses dados em um array onde cada elemento é outro array com os dados do colaborador.
    
    Returns:
        tuple: (True, lista_de_colaboradores) se colaboradores forem encontrados.
        bool: False caso nenhum colaborador seja encontrado.
    """
    colaboradores = db.session.query(Colaborador)\
                        .filter_by(estabelecimento_id=estabelecimento_id).all()
    
    if colaboradores:
        lista_colaboradores = []
        for colaborador in colaboradores:
            dados = [
                str(colaborador.id),
                colaborador.nome
            ]
            lista_colaboradores.append(dados)
        return True, lista_colaboradores
    
    return False