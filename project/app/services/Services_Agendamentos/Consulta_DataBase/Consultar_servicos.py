from app.models.models import Servico
from app.extensions import db

def consultar_servicos_por_estabelecimento(estabelecimento_id: str):
    """
    Recebe o ID de um estabelecimento e consulta o banco de dados por todos os serviços 
    que possuem o estabelecimento referenciado.
    
    Para cada serviço encontrado, extrai:
      - ID do serviço
      - Nome (campo nome)
      - Descrição (campo descricao)
      - Valor (campo preco)
      - Duração (campo duracao)
    
    Organiza esses dados em um array onde cada elemento é outro array com os dados do serviço.
    
    Returns:
        tuple: (True, lista_de_servicos) se serviços forem encontrados.
        bool: False caso não sejam encontrados serviços.
    """
    servicos = db.session.query(Servico).filter_by(estabelecimento_id=estabelecimento_id).all()
    
    if servicos:
        lista_servicos = []
        for servico in servicos:
            dados_servico = [
                str(servico.id),
                servico.nome,
                servico.descricao,
                str(servico.preco),  # convertendo o valor para string se necessário
                servico.duracao
            ]
            lista_servicos.append(dados_servico)
        return True, lista_servicos
    
    return False