from app.models.models import Cliente
from app.extensions import db

def consultar_id_user(estabelecimento_id: str, email: str):
    """
    Recebe um ID de estabelecimento e um e-mail e verifica se existe algum Cliente
    vinculado a esse estabelecimento com o e-mail correspondente (email_login).
    
    Returns:
        tuple: (True, cliente_id) se o cliente for encontrado.
        bool: False se nenhum cliente for localizado.
    """
    cliente = db.session.query(Cliente).filter(
        Cliente.estabelecimento_id == estabelecimento_id,
        Cliente.email_login == email
    ).first()
    
    if cliente:
        return True, str(cliente.id)
    return False