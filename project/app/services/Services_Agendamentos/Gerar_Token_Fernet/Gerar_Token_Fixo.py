from cryptography.fernet import Fernet

def gerar_token(chave: str, dado: str) -> str:
    """
    Recebe uma chave e uma string e gera um token criptografado utilizando Fernet.
    
    Parameters:
        chave (str): A chave de encriptação (deve ser gerada previamente com Fernet.generate_key() e codificada em str).
        dado (str): A string a ser encriptada.
        
    Returns:
        str: O token criptografado.
    """
    # Converte a chave para bytes se ela estiver em formato de string
    chave_bytes = chave.encode() if isinstance(chave, str) else chave
    fernet = Fernet(chave_bytes)
    
    # Criptografa o dado, convertendo-o para bytes
    token = fernet.encrypt(dado.encode())
    print(token.decode())
    
    # Retorna o token como string
    return token.decode()

gerar_token("G7c9N5lbR3xVzY2P0KfXtQq8mLsTu1vJfGhI3oRpL0Y=", "Mz7vQ3kN1sU0tW5aX2hR9pE4dL6yF8bG1nH7cV2mJ5qT0zY3rC9oI4uK6eP8sL1tN7dR2wX5gH0xP6rK8sD4nB1mC3qW7vZ9tL2Y")