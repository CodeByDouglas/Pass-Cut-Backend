from app.models.models import Estabelecimento
from app.extensions import db

def consultar_estabelecimento(nome: str, id_base: str):
    """
    Recebe as variáveis 'nome' e 'ID base', busca no banco de dados um estabelecimento
    cujo identificador_base seja igual ao id_base e o nome_fantasia seja igual ao nome.
    
    Parameters:
        nome (str): Nome a ser buscado (corresponde ao campo nome_fantasia).
        id_base (str): ID base a ser buscado (corresponde ao campo identificador_base).
        
    Returns:
        tuple: (True, estabelecimento.id) se encontrado;
        bool: False caso nenhum estabelecimento correspondente seja localizado.
    """
    estabelecimento = db.session.query(Estabelecimento).filter(
        Estabelecimento.identificador_base == id_base,
        Estabelecimento.nome_fantasia == nome
    ).first()
    
    if estabelecimento:
        return True, str(estabelecimento.id)
    else:
        return False