import os
from dotenv import load_dotenv

load_dotenv()

def validar_token_inicial(token: str) -> bool:
    expected_token = os.getenv("TOKEN_INICAL")
    return token == expected_token