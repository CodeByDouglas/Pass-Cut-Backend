import bcrypt

def hashear_senha(senha: str) -> str:
    """
    Recebe uma senha em formato string, gera um salt e utiliza bcrypt para hashear
    a senha. Em seguida, imprime o hash resultante no terminal e o retorna.
    
    Parameters:
        senha (str): A senha a ser hasheada.
    
    Returns:
        str: A senha hasheada.
    """
    # Gera um salt
    salt = bcrypt.gensalt()
    # Converte a senha para bytes, pois o bcrypt trabalha com bytes
    senha_bytes = senha.encode('utf-8')
    # Gera o hash da senha utilizando o salt
    hash_bytes = bcrypt.hashpw(senha_bytes, salt)
    # Converte o hash de bytes para string
    hash_str = hash_bytes.decode('utf-8')
    
    return hash_str
print(hashear_senha('Senha.123'))
