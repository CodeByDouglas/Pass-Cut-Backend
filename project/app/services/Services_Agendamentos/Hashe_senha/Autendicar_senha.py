import bcrypt
from app.models.models import Cliente
from app.extensions import db

def autenticar_senha(estabelecimento_id: str, cliente_id: str, senha: str) -> bool:
    """
    Recebe o ID do estabelecimento, o ID do cliente e uma senha em formato string.
    Busca pelo cliente no banco de dados; caso encontre, extrai o hash da senha armazenada
    (campo 'senha_hash') e utiliza bcrypt.checkpw() para comparar com a senha fornecida.
    
    Parameters:
        estabelecimento_id (str): ID do estabelecimento.
        cliente_id (str): ID do cliente.
        senha (str): A senha em texto puro fornecida pelo usuário.
        
    Returns:
        bool: True se a senha corresponder ao hash armazenado, False caso contrário.
    """
    cliente = db.session.query(Cliente).filter_by(id=cliente_id, estabelecimento_id=estabelecimento_id).first()
    if not cliente:
        return False

    senha_bytes = senha.encode('utf-8')
    hash_bytes = cliente.senha_hash.encode('utf-8') if isinstance(cliente.senha_hash, str) else cliente.senha_hash

    return bcrypt.checkpw(senha_bytes, hash_bytes)