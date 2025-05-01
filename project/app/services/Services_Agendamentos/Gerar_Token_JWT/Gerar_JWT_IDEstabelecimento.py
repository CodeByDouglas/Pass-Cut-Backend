import os
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def gerar_jwt_id_estabelecimento(estabelecimento_id: str, exp_minutes: int = 60) -> str:
    """
    Gera um JWT contendo o id do estabelecimento e um exp para validade do token.
    
    Parameters:
        estabelecimento_id (str): O ID do estabelecimento.
        exp_minutes (int, optional): Tempo de expiração em minutos (padrão 60).
        
    Returns:
        str: O token JWT.
    """
    secret = os.getenv("SECRET_KEY_ID_ESTABELECIMENTO")
    if not secret:
        raise ValueError("SECRET_KEY_ID_ESTABELECIMENTO não está definida nas variáveis de ambiente.")
    
    payload = {
        "id": estabelecimento_id,
        "exp": datetime.utcnow() + timedelta(minutes=exp_minutes)
    }
    
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token