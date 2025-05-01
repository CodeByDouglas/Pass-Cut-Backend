import os
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

def gerar_jwt_id_estabelecimento(cliente_id: str, exp_minutes: int = 60) -> str:
    """
    Gera um JWT contendo o id do cliente e um exp para validade do token.
    
    Parameters:
        Cliente_id (str): O ID do cliente.
        exp_minutes (int, optional): Tempo de expiração em minutos (padrão 60).
        
    Returns:
        str: O token JWT.
    """
    secret = os.getenv("SECRET_KEY_ID_USER")
    if not secret:
        raise ValueError("SECRET_KEY_ID_USER não está definida nas variáveis de ambiente.")
    
    payload = {
        "id": cliente_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=exp_minutes)
    }
    
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token

